# -*- coding: utf-8 -*-
<%inherit file="new_layout.mako"/>
<%block name="top_bar_actions">
</%block>
<div class="row">
    <div class="small-12 columns">
        <h1>Application Orchestration Framework</h1>

        <ul>
            <li>There are currently ${number_of_apps} Apps in the <a href="/app-pool.html">App-Pool</a>.</li>
            <li>We have ${number_of_ae} App-Ensembles <a href="/app-ensembles.html">available</a>.</li>
            <li>The model currently consists of ${unique_triples} unique triples!</li>
        </ul>
    </div>
</div>
<%block name="local_js">
</%block>