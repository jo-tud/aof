# -*- coding: utf-8 -*-
<%inherit file="new_layout.mako"/>
<%block name="top_bar_actions"/>
<%block name="header">
    <link rel="stylesheet" href="/static/bower_components/bpmn-js/dist/assets/diagram-js.css"/>
    <link rel="stylesheet" href="/static/bower_components/bpmn-js/dist/assets/bpmn-font/css/bpmn-embedded.css"/>
    <link rel="stylesheet" href="/static/stylesheets/ae_bpmn-js.css"/>
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
    <script type="text/javascript">
        var ae_id = "${ae_id}";
    </script>
    <!-- viewer dependencies -->
    <script src="/static/bower_components/jquery-mousewheel/jquery.mousewheel.js"></script>
    <script src="/static/bower_components/lodash/dist/lodash.js"></script>
    <script src="/static/bower_components/sax/lib/sax.js"></script>
    <script src="/static/bower_components/Snap.svg/dist/snap.svg.js"></script>
    <script src="/static/bower_components/hammerjs/hammer.min.js"></script>

    <!-- viewer -->
    <script src="/static/bower_components/bpmn-js/dist/bpmn-modeler.js"></script>

    <!-- local js -->
    <script src="/static/js/ae_bpmn-js.js"></script>


</%block>