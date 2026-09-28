extends Node3D
const Store = preload("res://room_store.gd")
var store: Node3D
var camera: Camera3D
var label: Label
var orbit := 0.65
var capture_path := ""
var opened := false

func _ready() -> void:
	store = Store.new()
	add_child(store)
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--seed="):
			store.seed_value = int(argument.trim_prefix("--seed="))
		elif argument.begins_with("--capture="):
			capture_path = argument.trim_prefix("--capture=")
	_build()
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55, -25, 0)
	light.light_energy = 1.3
	light.shadow_enabled = true
	add_child(light)
	var world_environment := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color("17232c")
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color("a6c9d0")
	environment.ambient_light_energy = 0.5
	world_environment.environment = environment
	add_child(world_environment)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 27.0
	add_child(camera)
	_position_camera()
	var layer := CanvasLayer.new()
	add_child(layer)
	var heading := Label.new()
	heading.position = Vector2(28, 24)
	heading.add_theme_font_size_override("font_size", 22)
	heading.text = "GODOT GAME SKILLS / SEEDED ROOM LAB\nSeed %d · 9 cells · original box geometry" % store.seed_value
	layer.add_child(heading)
	label = Label.new()
	label.position = Vector2(28, 618)
	label.add_theme_font_size_override("font_size", 17)
	layer.add_child(label)
	_update_label("Same seed. Stable rooms. Retained door state.")
	if not capture_path.is_empty():
		_capture()

func _build() -> void:
	for x in range(-1, 2):
		for z in range(-1, 2):
			store.load_cell(Vector2i(x, z))

func _position_camera() -> void:
	var center := Vector3(3, 0, 3)
	camera.position = center + Vector3(cos(orbit) * 23.0, 22.0, sin(orbit) * 23.0)
	camera.look_at(center)

func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	match event.keycode:
		KEY_SPACE:
			opened = not opened
			store.set_door(Vector2i.ZERO, opened)
			_update_label("Center door opened." if opened else "Center door closed.")
		KEY_R:
			for cell in store.rooms.keys():
				store.unload_cell(cell)
			_build()
			_update_label("All rooms rebuilt; center door state retained.")
		KEY_F:
			store.replace_cell(Vector2i.ZERO, true, true)
			_update_label("Staging failed deliberately; installed room kept.")
		KEY_M:
			var present: bool = is_instance_valid(store.rooms[Vector2i.ZERO].door)
			store.replace_cell(Vector2i.ZERO, not present)
			_update_label("Door presence toggled; its recorded state retained.")
		KEY_LEFT, KEY_RIGHT:
			orbit += -0.15 if event.keycode == KEY_LEFT else 0.15
			_position_camera()

func _update_label(status: String) -> void:
	label.text = "%s\nSpace  toggle door   /   R  unload + rebuild   /   ← →  orbit camera\nM  remove + restore door   /   F  fail staging" % status

func _capture() -> void:
	for frame in range(8):
		await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	var result := image.save_png(capture_path)
	if result != OK:
		push_error("Capture failed: %s" % error_string(result))
		get_tree().quit(1)
		return
	print("PASS: capture ", capture_path)
	get_tree().quit(0)
