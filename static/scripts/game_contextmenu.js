Game.funcs.on_element_contextmenu = (event) => {
    event.preventDefault()

    Game.contextmenu_pk = parseInt($(event.target).attr("data-pk"))
    console.log("Hi")
    $("div.contextmenu")
        .css("display", "grid")
        .css("top", event.clientY)
        .css("left", event.clientX)

    $("div.contextmenu .name-field")
        .text(Game.element_data[
            parseInt($(event.target).attr("data-pk"))
        ].fields.name)


}

Game.funcs.contextmenu_setup = function() {

    $(".contextmenu > div.btn").on("click", () => {
        $(".contextmenu").hide()
    })
    $(".contextmenu > div.btn.edit").on("click", () => {
        Game.creation_reason = "edit"
        $(".element-suggestion").show()
        let element = Game.element_data[
            Game.contextmenu_pk
        ]
        console.log()
        Game.funcs.load_edit_data(element)
    })
}