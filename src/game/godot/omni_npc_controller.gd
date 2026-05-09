# OMNI Game Layer — Godot GDScript AI NPC Controller
# Transformer-powered NPC dialogue and decision making.

extends Node
class_name OmniNPCController

@export var model_endpoint: String = "http://localhost:8080/api/v1/infer"
@export var npc_name: String = "Guardian"
@export var personality: String = "wise and helpful"
@export var max_context_turns: int = 10
@export var response_temperature: float = 0.8

var dialogue_history: Array[Dictionary] = []
var is_generating: bool = false
var http_request: HTTPRequest

signal response_received(text: String)
signal generation_started()
signal generation_completed()

func _ready() -> void:
	http_request = HTTPRequest.new()
	add_child(http_request)
	http_request.request_completed.connect(_on_request_completed)
	_init_system_prompt()

func _init_system_prompt() -> void:
	dialogue_history.append({
		"role": "system",
		"content": "You are %s, a %s NPC in a fantasy world. Stay in character. Keep responses under 100 words." % [npc_name, personality]
	})

func send_message(player_message: String) -> void:
	if is_generating:
		return
	
	is_generating = true
	generation_started.emit()
	
	dialogue_history.append({"role": "user", "content": player_message})
	_trim_history()
	
	var prompt := _format_prompt()
	var body := JSON.stringify({
		"prompt": prompt,
		"max_tokens": 150,
		"temperature": response_temperature,
		"stop_sequences": ["\nPlayer:", "\nUser:"]
	})
	
	var headers := ["Content-Type: application/json"]
	var error := http_request.request(model_endpoint, headers, HTTPClient.METHOD_POST, body)
	
	if error != OK:
		_fallback_response(player_message)

func _on_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
	is_generating = false
	
	if response_code != 200:
		_fallback_response("")
		return
	
	var json := JSON.parse_string(body.get_string_from_utf8())
	if json and json.has("generated_text"):
		var response_text: String = json["generated_text"].strip_edges()
		dialogue_history.append({"role": "assistant", "content": response_text})
		response_received.emit(response_text)
	else:
		_fallback_response("")
	
	generation_completed.emit()

func _format_prompt() -> String:
	var parts: PackedStringArray = []
	for entry in dialogue_history:
		match entry["role"]:
			"system":
				parts.append("[System] %s" % entry["content"])
			"user":
				parts.append("Player: %s" % entry["content"])
			"assistant":
				parts.append("%s: %s" % [npc_name, entry["content"]])
	parts.append("%s:" % npc_name)
	return "\n".join(parts)

func _trim_history() -> void:
	while dialogue_history.size() > max_context_turns * 2 + 1:
		dialogue_history.remove_at(1)

func _fallback_response(context: String) -> void:
	var fallbacks := [
		"I sense something... but the words escape me.",
		"The ancient knowledge stirs, yet remains elusive.",
		"Perhaps we should speak of this another time.",
		"My thoughts are scattered like leaves in the wind.",
	]
	var response: String = fallbacks[randi() % fallbacks.size()]
	dialogue_history.append({"role": "assistant", "content": response})
	response_received.emit(response)
	generation_completed.emit()
	is_generating = false

func clear_history() -> void:
	var system_prompt := dialogue_history[0] if dialogue_history.size() > 0 else null
	dialogue_history.clear()
	if system_prompt:
		dialogue_history.append(system_prompt)

func get_dialogue_summary() -> Dictionary:
	return {
		"npc": npc_name,
		"turns": dialogue_history.size(),
		"is_generating": is_generating
	}
