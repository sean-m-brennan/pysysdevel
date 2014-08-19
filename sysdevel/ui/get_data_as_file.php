<?php
/*
 * Copyright 2013.  Los Alamos National Security, LLC.
 * This material was produced under U.S. Government contract
 * DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which
 * is operated by Los Alamos National Security, LLC for the
 * U.S. Department of Energy. The U.S. Government has rights to use,
 * reproduce, and distribute this software.  NEITHER THE GOVERNMENT
 * NOR LOS ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS
 * OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.
 * If software is modified to produce derivative works, such modified
 * software should be clearly marked, so as not to confuse it with the
 * version available from LANL.
 * 
 * Licensed under the Mozilla Public License, Version 2.0 (the
 * "License"); you may not use this file except in compliance with the
 * License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/2.0/
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
 * implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */

// Download POSTed data string as a file.

ini_set('display_errors', 1);
error_reporting(E_ALL);

if (php_sapi_name() === 'cli') {
  $input = getopt("", array("filename:", "data:",));
}
else {
  $input =& $_REQUEST;
}

$file_path = pathinfo($input["filename"]);
$file_name = $file_path["basename"];
$file_ext = $file_path["extension"];

header("Content-Description: File Transfer"); 
if ($file_ext == 'zip') {
  header('Content-Type: application/zip');
} else if ($file_ext == 'json') {
  header('Content-Type: application/json');
} else if ($file_ext == 'pdf') {
  header('Content-Type: application/pdf');
} else {
  header('Content-Type: application/octet-stream');
}
header('Content-Disposition: attachment; filename="' . $file_name. '"');
header('Pragma: public');
header('Expires: -1');
header("Cache-Control: must-revalidate, post-check=0, pre-check=0");
//header("Cache-Control: private", false);
header('Content-Length: ' . strlen($input["data"]));
flush();
echo $input["data"];
exit;

?>
