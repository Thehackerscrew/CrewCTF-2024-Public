extends Camera2D


var last_mouse_position = null


func reset() -> void:
	position = Vector2(221.5, 128)
	zoom = Vector2(0.5, 0.5)


func _process(delta: float) -> void:
	if Input.is_action_pressed("left_click"):
		var mouse_position = get_local_mouse_position()
		if last_mouse_position != null:
			position += last_mouse_position - mouse_position
		last_mouse_position = mouse_position
	else:
		last_mouse_position = null


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action("zoom_in"):
		zoom *= 1.1
	
	if event.is_action("zoom_out"):
		zoom /= 1.1
