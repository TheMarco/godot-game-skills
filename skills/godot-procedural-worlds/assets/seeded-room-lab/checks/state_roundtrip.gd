extends SceneTree
const Store = preload("res://room_store.gd")
var failed := false

func _init() -> void:
	call_deferred("_run")

func expect(condition: bool, message: String) -> void:
	if not condition:
		failed = true
		push_error(message)

func _run() -> void:
	var store := Store.new()
	root.add_child(store)
	var cell := Vector2i(-1, 2)
	store.load_cell(cell)
	store.set_door(cell, true)
	store.unload_cell(cell)
	var restored: Node3D = store.load_cell(cell)
	expect(restored.door_open, "Streaming lost door state")
	expect(store.replace_cell(cell, false), "Removal failed")
	expect(not is_instance_valid(store.rooms[cell].door), "Door should be absent")
	store.unload_cell(cell)
	store.load_cell(cell, false)
	expect(store.replace_cell(cell, true), "Restoration failed")
	expect(store.rooms[cell].door_open, "Temporary absence lost state")
	var installed: Node3D = store.rooms[cell]
	var old_children := installed.get_child_count()
	expect(not store.replace_cell(cell, true, true), "Failure injection should reject commit")
	expect(store.rooms[cell] == installed and installed.get_parent() == store, "Failed staging removed installed room")
	expect(installed.get_child_count() == old_children and installed.door_open, "Failure altered geometry or state")
	store.free()
	if not failed:
		print("PASS: state_roundtrip")
	quit(1 if failed else 0)
