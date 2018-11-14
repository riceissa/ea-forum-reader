<?php

if ($_REQUEST['id'] ?? '') {
  $post_id = $_REQUEST['id'];
  $post_id = preg_replace('/[^a-zA-Z0-9_-]/', '', $post_id);

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
  $command = "PYTHONIOENCODING=utf-8 ../posts.py " . escapeshellarg($post_id) . " " . escapeshellarg($format);

  $output = shell_exec($command);

  echo $output;
} else {
  echo 'Please enter a post ID as the "id" parameter in the URL.';
}
