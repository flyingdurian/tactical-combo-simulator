from pathlib import Path
import zipfile,sys
root=Path(__file__).resolve().parents[1]
output=Path(sys.argv[1]) if len(sys.argv)>1 else root.parent/'Roster5.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in root.rglob('*'):
  if not p.is_file() or any(v.startswith('capture') or v=='.godot' for v in p.relative_to(root).parts) or p.suffix=='.import':continue
  if p==output:continue
  if (p.suffix=='.pyc' or (p.suffix=='.mp4' and p.name!='Roster16_ChestDischarge.mp4')) or 'contact_audit' in p.parts or p.name.startswith(('Impact4_scene','Sequence_')):continue
  z.write(p,p.relative_to(root))
print(output,output.stat().st_size)
