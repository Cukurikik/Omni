-- omni-video-ffmpeg Initial Migration
CREATE TABLE IF NOT EXISTS omni_video_ffmpeg_entities (
    id UUID PRIMARY KEY,
    data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    metadata JSONB
);
CREATE INDEX idx_omni_video_ffmpeg_status ON omni_video_ffmpeg_entities(status);
CREATE INDEX idx_omni_video_ffmpeg_created ON omni_video_ffmpeg_entities(created_at);