# RPG Diffusion content safety policy
package rpg.safety

default allow = true

deny {
    input.prompt_score < 0.2 # Below safety threshold
}
