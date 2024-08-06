extends Node2D
@onready var tilemap = $tilemap
var beckett0: Dictionary = {}
var beckett1: int = 0
var beckett2: int = 0
var beckett3: int = 0
var beckett4: int = 0
var beckett5: int = 0
var beckett6 = null
var beckett7: Array = []
var beckett8: bool = false
func beckett9(x: int):  # Godot rounds towards 0, so we need a special case.
	if x < 0:
		return (x - 1) / 2
	else:
		return x / 2
func beckett10(beckett11: Vector2i) -> Vector2i:
	return Vector2i(beckett9(beckett11.x + beckett11.y), beckett11.x - beckett11.y)
func beckett12(beckett11: Vector2i) -> Vector2i:
	return Vector2i(beckett9(2 * beckett11.x + beckett11.y + 1), beckett9(2 * beckett11.x - beckett11.y + 1))
func beckett13(beckett14: int) -> int:
	if beckett14 & 0x80000000:
		return -0x80000000 + (beckett14 & 0x7fffffff)
	else:
		return beckett14
func beckett15() -> void:
	tilemap.clear_layer(0)
	for beckett16 in beckett0:
		if beckett16.z == beckett4:
			tilemap.set_cell(0, beckett10(Vector2i(beckett16.x, beckett16.y)), 1337, Vector2i(0, beckett0[beckett16]))
func beckett17(beckett18: int) -> void:
	beckett0.clear()
	beckett1 = beckett18
	beckett4 = 0
	beckett5 = 0
	var beckett19 = FileAccess.open("res://levels/%d" % beckett18, FileAccess.READ)
	while beckett19.get_position() < beckett19.get_length():
		var x = beckett13(beckett19.get_32())
		var y = beckett13(beckett19.get_32())
		var z = beckett13(beckett19.get_32())
		beckett2 = min(beckett2, z)
		beckett3 = max(beckett3, z)
		var beckett20 = beckett19.get_8()
		beckett0[Vector3i(x, y, z)] = beckett20
	beckett15()
	$camera.reset()
func beckett21() -> void:
	beckett6 = 0.0
func beckett22() -> void:
	beckett8 = true
	var beckett23 = []
	for beckett16 in beckett0:
		if beckett0[beckett16] == 44:
			beckett23.append([beckett16.x, false])
		elif beckett0[beckett16] == 45:
			beckett23.append([beckett16.x, true])
	beckett23.sort()
	var beckett25 = ["Congratulations! The flag is: "]
	var beckett26 = 0
	for beckett27 in range(len(beckett23)):
		beckett26 <<= 1
		if beckett23[beckett27][1]:
			beckett26 |= 1
		if (beckett27 % 8) == 7:
			beckett25.append(String.chr(beckett26))
			beckett26 = 0
	$camera/canvas/label.text = "".join(beckett25)
func beckett28(beckett16: Vector3i, beckett29: bool) -> void:
	if beckett29:
		beckett5 += 1
	else:
		beckett5 -= 1
func beckett30() -> void:
	if beckett1 in [0, 2] and beckett5 == 1:
		beckett21()
	if beckett1 == 1 and beckett5 == 4:
		beckett21()
	if beckett1 == 3 and beckett5 == 1:
		beckett22()
func beckett31(beckett16: Vector3i, beckett20: int) -> void:
	if beckett0[beckett16] != beckett20:
		beckett0[beckett16] = beckett20
		if beckett16.z == beckett4:
			tilemap.set_cell(0, beckett10(Vector2i(beckett16.x, beckett16.y)), 1337, Vector2i(0, beckett0[beckett16]))
func beckett32(beckett33: Vector3i, beckett34: Vector3i, beckett35: bool) -> void:
	beckett7.push_back([beckett33, beckett34, beckett35])
