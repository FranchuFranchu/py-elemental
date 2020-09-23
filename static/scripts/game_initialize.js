window.Game = {
    funcs: {},
    dragged: undefined,
    known_elements: {},
    fg_patterns: [
        "NONE",
        "STAR",
        "SQUARE",
        "CIRCLE",
        "CROSS",
        "PLUS",
    ],
    bg_patterns:[
        "FLAT",
        "LEFT-RIGHT",
        "TOP-BOTTOM",
        "TOPLEFT-BOTTOMRIGHT",
        "TOPRIGHT-BOTTOMLEFT",
    ],
    creating_element: { 
        fields: {
            bg_colors: "#000000,#000000",
            fg_colors: "#000000,#000000",
            name: "",
            bg_pattern: "FLAT",
            fg_pattern: "NONE",
        } 
    },
    element_data: {},
    mobile: ('ontouchstart' in document.documentElement) || localStorage.debug_mobile
}
