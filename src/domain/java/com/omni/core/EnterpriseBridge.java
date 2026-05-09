package com.omni.core;

import java.util.logging.Logger;

/**
 * OMNI MOTHER: Enterprise Java Spring Bridge (Production Grade)
 * Connects legacy JVM monolithic systems to the Omni Polyglot Network.
 */
public class EnterpriseBridge {
    private static final Logger logger = Logger.getLogger(EnterpriseBridge.class.getName());
    
    private final LegacyAdapter legacyAdapter;

    public EnterpriseBridge(LegacyAdapter legacyAdapter) {
        this.legacyAdapter = legacyAdapter;
    }

    public String dispatchToLegacy(String payload) {
        logger.info("[OMNI JAVA] Dispatching payload to legacy JVM system.");
        try {
            return legacyAdapter.processSOAP(payload);
        } catch (Exception e) {
            logger.severe("[OMNI JAVA] Legacy dispatch failed: " + e.getMessage());
            throw new RuntimeException("Bridge Failure", e);
        }
    }
}
