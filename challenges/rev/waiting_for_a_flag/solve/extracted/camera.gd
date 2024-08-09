extends Camera2D
var beckett0 = null
func reset() -> void:
	position = Vector2(221.5, 128)
	zoom = Vector2(0.5, 0.5)
func _process(beckett1: float) -> void:
	if Input.is_action_pressed("left_click"):
		var beckett2 = get_local_mouse_position()
		if beckett0 != null:
			position += beckett0 - beckett2
		beckett0 = beckett2
	else:
		beckett0 = null
func _unhandled_input(beckett3: InputEvent) -> void:
	if beckett3.is_action("zoom_in"):
		zoom *= 1.1
	if beckett3.is_action("zoom_out"):
		zoom /= 1.1