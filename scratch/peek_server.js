const fs = require('fs');
const content = fs.readFileSync('C:\\Users\\gliam\\AppData\\Local\\Programs\\Microsoft VS Code\\6bab64e2d1\\resources\\app\\extensions\\css-language-features\\server\\dist\\node\\cssServerMain.js', 'utf8');
console.log(content.substring(0, 300));
