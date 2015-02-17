// Foundation JavaScript
// Documentation can be found at: http://foundation.zurb.com/docs
$(document).foundation({
    equalizer: {
        equalize_on_stack: true
    }
});

$(document).ajaxStart(function () {
    $("#loading-overlay").show();
    //console.log("ajaxStart")
});

$(document).ajaxComplete(function () {
    $("#loading-overlay").hide();
    //console.log("ajaxComplete")

});