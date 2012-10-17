function redirectTo(arg) {
	var window = Ti.UI.createWindow({
		url : arg,
	});

	Titanium.UI.currentTab.open(window, {
		animated : true
	});
}

function openNestedWindow(file, params) {
	var win = null;
	if (Ti.Platform.name == "android") {
		win = Titanium.UI.createWindow({
			url : file,
			title : e.params.newWindowTitle
		});
	} else {
		win = Titanium.UI.createWindow({
			url : file,
			title : params.newWindowTitle,
			backgroundColor : '#fff',
			barColor : '#111',
			params : params
		});
	}
	Titanium.UI.currentTab.open(win, {
		animated : true
	});
}

var getPixels = function(percent, relative) {
	var percentInt = percent.replace("%", "");
	var percentInt = parseInt(percentInt);
	return Math.round(percentInt * (relative / 100));
};

function inArray(arr, val) {
	for (var i = 0; i < arr.length; i++) {
		if (val == arr[i]) {
			return true;
		}
	}
	return false;
};

function getTableLength(table) {
	var total = 0;
	for(var i = 0; i < table.data.length; i++){
	    total = total + table.data[i].rowCount;
	}
	return total;
}
