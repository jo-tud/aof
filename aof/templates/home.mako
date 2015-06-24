# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions">
</%block>
<div class="row">
    % if ae_inst_qrcode != "None":
    <div class="small-12 large-9 columns">
    % else:
    <div class="small-12 large-12 columns">
    % endif
        <h1>${meta['appname']}</h1>

        <ul>
            <li>There are currently <a href="${app_pool_uri}">${number_of_apps} Apps</a> in the App-Pool.</li>
            <li>We have <a href="${app_ensemble_pool_uri}">${number_of_ae} App-Ensembles</a> available.</li>
            <li>The model currently consists of ${unique_triples} unique triples!</li>
        </ul>
        <div class="row">
            <div class="small-12 columns">To be able to install App-Ensembles you must download and install the
                <a href="/apps/details.html?URI=${ae_inst_uri}">App-Ensemble installer</a>.
            </div>


        </div>
    </div>
    % if ae_inst_qrcode != "None":
        <div class="small-12 large-3 columns panel pagination-centered end">
            <img src="${ae_inst_qrcode}" alt="${ae_inst_qrcode}"/>
            <br /><span class="secondary label">Download App-Ensemble installer</span>
        </div>
    % endif
</div>
<%block name="local_js">
</%block>
