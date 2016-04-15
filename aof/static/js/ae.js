/**
 * Created by jo on 12.02.15.
 */
$(document).ajaxStart(function () {
    //console.log("ajaxStart")
    $.loader({
        className:"bar-with-text",
        content:"<div>Loading App-Ensembles ...</div>"
    });
});

$(document).ajaxComplete(function () {
    //console.log("ajaxComplete")
    $.loader('close');

});

$(function() {
    var liveFilter = $('#ae_tables').liveFilter('.livefilter-input', 'div.columns', {
        filterChildSelector: 'li.title'
        }
    );
    get_updates();

    function get_updates () {
        $.getJSON('/api/app-ensembles', function(data) {
            var target = $('div#ae_tables');
            target.empty();
            // console.log(data.json);
            $.each(data, function (key, ae) {
                target.append('<div class="small-12 medium-4 large-3 columns"></div>');
                main_div = target.children().last();
                main_div.attr('id',ae.uri);
                main_div.append('<ul class="pricing-table"></ul>');
                var pricing_table = main_div.find('ul.pricing-table');
                pricing_table.append('<div class="eq" data-equalizer-watch></div>')
                var eq_div=pricing_table.find('.eq')
                eq_div.append('<li class="title">'+ ae.uri + '</li>');

                $('<li class="bullet-item" id="documentation">' + ae.documentation + '</li>').appendTo(pricing_table);
                $('<li class="cta-button details"><a style="width:140px" class="button success" href="/app-ensembles/'+encodeURI(ae.uri)+'/details.html">Details</a></li>').attr('id',ae.uri).appendTo(pricing_table);
                $('<li class="cta-button deploy"><a style="width:140px" class="button floor" href="#">Install</a></li>').attr('uri',ae.uri).appendTo(pricing_table);

            });
            target.children().last().attr('class','small-12 medium-4 large-3 columns end')
            $(document).foundation('reflow');
            liveFilter.refresh();
        });
    }

        function updateAppEnsembles () {
            $.get('/api/actions/app-ensembles/update', function(data) {
                get_updates();
                var alertHTML = $(
                        '<div data-alert class="alert-box info radius" style="margin-top:5px">' +
                        'App-Ensembles updated. Number of App-Ensembles: ' + data.toString() +
                        '</div>'
                        ).hide().fadeToggle().delay(2000).slideToggle();
                $('#alerts').append(alertHTML);
            });
        }



    $('#action_update').click(function () {
        updateAppEnsembles()
    });

    setInterval(get_updates, 5000);

    $('div#ae_tables').on('click','.cta-button.deploy',(function (e) {
        var ae_uri = $(this).attr('uri');
        console.log("Requested download of App-Ensemble: " + ae_uri);
        top.location.href = '/api/app-ensembles/'+encodeURI(ae_uri)+'/package';
        e.preventDefault();
    }));
});