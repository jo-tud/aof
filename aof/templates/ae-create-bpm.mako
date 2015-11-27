# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions"/>
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
  </div>

  <ul class="buttons">
    <li>
      download
    </li>
    <li>
      <a id="js-download-diagram" href title="download BPMN diagram">
        BPMN diagram
      </a>
    </li>
    <li>
      <a id="js-download-svg" href title="download as SVG image">
        SVG image
      </a>
    </li>
      <li>
      <a id="js-save-appensemble" href title="save the AppEnsemble">
        SAVE APPENSEMBLE
      </a>
    </li>
  </ul>

<%block name="local_js">

    <!-- viewer dependencies -->


    <!-- viewer -->
    <script src="/static/js/ae-modeler.js"></script>

    <!-- local js -->



</%block>