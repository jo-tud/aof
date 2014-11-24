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
            var json_data=data['result']
            var dataObj=eval("("+json_data+")")
                $.each(dataObj.result,function(idx,item){
                    alert(item.name)
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