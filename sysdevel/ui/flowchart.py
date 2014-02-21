"""
Copyright 2013.  Los Alamos National Security, LLC.
This material was produced under U.S. Government contract
DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
operated by Los Alamos National Security, LLC for the U.S. Department
of Energy. The U.S. Government has rights to use, reproduce, and
distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should be
clearly marked, so as not to confuse it with the version available
from LANL.

Licensed under the Mozilla Public License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/2.0/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""

try:
    # pylint: disable=F0401
    from __pyjamas__ import JS

    # pylint: disable=W0613,W0102

    def add_endpoint(what, style={}, extra={}):
        return JS("""$wnd.jsPlumb.addEndpoint( @{{what}}, @{{style}}, @{{extra}} )""")

    def connect_points(frm, to, can_edit=False):
        if can_edit:
            JS("""$wnd.jsPlumb.connect( { uuids:[ @{{frm}}, @{{to}} ], editable:true } );""")
        else:
            JS("""$wnd.jsPlumb.connect( { uuids:[ @{{frm}}, @{{to}} ], editable:false } );""")

    def init_flowchart(fc):
        JS("""$wnd.jsPlumb.bind( "connection", function( connInfo, evt ) {
                  if ( typeof @{{fc}}.connect_callback === 'function' )
	              @{{fc}}.connect_callback( 'connect',
		  		                 connInfo.connection.sourceId,
				                 connInfo.connection.targetId );
              } );""")
        JS("""$wnd.jsPlumb.bind( "connectionDetached", function( connInfo, evt ) {
	          if ( typeof @{{fc}}.connect_callback === 'function' )
		      @{{fc}}.connect_callback( 'disconnect',
				                 connInfo.connection.sourceId,
				                 connInfo.connection.targetId );
              } );""")
        JS("""$wnd.jsPlumb.bind("click", function(conn, evt) { jsPlumb.detach( conn ); });""")

except ImportError:
    raise NotImplementedError("Pure Python Flowchart not yet implemented.")


##############################



class Flowchart(object):
    def __init__(self, in_color='#882255', in_size=9,
                 out_color='#558822', out_size=9,
                 connect_color='#deea18', connect_size=4,
                 highlight_color='#2e2af8', onConnect=None):
        self.connect_callback = onConnect
        if onConnect is None:
            self.connect_callback = self.debugConnect

        self.debug = False
        self.ready = False
        self.source_backlog = []
        self.sink_backlog = []
        self.connection_backlog = []
        self.allSourceEndpoints = []
        self.allTargetEndpoints = []

        connectorPaintStyle = {
            'lineWidth': connect_size,
            'strokeStyle': connect_color,
            'joinstyle': "round",
            'outlineColor': "#eaedef",
            'outlineWidth': 2,
        }

        connectorHoverStyle = {
            'lineWidth': 4,
            'strokeStyle': highlight_color,
        }

        endpointHoverStyle = {
            'fillStyle': highlight_color,
        }
    
        self.sourceEndpointStyle = {
            'endpoint': "Dot",
            'paintStyle':{
                'fillStyle': out_color,
                'radius': out_size,
            },
            'isSource': True,
            'connector':[ "Flowchart", {
                'stub': [40, 60],
                'gap': 10,
                'cornerRadius': 5,
                'alwaysRespectStubs': True } ],
            'connectorStyle': connectorPaintStyle,
            'hoverPaintStyle': endpointHoverStyle,
            'connectorHoverStyle': connectorHoverStyle,
            'dragOptions': {},
            'overlays':[
                [ "Label", { 
                    'location': [0.5, 1.5], 
                    'cssClass': "endpointSourceLabel" 
                } ]
            ]
        }

        self.targetEndpointStyle = {
            'endpoint': "Dot",
            'paintStyle':{ 
                'strokeStyle': in_color,
                'radius': in_size,
                'fillStyle': "transparent",
                'lineWidth': 2,
            },				
            'hoverPaintStyle': endpointHoverStyle,
            'maxConnections': -1,
            'dropOptions': {
                'hoverClass': "hover",
                'activeClass': "active",
            },
            'isTarget': True,
            'overlays':[
                [ "Label", {
                    'location': [0.5, -0.5],
                    'cssClass': "endpointTargetLabel" } ]
            ]
        }


    def post_init(self):
        init_flowchart(self)
        self.ready = True
        for src in self.source_backlog:
            self.addSourcePoint(src[0], src[1])
        self.source_backlog = []
        for snk in self.sink_backlog:
            self.addSinkPoint(snk[0], snk[1])
        self.sink_backlog = []
        for conn in self.connection_backlog:
            self.connectPoints(conn[0], conn[1], conn[2])
        self.connection_backlog = []
        

    def debugConnect(self, which, frm, to):
        if self.debug:
            print(str(which) + "ed " + str(frm) + " to " + str(to))


    def addSourcePoint(self, what, where):
        if not self.ready:
            self.source_backlog.append([what, where])
        else:
            sourceUUID = what + where
            style = self.sourceEndpointStyle
            extra = { 'anchor': where, 'uuid': sourceUUID }
            pt = add_endpoint(what, style, extra)
            self.allSourceEndpoints.append(pt)


    def addSinkPoint(self, what, where):
        if not self.ready:
            self.sink_backlog.append([what, where])
        else:
            targetUUID = what + where
            style = self.targetEndpointStyle
            extra = { 'anchor': where, 'uuid': targetUUID }
            pt = add_endpoint(what, style, extra)
            self.allTargetEndpoints.append(pt)


    def connectPoints(self, frm, to, can_edit=False):
        if not self.ready:
            self.connection_backlog.append([frm, to, can_edit])
        else:
            connect_points(frm, to, can_edit)


    def clear(self):
        JS("""$wnd.jsPlumb.detachEveryConnection();""")
