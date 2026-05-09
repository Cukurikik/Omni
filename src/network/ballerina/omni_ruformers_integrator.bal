// OMNI Framework - Ballerina REST Integration for Ruformers
import ballerina/http;
import ballerina/log;

// Connects to the internal Python FastAPI/Flask backend
http:Client ruformersClient = check new ("http://omni-ruformers-compute:8080");

service /api/nlp on new http:Listener(9090) {

    resource function post classify(@http:Payload json payload) returns json|error {
        log:printInfo("OMNI: Received classification request for Ruformers");
        
        http:Response backendResponse = check ruformersClient->post("/predict", payload);
        json result = check backendResponse.getJsonPayload();
        
        return {
            "status": "success",
            "engine": "OMNI Ballerina Gateway -> Ruformers",
            "data": result
        };
    }
}
