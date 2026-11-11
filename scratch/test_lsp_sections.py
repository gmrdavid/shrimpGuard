import subprocess
import json
import os
import time

server_path = r"C:\Users\gliam\AppData\Local\Programs\Microsoft VS Code\c4453f8ea4\resources\app\extensions\css-language-features\server\dist\node\cssServerMain.js"

with open("static/css/style.css", "r", encoding="utf-8") as f:
    full_lines = f.readlines()

def check_css_snippet(snippet_text, label="snippet"):
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

    doc_uri = f"file:///c:/chunk_{hash(label)}.css"
    send_msg({
        "jsonrpc": "2.0",
        "method": "textDocument/didOpen",
        "params": {
            "textDocument": {
                "uri": doc_uri,
                "languageId": "css",
                "version": 1,
                "text": snippet_text
            }
        }
    })

    diags_received = []
    start_time = time.time()
    while time.time() - start_time < 4:
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
                        "hexColorLength": "error",
                        "unknownAtRules": "error"
                    }
                }]
            })
        elif msg.get("method") == "textDocument/publishDiagnostics":
            diags = msg.get("params", {}).get("diagnostics", [])
            diags_received = diags
            break

    proc.terminate()
    return diags_received

# Let's test the recent additions specifically (lines 23500 to end)
recent_text = "".join(full_lines[23500:])
print(f"Testing lines 23501-{len(full_lines)} ({len(recent_text)} chars)...")
diags = check_css_snippet(recent_text, "recent")
print(f"Diagnostics for recent section: {len(diags)}")
for d in diags:
    print(d)
