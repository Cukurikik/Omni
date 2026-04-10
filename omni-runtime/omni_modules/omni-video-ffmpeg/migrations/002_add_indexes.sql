-- omni-video-ffmpeg Add performance indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_video_ffmpeg_data_gin ON omni_video_ffmpeg_entities USING gin(data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_omni_video_ffmpeg_metadata_gin ON omni_video_ffmpeg_entities USING gin(metadata);