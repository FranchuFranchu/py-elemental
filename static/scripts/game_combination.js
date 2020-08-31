Game.funcs.combine_elements = function() {
    let element_ids = []

    $(".drop-slot").each(function(idx, e) {
        element_ids.push($(e).attr("data-pk"))
    })

    let send_string = "combine "
    for (var i = 0; i < element_ids.length; i++) {
        if (element_ids[i] === undefined) {
            element_ids[i] = "0"
        }
        send_string += parseInt(element_ids[i]) + " "
    }
    Game.socket.send(send_string)
    console.log(send_string)
}