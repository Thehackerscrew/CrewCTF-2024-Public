extends Node2D

enum {
	WIRE_NS_OFF = 0,
	WIRE_EW_OFF = 1,
	WIRE_NS_ON = 2,
	WIRE_EW_ON = 3,
	CORNER_NE_OFF = 4,
	CORNER_ES_OFF = 5,
	CORNER_SW_OFF = 6,
	CORNER_WN_OFF = 7,
	CORNER_NE_ON = 8,
	CORNER_ES_ON = 9,
	CORNER_SW_ON = 10,
	CORNER_WN_ON = 11,
	FORK_NES_OFF = 12,
	FORK_ESW_OFF = 13,
	FORK_SWN_OFF = 14,
	FORK_WNE_OFF = 15,
	FORK_NES_ON = 16,
	FORK_ESW_ON = 17,
	FORK_SWN_ON = 18,
	FORK_WNE_ON = 19,
	ALL_OFF = 20,
	ALL_ON = 21,
	VIA_N_OFF = 22,
	VIA_E_OFF = 23,
	VIA_S_OFF = 24,
	VIA_W_OFF = 25,
	VIA_N_ON = 26,
	VIA_E_ON = 27,
	VIA_S_ON = 28,
	VIA_W_ON = 29,
	AND_E_OFF_W_OFF = 30,
	AND_E_ON_W_OFF = 31,
	AND_E_OFF_W_ON = 32,
	AND_E_ON_W_ON = 33,
	OR_E_OFF_W_OFF = 34,
	OR_E_ON_W_OFF = 35,
	OR_E_OFF_W_ON = 36,
	OR_E_ON_W_ON = 37,
	XOR_E_OFF_W_OFF = 38,
	XOR_E_ON_W_OFF = 39,
	XOR_E_OFF_W_ON = 40,
	XOR_E_ON_W_ON = 41,
	NOT_S_OFF = 42,
	NOT_S_ON = 43,
	SWITCH_N_OFF = 44,
	SWITCH_N_ON = 45,
	LIGHT_S_OFF = 46,
	LIGHT_S_ON = 47,
	VIA_NONE_OFF = 48,
	VIA_NONE_ON = 49,
}


const NORTH = Vector3i(0, 1, 0)
const SOUTH = Vector3i(0, -1, 0)
const EAST = Vector3i(1, 0, 0)
const WEST = Vector3i(-1, 0, 0)
const UP = Vector3i(0, 0, 1)
const DOWN = Vector3i(0, 0, -1)

@onready var tilemap = $tilemap

var grid: Dictionary = {}
var current_level: int = 0
var min_z: int = 0
var max_z: int = 0
var current_z: int = 0
var lights_on: int = 0
var transition_time = null
var propogation: Array = []
var finished: bool = false


func div2(x: int):  # Godot rounds towards 0, so we need a special case.
	if x < 0:
		return (x - 1) / 2
	else:
		return x / 2


func iso2tm(v: Vector2i) -> Vector2i:
	return Vector2i(div2(v.x + v.y), v.x - v.y)


func tm2iso(v: Vector2i) -> Vector2i:
	return Vector2i(div2(2 * v.x + v.y + 1), div2(2 * v.x - v.y + 1))


func s32(u32: int) -> int:
	if u32 & 0x80000000:
		return -0x80000000 + (u32 & 0x7fffffff)
	else:
		return u32


func render() -> void:
	tilemap.clear_layer(0)
	for coordinate in grid:
		if coordinate.z == current_z:
			tilemap.set_cell(0, iso2tm(Vector2i(coordinate.x, coordinate.y)), 1337, Vector2i(0, grid[coordinate]))


func load_level(level: int) -> void:
	grid.clear()
	current_level = level
	current_z = 0
	lights_on = 0
	
	var file = FileAccess.open("res://levels/%d" % level, FileAccess.READ)
	
	while file.get_position() < file.get_length():
		var x = s32(file.get_32())
		var y = s32(file.get_32())
		var z = s32(file.get_32())
		
		min_z = min(min_z, z)
		max_z = max(max_z, z)
		
		var tile = file.get_8()
		grid[Vector3i(x, y, z)] = tile

	render()
	
	$camera.reset()
	

