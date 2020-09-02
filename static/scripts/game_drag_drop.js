Game.funcs.on_slot_drop = function(ev) {
    ev.target.getContext('2d')
        .drawImage(Game.dragged, 0, 0)

    $(ev.target)
        .attr("data-password", Game.dragged.attributes["data-password"].nodeValue)
    Game.dragged = undefined
}
Game.funcs.on_dragover = function(ev) {
    ev.preventDefault()
}
Game.funcs.on_slot_drag_start = function(ev) {
    Game.dragged = ev.target
}
