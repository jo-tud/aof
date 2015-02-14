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
            //console.log(data.json);
            $.each(data.json, function (key, ae) {
                target.append('<div class="small-12 large-4 columns" id="'+ ae.id +'"></div>');
                $('#'+ae.id).append('<ul class="pricing-table">');
                t2 = $('#'+ae.id+'> ul');
                t2.append('<li class="title">'+ ae.id + '</li>');
                t2.append('<li class="description">'+ ae.path + '</li>');
                apps = JSON.parse(ae.apps);
                t2.append('<li class="bullet-item"><b>Apps:</b></li>')
                $.each(apps.results.bindings, function (key, app) {
                    t2.append('<li class="bullet-item">'+app.name.value+'</li>')
                });
            t2.append('<li class="cta-button"><a class="button" href="#">Install</a></li>')
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
});