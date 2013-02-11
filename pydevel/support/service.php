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

$PYTHON_PATH = ''; //FIXME set PYTHONPATH
$MODULE_PATH = '.'; //FIXME set path to impact_query.py

if (php_sapi_name() === 'cli') {
  $input = getopt("", array("init",
			    "param:", //required
			    "param2::", //optional
			    )); // FIXME list parameters
}
else {
  $input =& $_REQUEST;
}

if (isset($input["init"])) {
  // get_available_satellites
  header('HTTP/1.1 200 Ok');
  if (file_exists($MODULE_PATH . '/impact_query.py')) {
    echo exec('python ' . $MODULE_PATH . '/impact_query.py --init');
  }
  else {  // default list
    echo json_encode(array(array(26405,'CHAMP'), array(27391,'Grace A'),
			   array(27392,'Grace B'), array(24946,'Iridium 33'),
			   array(22675,'Cosmos 2251')));
  }
  exit(0);
}

if (!file_exists($MODULE_PATH . '/impact_query.py')) {
  header('HTTP/1.1 500 Internal Server Error');
  echo '<b>IMPACT Python service not properly set up:</b><br/>';
  echo '<pre>    Looking for modules in "' . $MODULE_PATH . '".</pre>';
  echo '<pre>    Using PYTHONPATH "' . $PYTHON_PATH . '".</pre>';
  echo '<pre>    Given parameters:  </pre>';
  foreach ($input as $k => $p) {
    echo '<pre>        ' . $k . ' = ' . $p . '</pre>';
  }
  exit(1);
}

$args = '';
$errors = array();
//FIXME parse/compile parameters, eg.

// required parameters
if (isset($input["file"])) {
  $args .= " --file=" . $input["file"];
}
else {
  array_push($errors, "No filename given.");
}

// optional parameters
if (isset($input["opt"])) {
  $args = $args . " --opt=" . $input["opt"];
}

if (count($errors) > 0) {
  header('HTTP/1.1 500 Internal Server Error');
  echo '<b>IMPACT parameter errors:</b><br/>';
  foreach ($errors as $e) {
    echo '<pre>    ' . $e . '</pre>';
  }
  exit(1);
}

header('HTTP/1.1 200 Ok');
echo exec('python ' . $MODULE_PATH . '/impact_query.py --web ' . $args);

?>
