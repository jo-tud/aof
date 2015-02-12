# -*- coding: utf-8 -*-
<%inherit file="new_layout.mako"/>
<%block name="top_bar_actions">
    <li class="divider"></li>
    <li class="action"><a href="#" id="action_update">UPDATE</a></li>
</%block>

<div class="row" id="app_tables">
  <div class="small-12 large-3 columns">
      Apps
  </div>

</div>

<%block name="local_js">
<script src="static/js/app-pool.js"></script>
</%block>