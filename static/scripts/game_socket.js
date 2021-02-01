Game.reconnect_tries = 3

Game.funcs.connect = function() {
    Game.socket = new WebSocket("ws://" + window.location.host + "/socket");

    Game.socket.onopen = function(e) {
        Game.socket.send_data("get_default_elements", {})
        Game.funcs.suggestion_list_setup()
        for (var i = 0; i < Object.keys(Game.known_elements).length; i++) {
            let element_id = Object.keys(Game.known_elements)[i]
            let element_pwd = Game.known_elements[element_id]
            Game.funcs.add_element({"pk": element_id, fields: {"password": element_pwd}, "incomplete": true})
            Game.socket.send_data("get_element_info", {id: element_id, pwd: element_pwd})
        }
    };

    Game.socket.onmessage = function(event) {
        action = event.data.split(' ')[0]
        data = JSON.parse(event.data.limited_split(' ', 2)[1])
        console.debug(action, data)
        
        if (!Game.message_handlers[action]) {
            console.warn("Unknown action:", action)
        } else {
            Game.message_handlers[action](data)
        }
        
        
    };

    Game.socket.send_data = function(action, data) {
        Game.socket.send(action + " " + JSON.stringify(data))
    }

    Game.socket.onclose = function(event) {
        if (!event.wasClean) {
            // e.g. server process killed or network down
            // event.code is usually 1006 in this case
            console.error('[close] Connection died');
            
            // Each try is has 1000ms of extra delay
            if (Game.reconnect_tries > 0) {
                setTimeout(() => {
                    console.info("Reconnecting...", Game.reconnect_tries, "tries remaining")
                    Game.funcs.connect()
                }, 1000 * (3 - Game.reconnect_tries))
            }
                
        }
    };

    Game.socket.onerror = function(error) {
        if (error.target && error.target.readyState == 3) {
            // Server not listening
            Game.reconnect_tries--
            
        }
        console.error("Websocket error:", error);
    };
}
Game.funcs.connect()