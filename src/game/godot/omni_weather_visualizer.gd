# OMNI Framework - Godot 4 Weather Visualizer (GDScript)
# Connects to TeleViT outputs to render global weather predictions in 3D

extends Node3D

var wind_particles: GPUParticles3D
var temperature_material: ShaderMaterial

func _ready():
	print("OMNI Godot: Initializing TeleViT Weather Visualizer...")
	wind_particles = $WindSystem
	temperature_material = $GlobeMesh.get_surface_override_material(0)
	
	# Simulate initial connection
	update_weather_state({"temp_anomaly": 1.5, "wind_speed": 45.0})

func update_weather_state(data: Dictionary):
	# Adjust particle speed based on TeleViT wind predictions
	if data.has("wind_speed"):
		wind_particles.process_material.initial_velocity_min = data["wind_speed"] * 0.5
		wind_particles.process_material.initial_velocity_max = data["wind_speed"]
		
	# Adjust globe shader tint based on temperature anomaly
	if data.has("temp_anomaly"):
		var heat_color = Color(1.0, 0.2, 0.2) if data["temp_anomaly"] > 0 else Color(0.2, 0.2, 1.0)
		temperature_material.set_shader_parameter("albedo", heat_color)

func _process(delta):
	# Rotate the globe slowly
	$GlobeMesh.rotate_y(delta * 0.1)