func beckett36(beckett33: Vector3i, beckett34: Vector3i, beckett35: bool) -> void:
	var beckett37 = beckett33 + beckett34
	if (not beckett37 in beckett0):
		return
	match [beckett0[beckett37], beckett34, beckett35]:
		[0, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 2)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[0, Vector3i(0, -1, 0), true]:
			beckett31(beckett37, 2)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
		[2, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 0)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[2, Vector3i(0, -1, 0), false]:
			beckett31(beckett37, 0)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
		[1, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 3)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
		[1, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 3)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
		[3, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 1)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
		[3, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 1)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
		[4, Vector3i(0, -1, 0), true]:
			beckett31(beckett37, 8)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
		[4, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 8)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[8, Vector3i(0, -1, 0), false]:
			beckett31(beckett37, 4)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
		[8, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 4)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[5, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 9)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
		[5, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 9)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
		[9, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 5)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
		[9, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 5)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
		[6, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 10)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
		[6, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 10)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
		[10, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 6)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
		[10, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 6)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
		[7, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 11)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[7, Vector3i(0, -1, 0), true]:
			beckett31(beckett37, 11)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
		[11, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 7)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[11, Vector3i(0, -1, 0), false]:
			beckett31(beckett37, 7)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
		[12, Vector3i(0, -1, 0), true]:
			beckett31(beckett37, 16)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
		[12, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 16)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[12, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 16)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
		[16, Vector3i(0, -1, 0), false]:
			beckett31(beckett37, 12)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
		[16, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 12)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[16, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 12)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
		[13, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 17)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
		[13, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 17)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
		[13, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 17)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
		[17, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 13)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
		[17, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 13)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
		[17, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 13)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
		[14, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 18)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[14, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 18)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
		[14, Vector3i(0, -1, 0), true]:
			beckett31(beckett37, 18)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
		[18, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 14)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[18, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 14)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
		[18, Vector3i(0, -1, 0), false]:
			beckett31(beckett37, 14)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
		[15, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 19)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
		[15, Vector3i(0, -1, 0), true]:
			beckett31(beckett37, 19)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
		[15, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 19)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[19, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 15)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
		[19, Vector3i(0, -1, 0), false]:
			beckett31(beckett37, 15)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
		[19, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 15)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[20, Vector3i(0, -1, 0), true]:
			beckett31(beckett37, 21)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
		[20, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 21)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[20, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 21)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
		[20, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 21)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
		[21, Vector3i(0, -1, 0), false]:
			beckett31(beckett37, 20)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
		[21, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 20)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[21, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 20)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
		[21, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 20)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
		[22, Vector3i(0, -1, 0), true]:
			beckett31(beckett37, 26)
			beckett32(beckett37, Vector3i(0, 0, 1), true)
			beckett32(beckett37, Vector3i(0, 0, -1), true)
		[22, Vector3i(0, 0, -1), true]:
			beckett31(beckett37, 26)
			beckett32(beckett37, Vector3i(0, 0, -1), true)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[22, Vector3i(0, 0, 1), true]:
			beckett31(beckett37, 26)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
			beckett32(beckett37, Vector3i(0, 0, 1), true)
		[26, Vector3i(0, -1, 0), false]:
			beckett31(beckett37, 22)
			beckett32(beckett37, Vector3i(0, 0, 1), false)
			beckett32(beckett37, Vector3i(0, 0, -1), false)
		[26, Vector3i(0, 0, -1), false]:
			beckett31(beckett37, 22)
			beckett32(beckett37, Vector3i(0, 0, -1), false)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[26, Vector3i(0, 0, 1), false]:
			beckett31(beckett37, 22)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
			beckett32(beckett37, Vector3i(0, 0, 1), false)
		[23, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 27)
			beckett32(beckett37, Vector3i(0, 0, 1), true)
			beckett32(beckett37, Vector3i(0, 0, -1), true)
		[23, Vector3i(0, 0, -1), true]:
			beckett31(beckett37, 27)
			beckett32(beckett37, Vector3i(0, 0, -1), true)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
		[23, Vector3i(0, 0, 1), true]:
			beckett31(beckett37, 27)
			beckett32(beckett37, Vector3i(1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, 0, 1), true)
		[27, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 23)
			beckett32(beckett37, Vector3i(0, 0, 1), false)
			beckett32(beckett37, Vector3i(0, 0, -1), false)
		[27, Vector3i(0, 0, -1), false]:
			beckett31(beckett37, 23)
			beckett32(beckett37, Vector3i(0, 0, -1), false)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
		[27, Vector3i(0, 0, 1), false]:
			beckett31(beckett37, 23)
			beckett32(beckett37, Vector3i(1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, 0, 1), false)
		[24, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 28)
			beckett32(beckett37, Vector3i(0, 0, 1), true)
			beckett32(beckett37, Vector3i(0, 0, -1), true)
		[24, Vector3i(0, 0, -1), true]:
			beckett31(beckett37, 28)
			beckett32(beckett37, Vector3i(0, 0, -1), true)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
		[24, Vector3i(0, 0, 1), true]:
			beckett31(beckett37, 28)
			beckett32(beckett37, Vector3i(0, -1, 0), true)
			beckett32(beckett37, Vector3i(0, 0, 1), true)
		[28, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 24)
			beckett32(beckett37, Vector3i(0, 0, 1), false)
			beckett32(beckett37, Vector3i(0, 0, -1), false)
		[28, Vector3i(0, 0, -1), false]:
			beckett31(beckett37, 24)
			beckett32(beckett37, Vector3i(0, 0, -1), false)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
		[28, Vector3i(0, 0, 1), false]:
			beckett31(beckett37, 24)
			beckett32(beckett37, Vector3i(0, -1, 0), false)
			beckett32(beckett37, Vector3i(0, 0, 1), false)
		[25, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 29)
			beckett32(beckett37, Vector3i(0, 0, 1), true)
			beckett32(beckett37, Vector3i(0, 0, -1), true)
		[25, Vector3i(0, 0, -1), true]:
			beckett31(beckett37, 29)
			beckett32(beckett37, Vector3i(0, 0, -1), true)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
		[25, Vector3i(0, 0, 1), true]:
			beckett31(beckett37, 29)
			beckett32(beckett37, Vector3i(-1, 0, 0), true)
			beckett32(beckett37, Vector3i(0, 0, 1), true)
		[29, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 25)
			beckett32(beckett37, Vector3i(0, 0, 1), false)
			beckett32(beckett37, Vector3i(0, 0, -1), false)
		[29, Vector3i(0, 0, -1), false]:
			beckett31(beckett37, 25)
			beckett32(beckett37, Vector3i(0, 0, -1), false)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
		[29, Vector3i(0, 0, 1), false]:
			beckett31(beckett37, 25)
			beckett32(beckett37, Vector3i(-1, 0, 0), false)
			beckett32(beckett37, Vector3i(0, 0, 1), false)
		[33, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 31)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[33, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 32)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[31, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 33)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[31, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 30)
		[32, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 30)
		[32, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 33)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[30, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 32)
		[30, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 31)
		[37, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 35)
		[37, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 36)
		[35, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 37)
		[35, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 34)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[36, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 34)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[36, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 37)
		[34, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 36)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[34, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 35)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[41, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 39)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[41, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 40)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[39, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 41)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[39, Vector3i(-1, 0, 0), false]:
			beckett31(beckett37, 38)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[40, Vector3i(1, 0, 0), false]:
			beckett31(beckett37, 38)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[40, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 41)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[38, Vector3i(1, 0, 0), true]:
			beckett31(beckett37, 40)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[38, Vector3i(-1, 0, 0), true]:
			beckett31(beckett37, 39)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[42, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 43)
			beckett32(beckett37, Vector3i(0, 1, 0), false)
		[43, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 42)
			beckett32(beckett37, Vector3i(0, 1, 0), true)
		[46, Vector3i(0, 1, 0), true]:
			beckett31(beckett37, 47)
			beckett28(beckett37, true)
		[47, Vector3i(0, 1, 0), false]:
			beckett31(beckett37, 46)
			beckett28(beckett37, false)
		[48, Vector3i(0, 0, -1), true]:
			beckett31(beckett37, 49)
			beckett32(beckett37, Vector3i(0, 0, -1), true)
		[48, Vector3i(0, 0, 1), true]:
			beckett31(beckett37, 49)
			beckett32(beckett37, Vector3i(0, 0, 1), true)
		[49, Vector3i(0, 0, -1), false]:
			beckett31(beckett37, 48)
			beckett32(beckett37, Vector3i(0, 0, -1), false)
		[49, Vector3i(0, 0, 1), false]:
			beckett31(beckett37, 48)
			beckett32(beckett37, Vector3i(0, 0, 1), false)
