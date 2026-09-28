extends SceneTree
const World = preload("res://world.gd")
const Room = preload("res://room.gd")
const Fingerprint = preload("res://fingerprint.gd")
var failed := false

func _init() -> void:
	call_deferred("_run")

func expect(condition: bool, message: String) -> void:
	if not condition:
		failed = true
		push_error(message)

func _run() -> void:
	var cells: Array[Vector2i] = [Vector2i(-2, -1), Vector2i(0, 0), Vector2i(3, 2), Vector2i(1, -4)]
	for seed_value in [7, 31, 901]:
		var forward: Dictionary = {}
		for cell in cells:
			var room := Room.new()
			room.build(seed_value, cell)
			forward[cell] = Fingerprint.digest(room)
			room.free()
		var reversed := cells.duplicate()
		reversed.reverse()
		for cell in reversed:
			var room := Room.new()
			room.build(seed_value, cell)
			expect(Fingerprint.digest(room) == forward[cell], "Build order changed geometry")
			room.free()
			for direction in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
				expect(World.edge_key(cell, direction) == World.edge_key(cell + direction, -direction), "Edge identity mismatch")
				expect(World.edge_open(seed_value, cell, direction) == World.edge_open(seed_value, cell + direction, -direction), "Opening mismatch")
	expect(World.world_to_cell(Vector3(-0.1, 0.0, -6.1)) == Vector2i(-1, -2), "Negative coordinates must floor")
	var original := Room.new()
	original.build(7, Vector2i.ZERO)
	var before: String = Fingerprint.digest(original)
	original.apply_state(true)
	expect(before != Fingerprint.digest(original), "Fingerprint missed a real transform change")
	original.free()
	if not failed:
		print("PASS: determinism")
	quit(1 if failed else 0)
