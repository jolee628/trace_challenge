import ijson, requests, collections, statistics
from pprint import pprint
from uuid import UUID
from models import Entry, Response, Request
from collections import defaultdict


class TrieNode:
    def __init__(self):
        self.children = {} # {"session": {"guid": {"window": rest_of_window_path, "elements": rest_of_element_path}}}
        self.count = 0
        self.total_time = 0
        self.avg_time = 0
        self.response_count = defaultdict(int)
        self.unique_response_set = set()


class Trie:
    """
                                 root
                              /        \
                           GET         POST
                       /    /           /
                session    json       session
                   /       count: x
                  |        total_time: x
                {guid}
                /
            element
               /
            {guid}
                /
                selected
                count: x
                total_time: x

    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, entry: Entry):
        cur = self.root
        method = entry.request.method
        path = entry.request.url
        time = entry.time

        # filter out empty string
        path = list(filter(None, path.split("/")))

        # create a set of path for quick look up later
        path_set = set(path)

        if method not in cur.children:
            cur.children[method] = TrieNode()

        cur = cur.children[method]
        for i, component in enumerate(path):
            final_component_path = str()

            # try-except block to capture hard-coded variable values and set to final_component_path variable
            try:
                # check if it's uuid
                _ = UUID(component)
                final_component_path = "{guid}"
            except ValueError:
                if i == len(path) - 1 and "assets" in path_set:
                    final_component_path = "{file_name}"

                if "sockjs-node" in path_set:
                    if "websocket" in path_set and 0 < i < len(path) - 1:
                        final_component_path = "{id}"
                    elif i != 0 and "info" in component:
                        final_component_path = "info"

            # if final_component_path is still none, that means it's a resource url path
            if not final_component_path:
                final_component_path = component

            if final_component_path not in cur.children:
                cur.children[final_component_path] = TrieNode()
            cur = cur.children[final_component_path]

        cur.count += 1
        cur.total_time += time
        cur.avg_time = cur.total_time // cur.count
        cur.response_count[entry.response.status] += 1
        if entry.response.text:
            cur.unique_response_set.add(entry.response.text)

    def print_trie(self, node=None, path=None):
        # Start from root node if none specified
        if node is None:
            node = self.root
        if path is None:
            path = []

        # Print the current path and the associated node data
        if node.count > 0:  # Only print nodes that have been visited
            print(f"Path: {'/'.join(path)}")
            print(f"  Count: {node.count}")
            print(f"  Total Time: {node.total_time}")
            print(f"  Avg Time: {node.avg_time}")
            print(f"  Response Stats: {dict(node.response_count)}")
            print(f"  Responses: {len(node.unique_response_set)}")

            if len(node.unique_response_set):
                duplicated_response_rate = ((node.count - len(node.unique_response_set)) / node.count) * 100
                print(f"  Duplicated Response Rate: {round(duplicated_response_rate,2)}%")

            print(f"\n\n")

        # Recursively print each child
        for child_component, child_node in node.children.items():
            self.print_trie(child_node, path + [child_component])


class TraceChallenge:

    def __init__(self):
        self.url_trie = Trie()

    @staticmethod
    def trace_count():
        counts = defaultdict(lambda: collections.defaultdict(int))
        method_set = set()
        with open("trace.har", "rb") as f:
            for entry in ijson.items(f, "log.entries.item"):
                method = entry["request"]["method"]
                method_set.add(method)
                response_code = entry["response"]["status"]
                counts[method][response_code] += 1

        pprint(dict(counts))

    def response_time_analytics(self):
        """
        Stats for the response time:
        1. GET - 200 - AVG / longest / shortest
        2. GET - Total - AVG / longest / shortest
        1. POST - 200 - AVG / longest / shortest
        2. GET - Total - AVG / longest / shortest
        :return:
        """
        response_time_dict = collections.defaultdict(list)
        with open("trace.har", "rb") as f:
            for entry in ijson.items(f, "log.entries.item"):
                method = entry["request"]["method"]
                response_time_ms = int(entry["time"])
                response_time_dict[method].append(response_time_ms)

        response_time_stats = dict()

        for method, times in response_time_dict.items():
            stats = dict()
            mean = statistics.mean(times)
            median = statistics.median(times)
            mode = statistics.mode(times)
            stats["mean"] = mean
            stats["median"] = median
            stats["mode"] = mode
            response_time_stats[method] = stats
        pprint(response_time_stats)

    def infer_path_params_and_stats(self):
        """
        1. Build a url trie
        2. count of each inferred param url
        3. Total and AVG time of each inferred param url
        4. Response stats - status_code: count
        5. Duplicated Response Rate to try to detect potential DoS / Spam
            5.a: (Potential Improvement, out of time to implement) - for a more accurate DoS/Spam, do something by looking at the time stamp

        Attempted:
        To print out the response and try to make sense of what they could be. But too many encoded
        and potentially encrypted strings and was hard to accomplish under 2 hours

        """
        with open("trace.har", "rb") as f:
            for entry in ijson.items(f, "log.entries.item"):
                url = entry["request"]["url"]
                method = entry["request"]["method"]
                request = Request(url=url, method=method)

                status = entry["response"]["status"]

                try:
                    text = entry["response"]["content"]["text"]
                except KeyError:
                    text = None

                response = Response(status=status, text=text)

                response_time = int(entry["time"])
                entry = Entry(request=request, response=response, time=response_time)
                self.url_trie.insert(entry)

        self.url_trie.print_trie()


tc = TraceChallenge()
tc.trace_count()
print()
tc.response_time_analytics()
print()
tc.infer_path_params_and_stats()
