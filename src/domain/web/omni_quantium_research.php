<?php

namespace Omni\Business\Quant;

use Exception;

/**
 * Quantium AI Research: Experiments exploring uncommon quant techniques.
 * Business Layer: PHP API integration for submitting multi-dimensional financial 
 * datasets into the OMNI HMM/LSTM/Transformer hybrid engine.
 */
class QuantiumResearchEngine
{
    private string $omniSocketPath;

    public function __construct(string $socketPath = '/tmp/omni_quant.sock')
    {
        $this->omniSocketPath = $socketPath;
    }

    /**
     * Dispatches a time-series pricing sequence into the Quantitative engine.
     * Enforces strict typing and monadic-style exception propagation.
     */
    public function evaluateStrategy(array $priceSeries, string $modelType): array
    {
        $allowedModels = ['hmm_hybrid', 'lstm_attention', 'transformer_pure'];
        if (!in_array($modelType, $allowedModels)) {
            throw new Exception("Unsupported quant model technique: {$modelType}");
        }

        $payload = json_encode([
            'action' => 'evaluate',
            'model' => $modelType,
            'data' => $priceSeries,
            'timestamp' => time()
        ]);

        return $this->dispatchToSocket($payload);
    }

    private function dispatchToSocket(string $payload): array
    {
        $socket = @fsockopen("unix://" . $this->omniSocketPath, -1, $errorCode, $errorString, 5);
        if (!$socket) {
            throw new Exception("Omni Engine IPC failure: [$errorCode] $errorString");
        }

        fwrite($socket, $payload . "\n");
        
        $response = '';
        while (!feof($socket)) {
            $response .= fgets($socket, 1024);
        }
        fclose($socket);

        $decoded = json_decode($response, true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception("Invalid JSON returned from Omni Engine.");
        }

        return $decoded;
    }
}
