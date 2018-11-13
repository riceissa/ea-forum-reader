<?php

if ($_REQUEST['offset'] ?? '') {
  $offset = $_REQUEST['offset'];
  $offset = intval(preg_replace('/[^0-9]/', '', $offset));
} else {
  $offset = "0";
}

if ($_REQUEST['view'] ?? '') {
  if ($_REQUEST['view'] === "top") {
    $view = "top";
  } else {
    $view = "new";
  }
} else {
  $view = "new";
}

if ($_REQUEST['before'] ?? '') {
  $before = $_REQUEST['before'];
  $before = preg_replace('/[^0-9a-zA-Z:-]/', '', $before);
} else {
  $before = "";
}

if ($_REQUEST['after'] ?? '') {
  $after = $_REQUEST['after'];
  $after = preg_replace('/[^0-9a-zA-Z:-]/', '', $after);
} else {
  $after = "";
}

// For some reason when Python is invoked through PHP, it runs into Unicode
// encoding issues when trying to print (because it defaults to some
// ASCII-only encoding). So we have to force it to use UTF-8 here.
$command = "PYTHONIOENCODING=utf-8 ../daily.py " . escapeshellarg($offset) . " " . escapeshellarg($view) . " " . escapeshellarg($before) . " " . escapeshellarg($after);

$output = shell_exec($command);

echo $output;
