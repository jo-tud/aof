# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>

    <link href="${request.static_url('aof:static/deploy.css')}" rel="stylesheet">

    <script Language="javascript">

	function deploy() {
        var device = ${hasDevice};
	     if(device=="1"){
	         window.location.href = "/deploy/deploy_select";
	     }else if(device=="0"){
	         $("#p1").text("No device connected, please connect your device and refresh");
	     }
    }

    </script>

    <div class="content" id="content_dp">
      <p class="lead">Deploy the App Ensemble to your Device.</p>
      <p id="p1">Please connect your device via USB and press the button</p>
      <div style="height:50px">
        <input onclick="deploy()" id="deploy"
          onmouseover="this.style.borderWidth='3px'"
          onmouseout="this.style.borderWidth='2px'" type="button"
          class="mybtn" value="Deploy now!"/>
      </div>
    </div>




