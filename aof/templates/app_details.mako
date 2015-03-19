# -*- coding: utf-8 -*-
<%inherit file="new_layout.mako"/>
<%block name="header"></%block>
<%block name="top_bar_actions"/>

<div class="row">
    <div class="small-8 columns">
        <h1><a href="http://dev.plt.et.tu-dresden.de:8085/jenkins/job/AOFConductor">AOF Conductor</a></h1>
        <img src="/static/img/logo_plt.png" class="imgLiquidFill imgLiquid" style="width: 48px; height: 48px">
        <p class="markdown">The *AOF Conductor* is an app that executes App-Ensembles on Android mobile devices.</p>
        <table>
            <thead>
            <tr>
                <th width="200">Property</th>
                <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>Role</td>
                <td>Conductor</td>
            </tr>
            </tbody>
        </table>
    </div>
    <div class="small-4 columns">
        <ul class="clearing-thumbs clearing-feature" data-clearing>
            <li class="clearing-featured-img"><a class="th"
                   href="http://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Steven_Sametz_conducting%2C_cropped.jpg/256px-Steven_Sametz_conducting%2C_cropped.jpg">
                <img class="imgLiquidFill imgLiquid" style="width:300px; height:300px;" src="http://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Steven_Sametz_conducting%2C_cropped.jpg/256px-Steven_Sametz_conducting%2C_cropped.jpg"></a>
            </li>
            <li><a class="th"
                   href="http://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Full_score.jpg/320px-Full_score.jpg"> <img
                    src="http://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Full_score.jpg/320px-Full_score.jpg"> </a>
            </li>
            <li><a class="th"
                   href="http://upload.wikimedia.org/wikipedia/commons/2/2f/Bundesarchiv_Bild_183-R92264%2C_Herbert_von_Karajan.jpg"> <img
                    src="http://upload.wikimedia.org/wikipedia/commons/2/2f/Bundesarchiv_Bild_183-R92264%2C_Herbert_von_Karajan.jpg"></a>
            </li>
        </ul>
    </div>
</div>

<div class="row">
    <div class="small-12 columns">
        <h2><a rel="dc:creator" href="http://www.et.tu-dresden.de/ifa/index.php?id=jp">Creator</a></h2>
        <table>
            <thead>
            <tr>
                <th width="200">Property</th>
                <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>Name</td>
                <td><span property="foaf:name">Johannes Pfeffer</span></td>
            </tr>
            <tr>
                <td>E-Mail</td>
                <td><a href="mailto:johannes.pfeffer@tu-dresden.de" rel="foaf:mbox">johannes.pfeffer@tu-dresden.de</a>
                </td>
            </tr>
            </tbody>
        </table>
    </div>
</div>

<div class="row">
    <div class="small-12 columns">
        <h2>Entry points</h2>
    </div>
    <div class="small-12 columns">
        <h3>Start Workflow</h3>

        <p class="markdown">When called with no extras, the *StartWorkflow* action brings up an activity that enables
            the user to choose an App-Ensemble from the file system. When the *org.aof.extra.AE_FILE* extra is provided,
            the App-Ensemble is loaded immediately.</p>
        <table>
            <thead>
            <tr>
                <th width="200">Property</th>
                <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>Type</td>
                <td>Android action</td>
            </tr>
            <tr>
                <td>android:name</td>
                <td>org.aof.action.START_WORKFLOW</td>
            </tr>
            </tbody>
        </table>
    </div>
    <div class="small-12 columns">
        <h4>Inputs</h4>
        <table>
            <thead>
            <tr>
                <th width="200">Property</th>
                <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>Type</td>
                <td>Android extra</td>
            </tr>
            <tr>
                <td>Required</td>
                <td>False</td>
            </tr>
            <tr>
                <td>android:name</td>
                <td>org.aof.extra.AE_FILE</td>
            </tr>
            <tr>
                <td>Data type</td>
                <td>xsd:anyURI</td>
            </tr>
            </tbody>
        </table>
    </div>
    <div class="small-12 columns">
        <h3>Main entry point</h3>

        <p class="markdown">This activity is the entry point for the application when it is used stand-alone. *It does
            not expect to receive data.*</p>
        <table>
            <thead>
            <tr>
                <th width="200">Property</th>
                <th>Value</th>
            </tr>
            </thead>
            <tbody>
            <tr>
                <td>Type</td>
                <td>Android action</td>
            </tr>
            <tr>
                <td>android:name</td>
                <td>android.intent.action.MAIN</td>
            </tr>
            </tbody>
        </table>
    </div>
</div>

<%block name="local_js">
    <script type="text/javascript">
        // var ae_id =;
    </script>
    <script src="/static/bower_components/imgLiquid/js/imgLiquid.js"></script>
    <script src="/static/bower_components/markdown-js/dist/markdown.js"></script>
    <script src="/static/js/jquery.loader-0.3.js"></script>
    <script src="/static/js/app_details.js"></script>
</%block>