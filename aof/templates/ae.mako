# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
<%block name="top_bar_actions">
    <li class="has-form show-for-medium-up">
        <div class="row collapse">
                <input class="livefilter-input" type="text" placeholder="Filter">
        </div>
    </li>
    <li class="divider"></li>
    <li><a href="#" id="action_update">UPDATE POOL</a></li>
    <li><a href="app-ensembles/create.html" id="action_update">CREATE APPENSEMBLE</a></li>
</%block>

<div class="row">
    <div class="small-12 columns">
        <li class="has-form show-for-small-only">
            <input class="livefilter-input" type="text" placeholder="Filter">
        </li>
    </div>
</div>

<div class="row" id="ae_tables" data-equalizer></div>

<%block name="local_js">
<script src="static/js/jquery.liveFilter.js"></script>
<script src="static/js/jquery.loader-0.3.js"></script>
<script src="static/js/ae.js"></script>
</%block>