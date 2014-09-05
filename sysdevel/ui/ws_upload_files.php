<?php
/***************************************************************************
 * 
 * This material was prepared by the Los Alamos National Security, LLC 
 * (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
 * Energy (DOE). All rights in the material are reserved by DOE on behalf 
 * of the Government and LANS pursuant to the contract. You are authorized 
 * to use the material for Government purposes but it is not to be released 
 * or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
 * STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
 * ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
 * ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
 * COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
 * PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
 * PRIVATELY OWNED RIGHTS.
 * 
 ***************************************************************************/
// Replacement for WebSockets (proxy through php)

error_reporting(E_ALL);
ini_set('display_errors', '1');

function reArrayFiles(&$file_post) {
  $file_ary = array();
  $file_count = count($file_post['name']);
  $file_keys = array_keys($file_post);

  for ($i=0; $i<$file_count; $i++) {
    foreach ($file_keys as $key) {
      $file_ary[$i][$key] = $file_post[$key][$i];
    }
  }

  return $file_ary;
}

$HOST = "@@{WEBSOCKET_SERVER}";
$PORT = "@@{WEBSOCKET_PORT}";
$ORIGIN = "@@{WEBSOCKET_ORIGIN}";
$SYSADMIN_EMAIL = "@@{WEB_ADMIN_EMAIL}";

// WARNING: resource defaults to the first configured alternate
$addtnl_res = explode(',', "@@{WEBSOCKET_ADD_RESOURCES")[0]);
$RESOURCE = "@@{WEBSOCKET_RESOURCE}";
if ($addtnl_res[0] != '') {
  $RESOURCE = implode('/', array("@@{WEBSOCKET_RESOURCE}", $addtnl_res));
}

if (strpos($HOST, "WEBSOCKET") !== FALSE) {
  $HOST = "localhost";
}
$HOST = str_replace('http://', '', $HOST);
$HOST = str_replace('https://', 'ssl://', $HOST);

if (strpos($PORT, "WEBSOCKET") !== FALSE) {
  $PORT = "9876";
}
if (strpos($ORIGIN, "WEBSOCKET") !== FALSE) {
  $ORIGIN = "localhost";
}
$have_email = TRUE;
if (strpos($SYSADMIN_EMAIL, "WEB_ADMIN") !== FALSE) {
  $have_email = FALSE;
}
$remote = TRUE;
if ($HOST == 'localhost' || $HOST == gethostname()) {
  $remote = FALSE;
}
if (isset($_POST['remote'])) {
  if (strtolower($_POST['remote']) == 'true') {
    $remote = TRUE;
  } else {
    $remote = FALSE;
  }
}
$prefix = "";
if (isset($_POST['prefix'])) {
  $prefix = $_POST['prefix'];
}
if (isset($_POST['resource'])) {
  $RESOURCE = $_POST['resource'];
}
if ($RESOURCE[0] != '/') {
  $RESOURCE = '/' . $RESOURCE;
}

$uploaded_files = array();
if (isset($_FILES['files']) && count($_FILES['files']) > 0) {
  $uploaded_files = reArrayFiles($_FILES['files']);
}


include 'websocketclient.php';

$client = FALSE;
if ($remote) {
  $client = new WebSocketClient();

  if (!$client->connect($HOST, $PORT, $RESOURCE, $ORIGIN)) {
    header('HTTP/1.1 503 Service Unavailable');
    echo '<strong>WebSocket service not running on ' .
      $HOST . ':' . $PORT .  '.</strong><br/>';
    if ($have_email) {
      echo 'Contact the system administrator: <a href="mailto:' .
           $SYSADMIN_EMAIL . '" target="_top">' . $SYSADMIN_EMAIL . '</a><br/>';
    }
    echo '<br/>Error: ' . $client->error . '<br/>';
    exit;
  }

  if (!$client->checkConnection()) {
    header('HTTP/1.1 503 Service Unavailable');
    echo '<strong>WebSocket service on ' .
      $HOST . ':' . $PORT . ' failed.</strong><br/>';
    if ($have_email) {
      echo 'Contact the system administrator: <a href="mailto:' .
           $SYSADMIN_EMAIL . '" target="_top">' . $SYSADMIN_EMAIL . '</a><br/>';
    }
    echo '<br/>Error: ' . $client->error . '<br/>';
    exit;
  }
}

foreach ($uploaded_files as $file) {
  if ($file['error'] !== 0) {
    header('HTTP/1.1 500 Internal Server Error');
    echo 'File upload for "' . $file['name'] . '" failed. Retry.';
    exit;
  }
  
  if ($client && $remote) {
    if (!$client->sendData('filename=' . $prefix . $file['name'])) {
      header('HTTP/1.1 500 Internal Server Error');
      echo 'Filename transfer failed.';
      echo '<br/>Error: ' . $client->error . '<br/>';
      exit;
    }

    $contents = file_get_contents($file['tmp_name']);
    if (!$client->sendData($contents)) {
      header('HTTP/1.1 500 Internal Server Error');
      echo 'File transfer failed.';
      echo '<br/>Error: ' . $client->error . '<br/>';
      exit;
    }
  }
  else {  // WS server is localhost
    $dir = sys_get_temp_dir() . $RESOURCE;
    if ($dir[-1] != '/') {
      $dir .= '/';
    }
    move_uploaded_file($file['tmp_name'], $dir . $prefix . $file['name']);
  }
}

if ($client && $remote) {
  $client->disconnect();
}
echo 'Files transferred successfully.';
exit;

?>
