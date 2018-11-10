<?php

if ($_REQUEST['q'] ?? '') {
  $query = $_REQUEST['q'];
  $query = preg_replace('/[^a-zA-Z0-9_" -]/', '', $query);

  $command = "PYTHONIOENCODING=utf-8 ../search.py " . "../algolia_url.txt " . escapeshellarg($query);

  $output = shell_exec($command);
  echo $output;
} else {
  echo '<pre>Please enter your search term as the parameter "q" in the URL.</pre>';
}

