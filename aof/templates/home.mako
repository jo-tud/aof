# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions">
</%block>
<div class="row">
    <div class="small-12 columns">
        <h1>${meta['appname']}</h1>

        <ul>
            <li>There are currently <a href="/app-pool.html">${number_of_apps} Apps</a> in the App-Pool.</li>
            <li>We have <a href="/app-ensembles.html">${number_of_ae} App-Ensembles</a> available.</li>
            <li>The model currently consists of ${unique_triples} unique triples!</li>
        </ul>
        <div class="row">
            <div class="medium-4 small-12 columns">To be able to install App-Ensembles you must download and install the <a
                    href="/app-pool/details.html?URI=${ae_inst_uri}">App-Ensemble installer</a>.</div>

            % if ae_inst_qrcode != "None":
                <div class="medium-3 small-12 columns panel pagination-centered end">
                    <img src="${ae_inst_qrcode}" alt="${ae_inst_qrcode}"/>
                    <span class="secondary label">Download App-Ensemble installer</span>
                </div>
            % endif
        </div>
    </div>
</div>
<%block name="local_js">
</%block>
