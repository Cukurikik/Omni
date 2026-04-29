# Omni REFLECT Service (Ruby)
# Ref: real-stanford/reflect — CoRL 2023
module Omni
  module ReflectService
    Correction = Struct.new(:failure_type, :suggestions, keyword_init: true)
    CORRECTIONS = {
      'grasp_fail' => ['Adjust gripper force', 'Re-estimate pose', 'Try different grasp point'],
      'navigation_fail' => ['Replan path', 'Check for obstacles', 'Reduce speed'],
      'perception_fail' => ['Increase exposure', 'Move closer', 'Switch sensor'],
    }.freeze
    def self.suggest(failure_type)
      Correction.new(failure_type: failure_type,
                     suggestions: CORRECTIONS.fetch(failure_type, ['Retry with different parameters']))
    end
  end
end
