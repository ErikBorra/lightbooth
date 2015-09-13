<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
        <title>Lightbooth slideshow</title>
        <style type="text/css">
            body {
                margin: 0;
                padding: 0;
                background-color: #000;
            }
            img {
                margin: 0;
                padding: 0;
                border: 0;
            }
        </style>
    </head>
    <body>
        <center>
            <?php
            // get first image
            exec("ls instagram/*.jpg", $images);
            echo "<img src='{$images[0]}' id='lightbooth_img'></img>";
            ?>

        </center>

        <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js"></script>
        <script type="text/javascript">

            $('img').height($(window).height());

            var cur = $('#lightbooth_img');
            var images = [];
            var iterator = 0;
            var iterator_newpic = 0;
            var started = 0;

            function animate() {

                $.getJSON("getImages.php", function (result) {
                    $.each(result, function (i, field) {
                        if ($.inArray(field, images) == -1) {
                            images.push(field);
                            iterator_newpic = images.length - 1;
                        }
                    });
                    if (started == 0) {
                        started = 1;
                        iterator_newpic = 0;
                    }
                });

                //console.log(iterator, iterator_newpic, started);
                
                // if new image, display that one first, then continue with the rest
                if (iterator_newpic != 0) {
                    cur_image = images[iterator_newpic];
                    iterator_newpic = 0;
                } else {
                    cur_image = images[iterator];
                    iterator++;
                    if (iterator >= images.length)
                        iterator = 0;
                }

                cur.fadeOut(1000, function () {
                    cur.attr('src', cur_image);
                });
                cur.fadeIn(1000);

            }
            animate();
            $(function () {
                setInterval("animate()", 5000);
            });
        </script>
    </body>
</html>