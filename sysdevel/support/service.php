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
// Replacement for WebSockets
// Given 'cmd=parameters',
//   where cmd is 'list-steps', 'last_step', or 'stepN' with N a step number,
//   and parameters is json encoded.
// Outputs json encoded results of query for step N.

$MAX_STEPS = @@{NUM_SERVICE_STEPS};
$SERVICE = "@@{SERVICE_SCRIPT}";

$sep = $DIRECTORY_SEPARATOR;
$DISTRIB_PATH = '.' . $sep . 'bin';  //FIXME

$steps = array("list_steps", "last_step",);
foreach (range(1, $MAX_STEPS) as $number) {
  $steps[] = "step" . $number;
}

if (php_sapi_name() === 'cli') {
  $input = getopt("", $steps);
}
else {
  $input =& $_REQUEST;
}

$service_path = pathinfo($SERVICE);
$service_ext = $service_path["extension"];

if (!file_exists($DISTRIB_PATH . $sep . $SERVICE)) {
  header('HTTP/1.1 500 Internal Server Error');
  echo '<b>IMPACT Python service not properly set up:</b><br/>';
  echo '<pre>    Looking for service in "' . $DISTRIB_PATH . '".</pre>';
  echo '<pre>    Using PYTHONPATH "' . $_ENV['PYTHONPATH'] . '".</pre>';
  echo '<pre>    Given parameters:  </pre>';
  foreach ($input as $k => $p) {
    echo '<pre>        ' . $k . ' = ' . $p . '</pre>';
  }
  exit;
}

$args = '';
$step_method = '';
// Only run the first listed step
foreach ($steps as $step) {
  if (isset($input[$step])) {
    $step_method = strtoupper($step)
    $args = $input[$step];
    break;
  }
}

if ($args == '' || $step_method == '') {
  header('HTTP/1.1 400 Bad Request');
  echo '<b>IMPACT Python service not given correct arguments:</b><br/>';
  echo '<pre>    Given parameters:  </pre>';
  foreach ($input as $k => $p) {
    echo '<pre>        ' . $k . ' = ' . $p . '</pre>';
  }
  exit;
}

header('HTTP/1.1 200 Ok');
if ($service_ext == 'py') {
  echo exec('python ' . $DISTRIB_PATH . $sep . $SERVICE .
	    ' --web ' . $step_method . ' ' . $args);
} else if ($service_ext == 'sh' || $service_ext == 'bat') {
  echo exec($DISTRIB_PATH . $sep . $SERVICE .
	    ' --web ' . $step_method . ' ' . $args);
}
exit;

?>
