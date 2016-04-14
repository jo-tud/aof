# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions"/>
<div class="row">
    % if ae_inst_qrcode != "None":
        <div class="small-12 large-9 columns">
    % else:
        <div class="small-12 large-12 columns">
    % endif
        <h1>AOF Web-App</h1>
    <h4>Some stats:</h4>
    <ul>
        <li>There are <a href="${app_pool_uri}">${number_of_apps} Apps</a> in the App-Pool.</li>
        <li><a href="${app_ensemble_pool_uri}">${number_of_ae} App-Ensembles</a> are available for Download.</li>

    </ul>
    <h4>Get ready:</h4>
        <div class="row">
            <div class="small-12 columns">
                <p>
                    If you haven't done so yet, now is the time to install the <i>App-Ensemble Installer</i>
                    and the <i>AOF Conductor</i> on your Android device. The first automates the installation of
                    App-Ensembles and the latter executes them.
                </p>
                <p>
                    <a class="button small" href="${ae_inst_artifact}">Download App-Ensemble installer</a>
                    <a class="button small" href="${aofc_inst_artifact}">Download AOF Conductor</a>
                </p>
            </div>


        </div>
    </div>
    <div class="small-12 large-3 columns panel pagination-centered end">
        <img src="${ae_inst_qrcode}" alt="${ae_inst_qrcode}"/>
        <br /><span class="secondary label">Scan to download App-Ensemble installer</span>
    </div>
    <div class="small-12 large-3 columns panel pagination-centered end">
        <img src="${aofc_inst_qrcode}" alt="${aofc_inst_qrcode}"/>
        <br /><span class="secondary label">Scan to download AOF-Conductor</span>
    </div>
</div>
<%block name="local_js"/>
