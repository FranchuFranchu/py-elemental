Game.funcs.suggestion_list_setup = () => {
    Game.socket.send("get_vote_pending latest")
    Game.socket.send("get_vote_pending oldest")
    Game.socket.send("get_vote_pending verge")
    Game.socket.send("get_vote_pending undecided")


}

Game.funcs.suggestion_list_client_setup = () => {
    
    $(".sorting-selection").on("input", (ev) => {
        console.log(ev.target.value)
        $(".sort-suggestions").hide()
        $("." + ev.target.value + "-elements").show()
    }).val("latest").trigger("input")

    $("button.refresh-button").on("click", (ev) => {
        $(".vote-list-" +$(".sorting-selection").val()).empty()
        Game.socket.send("get_vote_pending " + $(".sorting-selection").val())
    })
}

Game.funcs.add_element_to_vote_list = function(order, element) {
    element = element[0]
    let e = $(".templates > .vote-row-template")
        .clone()
        .addClass("vote-item")
        .appendTo($(".vote-list-"+order))
        .attr("data-pk", element.pk)

    e.find(".up-button").on("click", () => {
        Game.socket.send("upvote " + element.pk)
    })
    e.find(".down-button").on("click", () => {
        Game.socket.send("downvote " + element.pk)
    })
    e.find(".suggestion-type").text(element.fields.suggestion_type)    

    Game.funcs.generate_element_canvas(e.find("canvas")[0], element)

    e.find(".voting-status .current").text(element.fields.current+element.fields.target)
    e.find(".voting-status .target").text(element.fields.target*2)
        
    let ingredients = element.fields.ingredients.split(',')
    for (var i = 0; i < ingredients.length; i++) {

        let c = $("<canvas></canvas>")
        let pk = parseInt(ingredients[i].split(',')[0])
        let ingredient = Game.element_data[pk]
        if (ingredient === undefined) {
            // We don't know about this element yet, ask the server to send us the data
            c.attr("data-pk", pk)
            c.addClass("canvas-draw-queue")
            Game.socket.send("get_element_data " + pk)

        } else {
            Game.funcs.generate_element_canvas(c[0], ingredient)
        }

        e.find(".ingredients")
            .append(c)

    }
}