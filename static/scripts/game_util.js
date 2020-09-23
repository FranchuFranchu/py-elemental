
String.prototype.limited_split = function(separator, n) {

    var split = this.split(separator);
    if (split.length <= n)
        return split;
    var out = split.slice(0,n-1);
    out.push(split.slice(n-1).join(separator));
    return out;
}

String.prototype.replace_at = function(index, replacement) {
    return this.substr(0, index) + replacement + this.substr(index + replacement.length);
}

Game.funcs.draw_rounded_rectangle = function(ctx, x, y, width, height, radius, fill, stroke) {
    if (typeof stroke === 'undefined') {
        stroke = true;
    }
    if (typeof radius === 'undefined') {
        radius = 5;
    }
    if (typeof radius === 'number') {
        radius = {tl: radius, tr: radius, br: radius, bl: radius};
    } else {
        var defaultRadius = {tl: 0, tr: 0, br: 0, bl: 0};
        for (var side in defaultRadius) {
            radius[side] = radius[side] || defaultRadius[side];
        }
    }
    ctx.beginPath();
    ctx.moveTo(x + radius.tl, y);
    ctx.lineTo(x + width - radius.tr, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius.tr);
    ctx.lineTo(x + width, y + height - radius.br);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius.br, y + height);
    ctx.lineTo(x + radius.bl, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius.bl);
    ctx.lineTo(x, y + radius.tl);
    ctx.quadraticCurveTo(x, y, x + radius.tl, y);
    ctx.closePath();
    if (fill) {
        ctx.fill();
    }
    if (stroke) {
        ctx.stroke();
    }

}


Game.funcs.is_dark = function(color) {
    num = parseInt(color.slice(1, 3), 16) + parseInt(color.slice(3, 5), 16) + parseInt(color.slice(5, 7), 16)

    return (num < parseInt("88", 16) * 3)
}

Game.funcs.get_interpolated_colors = function() {
    var ingredients = Game.funcs.get_current_ingredients()
    var colors = []
    for (var i = 0; i < ingredients.length; i++) {
        colors.push(Game.element_data[parseInt(ingredients[i].split(',')[0])].fields.bg_colors.split(',')[0])
    }
    
    var reds = []
    var greens = []
    var blues = []

    for (var i = 0; i < colors.length; i++) {
        let color = colors[i]
        reds.push(parseInt(color.slice(1, 3), 16))
        greens.push(parseInt(color.slice(3, 5), 16))
        blues.push(parseInt(color.slice(5, 7), 16))

    }
    console.log(colors)
    var ravg = Math.floor(reds.reduce((a, b) => (a + b)) / reds.length)
    var gavg = Math.floor(greens.reduce((a, b) => (a + b)) / greens.length)
    var bavg = Math.floor(blues.reduce((a, b) => (a + b)) / blues.length)

    console.log(ravg, gavg, bavg)

    console.log(`rgba(${ravg},${gavg},${bavg},1)`)

    return `rgba(${ravg},${gavg},${bavg},1)`

}