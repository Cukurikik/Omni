# @omni-layer Game | @omni-lang GDScript (Godot) | @omni-batch 17
# @omni-description Neural world simulator: Godot GDScript node for
# real-time RL environment rendering with physics and reward signals.

extends Node3D
class_name OmniRLEnvironment

## Environment configuration
@export var grid_size: int = 16
@export var max_steps: int = 500
@export var reward_scale: float = 1.0
@export var render_debug: bool = true

var _state: PackedFloat64Array
var _step_count: int = 0
var _total_reward: float = 0.0
var _episode_count: int = 0
var _is_done: bool = false

signal episode_started(episode: int)
signal step_completed(step: int, reward: float, done: bool)
signal episode_ended(total_reward: float, steps: int)

func _ready() -> void:
	_state = PackedFloat64Array()
	_state.resize(grid_size * grid_size)
	reset()
	print("[OmniRL] Environment ready: grid=%d, max_steps=%d" % [grid_size, max_steps])

func reset() -> PackedFloat64Array:
	_step_count = 0
	_total_reward = 0.0
	_is_done = false
	_episode_count += 1

	# Initialize state with structured noise
	for i in range(_state.size()):
		_state[i] = sin(float(i) * 0.1 + float(_episode_count) * 0.01) * 0.5

	emit_signal("episode_started", _episode_count)
	return _state

func step(action: int) -> Dictionary:
	if _is_done:
		return {"error": "Episode is done, call reset()"}

	_step_count += 1
	var prev_state := _state.duplicate()

	# Apply action to state (4 directional actions)
	var agent_pos := _step_count % _state.size()
	match action:
		0: # Up
			if agent_pos >= grid_size:
				_state[agent_pos - grid_size] += 0.3
		1: # Down
			if agent_pos < _state.size() - grid_size:
				_state[agent_pos + grid_size] += 0.3
		2: # Left
			if agent_pos % grid_size > 0:
				_state[agent_pos - 1] += 0.3
		3: # Right
			if agent_pos % grid_size < grid_size - 1:
				_state[agent_pos + 1] += 0.3

	# Compute reward
	var reward := _compute_reward(prev_state, _state, action)
	_total_reward += reward

	# Check termination
	_is_done = _step_count >= max_steps or _compute_goal_reached()

	var result := {
		"state": _state,
		"reward": reward * reward_scale,
		"done": _is_done,
		"step": _step_count,
		"total_reward": _total_reward,
	}

	emit_signal("step_completed", _step_count, reward, _is_done)
	if _is_done:
		emit_signal("episode_ended", _total_reward, _step_count)

	return result

func get_observation_space() -> Dictionary:
	return {"shape": [grid_size, grid_size], "dtype": "float64", "low": -1.0, "high": 1.0}

func get_action_space() -> Dictionary:
	return {"n": 4, "type": "discrete", "labels": ["up", "down", "left", "right"]}

func get_stats() -> Dictionary:
	return {
		"episodes": _episode_count,
		"current_step": _step_count,
		"total_reward": _total_reward,
		"is_done": _is_done,
		"grid_size": grid_size,
	}

func _compute_reward(prev: PackedFloat64Array, curr: PackedFloat64Array, action: int) -> float:
	var delta := 0.0
	for i in range(min(prev.size(), curr.size())):
		delta += abs(curr[i] - prev[i])
	return delta * 0.1 - 0.01  # Small penalty per step

func _compute_goal_reached() -> bool:
	var center := grid_size / 2 * grid_size + grid_size / 2
	return center < _state.size() and _state[center] > 0.8

func _process(delta: float) -> void:
	if render_debug and not _is_done:
		_render_debug_overlay()

func _render_debug_overlay() -> void:
	pass  # Override in derived class for visualization
