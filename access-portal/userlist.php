<?php

if ($_REQUEST['format'] ?? '') {
  if ($_REQUEST['format'] === "queries") {
    $format = "queries";
  } else {
    $format = "html";
  }
} else {
  $formt = "html";
}

// For some reason when Python is invoked through PHP, it runs into Unicode
// encoding issues when trying to print (because it defaults to some
// ASCII-only encoding). So we have to force it to use UTF-8 here.
$command = "PYTHONIOENCODING=utf-8 ../userlist.py " . escapeshellarg($format);

$output = shell_exec($command);

echo $output;
