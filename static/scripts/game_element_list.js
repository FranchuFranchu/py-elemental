Game.funcs.element_list_setup = () => {
    Game.socket.send("get_vote_pending latest")
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

    Game.funcs.generate_element_canvas(e.find("canvas")[0], element)

    e.find(".voting-status .current").text(element.fields.current+element.fields.target)
    e.find(".voting-status .target").text(element.fields.target*2)
        
}