// KG-RAG Explorer
package com.omni.kgrag

class OmniResult<T, E>(val isOk: Boolean, val value: T?, val error: E?)

class KGExplorer {
    fun formatNode(entityId: String, label: String): OmniResult<String, String> {
        if (entityId.isEmpty() || label.isEmpty()) {
            return OmniResult(false, null, "Entity ID and Label cannot be empty")
        }
        return OmniResult(true, "[$entityId]: $label", null)
    }
}
