Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');

var win = Titanium.UI.currentWindow;
win.addEventListener('focus', function(e) {
	var eventAnnotation = Titanium.Map.createAnnotation({
		latitude : win.params.lat,
		longitude : win.params.lon,
	});
	eventAnnotation.addEventListener('click', function(evt) {
	});
	var mapview = Titanium.Map.createView({
		mapType : Titanium.Map.STANDARD_TYPE,
		region : {
			latitude : win.params.lat,
			longitude : win.params.lon,
			latitudeDelta : 0.05,
			longitudeDelta : 0.05
		},
		animate : true,
		regionFit : true,
		userLocation : true,
		width : getPixels("45.00%", Titanium.Platform.displayCaps.platformWidth),
		height : getPixels("35.00%", Titanium.Platform.displayCaps.platformHeight),
		top : getPixels("2.00%", Titanium.Platform.displayCaps.platformHeight),
		right : getPixels("2.00%", Titanium.Platform.displayCaps.platformWidth),
	});
	mapview.addAnnotation(eventAnnotation);
	mapview.selectAnnotation(eventAnnotation);
	mapview.addEventListener('click', function(evt) {
	});
	win.add(mapview);
	zoomin = Titanium.UI.createButton({
		title : '+',
		style : Titanium.UI.iPhone.SystemButtonStyle.BORDERED
	});
	// button to zoom-out
	zoomout = Titanium.UI.createButton({
		title : '-',
		style : Titanium.UI.iPhone.SystemButtonStyle.BORDERED
	});
	zoomin.addEventListener('click', function() {
		mapview.zoom(1);
	});

	zoomout.addEventListener('click', function() {
		mapview.zoom(-1);
	});
	var buttonBar = Titanium.UI.createButtonBar({
		labels : [{
			title : '+',
			style : Titanium.UI.iPhone.SystemButtonStyle.BORDERED
		}, {
			title : '-',
			style : Titanium.UI.iPhone.SystemButtonStyle.BORDERED
		}],
		backgroundColor : '#336699',
		top : getPixels("37.00%", Titanium.Platform.displayCaps.platformHeight),
		right : getPixels("2.00%", Titanium.Platform.displayCaps.platformWidth),
		style : Titanium.UI.iPhone.SystemButtonStyle.BAR,
		width : getPixels("45.00%", Titanium.Platform.displayCaps.platformWidth),
		height : getPixels("5.00%", Titanium.Platform.displayCaps.platformHeight),
	});
	buttonBar.addEventListener('click', function(e) {
		if (e.index == 0) {
			mapview.zoom(1);
		} else {
			mapview.zoom(-1);
		}
	});
	var imageView = Ti.UI.createImageView({
		image : win.params.photo,
		top : getPixels("15.00%", Titanium.Platform.displayCaps.platformHeight),
		left : getPixels("2.00%", Titanium.Platform.displayCaps.platformWidth),
		width : getPixels("45.00%", Titanium.Platform.displayCaps.platformWidth),
		height : getPixels("27.00%", Titanium.Platform.displayCaps.platformHeight)
	});
	Ti.API.info(win.params);
	var openingDateArea = Ti.UI.createView({
		backgroundColor : 'white',
		top : getPixels("2.00%", Titanium.Platform.displayCaps.platformHeight),
		left : getPixels("2.00%", Titanium.Platform.displayCaps.platformWidth),
		width : getPixels("45.00%", Titanium.Platform.displayCaps.platformWidth),
		height : getPixels("13.00%", Titanium.Platform.displayCaps.platformHeight),
		borderWidth : 1,
		name : 'openingDate',
		title : "Opening Date"
	});
	var openingDateLabel = Ti.UI.createLabel({
		text : 'Opening Date: ' + win.params.openingDate,
		textAlign : 'center',
		name : 'openingDate',
		title : "Opening Date"
	});
	var eventDescriptionScrollView = Titanium.UI.createScrollView({
		contentWidth : 'auto',
		contentHeight : 'auto',
		top : getPixels("45.00%", Titanium.Platform.displayCaps.platformHeight),
		bottom : getPixels("2.00%", Titanium.Platform.displayCaps.platformHeight),
		showVerticalScrollIndicator : true,
		showHorizontalScrollIndicator : false
	});
	var eventDescriptionLabel = Ti.UI.createLabel({
		text : win.params.description + 'descriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescriptiondescription ',
		textAlign : 'riight',
		top : 0,
		bottom : 0,
		name : 'eventDescription',
		title : "Event Description",
		height : 'auto'

	});
	var eventDescriptionArea = Ti.UI.createView({
		backgroundColor : '#5993E5',
		borderRadius : 10,
		top : 0,
		left : getPixels("2.00%", Titanium.Platform.displayCaps.platformWidth),
		width : getPixels("45.00%", Titanium.Platform.displayCaps.platformWidth),
		height : 'auto'
	});
	var friendsAttendingButton = Ti.UI.createButton({
		title : '22 Friends are going',
		color : 'black',
		backgroundColor : '#5993E5',
		borderRadius : 8,
		backgroundImage : 'none',
		font : {
			fontFamily : 'Arial',
			fontWeight : 'bold',
			fontSize : 14
		},
		right : getPixels("2.00%", Titanium.Platform.displayCaps.platformWidth),
		width : getPixels("45.00%", Titanium.Platform.displayCaps.platformWidth),
		bottom : getPixels("17.00%", Titanium.Platform.displayCaps.platformHeight),
		height : getPixels("11.00%", Titanium.Platform.displayCaps.platformHeight)
	});
	var attendButton = Ti.UI.createButton({
		title : 'Attend',
		color : 'black',
		backgroundColor : '#32CC99',
		borderRadius : 8,
		backgroundImage : 'none',
		font : {
			fontFamily : 'Arial',
			fontWeight : 'bold',
			fontSize : 14
		},
		right : getPixels("2.00%", Titanium.Platform.displayCaps.platformWidth),
		width : getPixels("45.00%", Titanium.Platform.displayCaps.platformWidth),
		bottom : getPixels("2.00%", Titanium.Platform.displayCaps.platformHeight),
		height : getPixels("11.00%", Titanium.Platform.displayCaps.platformHeight)
	});
	attendButton.addEventListener('click', function() {
		var alertDialog = Titanium.UI.createAlertDialog({
			title : 'Attend ' + win.params.newWindowTitle,
			message : 'Are you sure you want to attend ' + win.params.newWindowTitle + ' ?',
			buttonNames : ['Cancel', 'Yes']
		});
		alertDialog.show();
		alertDialog.addEventListener('click', function(e) {
			if (e.index == 1) {
				var attendEventRequest = Titanium.Network.createHTTPClient();
				attendEventRequest.onload = function() {
					var json = this.responseText;
					var response = JSON.parse(json);
					alert(response.message);
					win.remove(attendButton);
					win.add(unattendButton);
					// Ti.UI.currentWindow.fireEvent('focus');
				};
				attendEventRequest.onerror = function(e) {
					alert(e);
				};
				var params = {
					eventID : win.params.eventID
				};
				attendEventRequest.open("POST", "http://crowdit.herokuapp.com/api/crowdit/event-person/attend/");
				attendEventRequest.setRequestHeader('Authorization', getOAuthHeader(attendEventRequest, params));
				attendEventRequest.setRequestHeader('Content-Type', 'application/json');
				attendEventRequest.send(params);
			}
		});
	});
	var unattendButton = Ti.UI.createButton({
		title : 'Unattend',
		color : 'black',
		backgroundColor : 'red',
		borderRadius : 8,
		backgroundImage : 'none',
		font : {
			fontFamily : 'Arial',
			fontWeight : 'bold',
			fontSize : 14
		},
		right : getPixels("2.00%", Titanium.Platform.displayCaps.platformWidth),
		width : getPixels("45.00%", Titanium.Platform.displayCaps.platformWidth),
		bottom : getPixels("2.00%", Titanium.Platform.displayCaps.platformHeight),
		height : getPixels("11.00%", Titanium.Platform.displayCaps.platformHeight)
	});
	unattendButton.addEventListener('click', function() {
		var alertDialog = Titanium.UI.createAlertDialog({
			title : 'Unattend ' + win.params.newWindowTitle,
			message : 'Are you sure you want to unattend ' + win.params.newWindowTitle + ' ?',
			buttonNames : ['Cancel', 'Yes']
		});
		alertDialog.show();
		alertDialog.addEventListener('click', function(e) {
			if (e.index == 1) {
				var unattendEventRequest = Titanium.Network.createHTTPClient();
				unattendEventRequest.onload = function() {
					var json = this.responseText;
					var response = JSON.parse(json);
					alert(response.message);
					win.remove(unattendButton);
					win.add(attendButton);
					// Ti.UI.currentWindow.fireEvent('focus');
				};
				unattendEventRequest.onerror = function(e) {
					alert(e);
				};
				var params = {
					eventID : win.params.eventID
				};
				unattendEventRequest.open("POST", "http://crowdit.herokuapp.com/api/crowdit/event-person/unattend/");
				unattendEventRequest.setRequestHeader('Authorization', getOAuthHeader(unattendEventRequest, params));
				unattendEventRequest.setRequestHeader('Content-Type', 'application/json');
				unattendEventRequest.send(params);
			}
		});
	});
	eventDescriptionArea.add(eventDescriptionLabel);
	eventDescriptionScrollView.add(eventDescriptionArea)
	openingDateArea.add(openingDateLabel);
	win.add(eventDescriptionScrollView);
	win.add(openingDateArea);
	win.add(imageView);
	win.add(buttonBar);
	win.add(friendsAttendingButton);
	win.params.attending ? win.add(unattendButton) : win.add(attendButton);
});
