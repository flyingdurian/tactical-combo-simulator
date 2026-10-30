class_name ElectricalFX
extends Node2D
## Anchor-relative CPU geometry. Eight bounded discharges, no timers/nodes per arc.
var discharges: Array[Dictionary] = []
var density: float = 1
var maximum_active: int = 8
func discharge(target: Node2D, profile: ImpactProfile, direction: int) -> void:
	if not is_instance_valid(target) or profile.electrical_branches<=0:return
	if discharges.size()>=maximum_active:discharges.pop_front()
	discharges.append({"target":target,"profile":profile,"life":0.0,"direction":direction})
func advance(delta: float) -> void:
	for arc in discharges:arc.life+=delta
	discharges=discharges.filter(func(a: Dictionary)->bool:return is_instance_valid(a.target) and a.life<minf(.8,a.profile.arc_lifetime))
	queue_redraw()
func clear_all() -> void:
	discharges.clear();queue_redraw()
func _draw() -> void:
	for arc in discharges:
		var p: ImpactProfile=arc.profile
		var target: BattleActor=arc.target
		var origin:=target.position+Vector2(0,-target.elevation)
		var fade: float=(1-float(arc.life)/p.arc_lifetime)*clampf(p.electrical_intensity,0,1)
		var phase:=floori(float(arc.life)*p.arc_frequency)
		for branch in range(clampi(roundi(p.electrical_branches*density),0,6)):
			var start:=origin+Vector2(-28+branch*10,-145+branch*12)
			var end:=origin+Vector2(28-branch*9,-30-branch*13)
			var points:=PackedVector2Array()
			for i in range(7):
				var at:=start.lerp(end,i/6.0)
				if i>0 and i<6:at.x+=sin((i*17+branch*23+phase*7)*1.7)*10
				points.append(at)
			draw_polyline(points,Color(p.color,fade*.35),p.arc_thickness*3)
			draw_polyline(points,Color(p.core_color,fade),p.arc_thickness)
			# Small secondary branch remains within the same silhouette envelope.
			draw_line(points[3],points[3]+Vector2(arc.direction*15,-13),Color(p.color,fade),p.arc_thickness)
