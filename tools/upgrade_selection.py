from pathlib import Path
R=Path(__file__).resolve().parents[1];p=R/'battle/BattleDemo.gd';s=p.read_text().replace('var role_pickers: Array[OptionButton] = []','''var role_pickers: Array[OptionButton] = []
var variant_pickers:Array[OptionButton]=[]
var pending_roles:Array[int]=[0,1,2]
var assist_variants:Array[int]=[0,0]
var pending_variants:Array[int]=[0,0]
var roster_status:Label''').replace('var path := definitions[roles[actor]].assist_sequence','''var definition:=definitions[roles[actor]]
	var choices:=definition.assist_variants
	var path:String=choices[assist_variants[actor-1]] if assist_variants[actor-1]<choices.size() else definition.assist_sequence''').replace('title.text = "  F1 / DEBUG — role changes reset the training run"','title.text = "F1 / ROSTER + TRAINING — apply at new battle"').replace('picker.add_item(data.display_name)','picker.add_item(data.display_name+" ["+data.completion_status+"]")').replace('picker.item_selected.connect(func(index: int): swap_role(slot, index))','picker.item_selected.connect(func(index: int): stage_role(slot, index))')
s=s.replace('\t_toggle(box, "Reduced flash / no target flashing", set_reduced_flash)','''	for slot in range(2):
		var picker:=OptionButton.new()
		picker.item_selected.connect(func(index:int):pending_variants[slot]=index)
		variant_pickers.append(picker);box.add_child(picker)
	roster_status=Label.new();roster_status.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;roster_status.custom_minimum_size.x=360;box.add_child(roster_status)
	var apply:=Button.new();apply.text="Launch new battle with selected team";apply.pressed.connect(apply_team);box.add_child(apply)
	_refresh_selection()
	_toggle(box, "Reduced flash / no target flashing", set_reduced_flash)''')
a=s.index('func swap_role(');b=s.index('func _override_phase',a)
s=s[:a]+'''func stage_role(slot:int,character_index:int)->void:
	if slot<0 or slot>2 or character_index<0 or character_index>=definitions.size():return
	var previous:=pending_roles[slot]
	var other:=pending_roles.find(character_index)
	pending_roles[slot]=character_index
	if other>=0 and other!=slot:pending_roles[other]=previous
	pending_variants=[0,0];_refresh_selection()
func _refresh_selection()->void:
	for i in range(3):role_pickers[i].select(pending_roles[i])
	for i in range(2):
		var picker:=variant_pickers[i];picker.clear()
		for path in definitions[pending_roles[i+1]].assist_variants:
			picker.add_item("Assist %d: " % (i+1)+(load(path) as SequenceData).display_name)
		if picker.item_count>0:picker.select(0)
	var data:=definitions[pending_roles[0]]
	roster_status.text=data.display_name+" — "+data.availability_note+"\\nVoice: optional / missing clips are silent. Changes apply only on launch."
func apply_team()->void:
	for slot in range(3):
		if not definitions[pending_roles[slot]].supported_roles.has("main" if slot==0 else "assist"):
			notify_action("REJECTED / unsupported role",false);return
	roles.assign(pending_roles);assist_variants.assign(pending_variants)
	reset_match();debug_panel.hide();notify_action("NEW BATTLE / team applied",true)
func swap_role(slot:int,character_index:int)->void:
	# Explicit programmatic new-match helper, also used by regression tests.
	pending_roles.assign(roles);stage_role(slot,character_index);apply_team()

''' +s[b:];p.write_text(s)
