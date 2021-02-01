Game.funcs.save_elements = function() {
    localStorage.known_elements = JSON.stringify(Game.known_elements)
}
Game.funcs.load_elements = function() {
    if (localStorage.known_elements) {
        Game.known_elements = JSON.parse(localStorage.known_elements)
    } else {
        Game.known_elements = {}
    }
}
Game.funcs.load_elements()