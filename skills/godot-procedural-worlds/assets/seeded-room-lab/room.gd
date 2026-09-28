extends Node3D
const World = preload("res://world.gd")
var cell := Vector2i.ZERO
var door: Node3D
var door_open := false

func build(seed_value: int, at: Vector2i, has_door := true) -> void:
	cell = at
	name = "Room_%d_%d" % [at.x, at.y]
	position = Vector3(at.x * World.CELL_SIZE, 0.0, at.y * World.CELL_SIZE)
	var data: Dictionary = World.facts(seed_value, cell)
	var palette := [Color("648782"), Color("8e9683"), Color("8b8076")]
	var floor_color: Color = palette[int(data["style"])]
	box(self, Vector3(6.0, 0.2, 6.0), Vector3(3.0, -0.1, 3.0), floor_color, true)
	# Each shared boundary is built only by its lower-coordinate owner.
	for axis in [0, 1]:
		var opening: bool = data["east_open"] if axis == 0 else data["south_open"]
		for part in [-1, 1] if opening else [0]:
			var width := 2.0 if opening else 6.0
			var center := 3.0 + float(part) * 2.0
			var size := Vector3(0.15, 1.6, width) if axis == 0 else Vector3(width, 1.6, 0.15)
			var offset := Vector3(6.0, 0.8, center) if axis == 0 else Vector3(center, 0.8, 6.0)
			box(self, size, offset, floor_color.lightened(0.25), true)
	box(self, Vector3(0.8, 0.65, 0.8), Vector3(2.2 + data["prop_offset"], 0.325, 3.8), Color("c9bda0"), true)
	if has_door:
		door = Node3D.new()
		door.name = "StatefulDoor"
		door.position = Vector3(2.4, 0.0, 1.6)
		add_child(door)
		box(door, Vector3(1.2, 1.5, 0.12), Vector3(0.6, 0.75, 0.0), Color("d99355"), true)

func apply_state(is_open: bool) -> void:
	door_open = is_open
	if is_instance_valid(door):
		door.rotation.y = -PI * 0.5 if is_open else 0.0

static func box(parent: Node3D, size: Vector3, offset: Vector3, color: Color, solid: bool) -> void:
	var mesh := MeshInstance3D.new()
	var shape := BoxMesh.new()
	shape.size = size
	mesh.mesh = shape
	mesh.position = offset
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = 0.85
	mesh.material_override = material
	parent.add_child(mesh)
	if solid:
		var body := StaticBody3D.new()
		var collider := CollisionShape3D.new()
		var bounds := BoxShape3D.new()
		bounds.size = size
		collider.shape = bounds
		body.position = offset
		body.add_child(collider)
		parent.add_child(body)
