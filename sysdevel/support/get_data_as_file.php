<?php
//**************************************************************************
// 
// This material was prepared by the Los Alamos National Security, LLC 
// (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
// Energy (DOE). All rights in the material are reserved by DOE on behalf 
// of the Government and LANS pursuant to the contract. You are authorized 
// to use the material for Government purposes but it is not to be released 
// or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
// STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
// ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
// ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
// COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
// PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
// PRIVATELY OWNED RIGHTS.
// 
//**************************************************************************
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
