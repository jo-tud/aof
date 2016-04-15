# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions">
    <li><a href="${ae_api_path}" id="action_update">INSTALL APP-ENSEMBLE</a></li>
</%block>

<div class="row">
  <div class="large-12 columns">
    <h1>${ae_uri}</h1>
  </div>
</div>

<div class="row">
  <div class="large-12 columns">
      <p>
          ${documentation.__str__()}
      </p>
      <h4>Apps in this Ensemble</h4>
      <p>
        % for app in ae_apps:
            % if not loop.last:
                <a href="${app['app_details_uri'].__str__()}">${app['name'].__str__()}</a> (${app['original_name'].__str__()}),
            % else:
                <a href="${app['app_details_uri'].__str__()}">${app['name'].__str__()}</a> (${app['original_name'].__str__()})
            % endif
        % endfor
      </p>
  </div>
    <style>

    .fixed_size { width: 130px; }

    </style>
  <div class="small-12 medium-12 columns">
      <h4>Actions</h4>
      <a class="small success button fixed_size" href="${bpmn_view_uri}">View </a>
      <a class="small warning button fixed_size" href="${bpmn_edit_uri}">Edit</a>
      <a class="small button fixed_size" href="${direct_download_uri}">Install</a>
  </div>
  <div class="small-12 medium-12 columns">
      <a class="small alert button fixed_size" id="delete-ae" href="${bpmn_delete_uri}">Delete</a>
  </div>
</div>

<div class="row">
% if qrcode != "None":
    <div class="small-9 columns">
% else :
    <div class="small-12 columns">
% endif

    % if qrcode != "None":
        <div class="medium-3 columns panel pagination-centered">
            <img src="${qrcode}" alt="${ae_uri}"/>
            <span class="secondary label"><a href="${direct_download_uri}">Download AppEnsemble</a></span>
        </div>
        % endif

    <%block name="local_js">
        <script type="text/javascript">
            var ae_uri = "${ae_uri}";
        </script>
        <script src="/static/js/jquery.liveFilter.js"></script>
        <script src="/static/js/jquery.loader-0.3.js"></script>
        <script src="/static/js/ae-details.js"></script>
    </%block>
    </div>
</div>