class_name PresentationController
extends RefCounted
## Only writer of world camera transforms. Collision always uses untransformed world data.
var owner: String = "battle"
var priority: int = 0
var focus := Vector2(640,360)
var zoom: float = 1
var wanted_zoom: float = 1
var impulse := Vector2.ZERO
var phase: float = 0
var reduced: bool = false
func claim(who: String, rank: int) -> bool:
	if rank<priority and who!=owner:return false
	owner=who;priority=rank;return true
func frame(who: String, at: Vector2, scale_value: float) -> void:
	if who!=owner:return
	focus=at;wanted_zoom=clampf(scale_value,1,1.12) if not reduced else 1
func accent(direction: int, strength: float) -> void:
	impulse=Vector2(direction*minf(strength,4)*3,-minf(strength,4)*1.1)
func release(who: String) -> void:
	if owner!=who:return
	owner="battle";priority=0;focus=Vector2(640,360);wanted_zoom=1
func advance(delta: float, world: Node2D, shake: float) -> void:
	phase+=delta
	zoom=lerpf(zoom,wanted_zoom,1-exp(-delta*12))
	if absf(zoom-1)<.0001 and wanted_zoom==1:zoom=1
	var offset:=Vector2(640,360)-focus*zoom
	offset.x=clampf(offset.x,-1280*(zoom-1),0)
	offset.y=clampf(offset.y,-720*(zoom-1),0)
	world.scale=Vector2.ONE*zoom
	world.position=offset+impulse*sin(phase*95)*shake
	impulse=impulse.move_toward(Vector2.ZERO,delta*65)
func reset(world: Node2D) -> void:
	owner="battle";priority=0;focus=Vector2(640,360);zoom=1;wanted_zoom=1;impulse=Vector2.ZERO
	world.scale=Vector2.ONE;world.position=Vector2.ZERO
