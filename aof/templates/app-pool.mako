# -*- coding: utf-8 -*-
<%inherit file="new_layout.mako"/>
<%block name="top_bar_actions">
    <li class="has-form">
        <div class="row collapse">
                <input id="livefilter-input" type="text" placeholder="Filter">
        </div>
    </li>
    <li class="divider"></li>
    <li class="action"><a href="#" id="action_update">UPDATE</a></li>
</%block>

<div class="row" id="app_tables"></div>

<%block name="local_js">
<script src="static/js/jquery.liveFilter.js"></script>
<script src="static/js/app-pool.js"></script>
</%block>