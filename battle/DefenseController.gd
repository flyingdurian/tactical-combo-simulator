class_name DefenseController
extends RefCounted
## Per-hit decisions in simulation ticks; no input reading by CPU selection.
var tick: int = 0
var held: bool = false
var pressed_tick: int = -1000
var dodge_until: int = -1
var recovery_until: int = -1
var ready_at: int = -1
var perfect_window: int = 8
var dodge_window: int = 6
var dodge_recovery: int = 24
var dodge_cooldown: int = 44
var block_factor: float = .5
var perfect_factor: float = .2
func advance() -> void: tick += 1
func block(pressed: bool) -> void:
	if pressed and not held: pressed_tick = tick
	held = pressed
func dodge() -> bool:
	if tick < ready_at: return false
	dodge_until=tick+dodge_window;recovery_until=tick+dodge_recovery;ready_at=tick+dodge_cooldown
	return true
func resolve(damage: int) -> Dictionary:
	if tick < dodge_until: return {"damage":0,"label":"DODGE"}
	if tick < recovery_until: return {"damage":damage,"label":"CAUGHT IN DODGE RECOVERY"}
	if held:
		if tick-pressed_tick <= perfect_window: return {"damage":maxi(1,roundi(damage*perfect_factor)),"label":"PERFECT BLOCK"}
		return {"damage":maxi(1,roundi(damage*block_factor)),"label":"BLOCK"}
	return {"damage":damage,"label":"HIT"}
func reset() -> void:
	tick=0;held=false;pressed_tick=-1000;dodge_until=-1;recovery_until=-1;ready_at=-1
