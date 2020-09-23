Game.socket = new WebSocket("ws://" + window.location.host + "/socket");
Game.prev_names
    

Game.socket.onopen = function(e) {
    Game.socket.send("get_default_elements")
    Game.funcs.suggestion_list_setup()
    for (var i = 0; i < Object.keys(Game.known_elements).length; i++) {
        let element_id = Object.keys(Game.known_elements)[i]
        let element_pwd = Game.known_elements[element_id]
        Game.socket.send("get_element_info " + element_id + " " + element_pwd)
    }
};

Game.socket.onmessage = function(event) {
    console.debug(`[message] Data received from server: ${event.data}`);
    console.log(event.data)
    action = event.data.split(' ')[0]
    args = event.data.limited_split(' ', 2)[1]
    if (action === "discover_element") {
        Game.funcs.add_element(JSON.parse(args)[0])
    }
    if (action === "new_element") {
        Game.creation_reason = "create"
        $(".bg-color-1")[0].jscolor.fromString(Game.funcs.get_interpolated_colors())
        $(".bg-color-1")[0].jscolor.onInput()
        $(".element-suggestion").show()
    }
    if (action === "element_data") {
        let e = JSON.parse(args)[0]
        let canvas = $(".canvas-draw-queue[data-pk=" + e.pk + "]")
        canvas.removeClass("canvas-draw-queue")
        canvas.each((idx, object) => {
            Game.funcs.generate_element_canvas(object, e)

        })
    }
    if (action === "element_suggestion_vote") {
        let order = event.data.limited_split(' ', 3)[1]
        let element = JSON.parse(event.data.limited_split(' ', 3)[2])
        Game.funcs.add_element_to_vote_list(order, element)
    } 
    if (action === "element_autocomplete_list") {
        let names = JSON.parse(args)

        let e = $(".element-suggestion .name-list").empty()

        for (var i = 0; i < names.length; i++) {
            e.append($("<option/>").val(names[i]))
        }

        Game.prev_names = names
            
    }

    if (action === "set_vote") {
        console.log(args)
        let e = $(".vote-item[data-pk="+args.split(' ')[0]+"] .current")

        e.text(parseInt(args.split(' ')[1]))
    }
    if (action === "vote_accept" || action === "vote_reject") {
        let e = $(".vote-item[data-pk="+args+"]").remove()
    }
};

Game.socket.onclose = function(event) {
    if (event.wasClean) {
    } else {
        // e.g. server process killed or network down
        // event.code is usually 1006 in this case
        console.error('[close] Connection died');
    }
};

Game.socket.onerror = function(error) {
    console.error(`[error] ${error.message}`);
};
