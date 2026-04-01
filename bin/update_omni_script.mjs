import fs from 'fs';
import path from 'path';

const filePath = 'c:/Users/IKYY/Downloads/HEAVY-TOOLS/bin/omni.mjs';
const content = fs.readFileSync(filePath, 'utf8');

const newFunction = `async function simulateRequest(toolId) {
    return new Promise((resolve) => {
        const boundary = "----OmniFormBoundary" + Math.random().toString(16).substring(2);
        const filename = "test_stub.mp4";
        const fileContent = "DUMMY_FILE_CONTENT_FOR_OMNI_TEST";

        const postData = 
            "--" + boundary + "\\r\\n" +
            "Content-Disposition: form-data; name=\\\"omni_file\\\"; filename=\\\"" + filename + "\\\"\\r\\n" +
            "Content-Type: video/mp4\\r\\n\\r\n" +
            fileContent + "\\r\\n" +
            "--" + boundary + "--\\r\\n";

        const options = {
            hostname: 'localhost',
            port: 3000,
            path: "/api/v1/omni/execute?tool_id=" + toolId,
            method: 'POST',
            headers: {
                'Content-Type': "multipart/form-data; boundary=" + boundary,
                'Content-Length': Buffer.byteLength(postData),
                'X-OMNI-KEY': 'TEST_BATTLE_KEY',
            }
        };

        const req = http.request(options, (res) => {
            let data = "";
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    resolve(json.success);
                } catch (e) {
                    resolve(false);
                }
            });
        });

        req.on('error', (e) => resolve(false));
        req.write(postData);
        req.end();
    });
}`;

// Match from my marker or the old function signature down to the end of that block
// Using a simpler approach: splitting by markers
const lines = content.split('\n');
const startIndex = lines.findIndex(line => line.includes('// PROTOKOL OMNI-TEST: SOLUSI LANGSUNG KAPTEN'));
const nextFuncIndex = lines.findIndex(line => line.includes('async function pollJobStatus'));

if (startIndex !== -1 && nextFuncIndex !== -1) {
    const pre = lines.slice(0, startIndex - 1); // Remove the line 'async function simulateRequest(toolId) {' too
    const post = lines.slice(nextFuncIndex);
    const finalContent = pre.join('\n') + '\n\n' + newFunction + '\n\n' + post.join('\n');
    fs.writeFileSync(filePath, finalContent, 'utf8');
    console.log('SUCCESS: omni.mjs updated successfully.');
} else {
    console.error('FAILED: Markers not found.');
    process.exit(1);
}
