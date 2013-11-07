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
 * Space shader - handles nightside albedo/urban lighting map
 * Supports up to tertiary solar systems (well, not yet)
 * 
 * Requires three.js r51 or later
 */

function split_code( code_str ) {
    var main = code_str.indexOf("void main()");
    var idx1 = code_str.lastIndexOf( "\n", main );
    var idx2 = code_str.indexOf( "\n", main ) + 1;
    var end = code_str.length - 1;
    return [ code_str.substring( 0, idx1 ), code_str.substring( idx2, end ) ];
}

var _normal_fragshader = THREE.ShaderLib[ "normalmap" ].fragmentShader;
var _normal_frag_parts = split_code( _normal_fragshader );
var _normal_frag_decl  = _normal_frag_parts[0];
var _normal_frag_main  = _normal_frag_parts[1];

var _normal_vertshader = THREE.ShaderLib[ "normalmap" ].vertexShader;
var _normal_vert_parts = split_code( _normal_vertshader );
var _normal_vert_decl  = _normal_vert_parts[0];
var _normal_vert_main  = _normal_vert_parts[1];


var spaceShader = {
    PLANET_MODE: 0,
    ATMOSPHERE_MODE: 1,

    uniforms: THREE.UniformsUtils.merge( [
	THREE.ShaderLib[ "normalmap" ].uniforms,
	{
	    "mode": { type: "i", value: 0 },

	    // planet rendering
	    "tDay": { type: "t",
		      value: THREE.ImageUtils.generateDataTexture(
			  1024, 512, new THREE.Color( 0xffffff ) ) },
	    "tNight": { type: "t",
			value: THREE.ImageUtils.generateDataTexture(
			    1024, 512, new THREE.Color( 0xffffff ) ) },
	    "dirPrimary": { type: "v3", value: new THREE.Vector3( 1, 0, -1 ) },
	    "magPrimary": { type: "f", value: 0.0 },
	    "dirSecondary": { type: "v3", value: new THREE.Vector3( -1, 0, -1 ) },
	    "magSecondary": { type: "f", value: 0.0 },
	    "dirTertiary": { type: "v3", value: new THREE.Vector3( 1, 1, 0 ) },
	    "magTertiary": { type: "f", value: 0.0 },

	    // atmosphere rendering
	    "glowView" : { type: "v3", value: new THREE.Vector3( 0, 0, 1 ) },
	    "glowC":   { type: "f", value: 0.6 },
	    "glowP":   { type: "f", value: 6.0 },
	    "glowColor" : { type: "c", value: new THREE.Color( 0xffffff ) },
	},
    ] ),

    fragmentShader: [
	"",
	"uniform int mode;",
	"uniform sampler2D tDay;",
	"uniform sampler2D tNight;",
	"uniform vec3 dirPrimary;",
	"uniform float magPrimary;",
	"uniform vec3 dirSecondary;",
	"uniform float magSecondary;",
	"uniform vec3 dirTertiary;",
	"uniform float magTertiary;",
	"uniform vec3 glowColor;",
	"varying float intensity;",
	"#ifdef GL_ES",
	"precision highp float;",
	"#endif",
	"",
	_normal_frag_decl,
	"void main() {",
	"  if ( mode == 0 ) {",
	_normal_frag_main,
	"    // Space shader functionality",
	"    vec3 dayColor = texture2D( tDay, vUv ).xyz;",
	"    vec3 nightColor = texture2D( tNight, vUv ).xyz;",
	"    vec3 norm = normalize( vNormal );",
	"    if ( magPrimary > 0.0 ) {",
	"      vec4 posPrimary = viewMatrix * vec4( dirPrimary, 0.0 );",
	"      vec3 relDirPrimary = normalize( posPrimary.xyz );",
	"      float magP = clamp( magPrimary, 0.0, 1.0);",
	"      if ( !enableDiffuse )",
	"        gl_FragColor.xyz = dayColor * magP;",
	"      float starOneAngle = dot( norm, relDirPrimary );",
	"      starOneAngle = clamp( starOneAngle * 10.0, -1.0, 1.0);",
    	"      float mixOneAmt = starOneAngle * 0.5 + 0.5;",
    	"      gl_FragColor.xyz = mix( nightColor, gl_FragColor.xyz, mixOneAmt * magP);",
    	// FIXME test multi-mixing for multiple light sources
	"      if ( magSecondary > 0.0 ) {",
	"        vec4 posSecondary = viewMatrix * vec4( dirSecondary, 0.0 );",
	"        vec3 relDirSecondary = normalize( posSecondary.xyz );",
	"        float magS = clamp( magSecondary, 0.0, 1.0);",
	"        float starTwoAngle = dot( norm, relDirSecondary );",
	"        starTwoAngle = clamp( starTwoAngle * 10.0, -1.0, 1.0);",
    	"        float mixTwoAmt = starTwoAngle * 0.5 + 0.5;",
    	"        gl_FragColor.xyz = mix( nightColor, gl_FragColor.xyz, mixTwoAmt * magS );",
	"        if ( magTertiary > 0.0 ) {",
	"          vec4 posTertiary = viewMatrix * vec4( dirTertiary, 0.0 );",
	"          vec3 relDirTertiary = normalize( posTertiary.xyz );",
	"          float magT = clamp( magTertiary, 0.0, 1.0);",
	"          float starThreeAngle = dot( norm, relDirTertiary );",
	"          starThreeAngle = clamp( starThreeAngle * 10.0, -1.0, 1.0);",
    	"          float mixThreeAmt = starThreeAngle * 0.5 + 0.5;",
    	"          gl_FragColor.xyz = mix( nightColor, gl_FragColor.xyz, mixThreeAmt * magT );",
	"        }",
	"      }",
	"    }",
	"  }",
	"  else if ( mode == 1 ) {",
	"    vec3 glow = glowColor * intensity;",
	"    gl_FragColor = vec4( glow, 1.0 );",
	"  }",
	"}",
    ].join("\n"),
	
    vertexShader: [
	"",
	"uniform int mode;",
	"uniform vec3 glowView;",
	"uniform float glowC;",
	"uniform float glowP;",
	"varying float intensity;",
	"",
	_normal_vert_decl,
	"void main() {",
	"  if ( mode == 0 ) {",
	_normal_vert_main,
	"  }",
	"  else if ( mode == 1 ) {",
	"    vec3 vNormal = normalize( normalMatrix * normal );",
	"    vec3 vNormel = normalize( normalMatrix * glowView );",
	"    intensity = pow( glowC - dot(vNormal, vNormel), glowP );",
	"    gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );",
	"  }",
	"}",
	].join("\n"),

};


// Disallow empty uniforms values
spaceShader.uniforms["tNormal"].value =
    THREE.ImageUtils.generateDataTexture( 1024, 512, new THREE.Color( 0xffffff ) );
spaceShader.uniforms["ambientLightColor"].value = [ 1.0, 1.0, 1.0 ];
spaceShader.uniforms["directionalLightDirection"].value = [ 0.0, 0.0, 0.0 ];
spaceShader.uniforms["directionalLightColor"].value = [ 1.0, 1.0, 1.0 ];
