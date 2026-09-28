extends RefCounted
## Pure example generator. Domain salts are part of its seed compatibility.
const CELL_SIZE := 6.0
const MASK := 0x7fffffff

static func sample(seed_value: int, cell: Vector2i, domain: int) -> int:
	var value := seed_value & MASK
	for component in [cell.x, cell.y, domain]:
		value = ((value ^ (int(component) & MASK)) * 1664525 + 1013904223) & MASK
		value = (value ^ (value >> 13)) & MASK
	return value

static func edge_key(cell: Vector2i, direction: Vector2i) -> String:
	assert(direction in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.UP, Vector2i.DOWN])
	var anchor := cell
	var axis := "x"
	if direction == Vector2i.LEFT:
		anchor.x -= 1
	elif direction == Vector2i.UP:
		anchor.y -= 1
		axis = "z"
	elif direction == Vector2i.DOWN:
		axis = "z"
	return "%d:%d/%s" % [anchor.x, anchor.y, axis]

static func edge_open(seed_value: int, cell: Vector2i, direction: Vector2i) -> bool:
	var anchor := cell
	if direction == Vector2i.LEFT:
		anchor.x -= 1
	elif direction == Vector2i.UP:
		anchor.y -= 1
	var domain := 17 if direction.x != 0 else 29
	return sample(seed_value, anchor, domain) % 4 != 0

static func facts(seed_value: int, cell: Vector2i) -> Dictionary:
	return {
		"style": sample(seed_value, cell, 101) % 3,
		"east_open": edge_open(seed_value, cell, Vector2i.RIGHT),
		"south_open": edge_open(seed_value, cell, Vector2i.DOWN),
		"prop_offset": float(sample(seed_value, cell, 211) % 13 - 6) / 10.0,
	}

static func object_id(cell: Vector2i) -> String:
	return "cell:%d:%d/door:demo" % [cell.x, cell.y]

static func world_to_cell(position: Vector3) -> Vector2i:
	return Vector2i(floori(position.x / CELL_SIZE), floori(position.z / CELL_SIZE))
