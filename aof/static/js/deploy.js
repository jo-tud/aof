/**
 * Created by jo on 12.02.15.
 */
$(function() {
    var liveFilter = $('#ae_tables').liveFilter('#livefilter-input', 'div.columns', {
        filterChildSelector: 'li.title'
        }
    );
    get_updates();

    function get_updates () {
        $.getJSON('/api/get_ae_info', function(data) {
            var target = $('div#ae_tables');
            //target.empty();
            console.log(data.json);
            $.each(data.json, function (key, ae) {
                target.append('<div class="small-12 large-4 columns"></div>');
                main_div = target.children().last();
                main_div.attr('id',ae.id);
                main_div.append('<ul class="pricing-table"></ul>');
                var pricing_table = main_div.find('ul.pricing-table');

                pricing_table.append('<li class="title">'+ ae.id + '</li>');
                pricing_table.append('<li class="description">'+ ae.path + '</li>');
                var apps = JSON.parse(ae.apps).results.bindings;
                pricing_table.append('<li class="bullet-item"><b>Apps:</b></li>')
                $.each(apps, function (key, app) {
                    pricing_table.append('<li class="bullet-item">'+app.name.value+'</li>')
                });
            $('<li class="cta-button deploy"><a class="button" href="#">Install</a></li>').attr('id',ae.id).appendTo(pricing_table);
            });

            liveFilter.refresh();
        });
    }

    $('#action_update').click(function () {
        get_updates();
        alert = $(
                '<div data-alert class="alert-box info radius">' +
                'App-Ensembles updated' +
                '<a href="#" class="close">&times;</a>' +
                '</div>'
        ).hide().slideDown().delay(2000).slideUp();

        $('#alerts').append(alert.fadeOut(500));
    });

    $('div#ae_tables').on('click','.cta-button.deploy',(function (e) {
        var ae_id = $(this).attr('id');
        console.log("Requested download of App-Ensemble: " + ae_id);
        top.location.href = '/api/get_ae_pkg?ae_id='+ ae_id;
        e.preventDefault();
    }));
});