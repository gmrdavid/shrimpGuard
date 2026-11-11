import subprocess
import json
import os
import time

server_path = r"C:\Users\gliam\AppData\Local\Programs\Microsoft VS Code\c4453f8ea4\resources\app\extensions\css-language-features\server\dist\node\cssServerMain.js"

proc = subprocess.Popen(
    ["node", server_path, "--stdio"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    bufsize=0
)

def send_msg(obj):
    body = json.dumps(obj)
    msg = f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n{body}"
    proc.stdin.write(msg.encode('utf-8'))
    proc.stdin.flush()

def read_msg():
    header = b""
    while not header.endswith(b"\r\n\r\n"):
        c = proc.stdout.read(1)
        if not c:
            return None
        header += c
    header_str = header.decode('utf-8')
    content_len = None
    for line in header_str.split("\r\n"):
        if line.lower().startswith("content-length:"):
            content_len = int(line.split(":")[1].strip())
            break
    if content_len is None:
        return None
    body = proc.stdout.read(content_len)
    return json.loads(body.decode('utf-8'))

send_msg({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "processId": os.getpid(),
        "rootUri": f"file:///{os.path.abspath('.').replace(os.sep, '/')}",
        "capabilities": {
            "textDocument": {
                "publishDiagnostics": { "relatedInformation": True }
            },
            "workspace": { "configuration": True }
        }
    }
})

resp = read_msg()
send_msg({ "jsonrpc": "2.0", "method": "initialized", "params": {} })

send_msg({
    "jsonrpc": "2.0",
    "method": "textDocument/didOpen",
    "params": {
        "textDocument": {
            "uri": "file:///c:/test.css",
            "languageId": "css",
            "version": 1,
            "text": "body { invalidprop: 10px; color: #12345; calc(100%-20px); }"
        }
    }
})

start_time = time.time()
while time.time() - start_time < 5:
    msg = read_msg()
    if not msg:
        break
    if msg.get("method") == "workspace/configuration":
        req_id = msg.get("id")
        send_msg({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": [{
                "validate": True,
                "lint": {
                    "unknownProperties": "error",
                    "hexColorLength": "error"
                }
            }]
        })
    elif msg.get("method") == "textDocument/publishDiagnostics":
        diags = msg.get("params", {}).get("diagnostics", [])
        print(f"Test diagnostics count: {len(diags)}")
        for d in diags:
            print("DIAG:", d)
        break

proc.terminate()
