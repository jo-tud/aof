<!DOCTYPE html>
<html lang="${request.locale_name}">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="${meta['appname']}:${page_title}">
    <meta name="author" content="Johannes Pfeffer">

    <link rel="shortcut icon" href="${request.static_url('aof:static/img/favicon.png')}">

    <title>${meta['appname']}:${page_title}</title>

    <!-- Bootstrap core CSS -->
    <link href="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">

    <!-- Main AOF style sheet -->
    <link href="${request.static_url('aof:static/theme.css')}" rel="stylesheet">

    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
    <script src="//oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
    <script src="//oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
</head>
<body>
    % if request.session.peek_flash():
    <div id="flash">
        <% flash = request.session.pop_flash() %>
            % for message in flash:
            ${message}<br />
            % endfor
    </div>
    % endif

  <div class="main" id="home">
      <div class="container">
        <div class="row">
          <div class="col-md-2">
            <a href="/"><img class="logo img-responsive" src="${request.static_url('aof:static/img/logo_aof.png')}" alt="Application Orchestration Framework logo"></a>
          </div>
          <div class="col-md-10">
            <div class="content">
              <h1> <span class="smaller">${meta['appname']}</span></h1>
              <p class="lead">Dashboard. </p>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-md-10">
            <div class="content">
              <p class="menu"><br /><br />
                  % if menu:
                    % for item in menu[:-1]:
                        <a href="${item['href']}">${item['title']}</a>&nbsp;|&nbsp;
                    % endfor
                      <a href="${menu[-1]['href']}">${menu[-1]['title']}</a>
                  %else:
                      There are no menu items
                  %endif
              </p>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="links">
            <ul>
              <li class="plt-logo"><a href="http://www.et.tu-dresden.de/ifa/index.php?id=plt"><img class="logo img-responsive" src="${request.static_url('aof:static/img/logo_plt.png')}" alt="Chair for Distributed Control Systems Engineering"></a></li>
            </ul>
          </div>
        </div>
      </div>
    </div>


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="//oss.maxcdn.com/libs/jquery/1.10.2/jquery.min.js"></script>
    <script src="//oss.maxcdn.com/libs/twitter-bootstrap/3.0.3/js/bootstrap.min.js"></script>
  </body>

</body>
</html>