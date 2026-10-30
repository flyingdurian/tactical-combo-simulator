@tool
extends EditorScript
## Godot 4.x: copy the PXZ2_10_Character_Import_Kit folder under res://,
## then open this script in the Godot editor and use File > Run.
## Generates SpriteFrames resources from UNVERIFIED pose-bank sequences.
## Does NOT bind combat hits, moves, audio, or change existing scenes.

const BASE := "res://PXZ2_10_Character_Import_Kit/characters"

func _run() -> void:
    var root := DirAccess.open(BASE)
    if root == null:
        push_error("Missing %s. Copy the folder under the project root first." % BASE)
        return
    root.list_dir_begin()
    var folder := root.get_next()
    var count := 0
    while folder != "":
        if root.current_is_dir() and not folder.begins_with("."):
            var character_root: String = BASE.path_join(folder)
            var manifest_path: String = character_root.path_join("manifest.json")
            if FileAccess.file_exists(manifest_path):
                var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
                if typeof(parsed) == TYPE_DICTIONARY:
                    var frames := SpriteFrames.new()
                    frames.add_animation("idle")
                    frames.set_animation_loop("idle", true)
                    frames.set_animation_speed("idle", 1.0)
                    var idle_png: String = str(parsed.get("default_still_pose_png", ""))
                    if idle_png != "":
                        var tex: Texture2D = load(character_root.path_join(idle_png)) as Texture2D
                        if tex != null:
                            frames.add_frame("idle", tex)
                    for item in parsed.get("animations", []):
                        var anim_name: String = item["id"]
                        frames.add_animation(anim_name)
                        frames.set_animation_loop(anim_name, false)
                        frames.set_animation_speed(anim_name, 10.0)
                        for rel_path in item.get("frames", []):
                            var tex: Texture2D = load(character_root.path_join(rel_path)) as Texture2D
                            if tex != null:
                                frames.add_frame(anim_name, tex)
                    var output: String = character_root.path_join("generated_spriteframes.tres")
                    var err: Error = ResourceSaver.save(frames, output)
                    if err != OK:
                        push_error("SpriteFrames failed: %s (%s)" % [output, err])
                    else:
                        count += 1
                        print("Generated: ", output)
        folder = root.get_next()
    root.list_dir_end()
    print("Generated SpriteFrames resources for ", count, " characters")
