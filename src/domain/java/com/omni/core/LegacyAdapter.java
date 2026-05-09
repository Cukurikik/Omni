package com.omni.core;

import java.util.UUID;

/**
 * OMNI MOTHER: Legacy SOAP Adapter Mock (Production Grade)
 */
public class LegacyAdapter {
    
    public String processSOAP(String requestXml) throws Exception {
        if (requestXml == null || requestXml.trim().isEmpty()) {
            throw new IllegalArgumentException("Empty XML Payload");
        }
        
        // Simulating heavy XML parsing and legacy DB hit
        Thread.sleep(150); 
        
        return "<response><status>200</status><id>" + UUID.randomUUID() + "</id></response>";
    }
}
