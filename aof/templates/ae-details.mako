# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions">
    <li><a href="${ae_api_path}" id="action_update">INSTALL APP-ENSEMBLE</a></li>
</%block>

<div class="row">
    <h1>${ae_uri}</h1>
</div>
<div class="row">
% if qrcode != "None":
    <div class="small-9 columns">
% else :
    <div class="small-12 columns">
% endif

        <table>
            <thead>
            <tr>
                <th width="200">Property</th>
                <th>Value</th>
            </tr>
            </thead>

            <tbody>
            <tr>
                <td>Apps</td>
                <td>
                    % for app in ae_apps:
                        % if not loop.last:
                            <a href="${app['?app_uri'].__str__()}">${app['?name'].__str__()}</a>,
                        % else:
                            <a href="${app['?app_uri'].__str__()}">${app['?name'].__str__()}</a>
                        % endif
                    % endfor

                </td>
            </tr>

                %if ae_has_bpm:
                    <tr>
                        <td>BPM</td>
                        <td>
                            <a class="button" href="/app-ensembles/visualize-bpm.html?URI=${ae_uri}">Visualize BPM</a>
                        </td>
                    </tr>
                %endif

            </tbody>
        </table>
    </div>
% if qrcode != "None":
    <div class="medium-3 columns panel pagination-centered">
        <img src="${qrcode}" alt="${ae_uri}"/>
        <span class="secondary label">Download AppEnsemble</span>
    </div>
    % endif
</div>



<%block name="local_js">
    <script type="text/javascript">
        var ae_uri = "${ae_uri}";
    </script>
    <script src="/static/js/jquery.liveFilter.js"></script>
    <script src="/static/js/jquery.loader-0.3.js"></script>
    <script src="/static/js/ae-details.js"></script>
</%block>