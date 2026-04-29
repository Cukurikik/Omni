# OpenAdapt RPA execution permissions
# Rego policy engine

package openadapt.authz

default allow = false

# Bound: Disallow clicking outside of screen bounds (1080p max assumption for policy)
allow {
    input.action == "mouse_click"
    input.x >= 0
    input.x <= 1920
    input.y >= 0
    input.y <= 1080
    input.user_role == "admin"
}

# Bound: Disallow sensitive keystrokes from automated agents
deny {
    input.action == "keyboard_input"
    input.key_code == "SUPER" # Windows/Command key block
}
