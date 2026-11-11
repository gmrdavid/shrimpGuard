import subprocess
import json
import os
import time

server_path = r"C:\Users\gliam\AppData\Local\Programs\Microsoft VS Code\c4453f8ea4\resources\app\extensions\css-language-features\server\dist\node\cssServerMain.js"
css_file = os.path.abspath("static/css/style.css")

with open(css_file, "r", encoding="utf-8") as f:
    css_text = f.read()

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
            "textDocument": { "publishDiagnostics": { "relatedInformation": True } },
            "workspace": { "configuration": True }
        }
    }
})

read_msg()
send_msg({ "jsonrpc": "2.0", "method": "initialized", "params": {} })

file_uri = f"file:///{css_file.replace(os.sep, '/')}"
send_msg({
    "jsonrpc": "2.0",
    "method": "textDocument/didOpen",
    "params": {
        "textDocument": {
            "uri": file_uri,
            "languageId": "css",
            "version": 1,
            "text": css_text
        }
    }
})

start_time = time.time()
while time.time() - start_time < 8:
    msg = read_msg()
    if not msg:
        break
    method = msg.get("method")
    if method == "workspace/configuration":
        req_id = msg.get("id")
        items = msg.get("params", {}).get("items", [])
        res = []
        for it in items:
            res.append({
                "validate": True,
                "lint": {
                    "unknownProperties": "error",
                    "duplicateProperties": "warning",
                    "emptyRules": "warning",
                    "hexColorLength": "error"
                }
            })
        send_msg({ "jsonrpc": "2.0", "id": req_id, "result": res })
    elif method == "textDocument/publishDiagnostics":
        diags = msg.get("params", {}).get("diagnostics", [])
        print(f"publishDiagnostics received: {len(diags)} items")
        for d in diags:
            code = d.get('code')
            sev = d.get('severity')
            msg_text = d.get('message')
            rng = d.get('range', {})
            line = rng.get('start', {}).get('line', 0) + 1
            col = rng.get('start', {}).get('character', 0) + 1
            print(f"Line {line}:{col} [{sev}] ({code}): {msg_text}")
    else:
        print("Other msg:", msg.get("method") or msg.get("id"))

proc.terminate()
