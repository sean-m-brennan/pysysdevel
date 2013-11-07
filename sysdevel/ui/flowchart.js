/*
 * Copyright 2013.  Los Alamos National Security, LLC.
 * This material was produced under U.S. Government contract
 * DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which
 * is operated by Los Alamos National Security, LLC for the
 * U.S. Department of Energy. The U.S. Government has rights to use,
 * reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
 * LOS ALAMOS NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR
 * IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If
 * software is modified to produce derivative works, such modified
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

/*
 * Requires jQuery, jQuery-UI, and jsPlumb
 */

if ( typeof DEBUG === 'undefined' )
    DEBUG = true


function Flowchart( onConnect, in_color, in_size, out_color, out_size,
		    connect_color, connect_size, highlight_color ) {
    if ( typeof in_color === 'undefined' )
	in_color = '#882255';
    if ( typeof in_size === 'undefined' )
	in_size = 9;
    if ( typeof out_color === 'undefined' )
	out_color = '#558822';
    if ( typeof out_size === 'undefined' )
	out_size = 9;
    if ( typeof connect_color === 'undefined' )
	connect_color = '#deea18';
    if ( typeof connect_size === 'undefined' )
	connect_size = 4;
    if ( typeof highlight_color === 'undefined' )
	highlight_color = '#2e2af8';

    this.connect_callback = onConnect;
    this.ready = false;
    this.source_backlog = [];
    this.sink_backlog = [];

    this.allSourceEndpoints = [];
    this.allTargetEndpoints = [];

    var connectorPaintStyle = {
	lineWidth: connect_size,
	strokeStyle: connect_color,
	joinstyle: "round",
	outlineColor: "#eaedef",
	outlineWidth: 2,
    };

    var connectorHoverStyle = {
	lineWidth: 4,
	strokeStyle: highlight_color,
    };

    var endpointHoverStyle = {
	fillStyle: highlight_color,
    };
    
    this.sourceEndpointStyle = {
	endpoint: "Dot",
	paintStyle:{
	    fillStyle: out_color,
	    radius: out_size,
	},
	isSource: true,
	connector:[ "Flowchart", {
	    stub: [40, 60],
	    gap: 10,
	    cornerRadius: 5,
	    alwaysRespectStubs: true } ],
	connectorStyle: connectorPaintStyle,
	hoverPaintStyle: endpointHoverStyle,
	connectorHoverStyle: connectorHoverStyle,
        dragOptions: {},
        overlays:[
            [ "Label", { 
	        location: [0.5, 1.5], 
	        //label: "Drag",
	        cssClass: "endpointSourceLabel" 
	    } ]
        ]
    };

    this.targetEndpointStyle = {
	endpoint: "Dot",
	paintStyle:{ 
	    strokeStyle: in_color,
	    radius: in_size,
	    fillStyle: "transparent",
	    lineWidth: 2,
	},				
	hoverPaintStyle: endpointHoverStyle,
	maxConnections: -1,
	dropOptions: {
	    hoverClass: "hover",
	    activeClass: "active",
	},
	isTarget: true,
        overlays:[
            [ "Label", {
		location: [0.5, -0.5],
		//label: "Drop",
		cssClass: "endpointTargetLabel" } ]
        ]
    };			


    var _fc = this;
    jsPlumb.bind( "ready", function() {
	_fc.init();
    } );


    this.init = function() {
	var _fc = this;

	jsPlumb.bind( "connection", function( connInfo, evt ) {
	    if ( typeof _fc.connect_callback === 'function' )
		_fc.connect_callback( 'connect',
				      connInfo.connection.sourceId,
				      connInfo.connection.targetId );
	} );			
	    
	jsPlumb.bind( "connectionDetached", function( connInfo, evt ) {
	    if ( typeof _fc.connect_callback === 'function' )
		_fc.connect_callback( 'disconnect',
				      connInfo.connection.sourceId,
				      connInfo.connection.targetId );
	} );

	jsPlumb.bind( "click", function( conn, evt ) {
	    jsPlumb.detach(conn); 
	} );	

	this.ready = true;
	for (var i in this.source_backlog )
	    this.addSourcePoint( this.source_backlog[i][0],
				 this.source_backlog[i][1] );
	this.source_backlog = [];
	for (var i in this.sink_backlog )
	    this.addSinkPoint( this.sink_backlog[i][0],
			       this.sink_backlog[i][1] )
	this.sink_backlog = [];
    };


    this.addSinkPoint = function( parent, where ) {
	if ( ! this.ready ) {
	    this.sink_backlog.push( [ parent, where ] );
	}
	else {
	    var targetUUID = parent + where;
	    this.allTargetEndpoints.push(
		jsPlumb.addEndpoint( parent, this.targetEndpointStyle,
				     { anchor: where, uuid: targetUUID } ) );
	}
    };

    this.addSourcePoint = function( parent, where ) {
	if ( ! this.ready ) {
	    this.source_backlog.push( [ parent, where ] );
	}
	else {
	    var sourceUUID = parent + where;
	    this.allSourceEndpoints.push(
		jsPlumb.addEndpoint( parent, this.sourceEndpointStyle,
				     { anchor: where, uuid: sourceUUID } ) );
	}
    };

    this.clear = function() {
	jsPlumb.detachEveryConnection();
    };
};
