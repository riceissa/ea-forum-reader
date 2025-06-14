<?php

include_once("cookiecheck.inc");

if ($_REQUEST['slug'] ?? '') {
  $tagslug = $_REQUEST['slug'];
  $tagslug = preg_replace('/[^a-zA-Z0-9_-]/', '', $tagslug);

  if ($_REQUEST['format'] ?? '') {
    if ($_REQUEST['format'] === "queries") {
      $format = "queries";
    } else {
      $format = "html";
    }
  } else {
    $format = "html";
  }
  // For some reason when Python is invoked through PHP, it runs into Unicode
  // encoding issues when trying to print (because it defaults to some
  // ASCII-only encoding). So we have to force it to use UTF-8 here.
  $command = "PYTHONIOENCODING=utf-8 ../tag.py " . escapeshellarg($tagslug) . " " . escapeshellarg($format);

  $output = shell_exec($command);

  echo $output;
} else {
  echo 'Please enter a tag slug as the "slug" parameter in the URL.';
}
