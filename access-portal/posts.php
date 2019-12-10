<?php

if ($_REQUEST['commentId'] ?? '') {
  // Not a very satisfying fix. This redirect works, but it removes the post
  // title (if a title was present in the URL). For instance,
  // /posts/7cAsBPGh98pGyrhz9/decoupling-vs-contextualising-norms?commentId=EuYu7C7sfqyWcQtue
  // becomes /posts.php?id=7cAsBPGh98pGyrhz9#EuYu7C7sfqyWcQtue
  // Ideally, the redirect would remove just the "commentId" part, converting
  // it to an anchor, without touching anything else in the URL.
  header('Location: /posts.php?id=' . ($_REQUEST['id'] ?? '') . '#' . $_REQUEST['commentId']);
  exit;
}

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
