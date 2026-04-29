package rules.hal9100

default command_override_allowed = false

command_override_allowed {
    input.commander == "Dave Bowman"
    input.mission_criticality < 9
    # Rego policy defining HAL-9100's primary operational directives and overrides
}