func transition_level() -> void:
	transition_time = 0.0
	

func show_flag() -> void:
	finished = true
	
	var bits = []
	for coordinate in grid:
		if grid[coordinate] == SWITCH_N_OFF:
			bits.append([coordinate.x, false])
		elif grid[coordinate] == SWITCH_N_ON:
			bits.append([coordinate.x, true])
	
	bits.sort()
	
	var message = ["Congratulations! The flag is: "]
	var byte = 0
	for i in range(len(bits)):
		byte <<= 1
		
		if bits[i][1]:
			byte |= 1
		
		if (i % 8) == 7:
			message.append(String.chr(byte))
			byte = 0
	
	$camera/canvas/label.text = "".join(message)


func change_light(coordinate: Vector3i, on: bool) -> void:
	if on:
		lights_on += 1
	else:
		lights_on -= 1


func assess_lights() -> void:
	if current_level in [0, 2] and lights_on == 1:
		transition_level()
		
	if current_level == 1 and lights_on == 4:
		transition_level()
		
	if current_level == 3 and lights_on == 1:
		show_flag()


func set_tile(coordinate: Vector3i, tile: int) -> void:
	if grid[coordinate] != tile:
		grid[coordinate] = tile
		if coordinate.z == current_z:
			tilemap.set_cell(0, iso2tm(Vector2i(coordinate.x, coordinate.y)), 1337, Vector2i(0, grid[coordinate]))


func propogate(source_cordinate: Vector3i, direction: Vector3i, state: bool) -> void:
	propogation.push_back([source_cordinate, direction, state])


