<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

/**
 * Very basic websocket client.
 * Supporting draft hybi-10. 
 * 
 * @author Simon Samtleben <web@lemmingzshadow.net>
 * @version 2011-10-18
 *
 * https://github.com/lemmingzshadow/php-websocket
 */

class WebSocketClient {
  private $_host;
  private $_port;
  private $_path;
  private $_origin;
  private $_Socket = null;
  private $_connected = false;

  public $error = '';
	
  public function __construct() { }
	
  public function __destruct() {
    $this->disconnect();
  }

  public function sendData($data, $type = 'text', $masked = true) {
    if ($this->_connected === false) {
      $this->error = "WS - Not connected";
      return false;
    }
    if (empty($data)) {
      $this->error = "WS send - No data given";
      return false;
    }
    $encoded_data = $this->_hybi10Encode($data, $type, $masked);
    $written = 0;
    while (strlen($encoded_data) > $written) {
      $count = fwrite($this->_Socket, $encoded_data);
      if ($count === 0 || $count === false) {
	$this->error = 'WS send - ' . $this->get_socket_error();
	return false;
      }
      $written += $count;
    }
    fflush($this->_Socket);
    return true;
  }

  public function receiveData() {
    $response= '';
    $buffer = true;
    $response = '';
    $len = 0;
    $final = 0;
    while ($final === 0) {
      $response .= fread($this->_Socket, 2);
      if (empty($response)) {
	$this->error = 'WS recv frame - ' . $this->get_socket_error();
	return false;
      }
      $final = ord($response[0]) >> 7; // first bit
      $masked = ord($response[1]) >> 7; // first bit
      $len = ord($response[1]) & 7; // all but first bit
      if ($len === 126) {
	$response .= fread($this->_Socket, 2);
	if (empty($response)) {
	  $this->error = 'WS recv frame len - ' . $this->get_socket_error();
	  return false;
	}
	$len = bindec(sprintf('%08b', ord($response[2])) .
		      sprintf('%08b', ord($response[3])));
      }
      elseif ($len === 127) {
	$response .= fread($this->_Socket, 8);
	if (empty($response)) {
	  $this->error = 'WS recv frame len - ' . $this->get_socket_error();
	  return false;
	}
	$tmp = '';
	for ($i = 0; $i < 8; $i++) {
	  $tmp .= sprintf('%08b', ord($response[$i+2]));
	}
	$len = bindec($tmp);
      }
      if ($masked) {
        $len += 4;
      }
      $response .= fread($this->_Socket, $len);
      if (empty($response)) {
	$this->error = 'WS recv - ' . $this->get_socket_error();
	return false;
      }
    }

    return $this->_hybi10Decode($response);
  }

  public function get_socket_error() {
    $sock = socket_import_stream($this->_Socket);
    return socket_strerror(socket_last_error($sock));
  }

  public function connect($host, $port, $path, $origin = false) {
    $this->_host = $host;
    $this->_port = $port;
    $this->_path = $path;
    $this->_origin = $origin;
		
    $key = base64_encode($this->_generateRandomString(16, false, true));
    $magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11';

    $header = "GET " . $path . " HTTP/1.1\r\n";
    $header.= "Host: ".$host.":".$port."\r\n";
    $header.= "Upgrade: websocket\r\n";
    $header.= "Connection: Upgrade\r\n";
    $header.= "Sec-WebSocket-Key: " . $key . "\r\n";
    if ($origin !== false) {
      $header.= "Sec-WebSocket-Origin: " . $origin . "\r\n";
    }
    $header.= "Sec-WebSocket-Version: 13\r\n\r\n";			

    //$this->_Socket = fsockopen($host, $port, $errno, $errstr, 5);
    $this->_Socket = stream_socket_client("$host:$port", $errno, $errstr, 5);
    if ($this->_Socket === false || $errno !== 0) {
      $this->_connected = false;
      $this->error = 'WS opening connection - ' . $errstr;
      return $this->_connected;
      }
    socket_set_timeout($this->_Socket, 0, 300);
    fwrite($this->_Socket, $header);
    $response = '';
    while (!feof($this->_Socket)) {
      $response .= fread($this->_Socket, 1);
      if (substr($response, -4) == '\r\n\r\n') {
    	break;
      }
    }
    if (empty($response)) {
      $this->_connected = false;
      $this->error = 'WS handshake - ' . $this->get_socket_error();
      return $this->_connected;	
    }

    preg_match('#Sec-WebSocket-Accept:\s(.*)$#mU', $response, $matches);
    $keyAccept = trim($matches[1]);
    $expectedResponse = base64_encode(pack('H*', sha1($key . $magic_string)));

    $this->_connected = ($keyAccept === $expectedResponse) ? true : false;
    sleep(1);
    return $this->_connected;	
  }
	
