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
            alert("OK");
        }
    </script>


    <body onload="init()">
      <div class="content">
        <p class="lead">App Orchestration.</p>
        <p id="p1">Please select the Model you want to orchestrate</p>
        <select>
          <option id="option">------------ Model   Name ------------</option>
        </select>
        <input onclick="deploy()" id="deploy"
          onmouseover="this.style.borderWidth='3px'"
          onmouseout="this.style.borderWidth='2px'" type="button"
          class="mybtn" value="Submit"/>
      </div>
    </body>