
function WebSocketsHandler( callback ) {
    this.sender = null;
    this.callback = null;
    if ( typeof callback === 'function' )
	this.callback = callback;

    this.close = function() {
        console.debug( 'Disconnected' );
    };

    this.receive = function( data ) {
        //console.debug( 'Received ' + data );
        if ( this.callback )
            this.callback( data );
        else if ( data.substring(0, 6).toLowerCase() == 'error:' )
            console.error( 'Error: ' + msg );
        else
            console.warning( 'Unknown data: ' + data );
    };

    this.send = function( data ) {
        if ( this.sender != null )
            this.sender.send( data );
    };
}


function AjaxHandler( callback ) {
    this.callback = null;
    if ( typeof callback === 'function' )
	this.callback = callback;

    this.close = function() {
        console.debug( 'Disconnected' );
    };

    this.newRequest = function( uri, msg, timeout ) {
	var xhr = new XMLHttpRequest();
	var handler = this;
	xhr.onreadystatechange = function() {
	    if ( xhr.readyState == 4 ) {
		if ( xhr.status == 200 || xhr.status == 0 ) {
		    if ( xhr.responseText ) {
			console.debug( 'Received ' + xhr.responseText );
			if ( handler.callback )
			    handler.callback( xhr.responseText );
		    }
		}
		else
		    handler.app.error( xhr.status, xhr.responseText );
	    }
	};
	xhr.ontimeout = function() {
	    if ( handler.app.timeout )
		handler.app.timeout();
            console.error( 'XMLHttpRequest to ' + uri + ' timeout.' );
	};
	xhr.onerror = function () {
	    console.error( 'XMLHttpRequest error ' + xhr.status + ': ' +
			   xhr.statusText );
	};
	xhr.open( 'POST', uri );
	xhr.setRequestHeader( "Content-type", "text/plain; charset=utf-8" );
	xhr.timeout = 4000;
	if ( typeof timeout === 'number' )
	    xhr.timeout = timeout;
	xhr.send( msg );
    }
}


function WebSocketsClient( resource, handler, fallback ) {
    this._opened = false;
    this.uri = '';
    this.resource = resource;
    this.handler = handler;
    this.handler.sender = this;
    this._ws = null;
    this._socket_type = 'unsupported';
    this.has_fallback = false;
    if ( fallback )
	this.has_fallback = true;


    this._detect_socket_support = function() {
        var loc = location.href;
        if ( typeof WebSocket != 'undefined' )
            this._socket_type = 'ws';
    };

    this.unsupported = function() {
        this._opened = false;
        if ( ! this.has_fallback ) {
            alert('Unsupported browser.\n' + 
                  'Try Google Chrome (redirecting now).');
            location.replace("http {//www.google.com/chrome");
	}
    };

    this.connect = function( host, port, proto ) {
	this._opened = false;
        this._ws = null;
        this._detect_socket_support();

	if ( typeof host === 'undefined' )
	    host = 'localhost';
	if ( typeof port === 'undefined' )
	    port = 9876;
	if ( typeof proto === 'undefined' )
	    proto = 'ws';

        if ( this._socket_type == 'ws' ) {
            this.uri = proto + '://' + host + ':' + port.toString() +
		'/' + this.resource;
            this._ws = new WebSocket( this.uri );
            this._ws.onopen = this.setOnOpen();
            this._ws.onclose = this.setOnClose();
            this._ws.onerror = this.setOnError();
            this._ws.onmessage = this.setOnMessage();
	}
        else
            this.unsupported();
    };

    this.send = function( message ) {
        try {
            this._ws.send( message );
	}
        catch( err ) {
            console.debug( err.toString() );
	}
    };

    this.close = function() {
        console.debug( 'WS closing' );
        if ( this._ws != null )
            this._ws.close();
        this._opened = false;
    };

    this.isConnecting = function() {
        if (this._ws != null )
            return this._ws.readyState == 0;
        return false;
    };

    this.isOpen = function() {
        if (this._ws != null )
            return this._ws.readyState == 1;
        return false;
    };


    this.setOnError = function() {
	return function( evt ) {
            console.error( 'WebSocket error: ' + evt.toString() );
	};
    };

    this.setOnOpen = function() {
	var client = this;
	return function( evt ) {
            if ( client._ws != null )
		console.debug( 'WS connected to ' + client.uri );
            client._opened = true;
	};
    };

    this.setOnClose = function() {
	var client = this;
	return function( evt ) {
            if ( client._opened ) {
		msg = 'Lost connection with the websocket server.';
		if ( client.has_fallback )
                    msg += '\nFalling back to PHP.';
		alert( msg );
		client.handler.close();
	    }
            else {
		if ( ! client.has_fallback )
                    alert( "No websocket server available at " + client.uri );
	    }
            client._opened = false;
	};
    };

    this.setOnMessage = function() {
	var client = this;
	return function( evt ) {
            try {
		client.handler.receive( evt.data );
	    }
            catch( err ) {
		console.debug( err.toString() );
	    }
	};
    };
}


function ServerLink( server, resource, data_callback ){
    this.server = server

    this.ws_dh = new WebSocketsHandler( data_callback );
    var search = location.search.substring(1);
    var params = search.split('&').join('/');
    var full_resource = resource + '/' + params;
    this.ws = new WebSocketsClient( full_resource, this.ws_dh, true );
    this.ws.connect( this.server );

    this.php_dh = new AjaxHandler( data_callback );
    this.php_script = resource + '.php';

    this.send_to_server = function( msg_type, data ) {
	msg = msg_type.toString().toLowerCase();
        if ( typeof data !== 'undefined' )
            msg += '=' + data.toString();
	if ( this.ws.isConnecting() ) {
	    // in case the socket is not yet up
	    setTimeout( function( link, msg ) { link._send( msg ); },
			2000, this, msg );
	}
	else
	    this._send( msg );
    };

    this._send = function( msg ) {
        //console.debug( "Sending '" + msg + "'" );
        if ( this.ws.isOpen() )
            this.ws_dh.send( msg );
        else {  // fallback to PHP
            console.info( 'Server at ' + this.server + ' not available.' );
	    this.php_dh.newRequest( this.php_script, msg );
	}
    };
}
