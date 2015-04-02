# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions">
</%block>
<div class="row">
    <div class="small-12 columns">
        <h1>Application Orchestration Framework</h1>

        <ul>
            <li>There are currently <a href="/app-pool.html">${number_of_apps} Apps</a> in the App-Pool.</li>
            <li>We have <a href="/app-ensembles.html">${number_of_ae} App-Ensembles</a> available.</li>
            <li>The model currently consists of ${unique_triples} unique triples!</li>
        </ul>
    </div>
</div>
<%block name="local_js">
</%block>