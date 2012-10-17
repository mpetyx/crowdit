Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');

var win = Titanium.UI.currentWindow;

var username = Titanium.UI.createTextField({
	color : '#336699',
	top : 10,
	left : 10,
	width : 300,
	height : 40,
	hintText : 'Username',
	keyboardType : Titanium.UI.KEYBOARD_DEFAULT,
	returnKeyType : Titanium.UI.RETURNKEY_DEFAULT,
	borderStyle : Titanium.UI.INPUT_BORDERSTYLE_ROUNDED
});
win.add(username);

var password = Titanium.UI.createTextField({
	color : '#336699',
	top : 60,
	left : 10,
	width : 300,
	height : 40,
	hintText : 'Password',
	passwordMask : true,
	keyboardType : Titanium.UI.KEYBOARD_DEFAULT,
	returnKeyType : Titanium.UI.RETURNKEY_DEFAULT,
	borderStyle : Titanium.UI.INPUT_BORDERSTYLE_ROUNDED
});
win.add(password);

var loginBtn = Titanium.UI.createButton({
	title : 'Login',
	top : 110,
	width : 90,
	height : 35,
	borderRadius : 1,
	font : {
		fontFamily : 'Arial',
		fontWeight : 'bold',
		fontSize : 14
	}
});
win.add(loginBtn);

var loginReq = Titanium.Network.createHTTPClient();
loginReq.onload = function() {
	var json = this.responseText;
	var response = JSON.parse(json);
	if (response.success == true) {
		Ti.App.Properties.setString("consumerKey", response.key);
		Ti.App.Properties.setString("consumerSecret", response.secret);
		Ti.App.Properties.setString("userID", response.userID);
		alert("Hello " + response.name + "! Welcome back to Crowdit!");
		redirectTo('../app.js');
	} else {
		alert(response.message);
	}
};

loginReq.onerror = function() {
	alert("Network error");
};

/*
 * Login Button Click Event
 */

loginBtn.addEventListener('click', function(e) {
	if (username.value != '' && password.value != '') {
		loginReq.open("POST", "http://crowdit.herokuapp.com/api/crowdit/user/signin/");
		var params = {
			username : username.value,
			password : Ti.Utils.md5HexDigest(password.value)
		};
		loginReq.send(params);
	} else {
		alert("Username/Password are required");
	}
});