func beckett38() -> void:
	while len(beckett7):
		var beckett39 = beckett7.pop_back()
		beckett36(beckett39[0], beckett39[1], beckett39[2])
	beckett30()
func beckett40(beckett16: Vector3i) -> void:
	if beckett16 not in beckett0:
		return
	match beckett0[beckett16]:
		44:
			beckett31(beckett16, 45)
			beckett32(beckett16, Vector3i(0, 1, 0), true)
		45:
			beckett31(beckett16, 44)
			beckett32(beckett16, Vector3i(0, 1, 0), false)
	beckett38()
func _ready() -> void:
	beckett17(0)
func _process(beckett41: float) -> void:
	if beckett6 != null:
		beckett6 += beckett41
		if beckett6 > 1.0:
			beckett6 = null
			beckett17(beckett1 + 1)
func _unhandled_input(beckett42: InputEvent) -> void:
	if beckett42.is_action_released("left_click") and beckett6 == null and not beckett8:
		var beckett43 = beckett12($tilemap.local_to_map($tilemap.get_local_mouse_position()))
		beckett40(Vector3i(beckett43.x, beckett43.y, beckett4))
	if beckett42.is_action_released("up"):
		if beckett4 != beckett3:
			beckett4 += 1
			beckett15()
	if beckett42.is_action_released("down"):
		if beckett4 != beckett2:
			beckett4 -= 1
			beckett15()
