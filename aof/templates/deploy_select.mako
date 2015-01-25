# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
    <link href="${request.static_url('aof:static/deploy.css')}" rel="stylesheet">

    <script Language="javascript">
        function init(){
            $.getJSON('/deploy_select.json',function(data){
                var json_data=data['select'];
                var dataObj=eval("("+json_data+")");
                    $.each(dataObj.select,function(idx,item){
                    $myli = $("<option>" + item.name + "</option>");
                    $myli.insertAfter('#option');
	            });
            });
            $("#file").change(function () {
                if ($("#file").val() == "") {
                return;
            }
                var content = $("#file").val()
                document.getElementById("selected_file_name").textContent = content;
                $("#file").val("");
            });
        }

        function deploy1(){
            parameter=$("#select").find("option:selected").text();
            $.getJSON('/deploy_set.json', {ae_location:parameter}, function(data){
            });
            window.location.href = "/deploy/tool/deploy_tool";
        }

        function deploy2(){
            var file = $('#file')[0].files[0];
                if(file){
                    parameter = file.name;
                    $.getJSON('/deploy_set.json', {ae_location:parameter}, function(data){
                });
                window.location.href = "/deploy/tool/deploy_tool";
                }
        }


    </script>


    <body onload="init()">
      <div class="content" id="content_dp_select">
        <p class="lead">Deploy the App Ensemble to your Device.</p>
        <p id="p1">Please select the app-ensemble you want to deploy</p>
        <div class="model_select" style="height:50px">
          <select id="select">
            <option id="option">------Please select app-ensemble------</option>
          </select>
          <input onclick="deploy1()" id="deploy_1"
            onmouseover="this.style.borderWidth='3px'"
            onmouseout="this.style.borderWidth='2px'" type="button"
            class="mybtn" value="Use the app ensemble"/>
          <input onmouseover="durchsuchen.style.borderWidth='3px'" onmouseout="durchsuchen.style.borderWidth='2px'"
                 id="file" type="file"/>
          <input onclick="deploy2()" id="deploy_2"
            onmouseover="this.style.borderWidth='3px'"
            onmouseout="this.style.borderWidth='2px'" type="button"
            class="mybtn" value="Use the app ensemble"/>
          <input id="durchsuchen"
            onmouseover="this.style.borderWidth='3px'"
            onmouseout="this.style.borderWidth='2px'" type="button"
            class="mybtn" value="Durchsuchen"/>
          <span id="selected_file_name">No file selected</span>
        </div>
      </div>
    </body>