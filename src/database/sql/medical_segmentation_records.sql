CREATE TABLE medical_segmentation_records (
    id UUID PRIMARY KEY,
    scan_id VARCHAR(255) NOT NULL,
    segmentation_mask_url TEXT NOT NULL,
    confidence_score FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
