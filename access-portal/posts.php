<?php

if ($_REQUEST['id'] ?? '') {
  $post_id = $_REQUEST['id'];
  $post_id = preg_replace('/[^a-zA-Z0-9_-]/', '', $post_id);
  ob_start();

  echo shell_exec("../scrape.py " . escapeshellarg($post_id));

  ob_end_flush();
} else {
  echo 'Please enter a post ID as the "id" parameter in the URL.';
}
