Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');

var win = Titanium.UI.currentWindow;
win.title = win.params.newWindowTitle;

Ti.App.addEventListener('removePendingFriendRequestLabel', function(data) {
	Ti.API.info('unsetting..');
	win.setToolbar();
});

win.addEventListener('focus', function(e) {

	var parentModal = win.params.parentModal;
	var nav = win.params.nav;

	var done = Titanium.UI.createButton({
		systemButton:Titanium.UI.iPhone.SystemButton.DONE
	});
	done.addEventListener('click',function() 
	{
		parentModal.close();
	});
	win.setRightNavButton(done);
	var userID = win.params.userID;
	var getFriendRequestsRequest = Titanium.Network.createHTTPClient();
	getFriendRequestsRequest.onload = function() {
		var json = this.responseText;
		var response = JSON.parse(json);
		if (response.success) {
			var invitations = JSON.parse(response.invitations);
			var notReadInvitations = [];
			for (index in invitations) {
				if (!invitations[index].date_read) {
					notReadInvitations.push(invitations[index]);
				}
			}
			Ti.App.fireEvent('setProfileTabBadge', {'number' : notReadInvitations.length ? notReadInvitations.length : null});
			win.notReadInvitations = notReadInvitations;
			win.invitations = invitations;
		} else {
			win.invitations = null;
			win.notReadInvitations = null;
		}
		var notReadInvitations = win.notReadInvitations;
		var invitations = win.invitations;

		var friendsReq = Titanium.Network.createHTTPClient();
		friendsReq.open("GET", "http://crowdit.herokuapp.com/api/crowdit/user/friends/?userID=" + userID);
		var params = {
			userID : userID
		};
		friendsReq.setRequestHeader('Authorization', getOAuthHeader(friendsReq, params));
		friendsReq.setRequestHeader('Content-Type', 'application/json');
		friendsReq.send();
		friendsReq.onerror = function() {
			alert('Validation error');
		};
		friendsReq.onload = function() {
			var json = this.responseText;
			var response = JSON.parse(json);
			if (response.success) {
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

				var friends = JSON.parse(response.friends);
				for (var i = 0; i < friends.length; i++) {
					var row = Ti.UI.createTableViewRow();
					row.selectedBackgroundColor = '#fff';
					row.height = 100;
					row.className = 'datarow';
					row.clickName = 'row';

					var photo = Ti.UI.createImageView({
						image : friends[i].photo,
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
						text : friends[i].username
					});

					row.filter = user.text;
					row.add(user);

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
						text : 'Got some fresh fruit, conducted some business, took a nap'
					});
					row.add(comment);

					var calendar = Ti.UI.createView({
						backgroundImage : '../images/crowdit_tableview/eventsButton.png',
						bottom : 2,
						left : 70,
						width : 32,
						clickName : 'calendar',
						height : 32
					});
					row.add(calendar);

					var button = Ti.UI.createView({
						backgroundImage : '../images/crowdit_tableview/commentButton.png',
						top : 35,
						right : 5,
						width : 36,
						clickName : 'button',
						height : 34
					});
					row.newWindowTitle = friends[i].username;
					row.add(button);

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
						width : 100,
						clickName : 'date',
						text : 'posted on 3/11'
					});
					row.add(date);
					row.hasChild = true;
					row.profilePictureUrl = photo.image;
					row.username = user.text;
					row.id = friends[i].id;
					data.push(row);
				}
				tableView = Titanium.UI.createTableView({
					data : data,
					search : search,
					filterAttribute : 'filter',
					backgroundColor : 'white'
				});

				tableView.addEventListener('click', function(e) {
					var	nestedModalWindow = Titanium.UI.createWindow({
						url:Titanium.Filesystem.resourcesDirectory + 'main_windows/profile/profile.js',
						title:e.row.username,
						backgroundColor:'#fff',
						barColor:'#111',
						params:{
							newWindowTitle : e.row.username,
							userID : e.row.id,
							parentModal : parentModal,
							nav : nav,
							parent: win
						}
					});
					nav.open(nestedModalWindow,{animated:true});
				});
				win.add(tableView);
			} else {
				var scrollView = Titanium.UI.createScrollView({
					contentWidth : 'auto',
					contentHeight : 'auto',
					top : 0,
					showVerticalScrollIndicator : true,
					showHorizontalScrollIndicator : false
				});
				win.add(scrollView);

				var messageView = Titanium.UI.createView({
					bottom : 10,
					backgroundColor : '#111',
					height : 40,
					width : 270,
					borderRadius : 10
				});

				var messageLabel = Titanium.UI.createLabel({
					color : '#fff',
					text : 'No friends found.',
					height : 'auto',
					width : 'auto',
					textAlign : 'center'
				});

				messageView.add(messageLabel);
				scrollView.add(messageView);
			}
		};
		var flexSpace = Titanium.UI.createButton({
			systemButton : Titanium.UI.iPhone.SystemButton.FLEXIBLE_SPACE
		});
		if (invitations != null) {
			var friendRequests = Titanium.UI.createButton({
				title : 'You have pending friend requests!',
				backgroundColor:'#fff'
			});
			win.setToolbar([flexSpace, friendRequests, flexSpace]);
			friendRequests.addEventListener('click', function(e) {
				var	nestedModalWindow = Titanium.UI.createWindow({
					url:Titanium.Filesystem.resourcesDirectory + 'main_windows/profile/pendingFriendRequests.js',
					backgroundColor:'#fff',
					barColor:'#111',
					params:{
						newWindowTitle : 'Pending Friend Requests',
						invitations : invitations,
						parentModal : parentModal,
						nav : nav
					}
				});
				nav.open(nestedModalWindow,{animated:true});
			});
		} else {
			win.setToolbar();
		}
	};
	getFriendRequestsRequest.open("GET", "http://crowdit.herokuapp.com/api/crowdit/invite/pending/");
	getFriendRequestsRequest.setRequestHeader('Authorization', getOAuthHeader(getFriendRequestsRequest));
	getFriendRequestsRequest.setRequestHeader('Content-Type', 'application/json');
	getFriendRequestsRequest.send();
});
