<!DOCTYPE html>
<html lang="${request.locale_name}">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AOF web application">
    <meta name="author" content="Johannes Pfeffer">
    <link rel="shortcut icon" href="${request.static_url('aof:static/favicon.png')}">

    <title>AOF:App-Pool:Show</title>

    <!-- Bootstrap core CSS -->
    <link href="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">

    <!-- Custom styles for this scaffold -->
    <link href="${request.static_url('aof:static/theme.css')}" rel="stylesheet">

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->

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

    <!--Require aof.tools Js-->
    <script type="text/javascript" src="${request.static_url('aof:static/js/aof.tools.js')}"></script>

    <script id="scriptInit" type="text/javascript">
	require(["wijmo.wijgrid"], function () {
	    $(document).ready(function () {
		var jsonObj = jQuery.parseJSON( '${json}');
		
		// Use the getGridData(jsonObj) function to turn a sparql result json-string into data suitable for a wijmo grid
		var gridData = getGridData(jsonObj);
		
		$("#wijgrid").wijgrid({
		    cellClicked: function (e, args) {
			// alert(args.cell.value());
		    },
		    allowSorting: true,
		    allowPaging: false,
		    pageSize: 10,
		    allowVirtualScrolling: true,
		    showFilter: true,
		    columns: gridData[0],
		    data: gridData[1]
		});
	    });
	});
    </script>



  </head>

  <body>
    <div class="starter-template">
      <div class="container">
        <div class="row">
          <div class="col-md-10">
            <div class="content">
              <h1><span class="font-semi-bold">AOF</span> <span class="smaller">Application Orchestration Framework</span></h1>
              <p class="lead">Content of the App-Pool.</p>
            </div>
          </div>
        </div>
        <div class="row">
	  <table id="wijgrid">
	  </table>
        </div>
        <div class="row">
          <div class="links">
            <ul>
              <li class="plt-logo"><img class="logo img-responsive" src="${request.static_url('aof:static/logo_plt.png')}" alt="Chair for Distributed Control Systems Engineering"></li>
          </div>
        </div>
        <div class="row">
          <div class="copyright">
            Copyright &copy; Johannes Pfeffer
          </div>
        </div>
      </div>
    </div>


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="//oss.maxcdn.com/libs/jquery/1.10.2/jquery.min.js"></script>
    <script src="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/js/bootstrap.min.js"></script>
  </body>
</html>
