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
    var liveFilter = $('#app_tables').liveFilter('.livefilter-input', 'div.columns', {
        filterChildSelector: 'li.title'
        }
    );
    loadAP();

    function loadAP () {
        $.getJSON('/api/get_app_pool', function(data) {
            var target = $('div#app_tables');
            target.empty();

            //console.log(data.json);
            obj = JSON.parse(data.json);
            //console.log(obj);
            $.each(obj.results.bindings, function (key, val) {
                var name, uri, binary, intent_string, intent_purpose;

                if (! val.name) { uri = "http://#"; } else {name = val.name.value; }
                if (! val.uri) { uri = "http://#"; } else {uri = val.uri.value; }
                if (! val.binary) { binary = "http://#"; } else {binary = val.binary.value; }
                if (! val.intent_string) { intent_string = "Not defined"; } else {intent_string = val.intent_string.value; }
                if (! val.intent_purpose) { intent_purpose = "Not defined"; } else {intent_purpose = val.intent_purpose.value}

                target.append(
                    '<div class="small-12 medium-4 large-3 columns">' +
                    '<ul class="pricing-table" data-equalizer-watch>' +
                    '<li class="title">'+ name + '</li>' +
                    '<li class="bullet-item"><a href="'+ uri + '">URI</a></li>' +
                    '<li class="cta-button"><a class="button" href="' + binary + '">Download</a></li>' +
                    '</ul>' +
                    '</div>'
                )
            });
            target.children().last().attr('class','small-12 medium-4 large-3 columns end');
            $(document).foundation('reflow');
            liveFilter.refresh();
        });
    }

    function updateAP () {
        $.get('/api/update_app_pool', function(data) {
            loadAP();
            var alertHTML = $(
                    '<div data-alert class="alert-box info radius" style="margin-top:5px">' +
                    'App-Pool updated. Number of apps: ' + data.toString() +
                    '</div>'
                    ).hide().fadeToggle().delay(2000).slideToggle();
            $('#alerts').append(alertHTML);
            });
    }

    $('#action_update').click(function () {
        updateAP();
    });
});
