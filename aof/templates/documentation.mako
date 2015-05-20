# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions">
</%block>
<div class="row">
    <div class="small-12 columns">
        <h1>Documentation</h1>
        <!--
        <ul>
            <li><b>AOF Language Specification</b> <i>Version 002</i> <a href="/docs/app-description_specification.html">HTML</a> <a href="/static/docs/AOF Language Specification v002.docx.pdf">PDF</a></li>
            <li><a href="https://eatplt02.et.tu-dresden.de/intrawiki/doku.php?id=wiki:documentation:aof:start">Information on the AOF in the PLT Wiki</a></li>
        </ul> -->
        <ul>

        % for lv1 in structure :
            <li>${lv1['name']}
                % if lv1['children']!=None :
                    <ul>
                        % for lv2 in lv1['children']:
                            <li>${lv2['name']}
                            % if lv2['children']!=None :
                                <ul>
                                    % for lv3 in lv2['children']:
                                        <li>${lv3['name']}
                                            % if lv3['children']!=None :
                                                <span>...</span>
                                            % elif lv3['resources'] != None:
                                                &#8594;
                                                % for res in lv3['resources']:

                                                    <%
                                                        if res != "HTML":
                                                            target='target="_blank"'
                                                        else:
                                                            target=""
                                                    %>
                                                    <a href="${lv3['resources'][res]}" ${target}>${res}</a>
                                                % endfor
                                            % endif
                                        </li>
                                    % endfor
                                </ul>
                            % elif lv2['resources'] != None:
                                &#8594;
                                % for res in lv2['resources']:
                                    <%
                                                        if res != "HTML":
                                                            target='target="_blank"'
                                                        else:
                                                          target=""
                                    %>
                                    <a href="${lv2['resources'][res]}" ${target}>${res}</a>
                                % endfor
                            % endif
                            </li>
                        % endfor
                    </ul>
                % elif lv1['resources'] != None:
                    &#8594;
                    % for res in lv1['resources']:
                        <%
                                                        if res != "HTML":
                                                            target='target="_blank"'
                                                        else:
                                                          target=""
                        %>
                        <a href="${lv1['resources'][res]}" ${target}>${res}</a>
                    % endfor
                % endif
            </li>
        % endfor
        </ul>
    </div>
</div>
<%block name="local_js">
</%block>