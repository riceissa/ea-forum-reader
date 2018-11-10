<?php

if ($_REQUEST['offset'] ?? '') {
  $offset = $_REQUEST['offset'];
  $offset = preg_replace('/[^0-9]/', '', $offset);
} else {
  $offset = "0";
}

// For some reason when Python is invoked through PHP, it runs into Unicode
// encoding issues when trying to print (because it defaults to some
// ASCII-only encoding). So we have to force it to use UTF-8 here.
$command = "PYTHONIOENCODING=utf-8 ../daily.py " . escapeshellarg($offset);

$output = shell_exec($command);

echo $output;
