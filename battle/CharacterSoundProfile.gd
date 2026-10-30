class_name CharacterSoundProfile
extends Resource
## Semantic keys: attack, exertion, special, ultimate, assist, hurt, defeat, victory.
## Empty clip pool deliberately means silence; weapon/impact audio is independent.
@export var clips:Dictionary={}
@export var provenance:Dictionary={}
@export var volume_db:float=0
@export var cooldown_seconds:float=.8
@export var priorities:Dictionary={"ultimate":100,"defeat":90,"special":60,"hurt":30,"attack":10}
@export var missing_fallback:String="silence"
