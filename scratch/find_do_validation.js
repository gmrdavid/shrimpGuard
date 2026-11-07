const fs = require('fs');

const content = fs.readFileSync('C:\\Users\\gliam\\AppData\\Local\\Programs\\Microsoft VS Code\\6bab64e2d1\\resources\\app\\extensions\\html-language-features\\server\\dist\\node\\htmlServerMain.js', 'utf8');

const regex = /doValidation/g;
let match;
while ((match = regex.exec(content)) !== null) {
    console.log('Match at index:', match.index);
    console.log(content.substring(match.index - 50, match.index + 100));
    console.log('---');
}
