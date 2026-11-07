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
const files = fs.readdirSync('templates')
    .filter(f => f.endsWith('.html'))
    .map(f => 'templates/' + f);

let results = {};

function handleMessage(data) {
    if (data.id === initId) {
        send({ jsonrpc: '2.0', method: 'initialized', params: {} });
        files.forEach((file, idx) => {
            const filePath = path.resolve(file);
            const text = fs.readFileSync(filePath, 'utf8');
            send({
                jsonrpc: '2.0',
                method: 'textDocument/didOpen',
                params: {
                    textDocument: {
                        uri: 'file:///' + filePath.replace(/\\/g, '/'),
                        languageId: 'html',
                        version: idx + 1,
                        text: text
                    }
                }
            });
        });
    }

    if (data.method === 'textDocument/publishDiagnostics') {
        const diags = data.params.diagnostics;
        const shortName = path.basename(data.params.uri);
        results[shortName] = diags;
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

setTimeout(() => {
    let total = 0;
    console.log('=== SUMMARY OF HTML DIAGNOSTICS ===');
    for (const [f, diags] of Object.entries(results)) {
        if (diags.length > 0) {
            console.log(`${f}: ${diags.length} problems`);
            diags.forEach((d, i) => {
                console.log(`  [${i+1}] Line ${d.range.start.line + 1}, Col ${d.range.start.character + 1}: ${d.message} (${d.code || d.source})`);
            });
            total += diags.length;
        }
    }
    console.log(`Total HTML problems across all templates: ${total}`);
    proc.kill();
    process.exit(0);
}, 4000);
