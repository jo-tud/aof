$(function () {
    // Convert all elements marked with the class "markdown" from Markdown to HTML
    $(".markdown").each(function (i) {
        this.innerHTML = markdown.toHTML(this.innerHTML);
    });

    // Make images square
    $(".imgLiquidFill").imgLiquid({
        fill: true,
        horizontalAlign: "top",
        verticalAlign: "50%"
    });


    // Full width
    $(".imgLiquidThumb").imgLiquid({
        fill: false,
        horizontalAlign: "50%",
        verticalAlign: "50%"
    });

});

