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
            "textDocument": {
                "publishDiagnostics": { "relatedInformation": True }
            },
            "workspace": {
                "configuration": True
            }
        }
    }
})

resp = read_msg()

send_msg({
    "jsonrpc": "2.0",
    "method": "initialized",
    "params": {}
})

# Send configuration
send_msg({
    "jsonrpc": "2.0",
    "method": "workspace/didChangeConfiguration",
    "params": {
        "settings": {
            "css": {
                "validate": True,
                "lint": {
                    "compatibleVendorPrefixes": "warning",
                    "vendorPrefix": "warning",
                    "duplicateProperties": "warning",
                    "emptyRules": "warning",
                    "importStatement": "warning",
                    "boxModel": "warning",
                    "universalSelector": "warning",
                    "zeroUnits": "warning",
                    "fontFaceProperties": "warning",
                    "hexColorLength": "error",
                    "argumentsInColorFunction": "error",
                    "unknownProperties": "error",
                    "ieHack": "warning",
                    "unknownVendorSpecificProperties": "warning",
                    "propertyIgnoredDueToDisplay": "warning",
                    "important": "warning",
                    "float": "warning",
                    "idSelector": "warning",
                    "unknownAtRules": "error"
                }
            }
        }
    }
})

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
while time.time() - start_time < 10:
    msg = read_msg()
    if not msg:
        break
    # Server might request workspace/configuration
    if msg.get("method") == "workspace/configuration":
        req_id = msg.get("id")
        # Reply with config
        items = msg.get("params", {}).get("items", [])
        result = []
        for it in items:
            section = it.get("section")
            if section == "css":
                result.append({
                    "validate": True,
                    "lint": {
                        "unknownProperties": "error",
                        "unknownAtRules": "error"
                    }
                })
            else:
                result.append({})
        send_msg({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result
        })
    elif msg.get("method") == "textDocument/publishDiagnostics":
        diags = msg.get("params", {}).get("diagnostics", [])
        print(f"\n--- Total Diagnostics with Lint: {len(diags)} ---")
        for d in diags:
            sev = {1: "ERROR", 2: "WARNING", 3: "INFO", 4: "HINT"}.get(d.get("severity"), "UNKNOWN")
            rng = d.get("range", {})
            start_l = rng.get("start", {}).get("line", 0) + 1
            start_c = rng.get("start", {}).get("character", 0) + 1
            print(f"[{sev}] Line {start_l}:{start_c} - ({d.get('code', '')}) {d.get('message')}")
        break

proc.terminate()
