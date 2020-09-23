Game.funcs.combine_elements = function() {
    let element_ids = Game.funcs.get_current_ingredients()


    let send_string = "combine "
    for (var i = 0; i < element_ids.length; i++) {
        if (element_ids[i] === undefined) {
            element_ids[i] = "0"
        }
        send_string += element_ids[i] + " "
    }
    Game.socket.send(send_string)
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