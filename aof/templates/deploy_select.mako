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
      <div class="content">
        <p class="lead">Deploy the App Ensemble to your Device.</p>
        <p id="p1">Please select the app-ensemble you want to deploy</p>
        <div class="model_select" style="height:50px">
          <select id="select" style="position:absolute;margin-left:4px;margin-top:4px;width:260px">
            <option id="option">------Please select app-ensemble------</option>
          </select>
          <input style="position:absolute;margin-left:4px;margin-top:45px" onclick="deploy1()" id="deploy_1"
            onmouseover="this.style.borderWidth='3px'"
            onmouseout="this.style.borderWidth='2px'" type="button"
            class="mybtn" value="Use the app ensemble"/>
          <input id="file" style="font-size:23px;position:absolute;margin-left:628px;margin-top:5px;" type="file"/>
          <input style="position:absolute;margin-left:628px;margin-top:45px" onclick="deploy2()" id="deploy_2"
            onmouseover="this.style.borderWidth='3px'"
            onmouseout="this.style.borderWidth='2px'" type="button"
            class="mybtn" value="Use the app ensemble"/>
        </div>
      </div>
    </body>