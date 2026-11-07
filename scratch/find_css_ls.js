const fs = require('fs');
const content = fs.readFileSync('C:\\Users\\gliam\\AppData\\Local\\Programs\\Microsoft VS Code\\6bab64e2d1\\resources\\app\\extensions\\css-language-features\\server\\dist\\node\\cssServerMain.js', 'utf8');

const regex = /getCSSLanguageService/g;
let m;
while ((m = regex.exec(content)) !== null) {
    console.log(content.substring(m.index - 50, m.index + 100));
}
