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
            if (foderName == "------------ Model   Name ------------"){
                $("#p1").text("No Model selected, please select a model");
            }else{
                orchestrate(foderName)
            }
        }

        function orchestrate(data){
        $.getJSON('/o_get_apps.json', {data: data}, function(data){
            $title = $("<p id='p2'>Pleaseselect the Application and submit</p>")
            $('#deploy').after($title);
            var json_data=data['requestApps']
            var dataObj=eval("("+json_data+")")
            var app_id = 1
                $.each(dataObj.request_apps,function(idx,item){
                    $myli = $("<div style='background-color:#0077FF' id= " + item.name + ">" + item.name
                              + "<select id='select'><option id=" + "app_" + app_id + ">" +
                              "------------- App   Name -------------"
                              + "</option></select>"+ "</div>");
                    $('#p2').after($myli);
                var json_data=data['availableApps']
                var dataObj=eval("("+json_data+")")
                    $.each(dataObj.available_apps,function(idx,item){
                        $myli = $("<option>" + item.name + "</option>");
                        $myli.insertAfter('#app_' + app_id);
	            });
            });


        });
	}

    </script>


    <body onload="init()">
      <div class="content">
        <p class="lead">App Orchestration.</p>
        <p id="p1">Please select the Model you want to orchestrate</p>
        <select id="select">
          <option id="option">------------ Model   Name ------------</option>
        </select>
        <input onclick="deploy()" id="deploy"
          onmouseover="this.style.borderWidth='3px'"
          onmouseout="this.style.borderWidth='2px'" type="button"
          class="mybtn" value="Submit"/>

      </div>
    </body>