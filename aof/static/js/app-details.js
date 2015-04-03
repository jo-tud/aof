$(function () {
    // Convert all elements marked with the class "markdown" from Markdown to HTML
    $(".markdown").each(function (i) {
        this.innerHTML = markdown.toHTML(this.innerHTML);
    });

    // Make images square
    $(".imgLiquidFill").imgLiquid({
        fill: true,
        horizontalAlign: "50%",
        verticalAlign: "50%"
    });


    // Full width
    $(".imgLiquidFullWidth").imgLiquid({
        fill: false,
        horizontalAlign: "50%",
        verticalAlign: "50%"
    });

});

