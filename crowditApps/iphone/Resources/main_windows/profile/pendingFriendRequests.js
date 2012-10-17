Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');

var win = Titanium.UI.currentWindow;
win.title = win.params.newWindowTitle;
var parentModal = win.params.parentModal;
var nav = win.params.nav;
var invitations = win.params.invitations;
var readInvitationIDs = '';
for (index in invitations) {
	if (!invitations[index].date_read) {
		readInvitationIDs += invitations[index].id + ',';
	};
}
if (readInvitationIDs) {
	readInvitationIDs = readInvitationIDs.slice(0, -1);
	var readFriendRequestReq = Titanium.Network.createHTTPClient();
	readFriendRequestReq.onload = function() {
		var json = this.responseText;
		var response = JSON.parse(json);
		if (response.success) {
			Titanium.UI.currentTab.badge = null;
		}
	};
	var params = {
		invitationIDs : readInvitationIDs
	};
	Ti.API.info(params);
	readFriendRequestReq.open("POST", "http://crowdit.herokuapp.com/api/crowdit/invite/read/");
	readFriendRequestReq.setRequestHeader('Authorization', getOAuthHeader(readFriendRequestReq, params));
	readFriendRequestReq.setRequestHeader('Content-Type', 'application/json');
	readFriendRequestReq.send(params);
}
var search = Titanium.UI.createSearchBar({
	barColor : '#385292',
	showCancel : false
});
search.addEventListener('change', function(e) {
	e.value // search string as user types
});
search.addEventListener('return', function(e) {
	search.blur();
});
search.addEventListener('cancel', function(e) {
	search.blur();
});

var tableView;
var data = [];

// create a var to track the active row
var currentRow = null;
var currentRowIndex = null;

for (var i = 0; i < invitations.length; i++) {
	var row = Ti.UI.createTableViewRow();
	row.selectedBackgroundColor = '#fff';
	row.height = 100;
	row.className = 'datarow';
	row.clickName = 'row';

	var photo = Ti.UI.createImageView({
		image : invitations[i].photo,
		top : 5,
		left : 10,
		width : 50,
		height : 50,
		clickName : 'photo'
	});
	row.add(photo);

	var user = Ti.UI.createLabel({
		color : '#576996',
		font : {
			fontSize : 16,
			fontWeight : 'bold',
			fontFamily : 'Arial'
		},
		left : 70,
		top : 2,
		height : 30,
		width : 200,
		clickName : 'user',
		text : invitations[i].username
	});

	row.filter = user.text;
	row.add(user);
	row.invitationID = invitations[i].id;
	row.username = invitations[i].username;
	row.userID = invitations[i].userID;

	var fontSize = 16;
	if (Titanium.Platform.name == 'android') {
		fontSize = 14;
	}
	var comment = Ti.UI.createLabel({
		color : '#222',
		font : {
			fontSize : fontSize,
			fontWeight : 'normal',
			fontFamily : 'Arial'
		},
		left : 70,
		top : 21,
		height : 50,
		width : 200,
		clickName : 'comment',
		text : invitations[i].message
	});
	row.add(comment);

	var calendar = Ti.UI.createView({
		backgroundImage : Titanium.Filesystem.resourcesDirectory + 'images/crowdit_tableview/eventsButton.png',
		bottom : 2,
		left : 70,
		width : 32,
		clickName : 'calendar',
		height : 32
	});
	row.add(calendar);

	var acceptButton = Ti.UI.createView({
		backgroundImage : Titanium.Filesystem.resourcesDirectory + 'images/accept.gif',
		top : 35,
		right : 5,
		width : 36,
		clickName : 'acceptButton',
		invitationID : invitations[i].id,
		index : i,
		height : 34
	});
	row.add(acceptButton);

	var declineButton = Ti.UI.createView({
		backgroundImage : Titanium.Filesystem.resourcesDirectory + 'images/decline.gif',
		top : 35,
		right : 60,
		width : 36,
		clickName : 'declineButton',
		invitationID : invitations[i].id,
		index : i,
		height : 34
	});
	row.add(declineButton);

	var date = Ti.UI.createLabel({
		color : '#999',
		font : {
			fontSize : 13,
			fontWeight : 'normal',
			fontFamily : 'Arial'
		},
		left : 105,
		bottom : 5,
		height : 20,
		width : 200,
		clickName : 'date',
		text : 'posted on ' + invitations[i].sent
	});
	row.add(date);

	data.push(row);
}
tableView = Titanium.UI.createTableView({
	data : data,
	search : search,
	filterAttribute : 'filter',
	backgroundColor : 'white'
});

Ti.App.addEventListener('removeInvitation', function(data) {
	Ti.API.info('removeInvitation..');
	var sections = tableView.data;
	Ti.API.info(sections);
	for(var i = 0; i < sections.length; i++){
	    var section = sections[i];
	    for(var j = 0; j < section.rowCount; j++){
	        var row = section.rows[j];
	        Ti.API.info(row.invitationID + ' shouldBe Equal with ' + data.invitationID);
	        if (row.invitationID == data.invitationID) {
	        	Ti.API.info('so close to delete');
	        	tableView.deleteRow(row.index);
	        }
	    }
	}
});

tableView.addEventListener('click', function(e) {
	var params = {
		invitationID : e.source.invitationID
	};
	if (e.source.clickName == 'acceptButton') {
		var acceptFriendRequestReq = Titanium.Network.createHTTPClient();
		acceptFriendRequestReq.onload = function() {
			var json = this.responseText;
			var response = JSON.parse(json);
			if (response.success) {
				tableView.deleteRow(e.source.index);
				if (!getTableLength(tableView)) {
					Ti.App.fireEvent('removePendingFriendRequestLabel');
				}
				Ti.UI.createAlertDialog({
					title : 'Success!',
					message : response.message
				}).show();
			}
		};
		acceptFriendRequestReq.open("POST", "http://crowdit.herokuapp.com/api/crowdit/invite/accept/");
		acceptFriendRequestReq.setRequestHeader('Authorization', getOAuthHeader(acceptFriendRequestReq, params));
		acceptFriendRequestReq.setRequestHeader('Content-Type', 'application/json');
		acceptFriendRequestReq.send(params);
	} else if (e.source.clickName == 'declineButton') {
		var declineFriendRequestReq = Titanium.Network.createHTTPClient();
		declineFriendRequestReq.onload = function() {
			var json = this.responseText;
			var response = JSON.parse(json);
			if (response.success) {
				tableView.deleteRow(e.source.index);
				if (!getTableLength(tableView)) {
					Ti.App.fireEvent('removePendingFriendRequestLabel');
				}
				Ti.UI.createAlertDialog({
					title : 'Success!',
					message : response.message
				}).show();
			}
		};
		declineFriendRequestReq.open("POST", "http://crowdit.herokuapp.com/api/crowdit/invite/decline/");
		declineFriendRequestReq.setRequestHeader('Authorization', getOAuthHeader(declineFriendRequestReq, params));
		declineFriendRequestReq.setRequestHeader('Content-Type', 'application/json');
		declineFriendRequestReq.send(params);
	} else {
		var nestedModalWindow = Titanium.UI.createWindow({
			url : Titanium.Filesystem.resourcesDirectory + 'main_windows/profile/profile.js',
			title : e.row.username,
			backgroundColor : '#fff',
			barColor : '#111',
			params : {
				newWindowTitle : e.row.username,
				userID : e.row.userID,
				parentModal : parentModal,
				nav : nav,
				parent : win
			}
		});
		nav.open(nestedModalWindow, {
			animated : true
		});
	}
	Ti.API.info(e.source.clickName);
});
win.add(tableView); 