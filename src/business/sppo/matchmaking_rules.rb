class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class MatchmakingRules
  def self.can_match(player_a_elo, player_b_elo)
    if player_a_elo < 0 || player_b_elo < 0
      return OmniResult.new(error: "ELO cannot be negative")
    end
    
    # Ruby business logic for SPPO tournament matchmaking
    elo_diff = (player_a_elo - player_b_elo).abs
    can_play = elo_diff < 400
    
    OmniResult.new(value: can_play)
  end
end
