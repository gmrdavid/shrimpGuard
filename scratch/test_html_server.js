const fs = require('fs');
const path = require('path');

const htmlServerPath = 'C:\\Users\\gliam\\AppData\\Local\\Programs\\Microsoft VS Code\\6bab64e2d1\\resources\\app\\extensions\\html-language-features\\server\\dist\\node\\htmlServerMain.js';

console.log('Testing HTML server load...');
const content = fs.readFileSync(htmlServerPath, 'utf8');
console.log('HTML server size:', content.length);
