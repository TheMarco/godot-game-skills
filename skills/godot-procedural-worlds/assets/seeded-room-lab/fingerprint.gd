extends RefCounted
## Explicitly scoped to this fixture: transforms, BoxMesh, BoxShape3D, color.
## Extend the property contract before using for a different scene family.
static func digest(root: Node) -> String:
	var records: Array = []
	_collect(root, records)
	assert(records.size() > 6, "Reject empty/incomplete generated fixtures")
	return JSON.stringify(records).sha256_text()

static func _vector(value: Vector3) -> Array:
	return [snappedf(value.x, 0.00001) + 0.0, snappedf(value.y, 0.00001) + 0.0, snappedf(value.z, 0.00001) + 0.0]

static func _collect(node: Node, records: Array) -> void:
	var record: Array = [node.get_class()]
	if node is Node3D:
		record.append(_vector(node.position))
		record.append(_vector(node.rotation))
		record.append(_vector(node.scale))
	if node is MeshInstance3D:
		assert(node.mesh is BoxMesh)
		record.append(_vector(node.mesh.size))
		var material: StandardMaterial3D = node.material_override
		record.append(material.albedo_color.to_html())
		record.append(material.roughness)
	if node is CollisionShape3D:
		assert(node.shape is BoxShape3D)
		record.append(_vector(node.shape.size))
		record.append(node.disabled)
	# Delimit child structure; generated node names and instance IDs are omitted.
	record.append(node.get_child_count())
	records.append(record)
	for child in node.get_children():
		_collect(child, records)
