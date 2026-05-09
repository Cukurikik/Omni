<?php
//=============================================================================
// OMNI DOMAIN LAYER — DICOM GRAPHQL BRIDGE (PHP)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Legacy PHP interface bridging into the Omni GraphQL Domain 
//              for accessing DICOM metadata parsed by Rust/Ruby.
//=============================================================================

namespace Omni\Domain\Medical;

use Exception;

class DicomGraphQLBridge {
    private string $graphqlEndpoint;

    public function __construct(string $endpoint = "http://localhost:8080/graphql") {
        $this->graphqlEndpoint = $endpoint;
    }

    public function getPatientScanDetails(string $patientId): ?array {
        $query = '
            query($id: ID!) {
                getReconstructionJob(id: $id) {
                    patientId
                    status
                    inputResolution
                    startTime
                }
            }
        ';

        $payload = [
            'query' => $query,
            'variables' => ['id' => $patientId]
        ];

        return $this->executeRequest($payload);
    }

    private function executeRequest(array $payload): ?array {
        // Zero-mock curl execution to Omni Go router
        $ch = curl_init($this->graphqlEndpoint);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        
        $response = curl_exec($ch);
        
        if (curl_errno($ch)) {
            throw new Exception("Omni Bridge Error: " . curl_error($ch));
        }
        
        curl_close($ch);
        
        $decoded = json_decode($response, true);
        return $decoded['data'] ?? null;
    }
}
