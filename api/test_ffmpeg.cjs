const http = require('http');

function simulateRequest(toolId, endpoint) {
    return new Promise((resolve) => {
        const boundary = '----OMNITESTBOUNDARY' + Math.random().toString(36).substring(2);
        const options = {
            hostname: 'localhost',
            port: 3000,
            path: `${endpoint}?tool_id=${toolId}`,
            method: 'POST',
            headers: {
                'Content-Type': `multipart/form-data; boundary=${boundary}`,
                'X-OMNI-KEY': 'TEST_BATTLE_KEY'
            }
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try {
                        const json = JSON.parse(data);
                        console.log(`✅ Success for ${toolId} (${endpoint}): ${data.substring(0, 150)}...`);
                        resolve(json.data ? (json.data.job_id || json.data.base_id) : "OK");
                    } catch (e) {
                        console.log(`✅ Success (but not JSON) for ${toolId}: ${data.substring(0, 50)}`);
                        resolve("OK");
                    }
                } else {
                    console.error(`❌ Request failed for ${toolId} (${endpoint}): ${res.statusCode} ${data}`);
                    resolve(null);
                }
            });
        });

        // Use 'omni_file' to pass FileQuarantineHandler
        const body = Buffer.concat([
            Buffer.from(`--${boundary}\r\n`),
            Buffer.from(`Content-Disposition: form-data; name="omni_file"; filename="test.mp4"\r\n`),
            Buffer.from(`Content-Type: video/mp4\r\n\r\n`),
            Buffer.from("FAKEVIDEO_CONTENT_ENOUGH_FOR_MAGIC"),
            Buffer.from(`\r\n--${boundary}--\r\n`),
            Buffer.from(`--${boundary}\r\n`),
            Buffer.from(`Content-Disposition: form-data; name="tool_id"\r\n\r\n`),
            Buffer.from(toolId),
            Buffer.from(`\r\n--${boundary}--\r\n`)
        ]);

        req.write(body);
        req.end();
    });
}

async function run() {
    console.log("🛡️ Starting Authenticated Infrastructure Test (Port 3000)...");
    
    // Testing the Async path
    console.log("\n[TEST 1] Async Path (/api/v1/process)");
    await simulateRequest('video_to_mp4', '/api/v1/process');
    
    // Note: Since Test 1 is async, we may need to wait for its log.
}

run();
