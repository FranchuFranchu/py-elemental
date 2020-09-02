$().ready(() => {
    $(".tab").each((idx, tab) => {
        let classes = tab.className.split(/\s+/)
        let tabname = classes.filter((v) => (v != "tab"))[0]
        $(".tab." + tabname)
            .hide()
        $(".tab-list")
            .append($("<div/>")
                .text(tabname)
                .addClass("tab-button")
                .on("click", () => {
                    Game.funcs.set_tab(tabname)
                })
            )
    })
})

Game.funcs.set_tab = (tabname) => {
    $(".tab").hide()
    $(".tab." + tabname).show()
}