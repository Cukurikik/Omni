-- OMNI MMDETECTION: Annotation Store
-- SQL schema designed to store COCO-format bounding box annotations for model training.
-- Source: open-mmlab/mmdetection

CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    dataset_id INT REFERENCES datasets(id) ON DELETE CASCADE,
    name VARCHAR(64) NOT NULL,
    supercategory VARCHAR(64),
    UNIQUE(dataset_id, name)
);

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    dataset_id INT REFERENCES datasets(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    width INT NOT NULL,
    height INT NOT NULL,
    date_captured TIMESTAMP WITH TIME ZONE,
    UNIQUE(dataset_id, file_name)
);

CREATE TABLE IF NOT EXISTS annotations (
    id BIGSERIAL PRIMARY KEY,
    image_id INT NOT NULL REFERENCES images(id) ON DELETE CASCADE,
    category_id INT NOT NULL REFERENCES categories(id),
    -- COCO format: [x_top_left, y_top_left, width, height]
    bbox_x DOUBLE PRECISION NOT NULL,
    bbox_y DOUBLE PRECISION NOT NULL,
    bbox_w DOUBLE PRECISION NOT NULL,
    bbox_h DOUBLE PRECISION NOT NULL,
    area DOUBLE PRECISION NOT NULL,
    iscrowd INT DEFAULT 0
);

-- Indexing for fast dataset compilation
CREATE INDEX idx_anno_image ON annotations(image_id);
CREATE INDEX idx_anno_category ON annotations(category_id);
