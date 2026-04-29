# Omni BlossomLM Data Service (Ruby)
module Omni; module BlossomLM
  def self.quality_filter(samples, min_len: 20, max_len: 4096)
    samples.select { |s| words = s[:text].split.size; words >= min_len && words <= max_len }
  end
  def self.dedup(samples)
    require 'digest'
    seen = Set.new; samples.select { |s| h = Digest::MD5.hexdigest(s[:text]); seen.add?(h) }
  end
end; end
