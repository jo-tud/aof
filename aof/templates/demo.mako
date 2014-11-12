# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>

    <link href="${request.static_url('aof:static/deploy.css')}" rel="stylesheet">

    <!--Require aof.tools Js-->
    <script type="text/javascript" src="${request.static_url('aof:static/js/aof.tools.js')}"></script>

    <script Language="javascript">
	function deploy() {
        var device = ${hasDevice};
	     if(device=="1"){
	         window.location.href = "/demo/demo_tool";
	     }else if(device=="0"){
		 $("#div2").text("Bitte Gerät anschließen und neu laden");
		 $("#div2").css("font-size","xx-large");
		 $("#div2").css("position","absolute");
		 $("#div2").css("padding-left","140px");
		 $("#div2").css("padding-top","140px");
	     }
    }
    </script>

    <div class="content">
      <p class="lead">Deploy the App Ensemble to your Device.</p>
      <p>Please connect your device via USB and press the button</p>
      <input onclick="deploy()" id="deploy"
        onmouseover="this.style.borderWidth='3px'"
        onmouseout="this.style.borderWidth='2px'" type="button"
    class="mybtn" value="Deploy now!"/>
    </div>




