<?php

setcookie("humancheck", "is_human", time()+60*60*24*365*10, "", "", true, true);
if (count($_COOKIE) === 0) {
    http_response_code(201);
    echo <<<END
<html>
    <head>
        <meta http-equiv="refresh" content="1">
    </head>
    <body>
        <p>Verifying that you are a human...</p>
        <p>Please refresh the page to continue (if it does not automatically refresh).</p>
    </body>
</html>
END;
    die();
}

?>