func do_propogate(source_cordinate: Vector3i, direction: Vector3i, state: bool) -> void:
	var destination_coordinate = source_cordinate + direction
	
	if (not destination_coordinate in grid):
		return

	match [grid[destination_coordinate], direction, state]:
		[WIRE_NS_OFF, NORTH, true]:
			set_tile(destination_coordinate, WIRE_NS_ON)
			propogate(destination_coordinate, NORTH, true)
		[WIRE_NS_OFF, SOUTH, true]:
			set_tile(destination_coordinate, WIRE_NS_ON)
			propogate(destination_coordinate, SOUTH, true)
		[WIRE_NS_ON, NORTH, false]:
			set_tile(destination_coordinate, WIRE_NS_OFF)
			propogate(destination_coordinate, NORTH, false)
		[WIRE_NS_ON, SOUTH, false]:
			set_tile(destination_coordinate, WIRE_NS_OFF)
			propogate(destination_coordinate, SOUTH, false)
		[WIRE_EW_OFF, EAST, true]:
			set_tile(destination_coordinate, WIRE_EW_ON)
			propogate(destination_coordinate, EAST, true)
		[WIRE_EW_OFF, WEST, true]:
			set_tile(destination_coordinate, WIRE_EW_ON)
			propogate(destination_coordinate, WEST, true)
		[WIRE_EW_ON, EAST, false]:
			set_tile(destination_coordinate, WIRE_EW_OFF)
			propogate(destination_coordinate, EAST, false)
		[WIRE_EW_ON, WEST, false]:
			set_tile(destination_coordinate, WIRE_EW_OFF)
			propogate(destination_coordinate, WEST, false)
		[CORNER_NE_OFF, SOUTH, true]:
			set_tile(destination_coordinate, CORNER_NE_ON)
			propogate(destination_coordinate, EAST, true)
		[CORNER_NE_OFF, WEST, true]:
			set_tile(destination_coordinate, CORNER_NE_ON)
			propogate(destination_coordinate, NORTH, true)
		[CORNER_NE_ON, SOUTH, false]:
			set_tile(destination_coordinate, CORNER_NE_OFF)
			propogate(destination_coordinate, EAST, false)
		[CORNER_NE_ON, WEST, false]:
			set_tile(destination_coordinate, CORNER_NE_OFF)
			propogate(destination_coordinate, NORTH, false)
		[CORNER_ES_OFF, WEST, true]:
			set_tile(destination_coordinate, CORNER_ES_ON)
			propogate(destination_coordinate, SOUTH, true)
		[CORNER_ES_OFF, NORTH, true]:
			set_tile(destination_coordinate, CORNER_ES_ON)
			propogate(destination_coordinate, EAST, true)
		[CORNER_ES_ON, WEST, false]:
			set_tile(destination_coordinate, CORNER_ES_OFF)
			propogate(destination_coordinate, SOUTH, false)
		[CORNER_ES_ON, NORTH, false]:
			set_tile(destination_coordinate, CORNER_ES_OFF)
			propogate(destination_coordinate, EAST, false)
		[CORNER_SW_OFF, NORTH, true]:
			set_tile(destination_coordinate, CORNER_SW_ON)
			propogate(destination_coordinate, WEST, true)
		[CORNER_SW_OFF, EAST, true]:
			set_tile(destination_coordinate, CORNER_SW_ON)
			propogate(destination_coordinate, SOUTH, true)
		[CORNER_SW_ON, NORTH, false]:
			set_tile(destination_coordinate, CORNER_SW_OFF)
			propogate(destination_coordinate, WEST, false)
		[CORNER_SW_ON, EAST, false]:
			set_tile(destination_coordinate, CORNER_SW_OFF)
			propogate(destination_coordinate, SOUTH, false)
		[CORNER_WN_OFF, EAST, true]:
			set_tile(destination_coordinate, CORNER_WN_ON)
			propogate(destination_coordinate, NORTH, true)
		[CORNER_WN_OFF, SOUTH, true]:
			set_tile(destination_coordinate, CORNER_WN_ON)
			propogate(destination_coordinate, WEST, true)
		[CORNER_WN_ON, EAST, false]:
			set_tile(destination_coordinate, CORNER_WN_OFF)
			propogate(destination_coordinate, NORTH, false)
		[CORNER_WN_ON, SOUTH, false]:
			set_tile(destination_coordinate, CORNER_WN_OFF)
			propogate(destination_coordinate, WEST, false)
		[FORK_NES_OFF, SOUTH, true]:
			set_tile(destination_coordinate, FORK_NES_ON)
			propogate(destination_coordinate, EAST, true)
			propogate(destination_coordinate, SOUTH, true)
		[FORK_NES_OFF, WEST, true]:
			set_tile(destination_coordinate, FORK_NES_ON)
			propogate(destination_coordinate, SOUTH, true)
			propogate(destination_coordinate, NORTH, true)
		[FORK_NES_OFF, NORTH, true]:
			set_tile(destination_coordinate, FORK_NES_ON)
			propogate(destination_coordinate, NORTH, true)
			propogate(destination_coordinate, EAST, true)
		[FORK_NES_ON, SOUTH, false]:
			set_tile(destination_coordinate, FORK_NES_OFF)
			propogate(destination_coordinate, EAST, false)
			propogate(destination_coordinate, SOUTH, false)
		[FORK_NES_ON, WEST, false]:
			set_tile(destination_coordinate, FORK_NES_OFF)
			propogate(destination_coordinate, SOUTH, false)
			propogate(destination_coordinate, NORTH, false)
		[FORK_NES_ON, NORTH, false]:
			set_tile(destination_coordinate, FORK_NES_OFF)
			propogate(destination_coordinate, NORTH, false)
			propogate(destination_coordinate, EAST, false)
		[FORK_ESW_OFF, WEST, true]:
			set_tile(destination_coordinate, FORK_ESW_ON)
			propogate(destination_coordinate, SOUTH, true)
			propogate(destination_coordinate, WEST, true)
		[FORK_ESW_OFF, NORTH, true]:
			set_tile(destination_coordinate, FORK_ESW_ON)
			propogate(destination_coordinate, WEST, true)
			propogate(destination_coordinate, EAST, true)
		[FORK_ESW_OFF, EAST, true]:
			set_tile(destination_coordinate, FORK_ESW_ON)
			propogate(destination_coordinate, EAST, true)
			propogate(destination_coordinate, SOUTH, true)
		[FORK_ESW_ON, WEST, false]:
			set_tile(destination_coordinate, FORK_ESW_OFF)
			propogate(destination_coordinate, SOUTH, false)
			propogate(destination_coordinate, WEST, false)
		[FORK_ESW_ON, NORTH, false]:
			set_tile(destination_coordinate, FORK_ESW_OFF)
			propogate(destination_coordinate, WEST, false)
			propogate(destination_coordinate, EAST, false)
		[FORK_ESW_ON, EAST, false]:
			set_tile(destination_coordinate, FORK_ESW_OFF)
			propogate(destination_coordinate, EAST, false)
			propogate(destination_coordinate, SOUTH, false)
		[FORK_SWN_OFF, NORTH, true]:
			set_tile(destination_coordinate, FORK_SWN_ON)
			propogate(destination_coordinate, WEST, true)
			propogate(destination_coordinate, NORTH, true)
		[FORK_SWN_OFF, EAST, true]:
			set_tile(destination_coordinate, FORK_SWN_ON)
			propogate(destination_coordinate, NORTH, true)
			propogate(destination_coordinate, SOUTH, true)
		[FORK_SWN_OFF, SOUTH, true]:
			set_tile(destination_coordinate, FORK_SWN_ON)
			propogate(destination_coordinate, SOUTH, true)
			propogate(destination_coordinate, WEST, true)
		[FORK_SWN_ON, NORTH, false]:
			set_tile(destination_coordinate, FORK_SWN_OFF)
			propogate(destination_coordinate, WEST, false)
			propogate(destination_coordinate, NORTH, false)
		[FORK_SWN_ON, EAST, false]:
			set_tile(destination_coordinate, FORK_SWN_OFF)
			propogate(destination_coordinate, NORTH, false)
			propogate(destination_coordinate, SOUTH, false)
		[FORK_SWN_ON, SOUTH, false]:
			set_tile(destination_coordinate, FORK_SWN_OFF)
			propogate(destination_coordinate, SOUTH, false)
			propogate(destination_coordinate, WEST, false)
		[FORK_WNE_OFF, EAST, true]:
			set_tile(destination_coordinate, FORK_WNE_ON)
			propogate(destination_coordinate, NORTH, true)
			propogate(destination_coordinate, EAST, true)
		[FORK_WNE_OFF, SOUTH, true]:
			set_tile(destination_coordinate, FORK_WNE_ON)
			propogate(destination_coordinate, EAST, true)
			propogate(destination_coordinate, WEST, true)
		[FORK_WNE_OFF, WEST, true]:
			set_tile(destination_coordinate, FORK_WNE_ON)
			propogate(destination_coordinate, WEST, true)
			propogate(destination_coordinate, NORTH, true)
		[FORK_WNE_ON, EAST, false]:
			set_tile(destination_coordinate, FORK_WNE_OFF)
			propogate(destination_coordinate, NORTH, false)
			propogate(destination_coordinate, EAST, false)
		[FORK_WNE_ON, SOUTH, false]:
			set_tile(destination_coordinate, FORK_WNE_OFF)
			propogate(destination_coordinate, EAST, false)
			propogate(destination_coordinate, WEST, false)
		[FORK_WNE_ON, WEST, false]:
			set_tile(destination_coordinate, FORK_WNE_OFF)
			propogate(destination_coordinate, WEST, false)
			propogate(destination_coordinate, NORTH, false)
		[ALL_OFF, SOUTH, true]:
			set_tile(destination_coordinate, ALL_ON)
			propogate(destination_coordinate, EAST, true)
			propogate(destination_coordinate, SOUTH, true)
			propogate(destination_coordinate, WEST, true)
		[ALL_OFF, WEST, true]:
			set_tile(destination_coordinate, ALL_ON)
			propogate(destination_coordinate, SOUTH, true)
			propogate(destination_coordinate, WEST, true)
			propogate(destination_coordinate, NORTH, true)
		[ALL_OFF, NORTH, true]:
			set_tile(destination_coordinate, ALL_ON)
			propogate(destination_coordinate, WEST, true)
			propogate(destination_coordinate, NORTH, true)
			propogate(destination_coordinate, EAST, true)
		[ALL_OFF, EAST, true]:
			set_tile(destination_coordinate, ALL_ON)
			propogate(destination_coordinate, NORTH, true)
			propogate(destination_coordinate, EAST, true)
			propogate(destination_coordinate, SOUTH, true)
		[ALL_ON, SOUTH, false]:
			set_tile(destination_coordinate, ALL_OFF)
			propogate(destination_coordinate, EAST, false)
			propogate(destination_coordinate, SOUTH, false)
			propogate(destination_coordinate, WEST, false)
		[ALL_ON, WEST, false]:
			set_tile(destination_coordinate, ALL_OFF)
			propogate(destination_coordinate, SOUTH, false)
			propogate(destination_coordinate, WEST, false)
			propogate(destination_coordinate, NORTH, false)
		[ALL_ON, NORTH, false]:
			set_tile(destination_coordinate, ALL_OFF)
			propogate(destination_coordinate, WEST, false)
			propogate(destination_coordinate, NORTH, false)
			propogate(destination_coordinate, EAST, false)
		[ALL_ON, EAST, false]:
			set_tile(destination_coordinate, ALL_OFF)
			propogate(destination_coordinate, NORTH, false)
			propogate(destination_coordinate, EAST, false)
			propogate(destination_coordinate, SOUTH, false)
		[VIA_N_OFF, SOUTH, true]:
			set_tile(destination_coordinate, VIA_N_ON)
			propogate(destination_coordinate, UP, true)
			propogate(destination_coordinate, DOWN, true)
		[VIA_N_OFF, DOWN, true]:
			set_tile(destination_coordinate, VIA_N_ON)
			propogate(destination_coordinate, DOWN, true)
			propogate(destination_coordinate, NORTH, true)
		[VIA_N_OFF, UP, true]:
			set_tile(destination_coordinate, VIA_N_ON)
			propogate(destination_coordinate, NORTH, true)
			propogate(destination_coordinate, UP, true)
		[VIA_N_ON, SOUTH, false]:
			set_tile(destination_coordinate, VIA_N_OFF)
			propogate(destination_coordinate, UP, false)
			propogate(destination_coordinate, DOWN, false)
		[VIA_N_ON, DOWN, false]:
			set_tile(destination_coordinate, VIA_N_OFF)
			propogate(destination_coordinate, DOWN, false)
			propogate(destination_coordinate, NORTH, false)
		[VIA_N_ON, UP, false]:
			set_tile(destination_coordinate, VIA_N_OFF)
			propogate(destination_coordinate, NORTH, false)
			propogate(destination_coordinate, UP, false)
		[VIA_E_OFF, WEST, true]:
			set_tile(destination_coordinate, VIA_E_ON)
			propogate(destination_coordinate, UP, true)
			propogate(destination_coordinate, DOWN, true)
		[VIA_E_OFF, DOWN, true]:
			set_tile(destination_coordinate, VIA_E_ON)
			propogate(destination_coordinate, DOWN, true)
			propogate(destination_coordinate, EAST, true)
		[VIA_E_OFF, UP, true]:
			set_tile(destination_coordinate, VIA_E_ON)
			propogate(destination_coordinate, EAST, true)
			propogate(destination_coordinate, UP, true)
		[VIA_E_ON, WEST, false]:
			set_tile(destination_coordinate, VIA_E_OFF)
			propogate(destination_coordinate, UP, false)
			propogate(destination_coordinate, DOWN, false)
		[VIA_E_ON, DOWN, false]:
			set_tile(destination_coordinate, VIA_E_OFF)
			propogate(destination_coordinate, DOWN, false)
			propogate(destination_coordinate, EAST, false)
		[VIA_E_ON, UP, false]:
			set_tile(destination_coordinate, VIA_E_OFF)
			propogate(destination_coordinate, EAST, false)
			propogate(destination_coordinate, UP, false)
		[VIA_S_OFF, NORTH, true]:
			set_tile(destination_coordinate, VIA_S_ON)
			propogate(destination_coordinate, UP, true)
			propogate(destination_coordinate, DOWN, true)
		[VIA_S_OFF, DOWN, true]:
			set_tile(destination_coordinate, VIA_S_ON)
			propogate(destination_coordinate, DOWN, true)
			propogate(destination_coordinate, SOUTH, true)
		[VIA_S_OFF, UP, true]:
			set_tile(destination_coordinate, VIA_S_ON)
			propogate(destination_coordinate, SOUTH, true)
			propogate(destination_coordinate, UP, true)
		[VIA_S_ON, NORTH, false]:
			set_tile(destination_coordinate, VIA_S_OFF)
			propogate(destination_coordinate, UP, false)
			propogate(destination_coordinate, DOWN, false)
		[VIA_S_ON, DOWN, false]:
			set_tile(destination_coordinate, VIA_S_OFF)
			propogate(destination_coordinate, DOWN, false)
			propogate(destination_coordinate, SOUTH, false)
		[VIA_S_ON, UP, false]:
			set_tile(destination_coordinate, VIA_S_OFF)
			propogate(destination_coordinate, SOUTH, false)
			propogate(destination_coordinate, UP, false)
		[VIA_W_OFF, EAST, true]:
			set_tile(destination_coordinate, VIA_W_ON)
			propogate(destination_coordinate, UP, true)
			propogate(destination_coordinate, DOWN, true)
		[VIA_W_OFF, DOWN, true]:
			set_tile(destination_coordinate, VIA_W_ON)
			propogate(destination_coordinate, DOWN, true)
			propogate(destination_coordinate, WEST, true)
		[VIA_W_OFF, UP, true]:
			set_tile(destination_coordinate, VIA_W_ON)
			propogate(destination_coordinate, WEST, true)
			propogate(destination_coordinate, UP, true)
		[VIA_W_ON, EAST, false]:
			set_tile(destination_coordinate, VIA_W_OFF)
			propogate(destination_coordinate, UP, false)
			propogate(destination_coordinate, DOWN, false)
		[VIA_W_ON, DOWN, false]:
			set_tile(destination_coordinate, VIA_W_OFF)
			propogate(destination_coordinate, DOWN, false)
			propogate(destination_coordinate, WEST, false)
		[VIA_W_ON, UP, false]:
			set_tile(destination_coordinate, VIA_W_OFF)
			propogate(destination_coordinate, WEST, false)
			propogate(destination_coordinate, UP, false)
		[AND_E_ON_W_ON, EAST, false]:
			set_tile(destination_coordinate, AND_E_ON_W_OFF)
			propogate(destination_coordinate, NORTH, false)
		[AND_E_ON_W_ON, WEST, false]:
			set_tile(destination_coordinate, AND_E_OFF_W_ON)
			propogate(destination_coordinate, NORTH, false)
		[AND_E_ON_W_OFF, EAST, true]:
			set_tile(destination_coordinate, AND_E_ON_W_ON)
			propogate(destination_coordinate, NORTH, true)
		[AND_E_ON_W_OFF, WEST, false]:
			set_tile(destination_coordinate, AND_E_OFF_W_OFF)
		[AND_E_OFF_W_ON, EAST, false]:
			set_tile(destination_coordinate, AND_E_OFF_W_OFF)
		[AND_E_OFF_W_ON, WEST, true]:
			set_tile(destination_coordinate, AND_E_ON_W_ON)
			propogate(destination_coordinate, NORTH, true)
		[AND_E_OFF_W_OFF, EAST, true]:
			set_tile(destination_coordinate, AND_E_OFF_W_ON)
		[AND_E_OFF_W_OFF, WEST, true]:
			set_tile(destination_coordinate, AND_E_ON_W_OFF)
		[OR_E_ON_W_ON, EAST, false]:
			set_tile(destination_coordinate, OR_E_ON_W_OFF)
		[OR_E_ON_W_ON, WEST, false]:
			set_tile(destination_coordinate, OR_E_OFF_W_ON)
		[OR_E_ON_W_OFF, EAST, true]:
			set_tile(destination_coordinate, OR_E_ON_W_ON)
		[OR_E_ON_W_OFF, WEST, false]:
			set_tile(destination_coordinate, OR_E_OFF_W_OFF)
			propogate(destination_coordinate, NORTH, false)
		[OR_E_OFF_W_ON, EAST, false]:
			set_tile(destination_coordinate, OR_E_OFF_W_OFF)
			propogate(destination_coordinate, NORTH, false)
		[OR_E_OFF_W_ON, WEST, true]:
			set_tile(destination_coordinate, OR_E_ON_W_ON)
		[OR_E_OFF_W_OFF, EAST, true]:
			set_tile(destination_coordinate, OR_E_OFF_W_ON)
			propogate(destination_coordinate, NORTH, true)
		[OR_E_OFF_W_OFF, WEST, true]:
			set_tile(destination_coordinate, OR_E_ON_W_OFF)
			propogate(destination_coordinate, NORTH, true)
		[XOR_E_ON_W_ON, EAST, false]:
			set_tile(destination_coordinate, XOR_E_ON_W_OFF)
			propogate(destination_coordinate, NORTH, true)
		[XOR_E_ON_W_ON, WEST, false]:
			set_tile(destination_coordinate, XOR_E_OFF_W_ON)
			propogate(destination_coordinate, NORTH, true)
		[XOR_E_ON_W_OFF, EAST, true]:
			set_tile(destination_coordinate, XOR_E_ON_W_ON)
			propogate(destination_coordinate, NORTH, false)
		[XOR_E_ON_W_OFF, WEST, false]:
			set_tile(destination_coordinate, XOR_E_OFF_W_OFF)
			propogate(destination_coordinate, NORTH, false)
		[XOR_E_OFF_W_ON, EAST, false]:
			set_tile(destination_coordinate, XOR_E_OFF_W_OFF)
			propogate(destination_coordinate, NORTH, false)
		[XOR_E_OFF_W_ON, WEST, true]:
			set_tile(destination_coordinate, XOR_E_ON_W_ON)
			propogate(destination_coordinate, NORTH, false)
		[XOR_E_OFF_W_OFF, EAST, true]:
			set_tile(destination_coordinate, XOR_E_OFF_W_ON)
			propogate(destination_coordinate, NORTH, true)
		[XOR_E_OFF_W_OFF, WEST, true]:
			set_tile(destination_coordinate, XOR_E_ON_W_OFF)
			propogate(destination_coordinate, NORTH, true)
		[NOT_S_OFF, NORTH, true]:
			set_tile(destination_coordinate, NOT_S_ON)
			propogate(destination_coordinate, NORTH, false)
		[NOT_S_ON, NORTH, false]:
			set_tile(destination_coordinate, NOT_S_OFF)
			propogate(destination_coordinate, NORTH, true)
		[LIGHT_S_OFF, NORTH, true]:
			set_tile(destination_coordinate, LIGHT_S_ON)
			change_light(destination_coordinate, true)
		[LIGHT_S_ON, NORTH, false]:
			set_tile(destination_coordinate, LIGHT_S_OFF)
			change_light(destination_coordinate, false)
		[VIA_NONE_OFF, DOWN, true]:
			set_tile(destination_coordinate, VIA_NONE_ON)
			propogate(destination_coordinate, DOWN, true)
		[VIA_NONE_OFF, UP, true]:
			set_tile(destination_coordinate, VIA_NONE_ON)
			propogate(destination_coordinate, UP, true)
		[VIA_NONE_ON, DOWN, false]:
			set_tile(destination_coordinate, VIA_NONE_OFF)
			propogate(destination_coordinate, DOWN, false)
		[VIA_NONE_ON, UP, false]:
			set_tile(destination_coordinate, VIA_NONE_OFF)
			propogate(destination_coordinate, UP, false)


func process_propogation() -> void:
	while len(propogation):
		var item = propogation.pop_back()
		do_propogate(item[0], item[1], item[2])
		
	assess_lights()


func tile_clicked(coordinate: Vector3i) -> void:
	if coordinate not in grid:
		return
	
	match grid[coordinate]:
		SWITCH_N_OFF:
			set_tile(coordinate, SWITCH_N_ON)
			propogate(coordinate, NORTH, true)
		SWITCH_N_ON:
			set_tile(coordinate, SWITCH_N_OFF)
			propogate(coordinate, NORTH, false)
			
	process_propogation()


func _ready() -> void:
	load_level(0)


func _process(delta: float) -> void:
	if transition_time != null:
		transition_time += delta
		
		if transition_time > 1.0:
			transition_time = null
			load_level(current_level + 1)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_released("left_click") and transition_time == null and not finished:
		var cooridnate = tm2iso($tilemap.local_to_map($tilemap.get_local_mouse_position()))
		tile_clicked(Vector3i(cooridnate.x, cooridnate.y, current_z))
		
	if event.is_action_released("up"):
		if current_z != max_z:
			current_z += 1
			render()
		
	if event.is_action_released("down"):
		if current_z != min_z:
			current_z -= 1
			render()
