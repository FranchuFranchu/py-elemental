Game.BG_PATHS = {
    undefined: (ctx) => {},
    "FLAT": (ctx) => {},
    "LEFT-RIGHT": (ctx, canvas) => {
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(canvas.width / 2, 0);
        ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.lineTo(0, canvas.height);
        ctx.fill()
    },
    "TOP-BOTTOM": (ctx, canvas) => {
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(0, canvas.height / 2);
        ctx.lineTo(canvas.width, canvas.height / 2);
        ctx.lineTo(canvas.width, 0);
        ctx.fill()
    },
    "TOPLEFT-BOTTOMRIGHT": (ctx, canvas) => {
        ctx.beginPath();
        ctx.moveTo(canvas.width, 0);
        ctx.lineTo(canvas.width, canvas.height);
        ctx.lineTo(0, canvas.height);
        ctx.fill()
    },
    "TOPRIGHT-BOTTOMLEFT": (ctx, canvas) => {
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(canvas.width, 0);
        ctx.lineTo(canvas.width, canvas.height);
        ctx.fill()
    },
}
Game.funcs.dpath = function(ctx, canvas, s) {

    for (var i = 0; i < s.split('\n').length; i++) {
        let line = s.split('\n')[i]
        x = parseFloat(line.split(' ')[0])
        y = parseFloat(line.split(' ')[1])
        if (i == 0) {
            ctx.beginPath(Math.round(x * canvas.width), Math.round(y * canvas.height))
        } else {
            ctx.lineTo(Math.round(x * canvas.width), Math.round(y * canvas.height))
        }


    }

}

Game.FG_PATHS = {
    undefined: (ctx) => {},
    "NONE": (ctx) => {},
    "STAR": (ctx, canvas) => {
        Game.funcs.dpath(ctx, canvas,"0.500 0.630\n0.735 0.824\n0.624 0.540\n0.880 0.376\n0.576 0.395\n0.500 0.100\n0.424 0.395\n0.120 0.376\n0.376 0.540\n0.265 0.824\n0.500 0.630")
        ctx.fill()
    },
    "SQUARE": (ctx, canvas) => {
        Game.funcs.dpath(ctx, canvas, "0.7 0.7\n0.7 0.3\n0.3 0.3\n0.3 0.7\n0.7 0.7")
        ctx.fill()
    },
    "CIRCLE": (ctx, canvas) => {
        ctx.beginPath()
        ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 5, 0, 2 * Math.PI);
        ctx.fill()

    },
    "CROSS": (ctx, canvas) => {
        Game.funcs.dpath(ctx, canvas, "0.4 0.4\n0.2 0.4\n0.2 0.6\n0.4 0.6\n0.4 0.8\n0.6 0.8\n0.6 0.6\n0.8 0.6\n0.8 0.4\n0.6 0.4\n0.6 0.2\n0.4 0.2\n0.4 0.4\n")
        ctx.fill()
    },
    "PLUS": (ctx) => {},
   
}

Game.funcs.draw_filling_text = function(ctx, canvas, text) {

    
    ctx.font = "1px serif"


    let curr_line = ""
    let lines = []

    var text_height;

    for (var i = 0; i < text.split(' ').length; i++) {
        let word = text.split(' ')[i]

        curr_line += word
        text_height = Math.round((canvas.width / ctx.measureText(curr_line).width) * 0.7)

        if (text_height < 15) {
            lines.push([text_height, curr_line])
            curr_line = ""
            continue
        } else {
        }


        curr_line += " "
    }
    lines.push([text_height, curr_line])
    for (var i = 0; i < lines.length; i++) {
        let size = lines[i][0]
        let textl = lines[i][1]
        ctx.font = size + "px sans-serif" 
        size *= 0.9
        size = Math.round(size)
        ctx.textBaseline = 'middle'
        ctx.textAlign = 'center'
        ctx.fillText(textl, canvas.width / 2, canvas.height / 2 + (-Math.floor((lines.length - 1) / 2) + i) * 13)
    }    

}

Game.funcs.generate_element_canvas = function(canvas, element) {
    canvas.width = 50
    canvas.height = 50


    let bg_colors = element.fields.bg_colors.split(",")
    let fg_colors = element.fields.fg_colors.split(",")

    ctx = canvas.getContext('2d')

    ctx.fillStyle = bg_colors[0]


    ctx.globalCompositeOperation = "source-over";
    Game.funcs.draw_rounded_rectangle(ctx, 5, 5, canvas.width - 10, canvas.height - 10, 5, true, false)

    ctx.globalCompositeOperation = "source-atop";


    ctx.lineWidth = "0";
    ctx.fillStyle = bg_colors[1]



    f = Game.BG_PATHS[element.fields.bg_pattern]
    f(ctx, canvas)

    ctx.globalCompositeOperation = "source-over";


    ctx.fillStyle = fg_colors[0]
    f = Game.FG_PATHS[element.fields.fg_pattern]
    f(ctx, canvas)

    ctx.fillStyle = "rgba(1,1,1,0)"
    ctx.strokeStyle = "rgba(0,0,0,1)"
    ctx.lineWidth = "1";
    Game.funcs.draw_rounded_rectangle(ctx, 5, 5, canvas.width - 10, canvas.height - 10, 5, false, true)

    if (Game.funcs.is_dark(element.fields.bg_colors)) {
        ctx.fillStyle = "#FFFFFF"
    } else {
        ctx.fillStyle = "#000000"
    }
    ctx.strokeStyle = ctx.fillStyle

    Game.funcs.draw_filling_text(ctx, canvas, element.fields.name)
}
Game.funcs.draw_slot = function(canvas) {
    ctx = canvas.getContext('2d')
    ctx.fillStyle = "#FFFFFF"
    Game.funcs.draw_rounded_rectangle(ctx, 5, 5, canvas.width - 10, canvas.height - 10, 5, "#FFFFFF", "#888888")
    ctx.fillStyle = "#000000"
    ctx.textBaseline = 'middle'
    ctx.textAlign = 'center'
    ctx.font = "10px sans-serif"
    ctx.fillText("[drop]", canvas.width / 2, canvas.height / 2)
}
Game.funcs.add_element = function(element) {

    if ($("canvas[data-pk=" + element.pk + "]").length != 0) {
        return
    }

    canvas = $("<canvas/>")
        .attr("data-pk", element.pk)
        .attr("data-password", element.fields.password) /* Password */
        .on("touchstart", Game.funcs.on_element_touch)
        .on("contextmenu", Game.funcs.on_element_contextmenu)

    if (!Game.mobile) {
        canvas
            .attr("draggable", "true")
            .attr("ondragstart", "Game.funcs.on_slot_drag_start(event)")
    } else {
        canvas
            .on("click", Game.funcs.on_element_touch)
    }


    $(".current-owned-elements").append(
        canvas
    )
    Game.known_elements[element.pk] = element.fields.password
    Game.element_data[element.pk] = element
    Game.funcs.save_elements()
    Game.funcs.generate_element_canvas(canvas[0], element)
}