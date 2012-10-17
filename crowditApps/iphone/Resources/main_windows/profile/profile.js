Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');

var win = Titanium.UI.currentWindow;
win.addEventListener('focus', function(e) {
	var nav = win.params.nav;
	var parentModal = win.params.parentModal;
	var parent = win.params.parent;
	var userID = win.params.userID;
	var getProfileDetailsRequest = Titanium.Network.createHTTPClient();
	getProfileDetailsRequest.onload = function() {
		var response = JSON.parse(this.responseText);
		if (response.success) {
			Ti.API.info(response);
			var profile = response.profile;
			var pendingInvitations = response.pendingInvitations;
			var allowEditing = profile.allowEditing;
			var profilePictureUrl = profile.photo;
			var isFriend = profile.isFriend;
			var profileID = profile.userID;
			var username = profile.username;
			var profilePictureUrl = profile.photo;
			var numberOfFriends = profile.numberOfFriends;
			var pendingInvitationExists = pendingInvitations.pendingInvitationExists;
			var canAccept = pendingInvitations.canAccept;
			var invitationMessage = pendingInvitations.invitationMessage
			var invitationID = pendingInvitations.invitationID;
			Ti.API.info(invitationID);
			if (allowEditing) {
				var moreBtn = Titanium.UI.createButton({
					backgroundImage : Titanium.Filesystem.resourcesDirectory + 'images/navbar/settings.png',
					hasChild : true,
					height : 33,
					width : 33
				});
				win.rightNavButton = moreBtn;
				moreBtn.addEventListener('click', function(e) {
					var params = {
						newWindowTitle : 'Options'
					};
					openNestedWindow(Titanium.Filesystem.resourcesDirectory + 'main_windows/more/more.js', params);
				});
			}
			var editProfileArea = Ti.UI.createView({
				backgroundColor : 'white',
				width : getPixels("35.00%", Titanium.Platform.displayCaps.platformWidth),
				height : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
				top : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
				right : getPixels("1.00%", Titanium.Platform.displayCaps.platformWidth),
				borderWidth : 1
			});

			var winsArea = Ti.UI.createView({
				backgroundColor : 'white',
				width : getPixels("35.00%", Titanium.Platform.displayCaps.platformWidth),
				height : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
				top : getPixels("1.00%", Titanium.Platform.displayCaps.platformHeight),
				right : getPixels("1.00%", Titanium.Platform.displayCaps.platformWidth),
				borderWidth : 1
			});
			var eventsArea = Ti.UI.createView({
				backgroundColor : 'white',
				width : getPixels("35.00%", Titanium.Platform.displayCaps.platformWidth),
				height : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
				top : getPixels("1.00%", Titanium.Platform.displayCaps.platformHeight),
				right : getPixels("35.00%", Titanium.Platform.displayCaps.platformWidth),
				borderWidth : 1,
				name : 'events',
				title : username + "'s events"
			});
			var awardsArea = Ti.UI.createView({
				backgroundColor : 'white',
				width : getPixels("35.00%", Titanium.Platform.displayCaps.platformWidth),
				height : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
				top : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
				right : getPixels("35.00%", Titanium.Platform.displayCaps.platformWidth),
				borderWidth : 1
			});

			var profilePictureArea = Ti.UI.createView({
				backgroundColor : 'white',
				width : getPixels("30.00%", Titanium.Platform.displayCaps.platformWidth),
				height : getPixels("29.00%", Titanium.Platform.displayCaps.platformHeight),
				top : getPixels("1.00%", Titanium.Platform.displayCaps.platformHeight),
				left : getPixels("1.00%", Titanium.Platform.displayCaps.platformWidth),
				borderWidth : 1
			});

			var friendsArea = Ti.UI.createView({
				backgroundColor : 'white',
				left : getPixels("1.00%", Titanium.Platform.displayCaps.platformWidth),
				right : getPixels("1.00%", Titanium.Platform.displayCaps.platformWidth),
				height : getPixels("10.00%", Titanium.Platform.displayCaps.platformHeight),
				top : getPixels("29.00%", Titanium.Platform.displayCaps.platformHeight),
				borderWidth : 1,
				title : username + "'s friends",
				name : 'friends'
			});
			if (profilePictureUrl) {
				var image = Titanium.UI.createImageView({
					title : 'Profile Picture',
					width : getPixels("25.00%", Titanium.Platform.displayCaps.platformWidth),
					height : getPixels("25.00%", Titanium.Platform.displayCaps.platformHeight),
					top : getPixels("2.00%", Titanium.Platform.displayCaps.platformHeight),
					left : getPixels("2.00%", Titanium.Platform.displayCaps.platformWidth)
				});
				var loadImage = function(url) {
					image.image = url;
				};
				loadImage(profilePictureUrl);
				profilePictureArea.add(image);
			} else {
				var profilePictureLabel = Ti.UI.createLabel({
					text : 'No profile picture uploaded',
					textAlign : 'center'
				});
				profilePictureArea.add(profilePictureLabel);
			}
			var eventsLabel = Ti.UI.createLabel({
				text : '23 events',
				textAlign : 'center',
				name : 'events',
				title : username + "'s events"
			});
			var awardsLabel = Ti.UI.createLabel({
				text : '24 awards',
				textAlign : 'center',
				name : 'awards'
			});
			var winsLabel = Ti.UI.createLabel({
				text : '25 wins',
				textAlign : 'center',
				name : 'wins'
			});

			var friendsLabel = Ti.UI.createLabel({
				text : numberOfFriends + ' Friends',
				textAlign : 'center',
				name : 'friends',
				title : username + "'s friends"
			});
			var editProfileLabel = Ti.UI.createLabel({
				text : 'Edit',
				textAlign : 'center',
				name : 'edit'
			});
			function clickOnAreasHandler(e) {
				if (isFriend || allowEditing) {
					var shouldContinueInModalMode = ['friends', 'events', 'edit', 'wins', 'awards'];
					if (inArray(shouldContinueInModalMode, e.source.name)) {
						var nestedModalWindow = Titanium.UI.createWindow({
							url : Titanium.Filesystem.resourcesDirectory + 'main_windows/profile/' + e.source.name + '.js',
							backgroundColor : '#fff',
							barColor : '#111',
							params : {
								newWindowTitle : e.source.title,
								userID : userID,
								parentModal : parentModal,
								nav : nav
							}
						});

						nav.open(nestedModalWindow, {
							animated : true
						});
					} else {
						redirectTo('profile/' + e.source.name + '.js');
					}
				} else {
					Ti.UI.createAlertDialog({
						title : 'Not a friend',
						message : 'You have to be friends with ' + username + " in order to see more details about " + username + " 's profile",
					}).show();
				}
			}


			friendsArea.addEventListener('click', clickOnAreasHandler);
			winsArea.addEventListener('click', clickOnAreasHandler);
			awardsArea.addEventListener('click', clickOnAreasHandler);
			eventsArea.addEventListener('click', clickOnAreasHandler);

			if (allowEditing) {
				editProfileArea.addEventListener('click', clickOnAreasHandler);
				editProfileArea.add(editProfileLabel);
				profilePictureArea.addEventListener('click', function(e) {
					var consumerSecret = Ti.App.Properties.getString("consumerSecret", '');
					var consumerKey = Ti.App.Properties.getString("consumerKey", '');

					Titanium.Media.openPhotoGallery({
						success : function(event) {
							var image = event.media;

							var uploadProfilePictureReq = Titanium.Network.createHTTPClient();

							uploadProfilePictureReq.onerror = function(e) {
								Ti.UI.createAlertDialog({
									title : 'Error',
									message : e.error
								}).show();
							};
							uploadProfilePictureReq.setTimeout(20000);
							uploadProfilePictureReq.onload = function(e) {
								var json = this.responseText;
								var response = JSON.parse(json);
								if (response.success) {
									Ti.UI.createAlertDialog({
										title : 'Success',
										message : 'Successfully uploaded your profile picrture!'
									}).show();
									var newProfilePictureUrl = response.profilePictureUrl;
									if (profilePictureUrl) {
										loadImage(newProfilePictureUrl);
									} else if (newProfilePictureUrl) {
										var image = Titanium.UI.createImageView({
											title : 'Profile Picture',
											width : getPixels("25.00%", Titanium.Platform.displayCaps.platformWidth),
											height : getPixels("25.00%", Titanium.Platform.displayCaps.platformHeight),
											top : getPixels("2.00%", Titanium.Platform.displayCaps.platformHeight),
											left : getPixels("3.00%", Titanium.Platform.displayCaps.platformWidth)
										});
										var loadImage = function(url) {
											image.image = url;
										};
										profilePictureArea.remove(profilePictureLabel);
										loadImage(newProfilePictureUrl);
										profilePictureArea.add(image);
									}
								} else {
									Ti.UI.createAlertDialog({
										title : 'Failure',
										message : 'Communication error'
									}).show();
								}
							};
							// open the client
							uploadProfilePictureReq.open("POST", "http://crowdit.herokuapp.com/api/crowdit/user/prof_picture_upload/");
							uploadProfilePictureReq.setRequestHeader('Authorization', getOAuthHeader(uploadProfilePictureReq));
							uploadProfilePictureReq.setRequestHeader("Content-Type", "multipart/form-data");

							// send the data
							uploadProfilePictureReq.send({
								file : image
							});

						},
						cancel : function() {

						},
						error : function(error) {
						},
						allowEditing : true
					});
				});
			}

			eventsArea.add(eventsLabel);
			winsArea.add(winsLabel);
			awardsArea.add(awardsLabel);
			friendsArea.add(friendsLabel);

			if (isFriend || allowEditing) {
				var data = [{
					title : 'John Econ added you as a friend',
					hasChild : true,
					color : 'red'
				}, {
					title : 'Iosif alvertis is going to Sakis Live',
					hasDetail : true,
					color : 'green'
				}, {
					title : 'Row 3',
					hasCheck : true,
					color : 'blue',
					selectedColor : '#fff'
				}, {
					title : 'Row 1',
					hasChild : true,
					color : 'red',
					selectedColor : '#fff'
				}];
				var tableview = Titanium.UI.createTableView({
					top : getPixels("43.00%", Titanium.Platform.displayCaps.platformHeight),
					data : data
				});
				win.add(tableview);
			} else if (pendingInvitationExists) {
				if (canAccept) {
					acceptDeclineButton = Ti.UI.createButton({
						title : 'Respond to Friend Request!',
						color : 'black',
						backgroundColor : '#5993E5',
						borderRadius : 8,
						backgroundImage : 'none',
						font : {
							fontFamily : 'Arial',
							fontWeight : 'bold',
							fontSize : 14
						},
						textAlign : 'center',
						width : getPixels("70.00%", Titanium.Platform.displayCaps.platformWidth),
						bottom : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
						height : getPixels("20.00%", Titanium.Platform.displayCaps.platformHeight)
					})
					acceptDeclineButton.addEventListener('click', function() {
						var alertDialog = Titanium.UI.createAlertDialog({
							title : 'Friend Request',
							message : 'From ' + username + ( invitationMessage ? ' : ' + invitationMessage : ''),
							buttonNames : ['Cancel', 'Deny', 'Accept']
						});
						alertDialog.show();
						alertDialog.addEventListener('click', function(e) {
							if (e.index == 1) {
								var params = {
									invitationID : invitationID
								};
								var declineFriendRequestReq = Titanium.Network.createHTTPClient();
								declineFriendRequestReq.onload = function() {
									var json = this.responseText;
									var response = JSON.parse(json);
									if (response.success) {
										alert(response.message);
										Ti.UI.currentWindow.fireEvent('focus');
										Ti.App.fireEvent('removeInvitation', {'invitationID' : invitationID});
										if (parent) {
											parent.fireEvent('focus');
										}
									}
								};
								declineFriendRequestReq.open("POST", "http://crowdit.herokuapp.com/api/crowdit/invite/decline/");
								declineFriendRequestReq.setRequestHeader('Authorization', getOAuthHeader(declineFriendRequestReq, params));
								declineFriendRequestReq.setRequestHeader('Content-Type', 'application/json');
								declineFriendRequestReq.send(params);
							} else if (e.index == 2) {
								var params = {
									invitationID : invitationID
								};
								var acceptFriendRequestReq = Titanium.Network.createHTTPClient();
								acceptFriendRequestReq.onload = function() {
									var json = this.responseText;
									var response = JSON.parse(json);
									if (response.success) {
										alert(response.message);
										Ti.UI.currentWindow.fireEvent('focus');
										Ti.App.fireEvent('removeInvitation', {'invitationID' : invitationID});
										if (parent) {
											parent.fireEvent('focus');
										}
									}
								};
								acceptFriendRequestReq.open("POST", "http://crowdit.herokuapp.com/api/crowdit/invite/accept/");
								acceptFriendRequestReq.setRequestHeader('Authorization', getOAuthHeader(acceptFriendRequestReq, params));
								acceptFriendRequestReq.setRequestHeader('Content-Type', 'application/json');
								acceptFriendRequestReq.send(params);
							}
						});
					});
					win.add(acceptDeclineButton);
				} else {
					pendingInvitationButton = Ti.UI.createButton({
						title : 'Friend Requested',
						color : 'black',
						backgroundColor : '#5993E5',
						borderRadius : 8,
						backgroundImage : 'none',
						font : {
							fontFamily : 'Arial',
							fontWeight : 'bold',
							fontSize : 14
						},
						width : getPixels("70.00%", Titanium.Platform.displayCaps.platformWidth),
						bottom : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
						height : getPixels("20.00%", Titanium.Platform.displayCaps.platformHeight)
					})
					win.add(pendingInvitationButton);
					pendingInvitationButton.addEventListener('click', function() {
						var alertDialog = Titanium.UI.createAlertDialog({
							title : 'Friend Requested',
							message : 'Do you want to cancel this invitation?',
							buttonNames : ['Cancel', 'Yes']
						});
						alertDialog.show();
						alertDialog.addEventListener('click', function(e) {
							if (e.index == 1) {
								var params = {
									invitationID : invitationID
								};
								var cancelFriendRequestReq = Titanium.Network.createHTTPClient();
								cancelFriendRequestReq.onload = function() {
									var json = this.responseText;
									var response = JSON.parse(json);
									if (response.success) {
										alert(response.message);
										Ti.UI.currentWindow.fireEvent('focus');
									}
								};
								cancelFriendRequestReq.open("POST", "http://crowdit.herokuapp.com/api/crowdit/invite/cancel/");
								cancelFriendRequestReq.setRequestHeader('Authorization', getOAuthHeader(cancelFriendRequestReq, params));
								cancelFriendRequestReq.setRequestHeader('Content-Type', 'application/json');
								cancelFriendRequestReq.send(params);
							}
						});
					});
				}
			} else {
				sendFriendRequestButton = Ti.UI.createButton({
					title : 'Add Friend',
					color : 'black',
					backgroundColor : '#5993E5',
					borderRadius : 8,
					backgroundImage : 'none',
					font : {
						fontFamily : 'Arial',
						fontWeight : 'bold',
						fontSize : 14
					},
					width : getPixels("70.00%", Titanium.Platform.displayCaps.platformWidth),
					bottom : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
					height : getPixels("20.00%", Titanium.Platform.displayCaps.platformHeight)
				})
				sendFriendRequestButton.addEventListener('click', function() {
					var alertDialog = Titanium.UI.createAlertDialog({
						title : 'Friend Request',
						message : 'Are you sure you want to add ' + username + ' as a friend?',
						buttonNames : ['Cancel', 'Yes']
					});
					alertDialog.show();
					alertDialog.addEventListener('click', function(e) {
						if (e.index == 1) {
							var sendFriendRequest = Titanium.Network.createHTTPClient();
							sendFriendRequest.onload = function() {
								var json = this.responseText;
								var response = JSON.parse(json);
								alert(response.message);
								Ti.UI.currentWindow.fireEvent('focus');
							};
							sendFriendRequest.onerror = function(e) {
								alert(e);
							};
							var params = {
								iusername_to : userID
							};
							sendFriendRequest.open("POST", "http://crowdit.herokuapp.com/api/crowdit/invite/send/");
							sendFriendRequest.setRequestHeader('Authorization', getOAuthHeader(sendFriendRequest, params));
							sendFriendRequest.setRequestHeader('Content-Type', 'application/json');
							sendFriendRequest.send(params);
						}
					});
				});
				win.add(sendFriendRequestButton);
			}

			// create table view
			var done = Titanium.UI.createButton({
				systemButton : Titanium.UI.iPhone.SystemButton.DONE
			});
			done.addEventListener('click', function() {
				parentModal.close();
			});
			win.setRightNavButton(done);
			win.add(eventsArea);
			win.add(winsArea);
			win.add(awardsArea);
			win.add(editProfileArea);
			win.add(profilePictureArea);
			win.add(friendsArea);
		} else {
			Ti.UI.createAlertDialog({
				title : 'Oops',
				message : 'Network error occured'
			}).show();
		}
	}
	getProfileDetailsRequest.ononerror = function() {
		Ti.UI.createAlertDialog({
			title : 'Oops',
			message : 'Network error occured'
		}).show();
	}
	getProfileDetailsRequest.open("GET", "http://crowdit.herokuapp.com/api/crowdit/user/profile/?userID=" + userID);
	params = {
		userID : userID
	};
	getProfileDetailsRequest.setRequestHeader('Authorization', getOAuthHeader(getProfileDetailsRequest, params));
	getProfileDetailsRequest.setRequestHeader('Content-Type', 'application/json');
	getProfileDetailsRequest.send();
});

