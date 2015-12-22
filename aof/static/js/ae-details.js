$(function() {
    $("#delete-ae").click(function(event){
        event.preventDefault();
        if (confirm("Do you really want to delete the App-Ensemble") == true) {
            $.get( $(this).attr('href'), function( data ) {
                var alertHTML = $(
                    '<div data-alert class="alert-box info radius" style="margin-top:5px">'+data.toString()+'</div>'
                    ).hide().fadeToggle().delay(2500).slideToggle();
                    $('#alerts').append(alertHTML);
                setTimeout(function(){$(location).attr('href', '/app-ensembles.html')},4500);
            });
        }
    });
});