# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions">
    <li class="has-form show-for-medium-up">
        <div class="row collapse">
            <input class="livefilter-input" type="text" placeholder="Filter">
        </div>
    </li>
    <li class="divider"></li>
    <li><a href="#" id="action_update">UPDATE POOL</a></li>
</%block>

<div class="row">
    <div class="small-12 columns">
        <li class="has-form show-for-small-only">
            <input class="livefilter-input" type="text" placeholder="Filter">
        </li>
    </div>
</div>
<div class="row collapse">
    <div class="small-12 columns">
        <div id="app_table">
            <table width="100%">
                <tbody>
                    % for app in apps:
                        <tr class="app_row">
                            <td>
                                <a href="${app['details_uri']}">
                                    % if app['icon'] != "None":
                                        <img src="${app['icon']}" width="64px" height="64px">
                                    % else :
                                        <img src="/static/img/icon_placeholder.svg" width="64px" height="64px">
                                    % endif
                                </a>
                            </td>
                            <td class="app_name">
                                <h4><a href="${app['details_uri']}">${app['name']}</a><small><br/>${app['description']}</small></h4>
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