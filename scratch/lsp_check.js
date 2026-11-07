const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const serverScript = 'C:\\Users\\gliam\\AppData\\Local\\Programs\\Microsoft VS Code\\6bab64e2d1\\resources\\app\\extensions\\html-language-features\\server\\dist\\node\\htmlServerMain.js';

const proc = spawn('node', [serverScript, '--stdio'], {
    stdio: ['pipe', 'pipe', 'inherit']
});

let buffer = '';

function send(msg) {
    const json = JSON.stringify(msg);
    const header = `Content-Length: ${Buffer.byteLength(json, 'utf8')}\r\n\r\n`;
    proc.stdin.write(header + json);
}

proc.stdout.on('data', (chunk) => {
    buffer += chunk.toString('utf8');
    while (true) {
        const headerEnd = buffer.indexOf('\r\n\r\n');
        if (headerEnd === -1) break;
        const header = buffer.substring(0, headerEnd);
        const match = header.match(/Content-Length:\s*(\d+)/i);
        if (!match) break;
        const contentLength = parseInt(match[1], 10);
        if (buffer.length < headerEnd + 4 + contentLength) break;
        const body = buffer.substring(headerEnd + 4, headerEnd + 4 + contentLength);
        buffer = buffer.substring(headerEnd + 4 + contentLength);
        try {
            const data = JSON.parse(body);
            handleMessage(data);
        } catch (e) {
            console.error('Error parsing:', e);
        }
    }
});

let initId = 1;

function handleMessage(data) {
    if (data.id === initId) {
        console.log('Server initialized!');
        send({ jsonrpc: '2.0', method: 'initialized', params: {} });

        // Open templates/devices.html
        const filePath = path.resolve('templates/devices.html');
        const text = fs.readFileSync(filePath, 'utf8');
        send({
            jsonrpc: '2.0',
            method: 'textDocument/didOpen',
            params: {
                textDocument: {
                    uri: 'file:///' + filePath.replace(/\\/g, '/'),
                    languageId: 'html',
                    version: 1,
                    text: text
                }
            }
        });
    }

    if (data.method === 'textDocument/publishDiagnostics') {
        console.log('=== DIAGNOSTICS FOR:', data.params.uri, '===');
        console.log(`Total problems: ${data.params.diagnostics.length}`);
        data.params.diagnostics.forEach((d, i) => {
            console.log(`[${i+1}] Line ${d.range.start.line + 1}, Col ${d.range.start.character + 1}: ${d.message} (${d.code || d.source})`);
        });
        setTimeout(() => proc.kill(), 500);
    }
}

send({
    jsonrpc: '2.0',
    id: initId,
    method: 'initialize',
    params: {
        processId: process.pid,
        rootUri: 'file:///' + path.resolve('.').replace(/\\/g, '/'),
        capabilities: {
            textDocument: {
                publishDiagnostics: { relatedInformation: true }
            }
        }
    }
});
