<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);


class SocketClient {
  private $_host;
  private $_port;
  private $_Socket = null;
  private $_connected = false;

  public $error = '';
	
  public function __construct() { }
	
  public function __destruct() {
    $this->disconnect();
  }

  public function sendData($data, $len) {
    if ($this->_connected === false) {
      $this->error = "WS - Not connected";
      return false;
    }
    if (empty($data)) {
      $this->error = "WS send - No data given";
      return false;
    }
    $header = $len . "|";
    $status = fwrite($this->_Socket, $header);
    if ($status === 0 || $status === false) {
      $this->error = 'WS send - ' . $this->get_socket_error();
      return false;
    }
    $written = 0;
    while ($len > $written) {
      $count = fwrite($this->_Socket, $data);
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
    #FIXME
    #read to '|', convert to int $count
    #read $count bytes
    while ($final === 0) {
      $response .= fread($this->_Socket, 2);
      if (empty($response)) {
	$this->error = 'WS recv frame - ' . $this->get_socket_error();
	return false;
      }
    }

    return $response;
  }

  public function get_socket_error() {
    $sock = socket_import_stream($this->_Socket);
    return socket_strerror(socket_last_error($sock));
  }

  public function connect($host, $port) {
    $this->_host = $host;
    $this->_port = $port;
		
    //$this->_Socket = fsockopen($host, $port, $errno, $errstr, 5);
    $this->_Socket = stream_socket_client("$host:$port", $errno, $errstr, 5);
    if ($this->_Socket === false || $errno !== 0) {
      $this->_connected = false;
      $this->error = 'WS opening connection - ' . $errstr;
      return $this->_connected;
    }
    socket_set_timeout($this->_Socket, 0, 300);
    $this->_connected = true;
    return $this->_connected;	
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
    $this->connect($this->_host, $this->_port);
  }
}

?>
