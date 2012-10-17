Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');


var win = Titanium.UI.currentWindow;
win.addEventListener('focus',function(e){

	win.title = win.params.newWindowTitle;
	var getEventsRequest = Titanium.Network.createHTTPClient();
	getEventsRequest.onload = function()
	{
		var thereIsAtLeastOneNotSoldOutAwardRemaining = function(awards, j)
		{
			for (var i = parseInt(j); i < (awards.length-1); i++) {
				Ti.API.info(awards[i].numberLeft);
				if (parseInt(awards[i].numberLeft) > 0) {
					return true;
				}
			}
			return false;
		}
		var json = this.responseText;
		var response = JSON.parse(json);
		var events = JSON.parse(response.events);
		if (response.success) {
			var data = [];

			for (var i=0; i<events.length; i++) 
			{
				var row = Ti.UI.createTableViewRow({height:130, header:events[i].title});
				var awards = JSON.parse(events[i].awards);
				var awardDetails = '';
				for (j in awards) {
					awardDetails += (parseInt(awards[j].numberLeft) > 0) ? awards[j].title + ', ' + awards[j].points + ' Points' : '';
					if ((j < (awards.length - 1)) && thereIsAtLeastOneNotSoldOutAwardRemaining(awards, parseInt(j))) {
						awardDetails += "     ";
					}
				}
				Ti.API.info(awardDetails);
				awardDetails = awardDetails == '' ? 'Sold out' : awardDetails;
				var awardLabel = Ti.UI.createLabel({
					text: awardDetails,
					color: '#111',
					textAlign:'left',
					bottom:getPixels("5.00%", 130),
					left:130,
					font:{fontSize:14},
					width:'auto',
					height:'auto'
				});
				row.add(awardLabel);
				var whenLabel = Ti.UI.createLabel({
					text: events[i].openingDate,
					color: '#111',
					shadowColor:'#900',
					shadowOffset:{x:0,y:1},
					textAlign:'left',
					top:getPixels("5.00%", 130),
					left:130,
					font:{fontSize:16},
					width:'auto',
					height:'auto'
				});
				row.add(whenLabel);
				var whereLabel = Ti.UI.createLabel({
					text: events[i].address,
					color: '#111',
					shadowColor:'#900',
					shadowOffset:{x:0,y:1},
					textAlign:'left',
					top:getPixels("20.00%", 130),
					left:130,
					font:{fontSize:16},
					width:'auto',
					height:'auto'
				});
				row.add(whereLabel);
				var friendsGoingLabel = Ti.UI.createLabel({
					text: '5 friends going',
					color: '#111',
					shadowColor:'#900',
					shadowOffset:{x:0,y:1},
					textAlign:'left',
					top:getPixels("40.00%", 130),
					left:130,
					font:{fontSize:16},
					width:'auto',
					height:'auto'
				});
				row.add(friendsGoingLabel);
				var imageView = Ti.UI.createImageView({
					image: events[i].photo,
					top: 10,
					left: 0,
					width:125,
					height:89
				});
				row.add(imageView);
				row.id=events[i].id;
				row.lat = events[i].geolocation.lat;
				row.lon = events[i].geolocation.lon;
				row.address = events[i].address;
				row.photo = events[i].photo;
				
				data[i] = row;
			}
			
			var eventsTableView = Titanium.UI.createTableView({
				data:data
			});
			eventsTableView.addEventListener('click', function(e) {
				openNestedWindow('events/event.js', {
					newWindowTitle : e.row.header,
					eventID : e.row.id,
					lat: e.row.lat,
					lon: e.row.lon,
					address: e.row.address,
					photo: e.row.photo
				});
			});
			win.add(eventsTableView);
		}
	};
	getEventsRequest.open("GET","http://crowdit.herokuapp.com/api/crowdit/event/upcoming/");
	getEventsRequest.setRequestHeader('Authorization', getOAuthHeader(getEventsRequest));
	getEventsRequest.setRequestHeader('Content-Type', 'application/json');
	getEventsRequest.send();
});
