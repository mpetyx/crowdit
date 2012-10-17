Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');

Titanium.UI.setBackgroundColor('#fff');

var tabGroup = Titanium.UI.createTabGroup();

var consumerSecret = Ti.App.Properties.getString("consumerSecret", '');

if (consumerSecret) {

	var tickets = Titanium.UI.createWindow({
		title : 'Generate QR Cod',
		url : 'main_windows/tickets.js',
	});

	var ticketsTab = Titanium.UI.createTab({
		title : 'Generate QR Code',
		window : tickets,
		icon : 'images/navbar/tickets.png'
	});

	var rewards = Titanium.UI.createWindow({
		title : 'Generate QR Cod',
		url : 'main_windows/rewards.js',
	});

	var rewardsTab = Titanium.UI.createTab({
		title : 'Rewards',
		window : tickets,
		icon : 'images/navbar/rewards.png'
	});

	var events = Titanium.UI.createWindow({
		title : 'Events',
		url : 'main_windows/events.js',
	});

	var eventsTab = Titanium.UI.createTab({
		title : 'Events',
		window : events,
		icon : 'images/navbar/stage.png'
	});

	var invite = Titanium.UI.createWindow({
		title : 'Invite',
		url : 'main_windows/invite.js'
	});

	var inviteTab = Titanium.UI.createTab({
		title : 'Invite',
		window : invite,
		icon : 'images/navbar/speaker.png'
	});

	var profile = Titanium.UI.createWindow({
		title : 'Profile',
		invitations : 0,
		params : {
			allowEditing : true
		},
		url : 'main_windows/profile.js',
		params: {'userID' : Ti.App.Properties.getString('userID', '')}
	});

	var profileTab = Titanium.UI.createTab({
		icon : Titanium.UI.iPhone.SystemIcon.CONTACTS,
		window : profile
	});

	tabGroup.addTab(rewardsTab);
	tabGroup.addTab(ticketsTab);
	tabGroup.addTab(eventsTab);
	tabGroup.addTab(inviteTab);
	tabGroup.addTab(profileTab);
} else {
	var login = Titanium.UI.createWindow({
		title : 'Login To Crowdit',
		url : 'main_windows/login.js'
	});

	var loginTab = Titanium.UI.createTab({
		title : "Login",
		window : login
	});

	var account = Titanium.UI.createWindow({
		title : 'Sign Up To Crowdit',
		url : 'main_windows/account.js'
	});

	var accountTab = Titanium.UI.createTab({
		title : 'New Account',
		window : account
	});

	tabGroup.addTab(loginTab);
	tabGroup.addTab(accountTab);
}

Ti.App.addEventListener('setProfileTabBadge', function(data) {
	Ti.API.info(profileTab + ' setProfileTabBadge : ' + data.number);
	profileTab.setBadge(data.number);
});

tabGroup.addEventListener('focus', function(e) {
	var getFriendRequestsRequest = Titanium.Network.createHTTPClient();
	getFriendRequestsRequest.onload = function() {
		var json = this.responseText;
		var response = JSON.parse(json);
		if (response.success) {
			var invitations = JSON.parse(response.invitations);
			var notReadInvitations = []
			for (index in invitations) {
				if (!invitations[index].date_read) {
					notReadInvitations.push(invitations[index]);
				}
			}
			Ti.App.fireEvent('setProfileTabBadge', {'number' : notReadInvitations.length ? notReadInvitations.length : null});
		}
	};
	getFriendRequestsRequest.open("GET", "http://crowdit.herokuapp.com/api/crowdit/invite/pending/");
	getFriendRequestsRequest.setRequestHeader('Authorization', getOAuthHeader(getFriendRequestsRequest));
	getFriendRequestsRequest.setRequestHeader('Content-Type', 'application/json');
	getFriendRequestsRequest.send();
});
tabGroup.open();

