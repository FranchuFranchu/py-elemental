$().ready(function() {
    $(".drop-slot")
        .attr("width", 50)
        .attr("height", 50)
        .attr("ondragover", "event.preventDefault()")
        .attr("ondrop", "Game.funcs.on_slot_drop(event)")

    $(document).click(function(event) { 
        var $target = $(event.target);
        if(!$target.closest('.contextmenu').length && $('.contextmenu').is(":visible")) {
             $('.contextmenu').hide();
        }
     });
    for (var i = 0; i < $(".drop-slot").length; i++) {
        let canvas = $(".drop-slot")[i]
        Game.funcs.draw_slot(canvas)

    }

    Game.funcs.creation_setup()
    Game.funcs.contextmenu_setup()
    Game.funcs.suggestion_list_client_setup()
    Game.funcs.setup_tabs()
})
