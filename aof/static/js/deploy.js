/**
 * Created by jo on 12.02.15.
 */
$(function() {
    var liveFilter = $('#ae_tables').liveFilter('.livefilter-input', 'div.columns', {
        filterChildSelector: 'li.title'
        }
    );
    get_updates();

    function get_updates () {
        $.getJSON('/api/get_ae_info', function(data) {
            var target = $('div#ae_tables');
            target.empty();
            console.log(data.json);
            $.each(data.json, function (key, ae) {
                target.append('<div class="small-12 medium-4 large-3 columns"></div>');
                main_div = target.children().last();
                main_div.attr('id',ae.id);
                main_div.append('<ul class="pricing-table"></ul>');
                var pricing_table = main_div.find('ul.pricing-table');
                pricing_table.append('<div class="eq" data-equalizer-watch></div>')
                var eq_div=pricing_table.find('.eq')
                eq_div.append('<li class="title">'+ ae.id + '</li>');
                $('<li class="bullet-item" id="app-path"></li>').appendTo(eq_div);
                $('<span data-tooltip aria-haspopup="true" class="has-tip">Path<span>').attr('title',ae.path).appendTo($(eq_div.find('#app-path')))
                var apps = JSON.parse(ae.apps).results.bindings;
                //pricing_table.append('')
                var app_list = "";
                $.each(apps, function (key, app) {
                    app_list = app_list.concat(", "+app.name.value);
                    //.pricing_table.append('<li class="bullet-item">'+app.name.value+'</li>')
                });
                if (app_list != ""){
                    $('<li class="bullet-item" id="app-list"></li>').appendTo(eq_div);
                    $('<span data-tooltip aria-haspopup="true" class="has-tip">Apps<span>').attr('title',app_list.slice(2)).appendTo($(pricing_table.find('#app-list')))
                }
                $('<li class="cta-button deploy"><a class="button floor" href="#">Install</a></li>').attr('id',ae.id).appendTo(pricing_table);

            });
            target.children().last().attr('class','small-12 medium-4 large-3 columns end')
            $(document).foundation('reflow');
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