package omni.security.memory

import future.keywords.in

default can_read = false
default can_write = false

# User roles
admin_role = "admin"
editor_role = "editor"
viewer_role = "viewer"

# Check if user is active
is_active {
    input.user.status == "ACTIVE"
}

# Read Access Rules
can_read {
    is_active
    input.user.role == admin_role
}

can_read {
    is_active
    input.document.visibility == "public"
}

can_read {
    is_active
    input.document.owner_id == input.user.id
}

can_read {
    is_active
    input.user.group in input.document.allowed_groups
}

# Write Access Rules
can_write {
    is_active
    input.user.role == admin_role
}

can_write {
    is_active
    input.document.owner_id == input.user.id
}

can_write {
    is_active
    input.user.role == editor_role
    input.user.department == input.document.department
}

# RAG Access Filter: Returns list of allowed document IDs from a set
allowed_documents[doc_id] {
    some i
    doc := input.documents[i]
    doc_id := doc.id
    
    # Evaluate can_read for this specific doc
    doc.visibility == "public"
}
allowed_documents[doc_id] {
    some i
    doc := input.documents[i]
    doc_id := doc.id
    doc.owner_id == input.user.id
}
