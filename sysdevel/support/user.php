<?php
  /*
   * Simple user registration, log-in and operation authentication framework
   *
   * Derived and altered from Usered at https://github.com/Pomax/Usered
   */
  /*
   * Original copyright (c) Mike "Pomax" Kamermans, 2011.
   *
   * Permission is hereby granted, free of charge, to any person
   * obtaining a copy of this software and associated documentation
   * files (the "Software"), to deal in the Software without
   * restriction, including without limitation the rights to use,
   * copy, modify, merge, publish, distribute, sublicense, and/or sell
   * copies of the Software, and to permit persons to whom the
   * Software is furnished to do so, subject to the following
   * conditions:
   *
   * The above copyright notice and this permission notice shall be
   * included in all copies or substantial portions of the Software.
   *
   * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
   * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
   * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
   * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
   * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
   * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
   * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
   */
  /*
   * Subsequent copyright (c) 2013.  Los Alamos National Security, LLC.
   *
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

$HERE = dirname(__FILE__) . DIRECTORY_SEPARATOR;
$DEFAULT_PATH = $HERE . "admin" . DIRECTORY_SEPARATOR;

// Create a file 'user.config.php' to override any or all of these:

$USER_PROJECT = "PROJECT";
$USER_DOMAIN_NAME = $_SERVER['SERVER_NAME'];
$USER_WEBSITE = "http://" . $_SERVER['SERVER_NAME'];
$USER_DATABASE_PATH = $DEFAULT_PATH;
$USER_HOME_PATH = $DEFAULT_PATH . "users" . DIRECTORY_SEPARATOR;
$USER_DATABASE_NAME = "users";
$USER_MAILER_NAME = "noreply@" . $_SERVER['SERVER_NAME'];
$USER_MAILER_REPLYTO = "user@" . $_SERVER['SERVER_NAME'];
$USER_SUBDIRECTORIES = array();


// load optional configuration file
$config_filename = $HERE . DIRECTORY_SEPARATOR . 'user.config.php';
if (is_readable($config_filename)) {
  include_once $config_filename;
}


class User {
  const use_mail = true;
  const unsafe_reporting = false;
  const time_out = 600;

  // These function as constants, 'const' just doesn't do it.
  public static function PROJECT() {
    global $USER_PROJECT;
    return $USER_PROJECT;
  }
  public static function WEBSITE() {
    global $USER_WEBSITE;
    return $USER_WEBSITE;
  }
  public static function USER_HOME() {
    global $USER_HOME_PATH;
    return $USER_HOME_PATH;
  }
  public static function DATABASE_LOCATION() {
    global $USER_DATABASE_PATH;
    return $USER_DATABASE_PATH;
  }
  public static function DATABASE_NAME() {
    global $USER_DATABASE_NAME;
    return $USER_DATABASE_NAME;
  }
  public static function DOMAIN_NAME() {
    global $USER_DOMAIN_NAME;
    return $USER_DOMAIN_NAME;
  }
  public static function MAILER_NAME() {
    global $USER_MAILER_NAME;
    return $USER_MAILER_NAME;
  }
  public static function MAILER_REPLYTO() {
    global $USER_MAILER_REPLYTO;
    return $USER_MAILER_REPLYTO;
  }
  public static function SUBDIRECTORIES() {
    global $USER_SUBDIRECTORIES;
    return $USER_SUBDIRECTORIES;
  }


  // this is the global error message. If anything goes wrong, this tells you why.
  var $error = "";

  // progress log
  var $info_log = array();

  // Information logging
  function info($string) { $this->info_log[] = $string; }

  // error log
  var $error_log = array();

  // Error logging
  function error($string) { $this->error_log[] = $string; }

  // States
  var $applying = false;
  var $changing_profile = false;

  // all possible values for a hexadecimal number
  var $hex = "0123456789abcdef";

  // all possible values for an ascii password, skewed a bit so the number to letter ratio is closer to 1:1
  var $ascii = "0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6A7B8C9D0E1F2G3H4I5J6K7L8M9N0O1P2Q3R4S5T6U7V8W9X0Y1Z23456789";

  // the regular expression for email matching (see http://www.regular-expressions.info/email.html)
  const emailregexp = "/[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/";

  // the regular expression for hash matching
  const passwdregexp = "/[0123456789abcdef]{40,40}/";

  // this will tell us whether the client that requested the page is authenticated or not.
  var $authenticated = false;

  // the guest user name
  const GUEST_USER  = "guest user";

  // this will contain the user name for the user doing the page request
  var $username = User::GUEST_USER;

  // if this is a properly logged in user, this will contain the data directory location for this user
  var $userdir = false;

  // the user's email address, if logged in.
  var $email = "";

  // the user's role in the system
  var $role = "";

  var $tasks = array();

  // global database handle
  var $database = false;

  // class object constructor
  function __construct($registration_callback=false, $live=false)
  {
    // session management comes first. Warnings are repressed with @ because it will warn if something else already called session_start()
    @session_start();
    if (empty($_SESSION["username"]) || empty($_SESSION["token"])) $this->resetSession();

    // file location for the user database
    $dbfile = User::DATABASE_LOCATION()  . User::DATABASE_NAME() . ".db";

    // do we need to build a new database?
    $rebuild = false;
    if(!file_exists($dbfile)) { $rebuild = true; }

    // bind the database handler
    $this->database = new PDO("sqlite:" . $dbfile);
    $this->database->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_WARNING);

    // If we need to rebuild, the file will have been automatically made by the PDO call,
    // but we'll still need to define the user table before we can use the database.
    if($rebuild) {
      @chgrp($dbfile, filegroup(__FILE__));
      @chmod($dbfile, 0770);
      $this->rebuild_database($dbfile);
    }

    // finally, process the page request.
    $this->process($registration_callback);
  }

  // this function rebuilds the database if there is no database to work with yet
  function rebuild_database($dbfile)
  {
    $this->info("rebuilding database as ".$dbfile);
    $this->database->beginTransaction();
    $create = "CREATE TABLE users (username TEXT UNIQUE, password TEXT, email TEXT UNIQUE, token TEXT, path TEXT, role TEXT, active TEXT, last TEXT, has_key INTEGER); ";
    $create .= "CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, date TEXT, completed INTEGER); ";
    $this->database->exec($create);
    $this->database->commit();
  }

  // process a page request
  function process(&$registration_callback=false)
  {
    $this->database->beginTransaction();
    $set_globals = 1;
    if(isset($_POST["op"])) {
      $operation = $_POST["op"];
      // logging in or out, and dropping your registration, may change authentication status
      if($operation == "login") {
	$this->authenticated = $this->login();
      }
      // logout and unregister will unset authentication if successful
      elseif($operation == "logout") {
	$this->authenticated = !$this->logout();
      }
      elseif($operation == "unregister") {
	$this->authenticated = !$this->unregister();
      }
      // anything else won't change authentication status.
      elseif($operation == "register") {
	$this->register($registration_callback);
      }
      elseif($operation == "unique") { $this->unique(); $set_globals = 0; }
      elseif($operation == "query") { $this->query(); $set_globals = 0; }
      elseif($operation == "update") { $this->update(); }
      elseif($operation == "task_update") { $this->task_update(); }
      elseif($operation == "task_delete") { $this->task_delete(); }
      elseif($operation == "user_update") { $this->user_update(); }
      elseif($operation == "gpg_update") { $this->gpg_update(); }
      elseif($operation == "apply") { $this->apply(); }
      // we only allow password resetting if we can send notification mails
      elseif($operation == "reset" && User::use_mail) {
	$this->reset_password();
      }
    }

    // if the previous operations didn't authorise the current user,
    // see if they're already marked as authorised in the database.
    if(!$this->authenticated) {
      $username = $_SESSION["username"];
      if($username != User::GUEST_USER) {
	$this->authenticated = $this->authenticate_user($username,"");
	if($this->authenticated) { $this->mark_user_active($username); }
      }
    }

    if ($set_globals) {
      // at this point we can make some globals available.
      $this->username = $_SESSION["username"];
      $this->userdir = $this->get_user_path($this->username);
      $this->email = $this->get_user_email($this->username);
      $this->role = $this->get_user_role($this->username);
      $this->has_key = $this->get_has_key($this->username);
      $this->tasks = $this->get_task_list();
    }

    // clear database
    $this->database->commit();
    $this->database = null;
  }

  // ---------------------
  // validation passthroughs
  // ---------------------

  /**
   * Called when the requested POST operation is "login"
   */
  function login()
  {
    // get relevant values
    $username = $_POST["username"];
    $password = $_POST["password1"];
    // step 1: someone could have bypassed the javascript validation, so validate again.
    if(!$this->validate_user_name($username)) {
      $this->info("log in error: user name did not pass validation");
      return false; }
    //if(preg_match(User::passwdregexp, $passwd)==0) {
    //  $this->info("log in error: password did not pass validation");
    //  return false; }
    // step 2: if validation passed, log the user in
    return $this->login_user($username, $password);
  }

  /**
   * Called when the requested POST operation is "logout"
   */
  function logout()
  {
    // get relevant value
    $username = $_POST["username"];
    // step 1: validate the user name.
    if(!$this->validate_user_name($username)) {
      $this->info("log in error: user name did not pass validation");
      return false; }
    // step 2: if validation passed, log the user out
    return $this->logout_user($username);
  }

  /**
   * Users should always have the option to unregister
   */
  function unregister()
  {
    // get relevant value
    $username = $_POST["username"];
    // step 1: validate the user name.
    if(!$this->validate_user_name($username)) {
      $this->info("unregistration error: user name did not pass validation");
      return false; }
    // step 2: if validation passed, drop the user from the system
    return $this->unregister_user($username);
  }

  /**
   * Called when the requested POST operation is "apply"
   */
  function apply()
  {
    $username = $_POST["username"];
    $emailaddr = $_POST["email"];

    // add a user registration task
    $descr = "Register user <b>$username</b> from <b>$emailaddr</b>";
    $dt = date('Y-m-d H:i');
    $insert_task = "INSERT INTO tasks (description, date, completed) ";
    $insert_task .= "VALUES ('$descr', '$dt', 0)";
    $this->database->exec($insert_task);

    // send email notification
    $email = User::MAILER_REPLYTO();
    $from = User::MAILER_NAME();
    $subject = User::DOMAIN_NAME() . " registration";
    $body = $this->apply_email($username, $emailaddr);
    $headers = "From: $from\r\n";
    $headers .= "X-Mailer: PHP/" . phpversion();
    if (!mail($email, $subject, $body, $headers)) {
      $this->error = "Application email failed.";
    }
    else {
      $this->info("New user application: $username from $emailaddr");
    }
  }


  /**
   * Called when the requested POST operation is "register"
   */
  function register(&$registration_callback=false)
  {
    // get relevant values
    $username = $_POST["username"];
    $email = $_POST["email"];
    // step 1: someone could have bypassed the javascript validation, so validate again.
    if(!$this->validate_user_name($username)) {
      $this->info("registration error: user name did not pass validation");
      return false; }
    if(preg_match(User::emailregexp, $email)==0) {
      $this->info("registration error: email address did not pass validation");
      return false; }
    // step 2: if validation passed, register user
    $newpassword = $this->random_ascii_string(20);
    $registered = $this->register_user($username, $email, $newpassword, $registration_callback);
    if($registered && User::use_mail)
      {
	// send email notification
	$from = User::MAILER_NAME();
	$replyto = User::MAILER_REPLYTO();
	$subject = User::DOMAIN_NAME() . " registration";
	$body = $this->registered_email($username, $newpassword);
	$headers = "From: $from\r\n";
	$headers .= "Reply-To: $replyto\r\n";
	$headers .= "X-Mailer: PHP/" . phpversion();
	mail($email, $subject, $body, $headers);
      }
    
    return $registered;
  }
  
  function unique()
  {
    $this->applying = true;
    $this->username = trim($_POST["username"]);
    if ($this->username == User::GUEST_USER) {
      $this->error = "Cannot use the guest user moniker. Try something else.";
      return true;
    }
    $query = "SELECT 1 FROM users WHERE username LIKE '$this->username'";
    $res = $this->database->query($query);
    $results = $res->fetchAll();
    foreach($results as $data) {
      $this->error = "Username: $username taken. Try something else.";
      break;
    }
    return true;
  }

  /**
   * Called when the requested POST operation is "query"
   */
  function query()
  {
    $this->changing_profile = true;
    $username = trim($_POST["username"]);
    if ($username == User::GUEST_USER) {
      return false;
    }
    $this->username = $username;
    $this->userdir = $this->get_user_path($username);
    $this->email = $this->get_user_email($username);
    return true;
  }

  /**
   * Called when the requested POST operation is "update"
   */
  function update()
  {
    // get relevant values
    $username = trim($_POST["username"]);
    $email = trim($_POST["email"]);
    $passwd = trim($_POST["password1"]);
    $path = trim($_POST["path"]);
    // step 1: someone could have bypassed the javascript validation, so validate again.
    if($email !="" && preg_match(User::emailregexp, $email)==0) {
      $this->info("registration error: email address did not pass validation");
      return false; }
    // FIXME password validation
    //if($passwd !="" && preg_match(User::passwdregexp, $passwd)==0) {
    //  $this->info("registration error: password did not pass validation");
    //  return false; }
    // step 2: if validation passed, update the user's information
    return $this->update_user($username, $email, $passwd, $path);
  }

  /**
   * Called when the requested POST operation is "task_update"
   */
  function task_update()
  {
    $task_id = $_POST["task"];
    $update = "UPDATE tasks SET completed = 1 WHERE id = $task_id";
    $this->database->exec($update);
    return true;
  }


  /**
   * Called when the requested POST operation is "task_delete"
   */
  function task_delete()
  {
    $task_id = $_POST["task"];
    $delete = "DELETE FROM tasks WHERE id = $task_id";
    $this->database->exec($delete);
    return true;
  }


  /**
   * Called when the requested POST operation is "user_update"
   */
  function user_update()
  {
    // get relevant values
    $username = $_SESSION["username"];
    $passwd = trim($_POST["password1"]);
    // step 1: someone could have bypassed the javascript validation, so validate again.
    // FIXME password validation
    //if($passwd !="" && preg_match(User::passwdregexp, $passwd)==0) {
    //  $this->info("registration error: password did not pass validation");
    //  return false; }
    // step 2: if validation passed, update the user's information
    return $this->update_user($username, "", $passwd, "");
  }
  

  /**
   * Called when the requested POST operation is "gpg_update"
   */
  function gpg_update()
  {
    // get relevant values
    $username = $_SESSION["username"];
    $key = trim($_POST["key"]);
    // step 1: someone could have bypassed the javascript validation, so validate again.
    if ($username == User::GUEST_USER) {
      return false;
    }
    // FIXME password validation
    //if($passwd !="" && preg_match(User::passwdregexp, $passwd)==0) {
    //  $this->info("registration error: password did not pass validation");
    //  return false; }
    // step 2: if validation passed, update the user's information
    $user_dir = $this->get_user_path($username);
    putenv("GNUPGHOME=$user_dir/.gnupg/");  // user's keychain

    $gpg = new gnupg();
    $gpg->seterrormode(gnupg::ERROR_EXCEPTION);

    try {
      $gpg->cleardecryptkeys();
      $gpg->clearencryptkeys();
      $gpg->clearsignkeys();

      $update = "UPDATE users SET has_key = 1 WHERE username= '$username'";
      $this->database->exec($update);

      $retVal = $gpg->import($key);
      echo $retVal['imported'] . ' key(s) imported.';
      $key = file_get_contents(User::USER_HOME() . 'consim.gpg'); //TODO public key name
      $retVal = $gpg->import($key);
      echo $retVal['imported'] . ' key(s) imported.';
    } catch (Exception $e) {
      return false;
    }
    return true;
  }
  
  /**
   * Reset a user's password
   */
  function reset_password()
  {
    // get the email for which we should reset
    $email = $_POST["email"];

    // step 1: someone could have bypassed the javascript validation, so validate again.
    if(preg_match(User::emailregexp, $email)==0) {
      $this->info("registration error: email address did not pass validation");
      return false; }

    // step 2: if validation passed, see if there is a matching user, and reset the password if there is
    $newpassword = $this->random_ascii_string(20);
    //$passwd = sha1($newpassword);
    $query = "SELECT username, token FROM users WHERE email = '$email'";
    $username = "";
    $token = "";
    $res = $this->database->query($query);
    $results = $res->fetchAll();
    foreach($results as $data) {
      $username = $data["username"];
      $token = $data["token"];
      break;
    }

    // step 2a: if there was no user to reset a password for, stop.
    if($username == "" || $token == "") return false;

    // step 2b: if there was a user to reset a password for, reset it.
    $dbpassword = $this->token_hash_password($username, $newpassword, $token);
    $update = "UPDATE users SET password = '$dbpassword' WHERE email= '$email'";
    $this->database->exec($update);

    // step 3: notify the user of the new password
    $from = User::MAILER_NAME();
    $replyto = User::MAILER_REPLYTO();
    $subject = User::DOMAIN_NAME() . " password reset request";
    $body = $this->reset_passwd_email($username, $newpassword);

    $headers = "From: $from\r\n";
    $headers .= "Reply-To: $replyto\r\n";
    $headers .= "X-Mailer: PHP/" . phpversion();
    mail($email, $subject, $body, $headers);
  }

  // ------------------
  // specific functions
  // ------------------

  // session management: set session values
  function setSession($username, $token)
  {
    $_SESSION["username"]=$username;
    $_SESSION["token"]=$token;
  }

  // session management: reset session values
  function resetSession()
  {
    $_SESSION["username"] = User::GUEST_USER;
    $_SESSION["token"] = -1;
  }

  /**
   * Validate a username. Empty usernames or names
   * that are modified by making them SQL safe are
   * considered not validated.
   */
  function validate_user_name($username)
  {
    $cleaned = $this->clean_SQLite_string($username);
    $validated = ($cleaned != "" && $cleaned==$username);
    if(!$validated) { $this->error = "user name did not pass validation."; }
    return $validated;
  }

  /**
   * Clean strings for SQL insertion as string in SQLite (single quote enclosed).
   * Note that if the cleaning changes the string, this system won't insert.
   * The validate_user_name() function will flag this as a validation failure and
   * the database operation is never carried out.
   */
  function clean_SQLite_string($string)
  {
    $search = array("'", "\\", ";");
    $replace = array('', '', '');
    return trim(str_replace($search, $replace, $string));
  }

  /**
   * Verify that the given username is allowed
   * to perform the given operation.
   */
  function authenticate_user($username, $operation)
  {
    // actually logged in?
    if($this->is_user_active($username)===false) { return false; }

    // logged in, but do the tokens match?
    $token = $this->get_user_token($username);
    if($token != $_SESSION["token"]) {
      $this->error("token mismatch for $username");
      return false; }

    // active, using the correct token -> authenticated
    return true;
  }

  /**
   * Unicode friendly(ish) version of strtolower
   * see: http://ca3.php.net/manual/en/function.strtolower.php#91805
   */
  function strtolower_utf8($string)
  {
    $convert_to = array( "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
			 "v", "w", "x", "y", "z", "à", "á", "â", "ã", "ä", "å", "æ", "ç", "è", "é", "ê", "ë", "ì", "í", "î", "ï",
			 "ð", "ñ", "ò", "ó", "ô", "õ", "ö", "ø", "ù", "ú", "û", "ü", "ý", "а", "б", "в", "г", "д", "е", "ё", "ж",
			 "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы",
			 "ь", "э", "ю", "я" );
    $convert_from = array( "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U",
			   "V", "W", "X", "Y", "Z", "À", "Á", "Â", "Ã", "Ä", "Å", "Æ", "Ç", "È", "É", "Ê", "Ë", "Ì", "Í", "Î", "Ï",
			   "Ð", "Ñ", "Ò", "Ó", "Ô", "Õ", "Ö", "Ø", "Ù", "Ú", "Û", "Ü", "Ý", "А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж",
			   "З", "И", "Й", "К", "Л", "М", "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ", "Ъ",
			   "Ь", "Э", "Ю", "Я" );
    return str_replace($convert_from, $convert_to, $string);
  }

  /**
   * This functions flattens user name strings for similarity comparison purposes
   */
  function homogenise_username($string)
  {
    // cut off trailing numbers
    $string = preg_replace("/\d+$/", '', $string);
    // and then replace non-terminal numbers with
    // their usual letter counterparts.
    $s = array("1","3","4","5","7","8","0");
    $r = array("i","e","a","s","t","ate","o");
    $string = str_replace($s, $r, $string);
    // finally, collapse case
    return $this->strtolower_utf8($string);
  }

  /**
   * We don't require assloads of personal information.
   * A username and a password are all we want. The rest
   * is profile information that can be set, but in no way
   * needs to be, in the user's profile section
   */
  function register_user($username, $email, $passwd, &$registration_callback = false)
  {
    $dbpassword = $this->token_hash_password($username, $passwd, "");
    if($dbpassword==$passwd) die("password hashing is not implemented.");

    // Does user already exist? (see notes on safe reporting)
    if(User::unsafe_reporting) {
      $query = "SELECT username FROM users WHERE username LIKE '$username'";
      $res = $this->database->query($query);
      $results = $res->fetchAll();
      foreach($results as $data) {
	$this->info("user account for $username not created.");
	$this->error = "this user name is already being used by someone else.";
	return false;
      }
    }
    else{
      $query = "SELECT username FROM users";
      $usernames = array();
      $res = $this->database->query($query);
      $results = $res->fetchAll();
      foreach($results as $data) {
	$usernames[] = $this->homogenise_username($data["username"]);
      }
      if(in_array($this->homogenise_username($username), $usernames)) {
	$this->info("user account for $username not created.");
	$this->error = "this user name is not allowed, because it is too similar to other user names.";
	return false; }}

    // Is email address already in use? (see notes on safe reporting)
    $query = "SELECT * FROM users WHERE email = '$email'";
    $res = $this->database->query($query);
    $results = $res->fetchAll();
    foreach($results as $data) {
      $this->info("user account for $username not created.");
      $this->error = "this email address is already in use.";
      return false; }

    $dir = User::USER_HOME() . $username;
    // This user can be registered
    $insert = "INSERT INTO users (username, email, password, token, path, role, active, last, has_key) ";
    $insert .= "VALUES ('$username', '$email', '$dbpassword', '', '$dir', 'user', 'true', '" . time() . "', 0) ";
    $this->database->exec($insert);
    $query = "SELECT * FROM users WHERE username = '$username'";
    $res = $this->database->query($query);
    $results = $res->fetchAll();
    foreach($results as $data) {
      $this->info("created user account for $username");
      $this->update_user_token($username, $passwd);
      if (!file_exists(User::USER_HOME())) {
	mkdir(User::USER_HOME(), 0770);
      }
      // make the user's data directory
      if(!mkdir($dir, 0770)) { $this->error("could not make user directory $dir"); return false; }
      chgrp($dir, filegroup(__FILE__));
      chmod($dir, 0770);
      foreach($this->SUBDIRECTORIES() as $subdir) {
	mkdir($dir . '/' . $subdir, 0770);
	chgrp($dir . '/' . $subdir, filegroup(__FILE__));
	chmod($dir . '/' . $subdir, 0770);
      }
      chgrp(User::USER_HOME(), filegroup(__FILE__));
      chmod(User::USER_HOME(), 0770);
      $this->info("created user directory $dir");
      // if there is a callback, call it
      if($registration_callback !== false) { $registration_callback($username, $email, $dir); }
      return true;
    }
    $this->error = "unknown database error occured.";
    return false;
  }

  /**
   * Log a user in
   */
  function login_user($username, $passwd)
  {
    // transform passwd into real password
    $dbpassword = $this->token_hash_password($username, $passwd, $this->get_user_token($username));
    if($dbpassword==$passwd) {
      $this->info("password hashing is not implemented.");
      return false; }

    // perform the authentication step
    $query = "SELECT password FROM users WHERE username = '$username'";
    $res = $this->database->query($query);
    $results = $res->fetchAll();
    foreach($results as $data) {
      if($dbpassword==$data["password"]) {
	// authentication passed - 1) mark active and update token
	$this->mark_user_active($username);
	$this->setSession($username, $this->update_user_token($username, $passwd));
	// authentication passed - 2) signal authenticated
	return true; }
      // authentication failed
      $this->info("password mismatch for $username");
      if(User::unsafe_reporting) { $this->error = "incorrect password for $username."; }
      else { $this->error = "the specified username/password combination is incorrect."; }
      return false; }

    // authentication could not take place
    $this->info("there was no user $username in the database");
    if(User::unsafe_reporting) { $this->error = "user $username is unknown."; }
    else { $this->error = "you either did not correctly input your username, or password (... or both)."; }
    return false;
  }

  /**
   * Update a user's information
   */
  function update_user($username, $email, $passwd, $path)
  {
    if($email !="") {
      $update = "UPDATE users SET email = '$email' WHERE username = '$username'";
      $this->database->exec($update);
      $this->info("updated the email address for $username");
    }
    if($passwd !="") {
      $dbpassword = $this->token_hash_password($username, $passwd, $this->get_user_token($username));
      $update = "UPDATE users SET password = '$dbpassword' WHERE username = '$username'";
      $this->database->exec($update);
      $this->info("updated the password for $username");
    }
    if($path !="") {
      $update = "UPDATE users SET path = '$path' WHERE username = '$username'";
      $this->database->exec($update);
      $this->info("updated the user path for $username");
    }
  }

  /**
   * Log a user out.
   */
  function logout_user($username)
  {
    $update = "UPDATE users SET active = 'false' WHERE username = '$username'";
    $this->database->exec($update);
    $this->resetSession();
    $this->info("logged $username out");
    return true;
  }

  function delete_dir($dir) {
    if (!file_exists($dir)) return true;
    if (!is_dir($dir) || is_link($dir)) return unlink($dir); 
    foreach (scandir($dir) as $file) { 
      if ($file == '.' || $file == '..') continue; 
      if (!$this->delete_dir($dir . "/" . $file)) { 
	chmod($dir . "/" . $file, 0777); 
	if (!$this->delete_dir($dir . "/" . $file)) return false; 
      }; 
    } 
    return rmdir($dir); 
  }

  /**
   * Drop a user from the system
   */
  function unregister_user($username)
  {
    $path = $this->get_user_path($username);
    $delete = "DELETE FROM users WHERE username = '$username'";
    if (!$this->delete_dir($path))
      return false;
    $this->database->exec($delete);
    $this->info("removed $username from the system");
    $this->resetSession();
    return true;
  }

  /**
   * The incoming password will already be a sha1 print (40 bytes) long,
   * but for the database we want it to be hased as sha256 (using 64 bytes).
   */
  function token_hash_password($username, $passwd, $token)
  {
    return hash("sha256", $username . $passwd . $token);
  }

  /**
   * Get a user's email address
   */
  function get_user_email($username)
  {
    if($username && $username !="" && $username !=User::GUEST_USER) {
      $query = "SELECT email FROM users WHERE username = '$username'";
      $res = $this->database->query($query);
      $results = $res->fetchAll();
      foreach($results as $data) { return $data["email"]; }
    }
    return "";
  }

  /**
   * Get a user's role
   */
  function get_user_role($username)
  {
    if($username && $username !="" && $username !=User::GUEST_USER) {
      $query = "SELECT role FROM users WHERE username = '$username'";
      $res = $this->database->query($query);
      $results = $res->fetchAll();
      foreach($results as $data) { return $data["role"]; }
    }
    return User::GUEST_USER;
  }

  /**
   * Get a user's filesystem path
   */
  function get_user_path($username)
  {
    if($username && $username !="" && $username !=User::GUEST_USER) {
      $query = "SELECT path FROM users WHERE username = '$username'";
      $res = $this->database->query($query);
      $results = $res->fetchAll();
      foreach($results as $data) { return $data["path"]; }
    }
    return "";
  }

  /**
   * Get the list of tasks
   */
  function get_task_list()
  {
    $task_list = array();
    $query = "SELECT * FROM tasks";
    $res = $this->database->query($query);
    $results = $res->fetchAll();
    foreach($results as $data) {
      array_push($task_list, $data);
    }
    return $task_list;
  }

  /**
   * Get whether user has a GPG key
   */
  function get_has_key($username)
  {
    if($username && $username !="" && $username !=User::GUEST_USER) {
      $query = "SELECT has_key FROM users WHERE username = '$username'";
      $res = $this->database->query($query);
      $results = $res->fetchAll();
      foreach($results as $data) { return $data["has_key"]; }
    }
    return User::USER_HOME() . "guest";
  }

  /**
   * Get the user token
   */
  function get_user_token($username)
  {
    $query = "SELECT token FROM users WHERE username = '$username'";
    $res = $this->database->query($query);
    $results = $res->fetchAll();
    foreach($results as $data) { return $data["token"]; }
    return false;
  }

  /**
   * Update the user's token and password upon successful login
   */
  function update_user_token($username, $passwd)
  {
    // update the user's token
    $token = $this->random_hex_string(32);
    $update = "UPDATE users SET token = '$token' WHERE username = '$username'";
    $this->database->exec($update);

    // update the user's password
    $newpassword = $this->token_hash_password($username, $passwd, $token);
    $update = "UPDATE users SET password = '$newpassword' WHERE username = '$username'";
    $this->database->exec($update);
    $this->info("updated token and password for $username");

    return $token;
  }

  /**
   * Mark a user as active.
   */
  function mark_user_active($username)
  {
    $update = "UPDATE users SET active = 'true', last = '" . time() . "' WHERE username = '$username'";
    $this->database->exec($update);
    $this->info("$username has been marked currently active.");
    return true;
  }

  /**
   * Check if user can be considered active
   */
  function is_user_active($username)
  {
    $last = 0;
    $active = "false";
    $query = "SELECT last, active FROM users WHERE username = '$username'";
    $res = $this->database->query($query);
    $results = $res->fetchAll();
    foreach($results as $data) {
      $last = intval($data["last"]);
      $active = $data["active"];
      break;
    }

    if($active=="true") {
      $diff = time() - $last;
      if($diff >= User::time_out) {
	$this->logout_user($username);
	$this->error("$username was active but timed out (timeout set at " . User::time_out . " seconds, difference was $diff seconds)");
	return false; }
      $this->info("$username is active");
      return true; }

    $this->error("$username is not active");
    $this->resetSession();
    return false;
  }

  /**
   * Random hex string generator
   */
  function random_hex_string($len)
  {
    $string = "";
    $max = strlen($this->hex)-1;
    while($len-->0) { $string .= $this->hex[mt_rand(0, $max)]; }
    return $string;
  }

  /**
   * Random password string generator
   */
  function random_ascii_string($len)
  {
    $string = "";
    $max = strlen($this->ascii)-1;
    while($len-->0) { $string .= $this->ascii[mt_rand(0, $max)]; }
    return $string;
  }

  function apply_email($username, $emailaddr)
  {
    return "A new user has applied for access to " . User::PROJECT() . ".\n" .
      "If approved, add this user at the web interface.\n" .
      "The system will assign a random password and inform him/her by email.\n" .
      "\n" .
      "Username:  " . $username . "\n" .
      "Email:     " . $emailaddr . "\n\n\n";
  }


  function registered_email($username, $password)
  {
    return "You have been approved for access to " . User::PROJECT() . ".\n" .
      "Please visit " . User::WEBSITE() . ", log in, and change your password soon.\n" .
      "\n" .
      "Your information:\n" .
      "Username:  " . $username . "\n" .
      "Password:  " . $password . "\n\n\n";
  }


  function reset_passwd_email($username, $password)
  {
    return "Your password for access to " . User::PROJECT() . " has been reset.\n" .
      "Please visit " . User::WEBSITE() . ", log in, and change your password soon.\n" .
      "\n" .
      "Your information:\n" .
      "Username:  " . $username . "\n" .
      "Password:  " . $password . "\n\n\n";
  }

}

?>