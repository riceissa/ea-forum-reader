<?php

if ($_REQUEST['id'] ?? '') {
  if (($_REQUEST['format'] ?? '') === "rss") {
    $format = "rss";
  } else {
    $format = "html";
  }
  $username = $_REQUEST['id'];
  $username = preg_replace('/[^a-zA-Z0-9_-]/', '', $username);

  // For some reason when Python is invoked through PHP, it runs into Unicode
  // encoding issues when trying to print (because it defaults to some
  // ASCII-only encoding). So we have to force it to use UTF-8 here.
  $command = "PYTHONIOENCODING=utf-8 ../userfeed.py " . escapeshellarg($username) . " " . $format;

  $output = shell_exec($command);

  echo $output;
} else {
  echo "<pre>";
  echo 'Please enter a username as the "id" parameter in the URL, and set format=rss or format=html.' . "\n";
  echo "For example, /users.php?id=vipulnaik&format=rss\n";
  echo "</pre>";
}
