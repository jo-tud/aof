# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<!DOCTYPE html>
    <title>AOF:App-Pool:Show</title>

    <link href="${request.static_url('aof:static/deploy.css')}" rel="stylesheet">

    <script type="text/javascript" src="${request.static_url('aof:static/js/workflow.js')}"></script>

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
	      getApps();
	}

	function getApps(){
        $.getJSON('/demo_apps.json', function(data){
            var json_data=data['apps']
            var dataObj=eval("("+json_data+")")
            $.each(dataObj.devices,function(idx,item){
                AppInstall(item.name);
            });
        });
    }

    function AppInstall(data){
        $.getJSON('/demo_install.json', {data: data}, function(data){
            var json_data=data['result']
            var dataObj=eval("("+json_data+")")
                $.each(dataObj.devices,function(idx,item){
                    $myli = $("<div style='background-color:#0077FF;' id= " + item.name + ">" + item.name + ":" + item.status + "</div>");
		            $('.Progress').after($myli);
	        });
        });
	}

    </script>

  <body onload="ini()">
    <div class="content">
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
  </body>
