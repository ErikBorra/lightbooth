<?php

exec("ls instagram/*.jpg",$images);
print json_encode($images);

?>