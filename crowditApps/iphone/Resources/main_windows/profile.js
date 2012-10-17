Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');

var win = Titanium.UI.currentWindow;
win.addEventListener('focus', function(e) {
	var userID = win.params.userID;
	var isModal = win.params.isModal;
	Ti.API.info(' userID ,  ' + win.params.userID);
	var getProfileDetailsRequest = Titanium.Network.createHTTPClient();
	getProfileDetailsRequest.onload = function() {
		var response = JSON.parse(this.responseText);
		if (response.success) {
			Ti.API.info(response);
			var profile = response.profile;
			var allowEditing = profile.allowEditing;
			var profilePictureUrl = profile.photo;
			var isFriend = profile.isFriend;
			var pendingInvitationExists = profile.pendingInvitationExists;
			var profileID = profile.userID;
			var username = profile.username;
			var profilePictureUrl = profile.photo;
			var numberOfFriends = profile.numberOfFriends;
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
				name : 'events'
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
				name : 'events'
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
				name : 'friends'
			});
			var editProfileLabel = Ti.UI.createLabel({
				text : 'Edit',
				textAlign : 'center',
				name : 'edit'
			});
			function clickOnAreasHandler(e) {
				if (e.source.name == 'friends') {
					var modal = Ti.UI.createWindow({
						navBarHidden:true
					});
					var nav = Ti.UI.iPhone.createNavigationGroup({
						backgroundColor:'blue'
					});
					modalWin = Titanium.UI.createWindow({
						url:Titanium.Filesystem.resourcesDirectory + 'main_windows/profile/' + e.source.name + '.js',
						title:username + "'s friends",
						backgroundColor:'#fff',
						barColor:'#111',
						params:{
							newWindowTitle : username + "'s friends",
							userID : userID,
							parentModal: modal,
							nav : nav
						}
					});
					nav.window = modalWin;
					var done = Titanium.UI.createButton({
						systemButton:Titanium.UI.iPhone.SystemButton.DONE
					});
					done.addEventListener('click',function() 
					{
						modal.close();
					});
					modalWin.setRightNavButton(done);
					modal.add(nav);
					modal.open({modal:true});
						// Titanium.UI.currentTab.open(win,{animated:true});
				} else {
					redirectTo('profile/' + e.source.name + '.js');
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
			}, {
				title : 'Row 2',
				hasDetail : true,
				color : 'green',
				selectedColor : '#fff'
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
			}, {
				title : 'Row 2',
				hasDetail : true,
				color : 'green',
				selectedColor : '#fff'
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
			}, {
				title : 'Row 2',
				hasDetail : true,
				color : 'green',
				selectedColor : '#fff'
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
			}, {
				title : 'Row 2',
				hasDetail : true,
				color : 'green',
				selectedColor : '#fff'
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
			}, {
				title : 'Row 2',
				hasDetail : true,
				color : 'green',
				selectedColor : '#fff'
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
			}, {
				title : 'Row 2',
				hasDetail : true,
				color : 'green',
				selectedColor : '#fff'
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
			}, {
				title : 'Row 2',
				hasDetail : true,
				color : 'green',
				selectedColor : '#fff'
			}, {
				title : 'Row 3',
				hasCheck : true,
				color : 'blue',
				selectedColor : '#fff'
			}, {
				title : 'Row 4',
				color : 'orange',
				selectedColor : '#fff'
			}];

			// create table view
			var tableview = Titanium.UI.createTableView({
				top : getPixels("43.00%", Titanium.Platform.displayCaps.platformHeight),
				data : data
			});
			if (isModal) {
				var done = Titanium.UI.createButton({
					systemButton:Titanium.UI.iPhone.SystemButton.DONE
				});
				done.addEventListener('click',function() 
				{
					win.params.parentModal.close();
				});
				win.setRightNavButton(done);
			}
			win.add(tableview);
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

