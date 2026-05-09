<?php
// OMNI API & Routing Layer
// Laravel API Gateway
// Based on laravel/laravel. Exposes a clean REST API for external clients 
// to access the Omni Engine's ML models, bridging PHP to the Go/Rust subsystems.

namespace App\Http\Controllers\Omni;

use Illuminate\Http\Request;
use Illuminate\Routing\Controller;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Http;

class OmniLaravelApiGateway extends Controller
{
    private string $goMicroserviceUrl;

    public function __construct()
    {
        // Route heavy compute requests to the Omni Go/Rust networking layer
        $this->goMicroserviceUrl = config('omni.internal_gateway_url', 'http://127.0.0.1:8080');
    }

    /**
     * Endpoint: POST /api/omni/infer
     */
    public function infer(Request $request)
    {
        $validated = $request->validate([
            'model' => 'required|string',
            'inputs' => 'required|array',
        ]);

        Log::info("OMNI Laravel: Routing inference request for model: " . $validated['model']);

        try {
            // Forward request to the high-performance Go router which handles the C-ABI
            $response = Http::timeout(10)->post("{$this->goMicroserviceUrl}/v1/infer", [
                'model' => $validated['model'],
                'inputs' => $validated['inputs']
            ]);

            if ($response->successful()) {
                return response()->json([
                    'status' => 'success',
                    'data' => $response->json()
                ]);
            }

            Log::warning("OMNI Laravel: Engine returned non-200 status.", ['status' => $response->status()]);
            return response()->json([
                'status' => 'error',
                'message' => 'Omni Engine failed to process the request'
            ], $response->status());

        } catch (\Exception $e) {
            Log::error("OMNI Laravel: Gateway timeout or connection refused: " . $e->getMessage());
            return response()->json([
                'status' => 'error',
                'message' => 'Service temporarily unavailable. Check Omni Go Gateway.'
            ], 503);
        }
    }
}
