# -*- coding: utf-8 -*-
<%inherit file="new_layout.mako"/>
<%block name="top_bar_actions">
    <li class="has-form show-for-medium-up">
        <div class="row collapse">
            <input class="livefilter-input" type="text" placeholder="Filter">
        </div>
    </li>
</%block>

<li class="has-form show-for-small-only">
    <div class="row collapse">
        <input class="livefilter-input" type="text" placeholder="Filter">
    </div>
</li>

<div class="row full-width" id="app_table">
    <table>
        <tbody>
            % for app in apps:
                <tr class="app_row">
                    % if app.icon :
                        <td><img src="${app.icon}" width="64px" height="64px"></td>
                    % else :
                        <td><img src="/static/img/icon_placeholder.svg" width="64px" height="64px"></td>
                    % endif
                    <td class="app_name">
                        ${app.name}
                    </td>
                    <td>
                        <a class="button" href="${app.binary}">Download</a>
                        <a class="button" href="/app-pool/details.html?URI=${app.uri}">Details</a>
                    </td>
                </tr>
            % endfor
        </tbody>
    </table>
</div>

<div class="row full-width" id="app_tables" data-equalizer></div>

<%block name="local_js">
    <script src="static/js/jquery.liveFilter.js"></script>
    <script src="static/js/jquery.loader-0.3.js"></script>
    <script src="static/js/app-pool.js"></script>
</%block>