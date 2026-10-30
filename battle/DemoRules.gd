class_name DemoRules
extends Resource
@export var intro_ticks: int = 45
@export var sequence_charges: int = 4
@export var grace_ticks: int = 150
@export var buffer_ticks: int = 18
@export var cross_window: int = 6
@export var cross_suspend_ticks: int = 12
@export var cross_cooldown_ticks: int = 36
@export var cross_limit_per_phase: int = 2
@export var juggle_limit: int = 12
@export var combo_scaling_step: float = 0.06
@export var minimum_scaling: float = 0.55
@export var target_hp: int = 400

@export var player_hp: int = 120
@export var perfect_block_ticks: int = 8
@export var dodge_ticks: int = 6
@export var dodge_recovery_ticks: int = 24
@export var dodge_cooldown_ticks: int = 44
@export var block_damage_factor: float = 0.5
@export var perfect_damage_factor: float = 0.2

@export var meter_maximum: int = 300
@export var cancel_cost: int = 60
@export var cancel_followup_ticks: int = 36
@export var cancel_slow_ticks: int = 10
@export var cancel_slow_rate: float = 0.35
@export var cancel_extra_actions_per_phase: int = 1
@export var overlap_meter_bonus: int = 8
@export var defense_meter_bonus: int = 10
