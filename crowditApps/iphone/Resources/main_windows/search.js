Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');

var win = Titanium.UI.currentWindow;

var scrollView = Titanium.UI.createScrollView({
	contentWidth : 'auto',
	contentHeight : 'auto',
	top : 0,
	showVerticalScrollIndicator : true,
	showHorizontalScrollIndicator : false
});
win.add(scrollView);

var usernameField = Titanium.UI.createTextField({
	hintText : 'Enter a username',
	height : 35,
	top : 35,
	left : 30,
	width : 250,
	borderStyle : Titanium.UI.INPUT_BORDERSTYLE_ROUNDED
});
scrollView.add(usernameField);

var searchBtn = Titanium.UI.createButton({
	title : 'Search For Crowdit User',
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
scrollView.add(searchBtn);

searchBtn.addEventListener('click', function() {
	if (usernameField.value) {
		var getUserReq = Titanium.Network.createHTTPClient();
		getUserReq.onload = function() {
			var json = this.responseText;
			var response = JSON.parse(json);
			if (response.success) {
				var sendFriendRequestBtn = Titanium.UI.createButton({
					title : 'Send Friend Request To ' + response.user,
					top : 160,
					width : 90,
					height : 35,
					borderRadius : 1,
					font : {
						fontFamily : 'Arial',
						fontWeight : 'bold',
						fontSize : 14
					}
				});
				scrollView.add(sendFriendRequestBtn);
				sendFriendRequestBtn.addEventListener('click', function() {
					var sendFriendRequest = Titanium.Network.createHTTPClient();
					sendFriendRequest.onload = function() {
						var json = this.responseText;
						var response = JSON.parse(json);
						alert(response.message);
					};
					sendFriendRequest.onerror = function(e) {
						alert(e);
					};
					var params = {
						iusername_to : response.userID
					};
					sendFriendRequest.open("POST", "http://crowdit.herokuapp.com/api/crowdit/invite/send/");
					sendFriendRequest.setRequestHeader('Authorization', getOAuthHeader(sendFriendRequest, params));
					sendFriendRequest.setRequestHeader('Content-Type', 'application/json');
					sendFriendRequest.send(params);
				});
			} else {
				Ti.UI.createAlertDialog({
					title : 'Oops',
					message : response.message
				}).show();
			}
		};
		getUserReq.onerror = function() {
			Ti.UI.createAlertDialog({
				title : 'Error',
				message : 'Communication error'
			}).show();
		};
		getUserReq.open("GET", "http://crowdit.herokuapp.com/api/crowdit/user/search/?username=" + usernameField.value);
		params = {
			username : usernameField.value
		};
		getUserReq.setRequestHeader('Authorization', getOAuthHeader(getUserReq, params));
		getUserReq.setRequestHeader('Content-Type', 'application/json');
		getUserReq.send();
	} else {
		alert("Please provide a username");
	}
}); 