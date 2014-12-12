# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>

<!--Theme-->
    <link href="http://cdn.wijmo.com/themes/sterling/jquery-wijmo.css" rel="stylesheet" type="text/css" />

    <!--Wijmo Widgets CSS-->
    <link href="http://cdn.wijmo.com/jquery.wijmo-pro.all.3.20142.45.min.css" rel="stylesheet" type="text/css" />

    <!--RequireJs-->
    <script type="text/javascript" src="http://cdn.wijmo.com/external/require.js"></script>

    <script type="text/javascript">
	requirejs.config({
	    baseUrl: "http://cdn.wijmo.com/amd-js/3.20142.45",
		paths: {
		    "jquery": "jquery-1.11.1.min",
		    "jquery-ui": "jquery-ui-1.11.0.custom.min",
		    "jquery.ui": "jquery-ui",
		    "jquery.mousewheel": "jquery.mousewheel.min",
		    "globalize": "globalize.min",
		    "bootstrap": "bootstrap.min", //Needed if you use Bootstrap.
		    "knockout": "knockout-3.1.0" //Needed if you use Knockout.
		}
	});
</script>

<script id="scriptInit" type="text/javascript">
	require(["wijmo.wijgrid"], function () {
	    $(document).ready(function () {
		    $.getJSON('/app-pool.json',function(data){
                alert('haha');
            });
	    });
	});
</script>
<body>
    <div class="container">
        <table id="wijgrid">
	    </table>
    </div>
</body>