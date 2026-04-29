class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class RobotsTxtPolicy
  def self.can_crawl(url, robots_content)
    if url.nil? || robots_content.nil?
      return OmniResult.new(error: "Missing URL or robots.txt")
    end
    
    # Ruby logic for robots.txt parsing and compliance
    is_allowed = !robots_content.include?("Disallow: #{url}")
    
    OmniResult.new(value: is_allowed)
  end
end
