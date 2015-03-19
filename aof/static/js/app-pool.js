/**
 * Created by jo on 12.02.15.
 */
$(document).ajaxStart(function () {
    console.log("ajaxStart")
    $.loader({
        className:"bar-with-text",
        content:"<div>Loading App-Pool ...</div>"
    });
});

$(document).ajaxComplete(function () {
    console.log("ajaxComplete")
    $.loader('close');

});

$(function() {
    var liveFilter = $('#app_table').liveFilter('.livefilter-input', 'tr.app_row', {
        filterChildSelector: 'td.app_name'
        }
    );
    loadAP();
});
