// node_test.js
const http = require('http');
http.createServer((req, res) => { res.end('NodeJS Response'); }).listen(3000);
console.log("Node.js Server ready to be crushed");
