class_name CharacterDefinition
extends Resource
## Roles bind resources, not character-specific branches in controllers.
@export var character_id: String = ""
@export var display_name: String = ""
@export var sprite_flip_h: bool = false
@export var idle_texture: String = ""
@export var tint: Color = Color.WHITE
@export var artwork_status: String = "MISSING SHEET / placeholder"
@export var main_sequences: Array[String] = ["", "", "", "", ""]
@export var assist_sequence: String = ""
@export var special_sequence: String = ""

@export var special_sequences: Array[String] = ["", ""]
@export var ultimate_sequence: String = ""
# Character package schema v2. Empty move paths are explicitly unavailable slots.
@export var package_version: int = 2
@export var portrait_texture: String = ""
@export var sprite_frames: String = ""
@export var source_manifest: String = ""
@export var native_facing: int = 1
@export var pivot: Vector2 = Vector2(128,176)
@export var sprite_scale: float = 1.7
@export var frame_size: Vector2 = Vector2(256,196)
@export var hurtbox: Rect2 = Rect2(-35,-176,70,176)
@export var hurt_texture: String = ""
@export var assist_variants: Array[String] = []
@export var voice_references: Array[String] = []
@export var effect_references: Array[String] = []
@export var supported_roles: Array[String] = ["assist"]
@export var availability_note: String = "Incomplete / use explicit empty slots"

@export var anchors: Dictionary = {}

@export var portrait_region: Rect2 = Rect2(100,70,55,55)
@export var sound_profile: CharacterSoundProfile
@export var effect_palette: Color = Color.CYAN
@export var completion_status: String = "provisional"
@export var recovery_texture: String = ""
@export var defeat_texture: String = ""
