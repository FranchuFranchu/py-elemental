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
        if (Game.creation_reason == "edit") {
            Game.socket.send("new_element_suggestion "+ JSON.stringify({
                "element": Game.creating_element,
                "ingredients": [],
            }))
        } else {
            Game.socket.send("new_element_suggestion "+ JSON.stringify({
                "element": Game.creating_element,
                "ingredients": Game.funcs.get_current_ingredients(),
            }))

        }
        $(".element-suggestion").hide()
    })

    $("button.cancel-button").on("click", () => {
        $(".element-suggestion").hide()
    })

    $(".element-creation-menu .name").on("input", (ev) => {
        Game.socket.send("query_name " + JSON.stringify($(".element-creation-menu .name").val()))
    })

    $(".element-creation-menu .name").on("blur", (ev) => {
        let l = []
        $(".element-suggestion .name-list option").each((idx, e) => {
            l.push(e.value)
        })
        console.log(l, ev.target.value)
        if (l.includes(ev.target.value) && !(Game.creation_reason == "edit")) {
            $(".element-combination-warning").show()
        }
        $(".create-element-name").text($(".element-creation-menu .name").val())
    })

    $(".element-combination-warning button.back").on("click", () => {
        $(".element-combination-warning").hide()
    })

    $(".element-combination-warning button.yes").on("click", () => {
        $(".element-combination-warning").hide()
        Game.socket.send("combination_suggestion " +  JSON.stringify({
            "name": $(".element-creation-menu .name").val(),
            "ingredients": Game.funcs.get_current_ingredients(),
        }))

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

Game.funcs.load_edit_data = function(element) {
    Game.creating_element = element
    $(".element-creation-menu .name")
        .val(element.fields.name)
        .trigger('input')
    $(".element-creation-menu .fg-pattern")
        .val(element.fields.fg_pattern)
        .trigger('input')
    $(".element-creation-menu .bg-pattern")
        .val(element.fields.bg_pattern)
        .trigger('input')


    let color_attrs = ["fg-color", "bg-color"]
    for (let i = 0; i < color_attrs.length; i++) {
        let attr = color_attrs[i]
        for (let j = 1; j < 3; j++) {
            let e = $("." + attr + "-" + j)[0]
            e.jscolor.fromString(
                element.fields[
                    attr.replace("-", "_") + "s"
                ].split(',')[j-1]
            )
            e.jscolor.onInput()
        }
    }

}