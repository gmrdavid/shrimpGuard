const ts = require('C:\\Users\\gliam\\AppData\\Local\\Programs\\Microsoft VS Code\\6bab64e2d1\\resources\\app\\extensions\\node_modules\\typescript\\lib\\typescript.js');
const fs = require('fs');

const code = fs.readFileSync('static/js/monitoring.js', 'utf8');
const sourceFile = ts.createSourceFile('monitoring.js', code, ts.ScriptTarget.Latest, true);

const program = ts.createProgram({
    rootNames: ['static/js/monitoring.js'],
    options: {
        allowJs: true,
        checkJs: true,
        noEmit: true,
        target: ts.ScriptTarget.Latest
    }
});

const diagnostics = ts.getPreEmitDiagnostics(program, sourceFile);
console.log('Total TS diagnostics on monitoring.js:', diagnostics.length);
diagnostics.slice(0, 10).forEach(d => {
    const { line, character } = sourceFile.getLineAndCharacterOfPosition(d.start);
    console.log(`Line ${line + 1}, Col ${character + 1}: ${ts.flattenDiagnosticMessageText(d.messageText, '\n')}`);
});
