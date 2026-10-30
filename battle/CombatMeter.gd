class_name CombatMeter
extends RefCounted
## Shared team economy; gains are called only by successful eligible contact.
signal changed(value: int)
var maximum: int = 300
var value: int = 0
func gain(amount: int) -> void:
	value = clampi(value + maxi(0, amount), 0, maximum)
	changed.emit(value)
func spend(amount: int) -> bool:
	if amount < 0 or value < amount: return false
	value -= amount
	changed.emit(value)
	return true
func spend_special() -> bool:
	return spend(100)
