// Foundation JavaScript
// Documentation can be found at: http://foundation.zurb.com/docs
$(document).foundation();

$(function() {

    function get_updates () {
        $.getJSON('/app-pool.json', function(data) {
            var target = $('div#app_tables');
            // target.empty();
            console.log(data);
            $.each(data, function (key, val) {
                target.append('<ul class="pricing-table">' +
                    '<li class="title">App</li>' +
                    '<li class="bullet-item">Key: ' + key + '</li>' +
                    '<li class="description">Value: ' + val + '</li>' +
                    '<li class="cta-button"><a class="button" href="#">Buy Now</a></li>' +
                    '</ul>')
            });
        });
    }

    $('#fetch_app_pool').click(function () {
        get_updates();
    });
});