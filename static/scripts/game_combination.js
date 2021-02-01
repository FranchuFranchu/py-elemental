Game.funcs.combine_elements = function() {
	let element_ids = Game.funcs.get_current_ingredients()
	
	for (var i = 0; i < element_ids.length; i++) {
		if (element_ids[i] === undefined) {
			element_ids[i] = "0"
		}
	}
	console.log(element_ids)
	
	Game.socket.send_data("combine", element_ids)
}

Game.funcs.get_current_ingredients = function () {

	let element_ids = []

	$(".drop-slot").each(function(idx, e) {
		element_ids.push($(e).attr("data-password"))
	})

	return element_ids
}
Game.funcs.on_touch_end = function(event) {
	alert("HI")
}