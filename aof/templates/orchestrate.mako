# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
    <link href="${request.static_url('aof:static/deploy.css')}" rel="stylesheet">

    <script Language="javascript">
        function init(){
            $.getJSON('/o_select.json',function(data){
                var json_data=data['select'];
                var dataObj=eval("("+json_data+")");
                    $.each(dataObj.select,function(idx,item){
                    $myli = $("<option>" + item.name + "</option>");
                    $myli.insertAfter('#option');
	            });
            });
        }

        function deploy(){
            var foderName=$("#select").find("option:selected").text();
            if (foderName == "------Please select a model------"){
                $("#p1").text("No Model selected, please select a model");
            }else{
                orchestrate(foderName)
            }
        }

        function orchestrate(data){
        $.getJSON('/o_get_apps.json', {data: data}, function(data){
            $title = $("<p id='p2'>Pleaseselect the Application and submit</p>")
            $('.model_select').after($title);
            var json_data=data['requestApps'];
            var dataObj=eval("("+json_data+")");
            var app_id = 1
                $.each(dataObj.request_apps,function(idx,item){
                    $myli = $("<label for='app_id_"+app_id+"' style ='float: left;'>"+item.name+"</label>"
                              + "<select id='app_id_"+app_id+"'style ='float: right;'>" +
                              "<option id='app_id_" + app_id + "_options_first'>" +
                              "-------------Please select an app-------------"
                              + "</option></select>" + "<div style='clear: both;'></div>");
                    $('#p2').after($myli);
                var selected = item.preselection;
                var json_data=data['availableApps'];
                var dataObj=eval("("+json_data+")");
                    $.each(dataObj.available_apps,function(idx,item){
                        if (item.name == selected) {
                            $myli = $("<option selected>" + item.name + "</option>");
                            $myli.insertAfter('#app_id_' + app_id + "_options_first");
                        } else {
                            $myli = $("<option>" + item.name + "</option>");
                            $myli.insertAfter('#app_id_' + app_id + "_options_first");
                        }
                });
                app_id++;
            });
        });
	}

    </script>


    <body onload="init()">
      <div class="content">
        <p class="lead">App Orchestration.</p>
        <p id="p1">Please select the Model you want to orchestrate</p>
        <div class="model_select" style="height:50px">
          <select id="select" style="position:absolute;margin-left:4px;margin-top:4px;width:240px">
            <option id="option">------Please select a model------</option>
          </select>
          <input style="position:absolute;margin-left:305px;margin-top:-2px" onclick="deploy()" id="deploy"
            onmouseover="this.style.borderWidth='3px'"
            onmouseout="this.style.borderWidth='2px'" type="button"
            class="mybtn" value="Submit"/>
        </div>
      </div>
    </body>