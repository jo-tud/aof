# -*- coding: utf-8 -*-
<%inherit file="new_layout.mako"/>
<%block name="header"></%block>
<%block name="top_bar_actions">
    <li><a href="${app_details['binary']}" id="action_update">DOWNLOAD</a></li>
</%block>

<div class="row">
    <div class="small-8 columns">
        <h1><a href="${app_uri}">${app_details['label']}</a></h1>
        <img src="${app_details['icon']}" class="imgLiquidFill imgLiquid" style="width: 48px; height: 48px">

        <p class="markdown">${app_details['comment'].strip()}</p>
        % if 'role' in app_details:
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
                    <td>${app_details['role']}</td>
                </tr>
                </tbody>
            </table>
        % endif
    </div>

    <div class="small-4 columns">
        <ul class="clearing-thumbs clearing-feature" data-clearing>
            <li class="clearing-featured-img">
                <a class="th" href="${app_details['main_screenshot_uri']}">
                    <img class="imgLiquidFill imgLiquid" style="width:300px; height:300px;"
                         src="${app_details['main_screenshot_thumb_uri']}"></a>
            </li>
            % for screenshot in screenshots:
                <li><a class="th" href="${screenshot.main_screenshot_uri}">
                    <img src="${screenshot.main_screenshot_thumb_uri}">
                </a>
                </li>
            % endfor
        </ul>
    </div>
</div>

<div class="row">
    <div class="small-12 columns">
        <h2><a rel="dc:creator" href="${app_details['creator']}">Creator</a></h2>
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
                <td><span property="foaf:name">${app_details['creator_name']}</span></td>
            </tr>
            <tr>
                <td>E-Mail</td>
                <td><a href="${app_details['creator_mbox']}" rel="foaf:mbox">${app_details['creator_mbox']}</a>
                </td>
            </tr>
            </tbody>
        </table>
    </div>
</div>

% if 'comment' in entry_points.bindings[0] :

    <div class="row">
    <div class="small-12 columns">
        <h2>Entry points</h2>
    </div>
    % for ep in entry_points :
        <div class="small-12 columns">
            <h3>${ep.label}</h3>

            <p class="markdown">${ep.comment.strip()}</p>
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
                    <td>${ep.type}</td>
                </tr>
                <tr>
                    <td>android:name</td>
                    <td>${ep.androidActionName}</td>
                </tr>
                </tbody>
            </table>
        </div>
        % if len(entry_points_inputs.bindings) > 0:
            <div class="small-12 columns">
                % for input in entry_points_inputs :
                    % if ep.entryPoint == input.entryPoint:
                        %if loop.first :
                            <h4>Inputs</h4>
                        %endif
                        <h5>${input.androidExtraName}</h5>
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
                                <td>${input.type}</td>
                            </tr>
                            <tr>
                                <td>Required</td>
                                <td>${input.isRequired}</td>
                            </tr>
                            <tr>
                                <td>android:name</td>
                                <td>${input.androidExtraName}</td>
                            </tr>
                            <tr>
                                <td>Data type</td>
                                <td>${input.datatype}I</td>
                            </tr>
                            </tbody>

                        </table>
                    % endif
                % endfor
            </div>
        % endif
    % endfor

% endif

<%block name="local_js">
    <script type="text/javascript">
        // var ae_id =;
    </script>
    <script src="/static/bower_components/imgLiquid/js/imgLiquid.js"></script>
    <script src="/static/bower_components/markdown-js/dist/markdown.js"></script>
    <script src="/static/js/jquery.loader-0.3.js"></script>
    <script src="/static/js/app-details.js"></script>
</%block>