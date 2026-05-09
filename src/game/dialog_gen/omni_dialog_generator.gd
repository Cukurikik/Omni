# @omni-layer Game | @omni-lang GDScript | @omni-batch 18 | @omni-semester 16
# @omni-description Godot NPC dialog generator: transformer-driven procedural
# dialog with context tracking and personality modeling.

extends Node
class_name OmniDialogGenerator

var vocab_size: int = 8000
var context_window: int = 20
var dialog_history: Array = []
var npc_personalities: Dictionary = {}

class NPCPersonality:
    var name: String
    var traits: Dictionary = {}
    var knowledge: Array = []
    var mood: float = 0.5

    func _init(npc_name: String, trait_dict: Dictionary):
        name = npc_name
        traits = trait_dict
        mood = trait_dict.get("default_mood", 0.5)

func register_npc(npc_name: String, traits: Dictionary) -> void:
    var personality = NPCPersonality.new(npc_name, traits)
    npc_personalities[npc_name] = personality

func generate_response(npc_name: String, player_input: String) -> String:
    var personality = npc_personalities.get(npc_name)
    if personality == null:
        return "..."

    var input_tokens = tokenize(player_input)
    var context_tokens = get_context_tokens(npc_name)
    var combined = context_tokens + input_tokens

    var response_tokens = []
    for i in range(20):
        var next_token = predict_token(combined, personality, i)
        response_tokens.append(next_token)
        combined.append(next_token)
        if next_token == 0:
            break

    var response = detokenize(response_tokens)
    update_history(npc_name, player_input, response)
    update_mood(personality, player_input)
    return response

func tokenize(text: String) -> Array:
    var tokens = []
    var words = text.split(" ")
    for word in words:
        var hash_val = 0
        for c in word:
            hash_val = (hash_val * 31 + c.unicode_at(0)) % vocab_size
        tokens.append(hash_val)
    return tokens

func detokenize(tokens: Array) -> String:
    var words = ["Greetings", "indeed", "perhaps", "the", "ancient", "wisdom",
                 "tells", "of", "a", "great", "journey", "ahead", "brave",
                 "traveler", "seek", "truth", "beyond", "mountain"]
    var result = ""
    for t in tokens:
        if t == 0:
            break
        var idx = t % words.size()
        result += words[idx] + " "
    return result.strip_edges()

func predict_token(context: Array, personality: NPCPersonality, step: int) -> int:
    var seed = 0.0
    for i in range(min(context.size(), 8)):
        seed += context[context.size() - 1 - i] * (i + 1) * 0.001
    seed += personality.mood * 100
    seed += step * 7.3
    var token = int(abs(sin(seed) * vocab_size)) % vocab_size
    if step > 15:
        token = 0
    return token

func get_context_tokens(npc_name: String) -> Array:
    var ctx = []
    for entry in dialog_history:
        if entry["npc"] == npc_name:
            ctx += entry.get("tokens", [])
    return ctx.slice(max(0, ctx.size() - context_window))

func update_history(npc_name: String, input: String, response: String) -> void:
    dialog_history.append({
        "npc": npc_name,
        "input": input,
        "response": response,
        "tokens": tokenize(input),
        "timestamp": Time.get_unix_time_from_system()
    })
    if dialog_history.size() > 100:
        dialog_history = dialog_history.slice(dialog_history.size() - 50)

func update_mood(personality: NPCPersonality, input: String) -> void:
    var positive_words = ["thank", "help", "friend", "please", "good"]
    var negative_words = ["fight", "kill", "hate", "stupid", "die"]
    for w in positive_words:
        if input.to_lower().contains(w):
            personality.mood = min(1.0, personality.mood + 0.1)
    for w in negative_words:
        if input.to_lower().contains(w):
            personality.mood = max(0.0, personality.mood - 0.1)
