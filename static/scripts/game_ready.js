$().ready(function() {
    $(".drop-slot")
        .attr("width", 50)
        .attr("height", 50)
        .attr("ondragover", "event.preventDefault()")
        .attr("ondrop", "Game.funcs.on_slot_drop(event)")

    for (var i = 0; i < $(".drop-slot").length; i++) {
        let canvas = $(".drop-slot")[i]
        Game.funcs.draw_slot(canvas)

    }

    Game.funcs.creation_setup()
})