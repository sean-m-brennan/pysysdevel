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


User = {
    /**
     * generates a random hex string
     */
    randomString: function(len) {
	var hex = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'];
	var string = "";
	while(len-->0) { string += hex[parseInt(16*Math.random())]; }
	return string;
    },
    
    /**
     * marks an input field as invalid/problematic
     */
    markInvalid: function(input, reason) {
	var classes = "";
	if (input.class) {
	    classes = input.getAttribute("class");
	}
	input.setAttribute("class", classes + " error");
	input.title = reason;
	document.getElementById("error").innerHTML = reason;
	return false;
    },
    
    /**
     * marks an input field as having passed validation
     */
    markValid: function(input) {
	if (input.getAttribute("class")) {
	    var stripped = input.getAttribute("class").replace("error", "");
	    input.setAttribute("class", stripped);
	}
	input.title = "";
	return true;
    },

    /**
     * user name validator
     */
    validName: function(input) {
	var username = input.value;
	if (username.trim() == "") {
	    return this.markInvalid(input, "You forgot your user name.");
	}
	if (username.indexOf("'") > -1) {
	    return this.markInvalid(input, "Apostrophes are not allowed in user names.");
	}
	if (username.length < 4) {
	    return this.markInvalid(input, "Sorry, user names must be more than 3 letters.");
	}
	return this.markValid(input);
    },


    /**
     * checks whether the twice typed password is the same
     */
    passwordMatch: function(input1, input2) {
	var matched = (input1.value==input2.value);
	if (!matched) {
	    return this.markInvalid(input2, "The two passwords don't match");
	}
	return this.markValid(input2);
    },

    /**
     * Checks whether there is a password set
     */
    validPassword: function(input) {
	var password = input.value;
	if (password.trim()=="") {
	    return this.markInvalid(input, "You need to fill in a password");
	}
	return this.markValid(input);
    },

    /**
     * Checks whether the password is strong enough.
     */
    strongPassword: function(input) {
	var password = input.value;
	if (!this.validPassword(input)) {
	    return false;
	}
	// you want to mofidy the following line to suit your personal preference in
	// secure passwords. And remember that any policy you set has to work in an
	// international setting. Passwords can contain any Unicode character, and
	// are case sensitive. Don't rely on space-separated words, because several
	// big languages don't use spaces. Don't demand "numbers and letters" because
	// that just confuses your users. If you want to enforce strong passwords,
	// calculate how easy it is to guess the password, and report how quickly
	// you can figure out their password so that they pick a better one.
	if (password.length<8) {
	    return this.markInvalid(input, "Your password is too easy to guess, please pick something longer.");
	}
	// FIXME password validation
	return this.markValid(input);
    },


    register: function () {
	$("#contents").css({  
            "opacity": "0.4"  
	});  
	$("#regpopup").css({  
            "opacity": "1.0"  
	});  
	$("#contents").fadeIn("slow");  
	$("#regpopup").fadeIn("slow");  
    },

    unregister: function () {
	$("#contents").css({  
	    "opacity": "1.0"  
	});  
	$("#contents").fadeIn("slow");  
	$("#regpopup").fadeOut("slow");  
    },

    profile: function () {
	$("#contents").css({  
            "opacity": "0.4"  
	});  
	$("#profilepopup").css({  
            "opacity": "1.0"  
	});  
	$("#contents").fadeIn("slow");  
	$("#profilepopup").fadeIn("slow");  
    },

    unprofile: function () {
	$("#contents").css({  
	    "opacity": "1.0"  
	});  
	$("#contents").fadeIn("slow");  
	$("#profilepopup").fadeOut("slow");  
    },

    /**
     * Validate all values used for user registration, before submitting the form.
     *
     * NOTE: while this function does front-end validation, it is possible to bypass
     * this function using a javascript console. So, in addition to this client-side
     * validation the server will also be performing validation once it receives the data
     */
    processRegistration: function() {
	var valid = true;
	var form = document.getElementById('registration');

	valid &= this.validName(form["username"]);
	valid &= this.validEmail(form["email"]);

	if (valid) {
	    form.submit();
	    console.log("Submit registration.");
	    //this.unregister();
 	}
    },

    /**
     * Validate all values used for user log in, before submitting the form.
     *
     * NOTE: while this function does front-end validation, it is possible to bypass
     * this function using a javascript console. So, in addition to this client-side
     * validation the server will also be performing validation once it receives the data
     */
    processLogin: function() {
	var valid = true;
	var form = document.getElementById('login');

	valid &= this.validName(form["username"]);
	valid &= this.validPassword(form["password1"]);

	if (valid) {
	    form.submit();
	}
    },

    /**
     * Validate all values used for email/password updating, before submitting the form.
     *
     * NOTE: while this function does front-end validation, it is possible to bypass
     * this function using a javascript console. So, in addition to this client-side
     * validation the server will also be performing validation once it receives the data
     */
    processUpdate: function() {
	var valid = true;
	var update = false;
	var form = document.getElementById('update');

	if ("email" in form && form["email"].value.trim()!="") {
	    valid &= this.validEmail(form["email"]);
	    if (valid) {
		update = true;
	    }
	}

	if (form["password1"].value.trim()!="") {
	    valid &= this.passwordMatch(form["password1"], form["password2"]);
	    valid &= this.strongPassword(form["password1"]);
	    if (valid) {
		update = true;
	    }
	}
	if (valid && update) {
	    form.submit();
	}
    },

    // ------------------------------------------------------------

    /**
     * A static shorthand function for appendChild
     */
    add: function(p, c) {
	p.appendChild(c);
    },

    /**
     * A more useful function for creating HTML elements.
     */
    make: function(tag, properties) {
	var tag = document.createElement(tag);
	if (properties !== null) {
	    for (property in properties) {
		tag[property] = properties[property];
	    }
	}
	return tag;
    },

    /**
     * Inject a generic login form into the element passed as "parent"
     */
    injectLogin: function(parent) {
	// eliminate the need to type "this." everywhere in the function
	var add = this.add;
	var make = this.make;

	var form = this.make("form", {id: "usered_login_form", action: ".", method: "POST"});
	add(form, make("label", {for: "usered_username", innerHTML: "user name"}));
	add(form, make("input", {id: "usered_username", type: "text"}));
	add(form, make("label", {for: "usered_password", innerHTML: "password"}));
	add(form, make("input", {id: "usered_password", type: "password"}));
	add(form, make("input", {id: "usered_login_button", type: "submit", value: "log in"}));
	add(parent, form);
    },

    /**
     * Inject a generic logout form into the element passed as "parent"
     */
    injectLogout: function(parent) {
	// eliminate the need to type "this." everywhere in the function
	var add = this.add;
	var make = this.make;

	var form = make("form", {id: "usered_logout_form", action: ".", method: "POST"});
	add(form, make("input", {type: "hidden", name: "op", value: "logout"}));
	add(form, make("input", {id: "usered_logout_button", type: "submit", value: "log out"}));
	add(parent, form)
    },

    lookup_user: function() {
	var who = document.getElementById("update_user").value;
	var form = document.createElement("form");
	form.setAttribute("method", "post");
	path = window.location.pathname;
	form.setAttribute("action", path);
	var op = document.createElement("input");
	op.setAttribute("type", "hidden");
	op.setAttribute("name", "op");
	op.setAttribute("value", "query");
	form.appendChild(op);
	var un = document.createElement("input");
	un.setAttribute("type", "hidden");
	un.setAttribute("name", "username");
	un.setAttribute("value", who);
	form.appendChild(un);
	document.body.appendChild(form);
	form.submit();
    },

    unique_user: function() {
	var who = document.getElementById("reg_username").value;
	var form = document.createElement("form");
	form.setAttribute("method", "post");
	path = window.location.pathname;
	form.setAttribute("action", path);
	var op = document.createElement("input");
	op.setAttribute("type", "hidden");
	op.setAttribute("name", "op");
	op.setAttribute("value", "unique");
	form.appendChild(op);
	var un = document.createElement("input");
	un.setAttribute("type", "hidden");
	un.setAttribute("name", "username");
	un.setAttribute("value", who);
	form.appendChild(un);
	document.body.appendChild(form);
	form.submit();
    },

    delete_task: function(form) {
	var del = confirm("Deleting task.");
	if (del) {
	    form.submit();
	}
    },

    /**
     * email address validator -- this uses the simplified email validation
     * RegExp found on http://www.regular-expressions.info
     */
    validEmail: function(input) {
	var valid = /[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?/.test(input.value);
        if(!valid) {
	    return this.markInvalid(input,"This is not a real email address...");
	}
        return this.markValid(input);
    },
};
