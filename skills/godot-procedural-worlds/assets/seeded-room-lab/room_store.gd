extends Node3D
## Synchronous contract example; not a threaded or distance-driven streamer.
const Room = preload("res://room.gd")
const World = preload("res://world.gd")
var seed_value := 7
var rooms: Dictionary = {}
var states: Dictionary = {}

func load_cell(cell: Vector2i, has_door := true) -> Node3D:
	if rooms.has(cell):
		return rooms[cell]
	var room := _prepare(cell, has_door)
	add_child(room)
	rooms[cell] = room
	return room

func unload_cell(cell: Vector2i) -> void:
	if not rooms.has(cell):
		return
	var room: Node3D = rooms[cell]
	_capture(room)
	rooms.erase(cell)
	remove_child(room)
	room.free()

func set_door(cell: Vector2i, is_open: bool) -> void:
	states[World.object_id(cell)] = {"schema": 1, "open": is_open}
	if rooms.has(cell):
		rooms[cell].apply_state(is_open)

func replace_cell(cell: Vector2i, has_door := true, simulate_failure := false) -> bool:
	if not rooms.has(cell):
		return false
	var old: Node3D = rooms[cell]
	_capture(old)
	var staged := _prepare(cell, has_door)
	if simulate_failure or staged.get_child_count() < 2:
		staged.free()
		return false
	# Call outside physics callbacks. Complex consumers must synchronize their
	# actors/registries and provide their own commit-side compensation.
	remove_child(old)
	add_child(staged)
	rooms[cell] = staged
	old.free()
	return true

func _prepare(cell: Vector2i, has_door: bool) -> Node3D:
	var room := Room.new()
	room.build(seed_value, cell, has_door)
	var saved: Dictionary = states.get(World.object_id(cell), {})
	if saved.get("schema", 0) == 1:
		room.apply_state(bool(saved.get("open", false)))
	return room

func _capture(room: Node3D) -> void:
	# Absence must not overwrite the retained record with a default value.
	if is_instance_valid(room.door):
		states[World.object_id(room.cell)] = {"schema": 1, "open": room.door_open}
