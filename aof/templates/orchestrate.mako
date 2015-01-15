# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
    <link href="${request.static_url('aof:static/deploy.css')}" rel="stylesheet">

    <script Language="javascript">
        // to do 2 : no app select
        var app_id = 0;
        var foderName = "";
        var requestApps = [];
        var availableApps = [];

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
            foderName=$("#select").find("option:selected").text();
            if (foderName == "------Please select a model------"){
                $("#p1").text("No Model selected, please select a model");
            }else{
                getApps(foderName)
            }
        }

        function submit(){
            var selected_apps = [];
            for (i = 0; i < app_id; i++){
                app_id_ = "#app_id_" + i;
                app_id_label_ = "app_id_label_" + i;
                app_selected = $(app_id_).find("option:selected").text();
                app_request = document.getElementById(app_id_label_).textContent;
                if (app_selected != '-------------Please select an app-------------'){
                    selected_apps[selected_apps.length] = app_request + "§§" + app_selected;
                } else {
                    selected_apps[selected_apps.length] = app_request + "§§" + "no_select";
                }

            }
            $.getJSON('/o_orchestration.json', {request_selected_apps: selected_apps.toString(),
                available_apps: availableApps.toString(), modelName: foderName}, function(data){

                    var json_data=data['ae_result'];
                    var dataObj=eval("("+json_data+")");
                        $.each(dataObj.ae_result,function(idx,item){
                        $myli = $("<option style='margin-top: 10px; margin-left: 10px'>" + item.name + "</option>");
                        $myli.insertAfter('#content_o');
	                });

            });
        }

        function getApps(data){
            $.getJSON('/o_get_apps.json', {data: data}, function(data){

                var json_data=data['availableApps'];
                    var dataObj=eval("("+json_data+")");
                        $.each(dataObj.available_apps,function(idx,item){
                            availableApps[availableApps.length] = item.name;
                    });
                $( ".functions" ).remove();
                $( "#p2" ).remove();
                $title = $("<p id='p2'>Pleaseselect the Application and submit</p>")
                $('.model_select').after($title);
                var json_data=data['requestApps'];
                var dataObj=eval("("+json_data+")");
                    $.each(dataObj.request_apps,function(idx,item){
                        requestApps[requestApps.length] = item.name;
                        $myli = $("<div class='functions'>" + "<label id='app_id_label_"+app_id+"' style ='float: left;'>"+item.name+"</label>"
                                  + "<select id='app_id_"+app_id+"'style ='float: right;'>" +
                                  "<option id='app_id_" + app_id + "_options_first'>" +
                                  "-------------Please select an app-------------"
                                  + "</option></select>" + "<div style='clear: both;'></div>" + "</div>");
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
      <div class="content" id="content_o">
        <p class="lead">App Orchestration.</p>
        <p id="p1">Please select the Model you want to orchestrate</p>
        <div class="model_select" style="height:50px">
          <select id="select" style="position:absolute;margin-left:4px;margin-top:4px;width:240px">
            <option id="option">------Please select a model------</option>
          </select>
          <input style="position:absolute;margin-left:275px;margin-top:-2px" onclick="deploy()" id="deploy"
            onmouseover="this.style.borderWidth='3px'"
            onmouseout="this.style.borderWidth='2px'" type="button"
            class="mybtn" value="Use the model"/>
          <input style="position:absolute;margin-left:615px;margin-top:-2px" onclick="submit()" id="submit"
            onmouseover="this.style.borderWidth='3px'"
            onmouseout="this.style.borderWidth='2px'" type="button"
            class="mybtn" value="Submit the selections of apps"/>
        </div>
      </div>
    </body>