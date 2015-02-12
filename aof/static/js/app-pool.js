/**
 * Created by jo on 12.02.15.
 */
$(function() {
    get_updates();

    function get_updates () {
        $.getJSON('/app-pool.json', function(data) {
            var target = $('div#app_tables');
            target.empty();

            console.log(data.json);
            obj = JSON.parse(data.json);
            console.log(obj);
            $.each(obj.results.bindings, function (key, val) {
                target.append(
                    '<div class="small-12 large-4 columns">' +
                    '<ul class="pricing-table">' +
                    '<li class="title">'+ val.name.value + '</li>' +
                    '<li class="bullet-item"><a href="'+ val.uri.value + '">URI</a></li>' +
                    '<li class="bullet-item"><a href="'+ val.binary.value + '">Binary</a></li>' +
                    '<li class="bullet-item">Purpose: '+ val.intent_purpose.value + '</li>' +
                    '<li class="bullet-item">Intent string: '+ val.intent_string.value + '</li>' +
                    '<li class="cta-button"><a class="button" href="' + val.uri.value + '">Dereference</a></li>' +
                    '</ul>' +
                    '</div>'
                )
            });
        });
    }

    $('#action_update').click(function () {
        get_updates();
    });
});