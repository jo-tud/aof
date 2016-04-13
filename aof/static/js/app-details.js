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

    getBuildNumber();

    function getBuildNumber(){
        $.getJSON('/api/apps/'+encodeURI($("#resource-uri").attr("href"))+'/version', function(data) {
            var target = $('tbody#app-details-general');
            if(data.build_number != null){
                $('tbody#app-details-general').append('<tr><td><a href="http://eatld.et.tu-dresden.de/aof/hasVersion">Build Number</a></td><td>'+data.json.build_number+'</td></tr>');
            }
        });
    }

});

