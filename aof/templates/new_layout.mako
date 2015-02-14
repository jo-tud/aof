<!DOCTYPE html>
<html class="no-js" lang="en">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>${page_title}</title>
        <link rel="stylesheet" href="static/stylesheets/app.css" />
        <script src="static/bower_components/modernizr/modernizr.js"></script>
    </head>
    <body>
        <div class="sticky">
            <nav class="top-bar" data-topbar role="navigation">
                <ul class="title-area">
                    <li class="name">
                        <h1><a href="/">AOF</a></h1>
                    </li> <!-- Remove the class "menu-icon" to get rid of menu icon. Take out "Menu" to just have icon alone -->

                    <li class="toggle-topbar menu-icon">
                        <a href="#"><span>Menu</span></a>
                    </li>
                </ul>
                <section class="top-bar-section"> <!-- Right Nav Section -->
                    <ul class="left">
                        <li><a href="app-pool.html">App-Pool</a></li>
                        <li><a href="deploy.html">Deploy</a></li>
                        <li><a href="info.html">Info</a></li>
                    </ul>
                    <ul class="right">
                        <%block name="top_bar_actions" />
                    </ul>
                </section>
            </nav>
        </div>
        <div class="row" id="alerts"></div>

        ${next.body()}
        <%block name="global_js">
        <script src="static/bower_components/foundation/js/vendor/jquery.js"></script>
        <script src="static/bower_components/foundation/js/vendor/fastclick.js"></script>
        <script src="static/bower_components/foundation/js/foundation.min.js"></script>
        <script src="static/js/app.js"></script>
        </%block>
        <%block name="local_js" />





    </body>
</html>