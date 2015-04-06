# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="header"></%block>
<%block name="top_bar_actions">
    <li><a href="${details['binary']}">DOWNLOAD</a></li>
</%block>
<div class="row">
    <div class="small-12 columns">
        <h1>${details['name']}</h1>
    </div>
</div>

<div class="row">
    <div class="small-12 medium-6 columns">
        <p class="markdown">${details['comment'].__str__().strip()}</p>
            <table width="100%">
                <thead>
                <tr>
                    <th width="200">Property</th>
                    <th>Values</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                    <td>Resource URI</td>
                    <td><a href="${uri}">${uri}</a></td>
                </tr>
                <tr>
                    <td><a href="${namespaces['AOF'].hasIcon}">Icon</a></td>
                    <td>
                        <a href="${details['icon']}" class="th radius">
                            <img src="${details['icon']}" class="imgLiquidFill imgLiquid"
                                 style="width: 48px; height: 48px">
                        </a>
                    </td>
                </tr>
        % if details['has_role']:
                    % for role in roles:
                        <tr>
                            <td><a href="${namespaces['AOF'].hasRole}">Role</a></td>
                            <td><a href="${role}">${role}</a></td>
                        </tr>
                    % endfor
        % endif
                </tbody>
            </table>
    </div>
    <div class="small-12 medium-6 columns">
        <ul class="clearing-thumbs clearing-feature" data-clearing>
            % if details['has_main_screenshot']:
                <li class="clearing-featured-img">
                    <div class="imgLiquidFill imgLiquid" style="width:300px; height:300px;" >
                    <a class="th" href="${main_screenshot['uri']}">
                        <img class="" data-caption="${main_screenshot['comment']}" src="${main_screenshot['thumb_uri']}">
                    </a>
                    </div>
                </li>
            % endif
            % if details['has_other_screenshots']:
                % for screenshot in screenshots:
                    <li>
                    <div class="imgLiquidFill imgLiquid" style="width:300px; height:300px;" >
                        <a class="th" href="${screenshot['uri']}">
                            <img data-caption="${screenshot['comment']} "src="${screenshot['thumb_uri']}" />
                        </a>
                    </div>
                    </li>
                % endfor
            % endif
        </ul>
    </div>
</div>

% if details['has_creator']:
    <div class="row">
        <div class="small-12 columns">
            <h2><a rel="dc:creator" href="${namespaces['DC'].creator}">Creators</a></h2>
        </div>
    </div>
    <div class="row">
        % for creator in creators:
            <div class="small-12 medium-6 columns">
                <table width="100%">
                    <thead>
                    <tr>
                        <th width="200">Property</th>
                        <th>Values</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td><a href="${namespaces['FOAF'].name}">Name</a></td>
                        <td><span property="foaf:name">${creator['name']}</span></td>
                    </tr>
                    <tr>
                        <td><a href="${namespaces['FOAF'].mbox}">E-Mail</a></td>
                        <td><a href="${creator['mbox']}" rel="foaf:mbox">${creator['mbox']}</a></td>
                    </tr>
                    <tr>
                        <td><a href="${namespaces['FOAF'].homepage}">Homepage</a></td>
                        <td><a href="${creator['homepage']}">${creator['homepage']}</a></td>
                    </tr>
                    </tbody>
                </table>
            </div>
        % endfor
    </div>
% endif

% if details['has_entry_points']:
    <div class="row">
        <div class="small-12 columns">
            <h2><a href="${namespaces['AOF'].providesEntryPoint}">Entry points</a></h2>
        </div>
    </div>
    % for ep in entry_points :
        <div class="row">
            <div class="small-12 columns">
                <h3>${ep['label']}</h3>

                <p class="markdown">${ep['comment'].__str__().strip()}</p>
                <table width="100%">
                    <thead>
                    <tr>
                        <th width="200">Property</th>
                        <th>Values</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td><a href="${namespaces['RDF'].type}">Type</a></td>
                        <td>
                            %for type in ep['types']:
                                <a href="${type}">${type}</a><br/>
                            %endfor
                        </td>
                    </tr>
                    <tr>
                        <td><a href="${namespaces['ANDROID'].name}">android:name</a></td>
                        <td>${ep['android_name']}</td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
        % if 'inputs' in ep:
            <div class="row">
                <div class="small-6 columns">
                    <h4><a href="${namespaces['AOF'].hasInput}">Inputs</a></h4>
                </div>
            </div>
            <div class="row">
                % for input in ep['inputs'] :
                    <div class="small-6 columns">
                        <table width="100%">
                            <thead>
                            <tr>
                                <th width="200">Property</th>
                                <th>Values</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr>
                                <td><a href="${namespaces['RDF'].type}">Type</a></td>
                                <td>
                                    %for type in input['types']:
                                        <a href="${type}">${type}</a><br/>
                                    %endfor
                                </td>
                            </tr>
                            <tr>
                                <td><a href="${namespaces['AOF'].isRequired}">Required</a></td>
                                <td>${input['is_required']}</td>
                            </tr>
                            <tr>
                                <td><a href="${namespaces['ANDROID'].name}">android:name</a></td>
                                <td>${input['android_name']}</td>
                            </tr>
                            <tr>
                                <td><a href="${namespaces['AOF'].datatype}">Data type</a></td>
                                <td><a href="{input['data_type']}">${input['data_type']}</a></td>
                            </tr>
                            <tr>
                                <td><a href="${namespaces['RDFS'].comment}">Comment</a></td>
                                <td class="markdown">${input['comment'].__str__().strip()}</td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                % endfor
            </div>
        % endif
    % endfor
% endif

% if details['has_exit_points']:
    <div class="row">
        <div class="small-12 columns">
            <h2><a href="${namespaces['AOF'].providesExitPoint}">Exit points</a></h2>
        </div>
    </div>
    % for ep in exit_points :
        <div class="row">
            <div class="small-12 columns">
                <h3>${ep['label']}</h3>

                <p class="markdown">${ep['comment'].__str__().strip()}</p>
                <table width="100%">
                    <thead>
                    <tr>
                        <th width="200">Property</th>
                        <th>Values</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td><a href="${namespaces['RDF'].type}">Type</a></td>
                        <td>
                            %for type in ep['types']:
                                <a href="${type}">${type}</a><br/>
                            %endfor
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
        % if 'outputs' in ep:
            <div class="row">
                <div class="small-6 columns">
                    <h4><a href="${namespaces['AOF'].hasOutput}">Outputs</a></h4>
                </div>
            </div>
            <div class="row">
                % for output in ep['outputs'] :
                    <div class="small-6 columns">
                        <table width="100%">
                            <thead>
                            <tr>
                                <th width="200">Property</th>
                                <th>Values</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr>
                                <td><a href="${namespaces['RDF'].type}">Type</a></td>
                                <td>
                                    %for type in output['types']:
                                        <a href="${type}">${type}</a><br/>
                                    %endfor
                                </td>
                            </tr>
                            <tr>
                                <td><a href="${namespaces['AOF'].isGuaranteed}">Guaranteed</a></td>
                                <td>${output['is_guaranteed']}</td>
                            </tr>
                            <tr>
                                <td><a href="${namespaces['ANDROID'].name}">android:name</a></td>
                                <td>${output['android_name']}</td>
                            </tr>
                            <tr>
                                <td><a href="${namespaces['AOF'].datatype}">Data type</a></td>
                                <td><a href="{output['data_type']}">${input['data_type']}</a></td>
                            </tr>
                            <tr>
                                <td><a href="${namespaces['RDFS'].comment}">Comment</a></td>
                                <td class="markdown">${output['comment'].__str__().strip()}</td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
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