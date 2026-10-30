class_name SequenceData
extends Resource
## Gameplay ticks and visual poses are independent tracks. All ticks are 1/60 s.
@export var sequence_id: String = ""
@export var display_name: String = ""
@export var character: String = ""
@export var role: String = "main"
@export var duration_ticks: int = 100
@export var poses: Array[Dictionary] = []
@export var hit_events: Array[Dictionary] = []
@export var movement: Array[Dictionary] = []
@export var cues: Array[Dictionary] = []
@export var chain_open: int = 75
@export var chain_close: int = 100
@export var resource_cost: int = 0
@export var resource_gain: int = 0
@export var reach: float = 350.0

@export var staging: Dictionary = {}

# Inclusive authored windows. Released projectiles persist unless explicitly removed.
@export var cancel_open: int = 8
@export var cancel_close: int = 45
@export var cancel_projectiles: bool = false
@export var category: String = "normal"
@export var purpose: String = ""

@export var cinematic_spec: Dictionary = {}
