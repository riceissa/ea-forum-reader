<?php

if ($_REQUEST['id'] ?? '') {
  $post_id = $_REQUEST['id'];
  $post_id = preg_replace('/[^a-zA-Z0-9_-]/', '', $post_id);

  $command = "PYTHONIOENCODING=utf-8 ../scrape.py " . escapeshellarg($post_id);
  $output = shell_exec($command);

  echo $output;
} else {
  echo 'Please enter a post ID as the "id" parameter in the URL.';
}