  public function checkConnection()
  {
    $this->_connected = false;
		
    // send ping:
    $data = 'ping?';
    if (!fwrite($this->_Socket, $this->_hybi10Encode($data, 'ping', true))) {
      $this->error = 'WS send ping - ' . $this->get_socket_error();
      return false;
    }
    $response = $this->receiveData();
    if (!$response) {
      $this->error = 'WS recv pong - ' . $this->get_socket_error();
      return false;
    }
    if (!is_array($response)) {			
      $this->error = "WS - Invalid pong decoding";
      return false;
    }
    if (!isset($response['type']) || $response['type'] !== 'pong') {
      $this->error = "WS - Bad pong response";
      return false;
    }
    $this->_connected = true;
    return true;
  }


  public function disconnect() {
    $this->_connected = false;
    if ($this->_Socket)
      fclose($this->_Socket);
  }
	
  public function reconnect() {
    sleep(10);
    $this->_connected = false;
    fclose($this->_Socket);
    $this->connect($this->_host, $this->_port, $this->_path, $this->_origin);
  }

  private function _generateRandomString($length = 10, $addSpaces = true, $addNumbers = true) {  
    $characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"§$%&/()=[]{}';
    $useChars = array();
    // select some random chars:    
    for ($i = 0; $i < $length; $i++) {
      $useChars[] = $characters[mt_rand(0, strlen($characters)-1)];
    }
    // add spaces and numbers:
    if ($addSpaces === true) {
      array_push($useChars, ' ', ' ', ' ', ' ', ' ', ' ');
    }
    if ($addNumbers === true) {
      array_push($useChars, rand(0,9), rand(0,9), rand(0,9));
    }
    shuffle($useChars);
    $randomString = trim(implode('', $useChars));
    $randomString = substr($randomString, 0, $length);
    return $randomString;
  }
	
