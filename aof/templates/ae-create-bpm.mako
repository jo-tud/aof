# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions"/>
<%block name="header">
    <link rel="stylesheet" href="/static/bower_components/bpmn-js/dist/assets/diagram-js.css"/>
    <link rel="stylesheet" href="/static/bower_components/bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css"/>
    <link rel="stylesheet" href="/static/stylesheets/ae-visualize-bpm.css"/>
</%block>
<div class="content" id="js-drop-zone">
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

<%block name="local_js">

    <!-- viewer dependencies -->


    <!-- viewer -->


    <!-- local js -->



</%block>