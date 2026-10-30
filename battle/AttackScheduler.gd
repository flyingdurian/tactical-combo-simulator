class_name AttackScheduler
extends RefCounted
## Owns actor timelines, independent of match phases. No animation callbacks.
signal hit_event(actor: int, move: SequenceData, event: Dictionary, token: String)
signal cue_event(actor: int, event: Dictionary)
var actions: Dictionary = {}
var serial: int = 0
var generation: int = 0

func start(actor: int, move: SequenceData) -> bool:
	if actions.has(actor) or move == null:
		return false
	serial += 1
	actions[actor] = {"move": move, "tick": 0, "id": serial, "fired": {}, "cues": {}}
	return true

func advance() -> void:
	for actor: int in actions.keys():
		var action: Dictionary = actions[actor]
		var move: SequenceData = action.move
		action.tick += 1
		for i in range(move.hit_events.size()):
			var event: Dictionary = move.hit_events[i]
			var first := int(event.get("tick", 0))
			var last := int(event.get("end_tick", first))
			# Repeat eligibility checks during the active interval, with one stable ID.
			# Resolver deduplicates only successful event-target contacts.
			if action.tick >= first and action.tick <= last:
				hit_event.emit(actor, move, event, "%d:%d:%s" % [generation, action.id, str(event.get("id", i))])
			if action.tick >= last:
				action.fired[i] = true
		for i in range(move.cues.size()):
			if action.tick >= int(move.cues[i].get("tick", 0)) and not action.cues.has(i):
				action.cues[i] = true
				cue_event.emit(actor, move.cues[i])
		if action.tick >= maxi(1, move.duration_ticks):
			actions.erase(actor)

func cancel(actor: int) -> Dictionary:
	# Erase only this actor's ownership. No timers or animation callbacks survive.
	var removed: Dictionary = actions.get(actor, {})
	actions.erase(actor)
	return removed

func reset() -> void:
	generation += 1
	actions.clear()

func busy(actor: int) -> bool:
	return actions.has(actor)
