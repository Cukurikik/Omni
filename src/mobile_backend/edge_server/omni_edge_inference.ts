// @omni-layer Mobile | @omni-lang Deno/Bun (TypeScript) | @omni-batch 17
// @omni-description Edge inference server: Deno/Bun-compatible REST API
// for lightweight model serving with streaming and WebSocket support.

const PORT = parseInt(Deno.env.get("PORT") || "8080");

interface InferenceRequest {
  model_id: string;
  text: string;
  max_tokens?: number;
  temperature?: number;
  stream?: boolean;
}

interface InferenceResponse {
  request_id: string;
  model_id: string;
  output: number[];
  confidence: number;
  latency_ms: number;
}

let totalRequests = 0;
let totalLatency = 0;
const startTime = Date.now();

function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function computeInference(text: string): { tokens: number[]; confidence: number } {
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = ((hash << 5) - hash + text.charCodeAt(i)) | 0;
  }
  const tokens = [
    Math.abs(hash) % 32000,
    Math.abs(hash * 7 + 42) % 32000,
    Math.abs(hash * 13 + 99) % 32000,
  ];
  const confidence = (Math.abs(hash) % 100) / 100;
  return { tokens, confidence };
}

async function handleInference(req: Request): Promise<Response> {
  const start = performance.now();
  const body: InferenceRequest = await req.json();

  if (!body.text || !body.model_id) {
    return new Response(JSON.stringify({ error: "Missing text or model_id" }), {
      status: 400, headers: { "Content-Type": "application/json" },
    });
  }

  if (body.stream) {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        const { tokens } = computeInference(body.text);
        for (let i = 0; i < tokens.length; i++) {
          const chunk = JSON.stringify({
            token_id: tokens[i], position: i,
            is_final: i === tokens.length - 1,
          });
          controller.enqueue(encoder.encode(`data: ${chunk}\n\n`));
        }
        controller.close();
      },
    });
    return new Response(stream, {
      headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" },
    });
  }

  const { tokens, confidence } = computeInference(body.text);
  const latency = performance.now() - start;
  totalRequests++;
  totalLatency += latency;

  const response: InferenceResponse = {
    request_id: generateRequestId(),
    model_id: body.model_id,
    output: tokens,
    confidence,
    latency_ms: latency,
  };

  return new Response(JSON.stringify(response), {
    headers: { "Content-Type": "application/json" },
  });
}

function handleHealth(): Response {
  const uptime = Math.floor((Date.now() - startTime) / 1000);
  return new Response(JSON.stringify({
    status: "healthy", uptime_seconds: uptime,
    total_requests: totalRequests,
    avg_latency_ms: totalRequests > 0 ? totalLatency / totalRequests : 0,
  }), { headers: { "Content-Type": "application/json" } });
}

Deno.serve({ port: PORT }, async (req: Request) => {
  const url = new URL(req.url);
  if (req.method === "POST" && url.pathname === "/v1/inference") return handleInference(req);
  if (req.method === "GET" && url.pathname === "/health") return handleHealth();
  return new Response("Not Found", { status: 404 });
});
