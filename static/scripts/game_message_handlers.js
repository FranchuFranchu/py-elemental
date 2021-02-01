Game.message_handlers = {
	discover_element: (data) => {		
        Game.funcs.add_element(data[0])
	},
	new_element: (data) => {
		Game.creation_reason = "create"
        $(".bg-color-1")[0].jscolor.fromString(Game.funcs.get_interpolated_colors())
        $(".bg-color-1")[0].jscolor.onInput()
        $(".element-suggestion").show()
	},
	element_data: (data) => {
        let e = data[0]
        let canvas = $(".canvas-draw-queue[data-pk=" + e.pk + "]")
        canvas.removeClass("canvas-draw-queue")
        canvas.each((idx, object) => {
            Game.funcs.generate_element_canvas(object, e)
        })
	},
	element_suggestion_vote: (data) => {
        let order = data["sort"]
        let element = data["element"]
       
        Game.funcs.add_element_to_vote_list(order, element)
	},
	element_autocomplete_list: (data) => {
        let names = data
        let e = $(".element-suggestion .name-list").empty()

        for (var i = 0; i < names.length; i++) {
            e.append($("<option/>").val(names[i]))
        }

        Game.prev_names = names
	},
	set_vote: (data) => {
        let e = $(".vote-item[data-pk="+data["pk"]+"] .current")

        e.text(data["votes"])
	},
	vote_accept: (data) => {
        let e = $(".vote-item[data-pk="+data+"]").remove()
	},
	vote_reject: (data) => {
		let e = $(".vote-item[data-pk="+data+"]").remove()
	},
	client_error: (data) => {
		console.error("Client side error:", data)
	},
	server_error: (data) => {
		console.error("Server side error:", data)
	},
}