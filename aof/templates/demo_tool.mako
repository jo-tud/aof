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

    <link href="${request.static_url('aof:static/deploy.css')}" rel="stylesheet">

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

    <script type="text/javascript" src="${request.static_url('aof:static/js/jquery.js')}"></script>

    <script type="text/javascript" src="${request.static_url('aof:static/js/workflow.js')}"></script>

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

    <script Language="javascript">
	function change(page) {
	      if(page=="deploy"){
		     tab1.style.background="#307AFF";
		     tab2.style.background="silver";
		     deploy.style.background="#307AFF";
		     deploy.style.display='block';
		     workflow.style.display='none';
	      }else if(page=="workflow"){
		     tab1.style.background="silver";
		     tab2.style.background="#307AFF";
		     workflow.style.background="#307AFF";
		     workflow.style.display='block';
		     deploy.style.display='none';
	      }
	}

	function test1(){
	      window.alert("haha");
	}

	var count=0;
	function progress(){
	      count++;
	      rest=count%5;
	      if(rest==1){
		    p0.style.color='black';
		    p1.style.color="#307AFF";
		    p2.style.color="#307AFF";
		    p3.style.color="#307AFF";
		    p4.style.color="#307AFF";
	      }else if(rest==2){
		    p0.style.color='black';
		    p1.style.color='black';
		    p2.style.color="#307AFF";
		    p3.style.color="#307AFF";
		    p4.style.color="#307AFF";
	      }if(rest==3){
		    p0.style.color='black';
		    p1.style.color='black';
		    p2.style.color='black';
		    p3.style.color="#307AFF";
		    p4.style.color="#307AFF";
	      }if(rest==4){
		    p0.style.color='black';
		    p1.style.color='black';
		    p2.style.color='black';
		    p3.style.color='black';
		    p4.style.color="#307AFF";
	      }if(rest==0){
		    p0.style.color='black';
		    p1.style.color='black';
		    p2.style.color='black';
		    p3.style.color='black';
		    p4.style.color='black';
	      }

	}

	function draw(){
	    var cvs = document.getElementById('cvs');
	    var ctx = cvs.getContext('2d');
	    ctx.roundRect(50, 50, 150, 100, 10, 2, 50, 52, "App1");
            ctx.arrow(200, 100, 300, 100, 297, 97, 297, 103);
            ctx.roundRect(300, 50, 150, 100, 10, 1, 50, 52, "App2");
            ctx.arrow(450, 100, 550, 100, 547, 97, 547, 103);
	}

	function ini(){
	      change('deploy');
	      setInterval("progress()",1000);
          $('.Progress').hide();
	}

	function ini(){
	      change('deploy');
	      setInterval("progress()",1000);
	      getData();
	}

	function getData(){
	    $.getJSON('/dp_json.json', function(data){
	            var json_data=data['result']
                var dataObj=eval("("+json_data+")");
		 $.each(dataObj.devices,function(idx,item){
	             if(item.status=="Success"){
		         $myli = $("<div style='background-color:#307ADD;' id= " + item.name + ">" + item.name + ":" + item.status + "</div>");
		         $('.Progress').after($myli);
		     }else{
			 $myli = $("<div style='background-color:#FF0000;' id= " + item.name + ">" + item.name + ":" + item.status + "</div>");
		         $('.Progress').after($myli);
		     }
		 });
		 $firstli = $("<div style='background-color:#307AFF;'>Results:</div>");
		 $('.Progress').after($firstli);
         $('.Progress').hide();
		 draw();

	    });
	}

    </script>

  </head>

  <body onload="ini()">
    <div class="starter-template">
      <div class="container">
        <div class="row">
          <div class="col-md-10">
            <div class="content">
              <h1><span class="font-semi-bold">AOF</span> <span class="smaller">Application Orchestration Framework</span></h1>
              <p class="lead">Deploy the App Ensemble to your Device.</p>
              <div class="navi">
                <ul>
                  <li id="tab1" onclick="change('deploy')">Deploy</li><li id="tab2" onclick="change('workflow')">Workflow</li>
                </ul>
              </div>
              <div id="deploy" class="deploy">
                <div class="Progress">
                  <ul>
                    <li id="p0">Deploy</li><li id="p1">.</li><li id="p2">.</li><li id="p3">.</li><li id="p4">.</li>
                  </ul>
                </div>
              </div>
              <div id="workflow" class="workflow">
                <canvas id="cvs" width="800" height="600">browser not supports canvas</canvas>
              </div>
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
