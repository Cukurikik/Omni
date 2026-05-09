import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';

const app = express();
const PORT = process.env.OMNI_PORT || 3000;

// OMNI Gateway inspired by text-generator.io
// Proxies incoming requests to specialized internal clusters

app.use('/api/v1/vision', createProxyMiddleware({ 
    target: 'http://omni-vision-cluster:8081', 
    changeOrigin: true 
}));

app.use('/api/v1/tts', createProxyMiddleware({ 
    target: 'http://omni-audio-cluster:8082', 
    changeOrigin: true 
}));

app.get('/health', (req, res) => {
    res.status(200).json({ status: "OMNI TextGen API Gateway Online" });
});

app.listen(PORT, () => {
    console.log(`OMNI Gateway running on port ${PORT}`);
});
