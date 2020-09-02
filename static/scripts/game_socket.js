Game.socket = new WebSocket("ws://localhost:8000/socket");
Game.prev_names

Game.socket.onopen = function(e) {
    Game.socket.send("get_default_elements")
    Game.funcs.element_list_setup()
};

Game.socket.onmessage = function(event) {
    console.debug(`[message] Data received from server: ${event.data}`);
    action = event.data.split(' ')[0]
    args = event.data.limited_split(' ', 2)[1]
    if (action === "discover_element") {
        Game.funcs.add_element(JSON.parse(args)[0])
    }
    if (action === "new_element") {
        Game.funcs.set_tab("element-suggestion")
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

    if (action === "upvote") {
        console.log(args)
        let e = $(".vote-item[data-pk="+args+"] .current")

        e.text(parseInt(e.text()) + 1)
    }

    if (action === "downvote") {
        console.log(args)
        let e = $(".vote-item[data-pk="+args+"] .current")

        e.text(parseInt(e.text()) + -1)
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
