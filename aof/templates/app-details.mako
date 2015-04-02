# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="header"></%block>
<%block name="top_bar_actions">
    <li><a href="${details['binary']}">DOWNLOAD</a></li>
</%block>

<div class="row">
    <div class="small-8 columns">
        <h1><a href="${uri}">${details['name']}</a></h1>
        <img src="${details['icon']}" class="imgLiquidFill imgLiquid" style="width: 48px; height: 48px">

        <p class="markdown">${details['comment'].__str__().strip()}</p>
        % if details['has_role']:
            <table>
                <thead>
                <tr>
                    <th width="200">Property</th>
                    <th>Value</th>
                </tr>
                </thead>
                <tbody>
                % for role in roles:
                    <tr>
                        <td>Role</td>
                        <td>${role}</td>
                    </tr>
                % endfor
                </tbody>
            </table>
        % endif
    </div>
    <div class="small-4 columns">
        <ul class="clearing-thumbs clearing-feature" data-clearing>
            % if details['has_main_screenshot']:
            <li class="clearing-featured-img">
                <a class="th" href="${main_screenshot['uri']}">
                    <img class="imgLiquidFill imgLiquid" style="width:300px; height:300px;"
                         src="${main_screenshot['thumb_uri']}"></a>
            </li>
            % endif
            % if details['has_other_screenshots']:
            % for screenshot in screenshots:
                <li><a class="th" href="${screenshot['uri']}">
                    <img src="${screenshot['thumb_uri']}">
                </a>
                </li>
            % endfor
            % endif
        </ul>
    </div>
</div>

% if details['has_creator']:
% for creator in creators:
<div class="row">
    <div class="small-12 columns">
        <h2><a rel="dc:creator" href="${creator['uri']}">Creator</a></h2>
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
                <td><span property="foaf:name">${creator['name']}</span></td>
            </tr>
            <tr>
                <td>E-Mail</td>
                <td><a href="${creator['mbox']}" rel="foaf:mbox">${creator['mbox']}</a></td>
            </tr>
            <tr>
                <td colspan="2"><a href="${creator['homepage']}">Homepage</a></td>
            </tr>
            </tbody>
        </table>
    </div>
</div>
% endfor
% endif

% if details['has_entry_points']:
    <div class="row">
    <div class="small-12 columns">
        <h2>Entry points</h2>
    </div>
    % for ep in entry_points :
        <div class="small-12 columns">
            <h3>${ep['label']}</h3>

            <p class="markdown">${ep['comment'].__str__().strip()}</p>
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
                    <td>
                        %for type in ep['types']:
                            ${type},
                        %endfor
                    </td>
                </tr>
                <tr>
                    <td>android:name</td>
                    <td>${ep['android_name']}</td>
                </tr>
                </tbody>
            </table>
        </div>
        % if 'inputs' in ep:
            <div class="small-12 columns">
                % for input in ep['inputs'] :
                        %if loop.first :
                            <h4>Inputs</h4>
                        %endif
                        <h5>${input['android_name']}</h5>
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
                                <td>
                                    %for type in input['types']:
                                        ${type},
                                    %endfor
                                </td>
                            </tr>
                            <tr>
                                <td>Required</td>
                                <td>${input['is_required']}</td>
                            </tr>
                            <tr>
                                <td>android:name</td>
                                <td>${input['android_name']}</td>
                            </tr>
                            <tr>
                                <td>Data type</td>
                                <td>${input['data_type']}</td>
                            </tr>
                            <tr>
                                <td>Comment</td>
                                <td>${input['comment'].__str__().strip()}</td>
                            </tr>
                            </tbody>
                        </table>
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