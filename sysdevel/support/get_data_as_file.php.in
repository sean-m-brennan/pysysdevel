<?php
// Download POSTed data string as a file.

if (php_sapi_name() === 'cli') {
  $input = getopt("", array("filename:", "data:",));
}
else {
  $input =& $_REQUEST;
}

$file_path = pathinfo($input["filename"])
$file_name = $file_path["basename"]
$file_ext = $file_path["extension"]

if ($file_ext == 'zip') {
  header('Content-Type: application/zip');
} else if ($file_ext == 'json') {
  header('Content-Type: application/json');
} else {
  header('Content-Type: application/octet-stream');
}
header('Content-Disposition: attachment; filename=' . $file_name);
header('Pragma: public');
header('Expires: -1');
header("Cache-Control: must-revalidate, post-check=0, pre-check=0");
header('Content-Length: ' . strlen($input["data"]);
ob_clean();
flush();
echo $input["data"];
exit;

?>
