from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'moves/choreography.json').read_text())
for move in data['moves']:
    lines = ['[gd_resource type="Resource" script_class="SequenceData" load_steps=2 format=3]', '[ext_resource type="Script" path="res://battle/SequenceData.gd" id="1"]', '[resource]', 'script = ExtResource("1")']
    for key, value in move.items():
        if key in ('poses', 'hit_events', 'movement', 'cues'):
            lines.append(key + ' = Array[Dictionary](' + json.dumps(value) + ')')
        else:
            lines.append(key + ' = ' + json.dumps(value))
    (ROOT / 'moves' / (move['sequence_id'] + '.tres')).write_text('\n'.join(lines) + '\n')
print('Compiled', len(data['moves']), 'editable move Resources')
