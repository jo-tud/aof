# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions">
   <li class="defaultinactive"><a class="action-icon" id="js-save-appensemble" href title="save the AppEnsemble">SAVE APPENSEMBLE</a></li>
   <li class="defaultinactive"><a class="action-icon" id="js-save-appensemble-and-close" href title="save the AppEnsemble">SAVE & CLOSE</a></li>
   <li class="defaultinactive"><a class="action-icon" id="js-download-svg" href title="download as SVG image">DOWNLOAD SVG</a></li>
   <li><a class="action-icon" id="close-modeler" href title="Close Modeler">CLOSE MODELER</a></li>
</%block>
<%block name="header">
    <link rel="stylesheet" href="/static/stylesheets/diagram-js.css"/>
    <link rel="stylesheet" href="/static/stylesheets/bpmn-font/css/bpmn-embedded.css"/>
    <link rel="stylesheet" href="/static/stylesheets/ae-modeler.css"/>
</%block>
<div class="content" id="js-drop-zone">

    <div class="message intro">
      <div class="note">
        BPMN-Modeler should start immediately!
      </div>
    </div>

    <div class="message error">
      <div class="note">
        <p>Ooops, we could not display the BPMN 2.0 diagram.</p>

        <div class="details">
          <span>cause of the problem</span>
          <pre></pre>
        </div>
      </div>
    </div>

    <div class="canvas" id="js-canvas"></div>
    <div id="js-properties-panel"></div>
  </div>

<%block name="local_js">
     <script type="text/javascript">
        var urlencodedXML = "${urlencodedXML}";
        var mode = "${mode}";
        var del="${uri}";
    </script>
    <!-- viewer -->
    <script src="/static/js/ae-modeler.js"></script>

    <!-- local js -->



</%block>