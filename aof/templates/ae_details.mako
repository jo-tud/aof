# -*- coding: utf-8 -*-
<%inherit file="new_layout.mako"/>
<%block name="top_bar_actions"/>

<div class="row">
    <div class="small-12 columns">
        <h1>${ae_id}</h1>
        <table>
            <thead>
            <tr>
                <th width="200">Property</th>
                <th>Value</th>
            </tr>
            </thead>

            <tbody>
            <tr>
                <td>Path</td>
                <td>${ae_path}</td>
            </tr>

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

                %if ae_has_bpmn:
                    <tr>
                        <td>BPMN</td>
                        <td>
                            <a class="button" href="/app-ensembles/bpmn-js/${ae_id}">Show BPMN</a>
                        </td>
                    </tr>
                %endif

            </tbody>
        </table>
    </div>
</div>



<%block name="local_js">
    <script type="text/javascript">
        var ae_id = "${ae_id}";
    </script>
    <script src="/static/js/jquery.liveFilter.js"></script>
    <script src="/static/js/jquery.loader-0.3.js"></script>
    <script src="/static/js/ae_details.js"></script>
</%block>