# OMNI TikTik Domain Engine — Business Layer
# Absorbing abranhe/TikTik (Video sharing social network clone)
# Ruby DSL representing core micro-video networking business logic

module OmniTikTikDomain
  class VideoFeedService
    attr_reader :algorithm_weight, :requests

    def initialize(algorithm_weight: 1.5)
      @algorithm_weight = algorithm_weight
      @requests = 0
    end

    def generate_feed(user_id, base_videos, user_preferences)
      @requests += 1

      if base_videos.empty?
        return { ok: false, error: "TikTikError: No videos available" }
      end

      # Deterministic recommendation mapping
      # Score videos based on preference hash match
      scored_videos = base_videos.map do |video|
        score = 0.0
        
        # Match tags
        intersection = video[:tags] & user_preferences[:favorite_tags]
        score += intersection.size * @algorithm_weight
        
        # Decay older videos (simulated by video ID length mod 10 for deterministic logic)
        decay = (video[:id].to_s.length % 10) * 0.1
        final_score = [score - decay, 0.0].max
        
        { video_id: video[:id], score: final_score }
      end

      # Sort descending
      feed = scored_videos.sort_by { |v| -v[:score] }.map { |v| v[:video_id] }

      { ok: true, feed_ids: feed[0..10] }
    end

    def diagnostics
      { engine: "OmniTikTikDomain", requests: @requests, status: "Operational" }
    end
  end
end
