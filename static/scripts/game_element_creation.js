Game.funcs.creation_setup = function() {
    $(".bg-pattern").each((idx, e) => {
        Game.bg_patterns.forEach((i, jdx) => {
            $(e).append($("<option/>").text(i))
        })
    })
    $(".fg-pattern").each((idx, e) => {
        Game.fg_patterns.forEach((i, jdx) => {
            $(e).append($("<option/>").text(i))
        })
    })

    $("button.create-button").on("click", () => {
        Game.socket.send("new_element_suggestion "+ JSON.stringify({
            "element": Game.creating_element,
            "ingredients": Game.funcs.get_current_ingredients(),
        }))
    })

    $("button.cancel-button").on("click", () => {
        $(".element-creation-menu").hide()
    })

    $(".element-creation-menu .name").on("input", (ev) => {
        console.log(JSON.stringify(ev.target.value))
        Game.socket.send("query_name " + JSON.stringify(ev.target.value))
    })

    let str_attrs = ["fg-pattern", "bg-pattern", "name"]

    for (let i = 0; i < str_attrs.length; i++) {
        let attr = str_attrs[i]
        $(".element-creation-menu ." + attr).on("input", function(ev) {
            Game.creating_element.fields[attr.replace('-', '_')] = ev.target.value
            Game.funcs.generate_element_canvas($(".element-creation-menu canvas")[0], Game.creating_element)
        })
        Game.creating_element.fields[attr.replace('-', '_')] = $(".element-creation-menu ." + attr).val()

    }

    let color_attrs = ["fg-color", "bg-color"]
    for (let i = 0; i < color_attrs.length; i++) {
        let attr = color_attrs[i]
        for (let j = 1; j < 3; j++) {
            let element = $("." + attr + "-" + j)[0]
            element.jscolor.onInput = (function() {

                let original_colors = Game.creating_element.fields[attr.replace("-", "_") + "s"]

                let colstart = (j-1)*8
                Game.creating_element.fields[attr.replace("-", "_") + "s"] = original_colors.replace_at(colstart, element.jscolor.toHEXString())
                Game.funcs.generate_element_canvas($(".element-creation-menu canvas")[0], Game.creating_element)
            })
            element.jscolor.onInput()
        }
    }
    Game.funcs.generate_element_canvas($(".element-creation-menu canvas")[0], Game.creating_element)
       

}