class_name CinematicBackdrop
extends Node2D
## Data-selected motifs: decorative choreography, never extra damage/capture.
var director:CinematicDirector
var fighter:BattleActor
var time:=0.0
var density:=1.0
func advance(delta:float)->void:
	time+=delta;queue_redraw()
func _draw()->void:
	if not director.active:return
	var color:=fighter.definition.effect_palette
	var motif:=str(director.spec.get("motif","energy"))
	draw_rect(Rect2(-10,-10,1300,620),Color(color.r*.06,color.g*.06,color.b*.1,.32))
	var at:=fighter.position
	draw_set_transform(at,0,Vector2(1,.24))
	draw_arc(Vector2.ZERO,65,0,TAU,48,Color(color,.45),3)
	draw_arc(Vector2.ZERO,80,time*.7,time*.7+PI,24,Color(color,.5),2)
	draw_set_transform(Vector2.ZERO)
	if density<=0:return
	var center:=fighter.position+Vector2(0,-90-fighter.elevation)
	match motif:
		"spiral", "orbit":
			for i in range(2):draw_arc(center,55+i*14,time*3+i*PI,time*3+i*PI+PI*.7,20,Color(color,.25),3)
		"foxfire":
			for i in range(5):
				var angle:=time*1.5+i*TAU/5
				var point:=center+Vector2(cos(angle)*95,sin(angle)*55)
				draw_circle(point,5,Color(color,.4));draw_circle(point,2,Color(1,1,.85,.7))
		"cross_slash":
			for sign_y in [-1,1]:draw_line(center+Vector2(-60,-sign_y*48),center+Vector2(60,sign_y*48),Color(color,.12),3)
		"nightfall":
			for side in [-1,1]:
				var wing:=PackedVector2Array([center+Vector2(side*35,0),center+Vector2(side*110,-62),center+Vector2(side*90,-10),center+Vector2(side*60,12)])
				draw_colored_polygon(wing,Color(color,.18))
		_:
			if director.stage=="DEPLOY / CHARGE":
				for i in range(10):
					var height:=fposmod(time*50+i*27,140)
					draw_line(Vector2(at.x-130+i*29,510-height),Vector2(at.x-130+i*29,500-height),Color(color,.18),2)
