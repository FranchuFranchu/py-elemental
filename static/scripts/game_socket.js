Game.socket = new WebSocket("ws://localhost:8000/socket");
Game.socket.onopen = function(e) {
    console.log("[open] Connection established");
    Game.socket.send("get_default_elements")
};

Game.socket.onmessage = function(event) {
    console.debug(`[message] Data received from server: ${event.data}`);
    action = event.data.split(' ')[0]
    args = event.data.limited_split(' ', 2)[1]
    if (action === "discover_element") {
        Game.funcs.add_element(JSON.parse(args)[0])
    }
    if (action === "new_element") {
        $(".element-creation-menu").show()
    }
};

Game.socket.onclose = function(event) {
    if (event.wasClean) {
        console.log(`[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`);
    } else {
        // e.g. server process killed or network down
        // event.code is usually 1006 in this case
        console.error('[close] Connection died');
    }
};

Game.socket.onerror = function(error) {
    console.error(`[error] ${error.message}`);
};
