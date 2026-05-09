# OMNI High-Performance Async HTTP Server in Nim
import asynchttpserver, asyncdispatch, json

var server = newAsyncHttpServer()

proc cb(req: Request) {.async.} =
  let headers = {"Content-type": "application/json"}
  if req.url.path == "/api/status":
    let response = %*{"status": "online", "framework": "OMNI Nim"}
    await req.respond(Http200, $response, headers.newHttpHeaders())
  else:
    let response = %*{"error": "Not Found"}
    await req.respond(Http404, $response, headers.newHttpHeaders())

echo "OMNI Nim Async Server starting on port 8080..."
waitFor server.serve(Port(8080), cb)