  private function _hybi10Encode($payload, $type = 'text', $masked = true) {
    $frameHead = array();
    $frame = '';
    $payloadLength = strlen($payload);
		
    switch($type) {		
    case 'text':
      // first byte indicates FIN, Text-Frame (10000001):
      $frameHead[0] = 129;				
      break;			
      
    case 'binary':
      // first byte indicates FIN, Text-Frame (10000010):
      $frameHead[0] = 130;				
      break;			
      
    case 'close':
      // first byte indicates FIN, Close Frame(10001000):
      $frameHead[0] = 136;
      break;
      
    case 'ping':
      // first byte indicates FIN, Ping frame (10001001):
      $frameHead[0] = 137;
      break;
      
    case 'pong':
      // first byte indicates FIN, Pong frame (10001010):
      $frameHead[0] = 138;
      break;
    }
		
    // set mask and payload length (using 1, 3 or 9 bytes) 
    if ($payloadLength > 65535)	{
      $payloadLengthBin = str_split(sprintf('%064b', $payloadLength), 8);
      $frameHead[1] = ($masked === true) ? 255 : 127;
      for ($i = 0; $i < 8; $i++) {
	$frameHead[$i+2] = bindec($payloadLengthBin[$i]);
      }
      // most significant bit MUST be 0 (close connection if frame too big)
      if ($frameHead[2] > 127) {
	$this->close(1004);
	return false;
      }
    }
    elseif ($payloadLength > 125) {
      $payloadLengthBin = str_split(sprintf('%016b', $payloadLength), 8);
      $frameHead[1] = ($masked === true) ? 254 : 126;
      $frameHead[2] = bindec($payloadLengthBin[0]);
      $frameHead[3] = bindec($payloadLengthBin[1]);
    }
    else {
      $frameHead[1] = ($masked === true) ? $payloadLength + 128 : $payloadLength;
    }

    // convert frame-head to string:
    foreach (array_keys($frameHead) as $i) {
      $frameHead[$i] = chr($frameHead[$i]);
    }
    if ($masked === true) {
      // generate a random mask:
      $mask = array();
      for ($i = 0; $i < 4; $i++) {
	$mask[$i] = chr(rand(0, 255));
      }
			
      $frameHead = array_merge($frameHead, $mask);			
    }						
    $frame = implode('', $frameHead);

    // append payload to frame:
    $framePayload = array();	
    for ($i = 0; $i < $payloadLength; $i++) {		
      $frame .= ($masked === true) ? $payload[$i] ^ $mask[$i % 4] : $payload[$i];
    }

    return $frame;
  }
	
  private function _hybi10Decode($data)	{
    if (!$data)
      return false;

    $payloadLength = '';
    $mask = '';
    $unmaskedPayload = '';
    $decodedData = array();
		
    // estimate frame type:
    $firstByteBinary = sprintf('%08b', ord($data[0]));		
    $secondByteBinary = sprintf('%08b', ord($data[1]));
    $opcode = bindec(substr($firstByteBinary, 4, 4));
    $isMasked = ($secondByteBinary[0] == '1') ? true : false;
    $payloadLength = ord($data[1]) & 127;		
		
    switch($opcode) {
      // text frame:
    case 1:
      $decodedData['type'] = 'text';
      break;
		
    case 2:
      $decodedData['type'] = 'binary';
      break;
			
      // connection close frame:
    case 8:
      $decodedData['type'] = 'close';
      break;
			
      // ping frame:
    case 9:
      $decodedData['type'] = 'ping';				
      break;
			
      // pong frame:
    case 10:
      $decodedData['type'] = 'pong';
      break;
			
    default:
      return false;
      break;
    }
		
    if ($payloadLength === 126) {
      $mask = substr($data, 4, 4);
      $payloadOffset = 8;
      $dataLength = bindec(sprintf('%08b', ord($data[2])) . sprintf('%08b', ord($data[3]))) + $payloadOffset;
    }
    elseif ($payloadLength === 127) {
      $mask = substr($data, 10, 4);
      $payloadOffset = 14;
      $tmp = '';
      for ($i = 0; $i < 8; $i++) {
	$tmp .= sprintf('%08b', ord($data[$i+2]));
      }
      $dataLength = bindec($tmp) + $payloadOffset;
      unset($tmp);
    }
    else {
      $mask = substr($data, 2, 4);	
      $payloadOffset = 6;
      $dataLength = $payloadLength + $payloadOffset;
    }	
		
    if ($isMasked === true) {
      for ($i = $payloadOffset; $i < $dataLength; $i++)	{
	$j = $i - $payloadOffset;
	if (isset($data[$i])) {
	  $unmaskedPayload .= $data[$i] ^ $mask[$j % 4];
	}
      }
      $decodedData['payload'] = $unmaskedPayload;
    }
    else {
      $payloadOffset = $payloadOffset - 4;
      $decodedData['payload'] = substr($data, $payloadOffset);
    }
    
    return $decodedData;
  }
}

?>
