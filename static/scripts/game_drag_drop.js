Game.funcs.on_slot_drop = function(ev) {
    ev.target.getContext('2d')
        .drawImage(Game.dragged, 0, 0)

    $(ev.target)
        .attr("data-pk", Game.dragged.attributes["data-pk"].nodeValue)
    Game.dragged = undefined
}
Game.funcs.on_dragover = function(ev) {
    ev.preventDefault()
}
Game.funcs.on_slot_drag_start = function(ev) {
    console.log(ev.target)
    Game.dragged = ev.target
}
