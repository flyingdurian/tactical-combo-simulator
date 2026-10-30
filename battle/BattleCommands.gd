class_name BattleCommands
extends RefCounted
## Direction is captured once on attack press. Vertical wins diagonals;
## opposing axes cancel, so Up+Down+Right selects Right. Never target-relative.
static func direction_slot(left: bool, up: bool, down: bool, right: bool) -> int:
	if up != down: return 2 if up else 3
	if left != right: return 1 if left else 4
	return 0
static func capture() -> int:
	return direction_slot(Input.is_action_pressed("select_left"), Input.is_action_pressed("select_up"), Input.is_action_pressed("select_down"), Input.is_action_pressed("select_right"))
static func label(action: String) -> String:
	var names: Array[String] = []
	for event in InputMap.action_get_events(action): names.append(event.as_text().replace(" (Physical)", ""))
	return "/".join(names) if not names.is_empty() else "UNBOUND"
