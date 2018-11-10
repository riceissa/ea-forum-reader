<?php

if (($_REQUEST['id'] ?? '') && ($_REQUEST['format'] ?? '') === "rss") {
  $username = $_REQUEST['id'];
  $username = preg_replace('/[^a-zA-Z0-9_-]/', '', $post_id);

  // For some reason when Python is invoked through PHP, it runs into Unicode
  // encoding issues when trying to print (because it defaults to some
  // ASCII-only encoding). So we have to force it to use UTF-8 here.
  $command = "PYTHONIOENCODING=utf-8 ../userfeed.py " . escapeshellarg($post_id);

  $output = shell_exec($command);

  echo $output;
} else {
  echo 'Please enter a post ID as the "id" parameter in the URL.';
}
