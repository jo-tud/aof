# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
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
<div class="row">
    <div class="small-12 columns">
        <div id="app_table">
            <table width="100%">
                <tbody>
                    % for app in apps:
                        <tr class="app_row">
                            <td width="80px">
                                <a href="/app-pool/details.html?URI=${app['uri']}">
                                    % if app['icon'] :
                                        <img src="${app['icon']}" width="64px" height="64px">
                                    % else :
                                        <img src="/static/img/icon_placeholder.svg" width="64px" height="64px">
                                    % endif
                                </a>
                            </td>
                            <td class="app_name">
                                <a href="/app-pool/details.html?URI=${app['uri']}">${app['name']}</a>
                            </td>
                            <td width="100px">
                                <a class="button tiny secondary round" style="margin-bottom: 0px"
                                   href="${app['binary']}">Download</a>
                            </td>
                        </tr>
                    % endfor
                </tbody>
            </table>
        </div>
    </div>
</div>

<%block name="local_js">
    <script src="static/js/jquery.liveFilter.js"></script>
    <script src="static/js/jquery.loader-0.3.js"></script>
    <script src="static/js/app-pool.js"></script>
</%block>