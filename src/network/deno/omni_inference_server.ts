// OMNI Mobile Backend Layer — Deno Inference API Server
// Edge-optimized inference server with Deno's built-in security model.

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
};

interface InferRequest {
  prompt: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
}

interface InferResponse {
  request_id: string;
  generated_text: string;
  tokens_generated: number;
  latency_ms: number;
  finish_reason: string;
}

let totalRequests = 0;
let totalLatencyMs = 0;

async function handleInference(req: Request): Promise<Response> {
  const start = performance.now();
  totalRequests++;

  try {
    const body: InferRequest = await req.json();
    if (!body.prompt) {
      return new Response(JSON.stringify({ error: "prompt required" }), {
        status: 400, headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
      });
    }

    // Production: forward to inference engine
    const result: InferResponse = {
      request_id: crypto.randomUUID(),
      generated_text: `Response for: ${body.prompt.slice(0, 100)}`,
      tokens_generated: body.max_tokens || 256,
      latency_ms: performance.now() - start,
      finish_reason: "stop",
    };

    totalLatencyMs += result.latency_ms;
    return new Response(JSON.stringify(result), {
      headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), {
      status: 500, headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
    });
  }
}

function handleHealth(): Response {
  return new Response(JSON.stringify({
    status: "healthy",
    total_requests: totalRequests,
    avg_latency_ms: totalRequests > 0 ? totalLatencyMs / totalRequests : 0,
    runtime: "deno",
    version: Deno.version.deno,
  }), { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } });
}

Deno.serve({ port: 8080 }, async (req: Request) => {
  const url = new URL(req.url);
  if (req.method === "OPTIONS") return new Response(null, { headers: CORS_HEADERS });
  if (url.pathname === "/api/v1/infer" && req.method === "POST") return handleInference(req);
  if (url.pathname === "/api/v1/health") return handleHealth();
  return new Response("Not Found", { status: 404 });
});

console.log("OMNI Deno Inference Server running on :8080");
