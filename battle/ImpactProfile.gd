class_name ImpactProfile
extends Resource
## One authored impact vocabulary; geometry/contact remains owned by combat.
@export var profile_id: String = "light"
@export var color: Color = Color("ffe7a0")
@export var core_color: Color = Color.WHITE
@export var spark_count: int = 6
@export var directional_streaks: int = 2
@export var radius: float = 24
@export var shock_ring: bool = false
@export var debris: int = 0
@export var electrical_branches: int = 0
@export var arc_lifetime: float = .25
@export var arc_thickness: float = 2
@export var arc_frequency: float = 18
@export var electrical_intensity: float = 1
@export var rim_strength: float = .25
@export var hitstop: int = 2
@export var camera_impulse: float = 1.2
@export var screen_flash: float = 0
@export var number_scale: float = 1
@export var lingering: float = .35
@export var sound_layers: Array[String] = ["tap"]
