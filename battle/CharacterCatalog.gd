class_name CharacterCatalog
extends RefCounted
## One registration source for battle, preview and validation.
static func load_all()->Array[CharacterDefinition]:
	var result:Array[CharacterDefinition]=[]
	var paths=JSON.parse_string(FileAccess.get_file_as_string("res://moves/roster.json"))
	if not paths is Array:return result
	for path in paths:
		var data=load(str(path))
		if data is CharacterDefinition:result.append(data)
	return result
