# -*- coding: utf-8 -*-
<%inherit file="new_layout.mako"/>
<%block name="top_bar_actions">
    <li class="has-form show-for-medium-up">
        <div class="row collapse">
                <input class="livefilter-input" type="text" placeholder="Filter">
        </div>
    </li>
    <li class="divider"></li>
    <li><a href="#" id="action_update">UPDATE</a></li>
</%block>

<li class="has-form show-for-small-only">
    <div class="row collapse">
            <input class="livefilter-input" type="text" placeholder="Filter">
    </div>
</li>

<div class="row full-width" id="app_tables"></div>

<%block name="local_js">
<script src="static/js/jquery.liveFilter.js"></script>
<script src="static/js/jquery.loader-0.3.js"></script>
<script src="static/js/app-pool.js"></script>
</%block>