"""
{
   "_id":"wit_2SsDeym4aq10vUTorJll4G",
   "cache":{

   },
   "request":{
      "bodySize":0,
      "cookies":[

      ],
      "headers":[
         {
            "name":"Sec-Fetch-Mode",
            "value":"no-cors"
         },
         {
            "name":"Sec-Fetch-Dest",
            "value":"empty"
         },
         {
            "name":"User-Agent",
            "value":"chromedriver"
         },
         {
            "name":"Accept-Encoding",
            "value":"gzip, deflate"
         },
         {
            "name":"Connection",
            "value":"keep-alive"
         },
         {
            "name":"Host",
            "value":"localhost:60087"
         },
         {
            "name":"Sec-Fetch-Site",
            "value":"none"
         }
      ],
      "headersSize":-1,
      "httpVersion":"HTTP/1.1",
      "method":"GET",
      "queryString":[

      ],
      "url":"/json/list"
   },
   "response":{
      "bodySize":347,
      "content":{
         "mimeType":"application/json",
         "size":347,
         "text":"[ {\n""   \"description\": \"\",\n""   ""\"devtoolsFrontendUrl\": ""\"/devtools/inspector.html?ws=localhost:60087/devtools/page/68152735C89E2BED4E135DA57A8F017D\",\n""   \"id\": ""\"68152735C89E2BED4E135DA57A8F017D\",\n""   \"title\": \"\",\n""   \"type\": \"page\",\n""   \"url\": \"data:,\",\n""   ""\"webSocketDebuggerUrl\": ""\"ws://localhost:60087/devtools/page/68152735C89E2BED4E135DA57A8F017D\"\n""} ]\n"
      },
      "cookies":[

      ],
      "headers":[
         {
            "name":"Content-Type",
            "value":"application/json; ""charset=UTF-8"
         },
         {
            "name":"Content-Length",
            "value":"347"
         }
      ],
      "headersSize":-1,
      "httpVersion":"HTTP/1.1",
      "redirectURL":"",
      "status":200,
      "statusText":"OK"
   },
   "startedDateTime":"2021-09-14T20:27:00.581328-07:00",
   "time":0.169,
   "timings":{
      "receive":0,
      "send":0,
      "wait":0.169
   }
}
"""

from pydantic import BaseModel
from typing import Any, Optional


class Request(BaseModel):
    url: str
    method: str


class Response(BaseModel):
    status: int
    text: Optional[Any]


class Entry(BaseModel):
    request: Request
    response: Response
    time: float
