extends SceneTree
## Director sandbox prototype, not available in the normal roster.
var checks := 0
var failures := 0
const PREVIEW := "res://moves/director_drafts/chunli_neutral_b_preview.tres"
const BASELINE := "res://moves/director_drafts/chunli_neutral_b_baseline.tres"

func ok(condition: bool, description: String) -> void:
    checks += 1
    if not condition: failures += 1
    print(("PASS " if condition else "FAIL ") + description)

func _initialize() -> void:
    run.call_deferred()

func run() -> void:
    var move: SequenceData = load(PREVIEW)
    ok(move != null, "Director preview resource parses")
    if move == null:
        quit(1)
        return
    ok(move.character == "chunli" and move.category == "normal", "correct preview identity")
    ok(move.poses.size() == 20 and move.hit_events.size() == 9, "twenty poses and nine authored kick contacts")
    var pose_sum := 0
    for pose in move.poses:
        pose_sum += int(pose.ticks)
    ok(pose_sum == move.duration_ticks and move.duration_ticks == 156, "156 tick pose budget / 2.6 seconds")
    ok(move.duration_ticks >= 120 and move.duration_ticks <= 300, "regular attack length 2 to 5 seconds")
    ok(move.staging.get("exit_end") == 156, "clean staging exit boundary")
    var previous: SequenceData = load(BASELINE)
    ok(previous != null and previous.duration_ticks == 88 and previous.hit_events.size() == 5, "88-tick reference preserved")
    for index in range(5):
        ok(move.hit_events[index].tick == previous.hit_events[index].tick and move.hit_events[index].region == previous.hit_events[index].region, "user-accepted first five hit regions unchanged " + str(index))
    var d: BattleDemo = load("res://scenes/BattleDemo.tscn").instantiate()
    root.add_child(d)
    d.versus_mode = false
    d.preview_only = true
    d.set_process(false)
    d.set_physics_process(false)
    d.fx.audio_enabled = false
    for definition in d.definitions:
        ok(not definition.main_sequences.has(PREVIEW) and not definition.main_sequences.has(BASELINE), "both previews excluded from roster: " + definition.character_id)
    for mirrored in [false, true]:
        d.roles.assign([1,0,2]) # Main Chun-Li
        if mirrored:
            d.mirror_setup()
        else:
            d.reset_match()
            d.phase = BattleDemo.Phase.PlayerAttackPhase
        ok(d.scheduler.start(0, move), "start Director move facing mirrored=" + str(mirrored))
        AttackStaging.prepare(d.scheduler.actions[0], d.actors[0], d.dummy, false)
        for i in range(move.duration_ticks + 150):
            d.simulate_tick()
            d._process(1.0/60)
        var contacts := d.hit_log.size()
        var confirmed_ids: Array[String] = []
        for accepted in d.hit_log:
            confirmed_ids.append(str(accepted.get("token", "")).split(":")[-1])
        for authored_event in move.hit_events:
            var event_id := str(authored_event.get("id", ""))
            if confirmed_ids.has(event_id):
                continue
            var attempts: Array[String] = []
            for entry in d.contact_log:
                if str(entry.get("token", "")).ends_with(":" + event_id):
                    attempts.append("%s strike=%s hurt=%s attacker=%s target=%s" % [
                        str(entry.get("result", "")),
                        str(entry.get("strike", "")),
                        str(entry.get("hurt", "")),
                        str(entry.get("attacker", "")),
                        str(entry.get("target", ""))])
            print("DIRECTOR MISS DETAIL facing=", mirrored, " event=", event_id, " attempts=", attempts)
        ok(contacts == move.hit_events.size(),
            "all nine sourced contacts connect " + str(mirrored) + ": " + str(contacts))
        var honest := true
        for h in d.hit_log:
            honest = honest and h.strike.has_point(h.contact) and h.hurt.has_point(h.contact)
        ok(honest, "honest hit region overlap " + str(mirrored))
        ok(d.scheduler.actions.is_empty() and not d.cinematic.active,
            "scheduler and cinematic ownership cleaned " + str(mirrored))
        d.roles.assign([1,0,2])
        d.reset_match()
        d.phase = BattleDemo.Phase.PlayerAttackPhase
        d.scheduler.start(0,move)
        AttackStaging.prepare(d.scheduler.actions[0], d.actors[0], d.dummy, false)
        for i in range(10):
            d.simulate_tick()
        d.reset_match()
        ok(d.scheduler.actions.is_empty() and d.hit_log.is_empty(),
           "safe active reset " + str(mirrored))
    print("DIRECTOR CHUNLI PREVIEW: %d checks / %d failures" % [checks, failures])
    d.queue_free()
    await process_frame
    quit(1 if failures else 0)
