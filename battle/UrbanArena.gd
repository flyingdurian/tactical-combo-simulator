class_name UrbanArena
extends Node2D
## Original code-drawn urban approximation. No downloaded environment assets.
func _draw() -> void:
	draw_rect(Rect2(0, 0, 1280, 720), Color("162637"))
	for i in range(24):
		draw_rect(Rect2(0, i * 20, 1280, 20), Color("142336").lerp(Color("47606d"), i / 24.0))
	# Far skyline / warm window rhythm.
	for i in range(15):
		var x := i * 96.0 - 20
		var height := 130.0 + (i * 37 % 130)
		draw_rect(Rect2(x, 335 - height, 79, height), Color("253d50"))
		for row in range(10):
			for col in range(4):
				if (row + col + i) % 3 != 0:
					draw_rect(Rect2(x + 11 + col * 15, 345 - height + row * 19, 5, 9), Color("65818a"))
	draw_rect(Rect2(0, 290, 1280, 22), Color("172c3b"))
	draw_line(Vector2(0, 290), Vector2(1280, 290), Color("7d9da4"), 3)
	for x in [60, 390, 780, 1180]:
		draw_rect(Rect2(x, 312, 22, 160), Color("243947"))
	# Shops and station frontage.
	for i in range(6):
		var x := i * 220.0
		draw_rect(Rect2(x, 340, 205, 133), Color("20323d"))
		draw_rect(Rect2(x + 12, 370, 180, 84), Color("314c57"))
		for slat in range(6):
			draw_line(Vector2(x + 12, 377 + slat * 13), Vector2(x + 192, 377 + slat * 13), Color("3e5c66"), 2)
		for col in range(3):
			draw_rect(Rect2(x + 15 + col * 60, 343, 48, 18), Color("807254") if i % 2 == 0 else Color("356c76"))
	draw_rect(Rect2(50, 325, 175, 29), Color("2a888e"))
	draw_string(ThemeDB.fallback_font, Vector2(65, 347), "EAST / STATION 07", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("d4f9ef"))
	draw_rect(Rect2(1020, 328, 195, 29), Color("ba6955"))
	draw_string(ThemeDB.fallback_font, Vector2(1040, 350), "NIGHT MARKET", HORIZONTAL_ALIGNMENT_LEFT, -1, 19, Color("fff0d8"))
	# Pavement establishes a single stable ground plane for all fighters.
	draw_rect(Rect2(0, 473, 1280, 145), Color("3c4d56"))
	draw_rect(Rect2(0, 476, 1280, 7), Color("77908d"))
	for i in range(8):
		draw_line(Vector2(i * 180, 483), Vector2(i * 210 - 90, 615), Color("273d49"), 2)
	for y in [515, 563, 608]:
		draw_line(Vector2(0, y), Vector2(1280, y), Color("30434d"), 2)
	for x in [60, 270, 480, 690, 900, 1110]:
		draw_rect(Rect2(x, 574, 110, 5), Color("acac87"))
	# Street lamp silhouettes sit behind the action.
	for x in [130, 1120]:
		draw_line(Vector2(x, 482), Vector2(x, 218), Color("1b2b36"), 7)
		draw_line(Vector2(x, 218), Vector2(x + 46, 218), Color("1b2b36"), 7)
		draw_circle(Vector2(x + 46, 222), 7, Color("ffe1a0"))

	for wall_x in [120,1160]:
		draw_line(Vector2(wall_x,260),Vector2(wall_x,520),Color(.45,.85,1,.42),3)
		for y in range(280,520,30):
			draw_line(Vector2(wall_x-7,y),Vector2(wall_x+7,y+10),Color(.75,.9,1,.5),2)
		draw_string(ThemeDB.fallback_font,Vector2(wall_x-38,539),"BOUNDARY",HORIZONTAL_ALIGNMENT_LEFT,-1,12,Color("a6d6e7"))
