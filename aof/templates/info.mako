# -*- coding: utf-8 -*-
<%inherit file="layout.mako"/>
    <link href="${request.static_url('aof:static/deploy.css')}" rel="stylesheet">

    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
    <script type="text/javascript">
        function init(){
            hell11.style.display = "none";
            hell12.style.display = "none";
            hell13.style.display = "none";
            hell14.style.display = "none";
            hell15.style.display = "none";
            hell21.style.display = "none";
            hell22.style.display = "none";
            hell23.style.display = "none";
            hell24.style.display = "none";
            hell25.style.display = "none";
            hell31.style.display = "none";
            hell32.style.display = "none";
            hell33.style.display = "none";
            hell34.style.display = "none";
            hell35.style.display = "none";
        }
        function hell_11(){
            hell11.style.display = "inline-block";
            hell12.style.display = "none";
            hell13.style.display = "none";
            hell14.style.display = "none";
            hell15.style.display = "none";
        }
        function hell_12(){
            hell11.style.display = "inline-block";
            hell12.style.display = "inline-block";
            hell13.style.display = "none";
            hell14.style.display = "none";
            hell15.style.display = "none";
        }
        function hell_13(){
            hell11.style.display = "inline-block";
            hell12.style.display = "inline-block";
            hell13.style.display = "inline-block";
            hell14.style.display = "none";
            hell15.style.display = "none";
        }
        function hell_14(){
            hell11.style.display = "inline-block";
            hell12.style.display = "inline-block";
            hell13.style.display = "inline-block";
            hell14.style.display = "inline-block";
            hell15.style.display = "none";
        }
        function hell_15(){
            hell11.style.display = "inline-block";
            hell12.style.display = "inline-block";
            hell13.style.display = "inline-block";
            hell14.style.display = "inline-block";
            hell15.style.display = "inline-block";
        }
        function hell_21(){
            hell21.style.display = "inline-block";
            hell22.style.display = "none";
            hell23.style.display = "none";
            hell24.style.display = "none";
            hell25.style.display = "none";
        }
        function hell_22(){
            hell21.style.display = "inline-block";
            hell22.style.display = "inline-block";
            hell23.style.display = "none";
            hell24.style.display = "none";
            hell25.style.display = "none";
        }
        function hell_23(){
            hell21.style.display = "inline-block";
            hell22.style.display = "inline-block";
            hell23.style.display = "inline-block";
            hell24.style.display = "none";
            hell25.style.display = "none";
        }
        function hell_24(){
            hell21.style.display = "inline-block";
            hell22.style.display = "inline-block";
            hell23.style.display = "inline-block";
            hell24.style.display = "inline-block";
            hell25.style.display = "none";
        }
        function hell_25(){
            hell21.style.display = "inline-block";
            hell22.style.display = "inline-block";
            hell23.style.display = "inline-block";
            hell24.style.display = "inline-block";
            hell25.style.display = "inline-block";
        }
        function hell_31(){
            hell31.style.display = "inline-block";
            hell32.style.display = "none";
            hell33.style.display = "none";
            hell34.style.display = "none";
            hell35.style.display = "none";
        }
        function hell_32(){
            hell31.style.display = "inline-block";
            hell32.style.display = "inline-block";
            hell33.style.display = "none";
            hell34.style.display = "none";
            hell35.style.display = "none";
        }
        function hell_33(){
            hell31.style.display = "inline-block";
            hell32.style.display = "inline-block";
            hell33.style.display = "inline-block";
            hell34.style.display = "none";
            hell35.style.display = "none";
        }
        function hell_34(){
            hell31.style.display = "inline-block";
            hell32.style.display = "inline-block";
            hell33.style.display = "inline-block";
            hell34.style.display = "inline-block";
            hell35.style.display = "none";
        }
        function hell_35(){
            hell31.style.display = "inline-block";
            hell32.style.display = "inline-block";
            hell33.style.display = "inline-block";
            hell34.style.display = "inline-block";
            hell35.style.display = "inline-block";
        }
    </script>

    <body onload="init()">
      <p class="lead">Information.</p>
      <div class="content" id="content_info">
        <div class="info">
          Information
        </div>
        <div class="bewerten_bewerten">
            <div class="bewerten_frage">1.Frage: Wie zufrieden Sind Sie mit der Applikation?</div>
            <div class="bewerten_sterne_line">
                <div class="star_bewerten" onclick="hell_11()">
                    <div class="star_hell" id="hell11" onclick="hell_11()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_12()">
                    <div class="star_hell" id="hell12" onclick="hell_12()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_13()">
                    <div class="star_hell" id="hell13" onclick="hell_13()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_14()">
                    <div class="star_hell" id="hell14" onclick="hell_14()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_15()">
                    <div class="star_hell" id="hell15" onclick="hell_15()"></div>
                </div>
            </div>
            <div class="bewerten_frage">2.Frage: Wie zufrieden Sie mit dem Apps-Orchestration?</div>
            <div class="bewerten_sterne_line">
                <div class="star_bewerten" onclick="hell_21()">
                    <div class="star_hell" id="hell21" onclick="hell_21()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_22()">
                    <div class="star_hell" id="hell22" onclick="hell_22()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_23()">
                    <div class="star_hell" id="hell23" onclick="hell_23()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_24()">
                    <div class="star_hell" id="hell24" onclick="hell_24()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_25()">
                    <div class="star_hell" id="hell25" onclick="hell_25()"></div>
                </div>
            </div>
            <div class="bewerten_frage">3.Frage: Wie zufrieden Sie mit Comvantage?</div>
            <div class="bewerten_sterne_line">
                <div class="star_bewerten" onclick="hell_31()">
                    <div class="star_hell" id="hell31" onclick="hell_31()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_32()">
                    <div class="star_hell" id="hell32" onclick="hell_32()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_33()">
                    <div class="star_hell" id="hell33" onclick="hell_33()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_34()">
                    <div class="star_hell" id="hell34" onclick="hell_34()"></div>
                </div>
                <div class="star_bewerten" onclick="hell_35()">
                    <div class="star_hell" id="hell35" onclick="hell_35()"></div>
                </div>
            </div>
            <div class="bewerten_frage_comment">Bitte schreiben Sie Ihre Rezension</div>
        </div>
      </div>
    </body>