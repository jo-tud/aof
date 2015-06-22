# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="header"></%block>
<%block name="top_bar_actions">
    <li><a href="${api_app_ttl_uri}">SHOW APP-DESCRIPTION</a></li>
    <li><a href="${details['binary']}">DOWNLOAD APP</a></li>
</%block>
<div class="row">
    % if details['has_main_screenshot']:
        <div class="small-12 columns">
            <ul class="clearing-thumbs clearing-feature" data-clearing>
                <li class="clearing-featured-img">
                    <div class="row">
                        <div class="small-12 medium-4 columns collapse">
                            <div class="imgLiquidFill imgLiquid" style="width:320px; height:320px; margin-bottom: 10px">
                                <a class="th" href="${main_screenshot['uri']}">
                                    <img class="" data-caption="${main_screenshot['comment']}"
                                         src="${main_screenshot['uri']}">
                                </a>
                            </div>
                        </div>
                    </div>
                </li>
                % if details['has_other_screenshots']:
                    % for screenshot in screenshots:
                        <li class="clearing-featured-img">
                            <div class="row">
                                <div class="small-12 medium-1 columns">
                                    <div class="imgLiquidFill imgLiquid" style="width:100px; height:100px; margin-bottom: 10px">
                                        <a class="th" href="${screenshot['uri']}">
                                            <img data-caption="${screenshot['comment']} "
                                                 src="${screenshot['uri']}"/>
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </li>
                    % endfor

                % endif
            </ul>
        </div>
    % endif
    <div class="small-12 columns">
        <h1>${details['name']}</h1>
    </div>
</div>

<div class="row">
    <div class="small-12 columns">
        <p class="markdown">${details['comment']}</p>
    </div>
    % if qrcode != "None":
        <div class="small-9 columns">
    % else :
        <div class="small-12 columns">
    % endif
        <table width="100%">
            <thead>
            <tr>
                <th width="200">Property</th>
                <th>Values</th>
            </tr>
            </thead>
            <tbody id="app-details-general">
            <tr>
                <td>Resource URI</td>
                <td><a href="${uri}" id="resource-uri">${uri}</a></td>
            </tr>
            <tr>
                <td><a href="${namespaces['AOF'].hasIcon}">Icon</a></td>
                <td>
                    % if details['icon'] != "None":
                        <a href="${details['icon']}" class="th radius">
                            <img src="${details['icon']}" class="imgLiquidFill imgLiquid"
                                 style="width: 48px; height: 48px">
                        </a>
                    % else :
                        <img src="/static/img/icon_placeholder.svg" alt="Placeholder icon"
                             class="imgLiquidFill imgLiquid"
                             style="width: 48px; height: 48px">
                    % endif
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
    % if qrcode != "None":
    <div class="medium-3 columns panel pagination-centered">
            <img src="${qrcode}" alt="${details['name']}"/>
            <span class="secondary label">Download App</span>
    </div>
    </div>
    % endif

</div>

% if details['has_creator']:
    <div class="row">
        <div class="small-12 columns">
            <h2><a rel="dc:creator" href="${namespaces['DC'].creator}">Creators</a></h2>
        </div>
    </div>
        % for creator in creators:
            ${'<div class="row">' if loop.even else '' | n}
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
            ${'</div>' if (loop.odd or loop.last) else '' | n}
        % endfor
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

                <p class="markdown">${ep['comment'].__str__()}</p>
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
                % for input in ep['inputs'] :
                    ${'<div class="row">' if loop.even else '' | n}
                        <div class="small-12 medium-6 columns${' end' if loop.last else ''}">
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
                                    <td><a href="${namespaces['AOF'].hasDatatype}">Data type</a></td>
                                    <td><a href="${input['has_datatype']}">${input['has_datatype']}</a></td>
                                </tr>
                                <tr>
                                    <td><a href="${namespaces['RDFS'].comment}">Comment</a></td>
                                    <td class="markdown">${input['comment'].__str__()}</td>
                                </tr>
                                </tbody>
                            </table>
                        </div>
                    ${'</div>' if (loop.odd or loop.last) else '' | n}
                % endfor
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

                <p class="markdown">${ep['comment'].__str__()}</p>
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
                <div class="small-12 columns">
                    <h4><a href="${namespaces['AOF'].hasOutput}">Outputs</a></h4>
                </div>
            </div>

                % for output in ep['outputs'] :
                    ${'<div class="row">' if loop.even else '' | n}
                        <div class="small-12 medium-6 columns${' end' if loop.last else ''}">
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
                                    <td><a href="${namespaces['AOF'].hasDatatype}">Data type</a></td>
                                    <td><a href="${output['has_datatype']}">${output['has_datatype']}</a></td>
                                </tr>
                                <tr>
                                    <td><a href="${namespaces['RDFS'].comment}">Comment</a></td>
                                    <td class="markdown">${output['comment']}</td>
                                </tr>
                                </tbody>
                            </table>
                        </div>
                    ${'</div>' if (loop.odd or loop.last) else '' | n}
                % endfor
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