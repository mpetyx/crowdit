Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/oAuth.js');
Ti.include(Titanium.Filesystem.resourcesDirectory + 'lib/myLib.js');

var win = Titanium.UI.currentWindow;

if (Ti.Platform.name == 'android') 
{
	win.backgroundColor = '#4e5c4d';
}
else
{
	win.backgroundColor = '#aebcad';
}

var supportBtn = Titanium.UI.createButton({title:'Support', hasChild: true});
win.rightNavButton = supportBtn;
supportBtn.addEventListener('click', function(e) {
	var params = {newWindowTitle: 'Support'};
	openNestedWindow('support.js', params);
});
// create table view data object
var data = [
	{title:'Find & Invite Friends', hasChild:true, test:'search.js', header:''},
	{title:'Logout', header:'Account'},
	{title:'Push Notification Settings', hasChild:true, test:'notificationSettings.js'},
	{title:'Clear Search History'}
];

// create table view
var tableViewOptions = {
	data:data,
	style:Titanium.UI.iPhone.TableViewStyle.GROUPED,
	backgroundColor:'transparent',
	rowBackgroundColor:'white'
};

var tableview = Titanium.UI.createTableView(tableViewOptions);

// create table view event listener
tableview.addEventListener('click', function(e)
{
	if (e.rowData.test)
	{
		var win = Titanium.UI.createWindow({
			url:e.rowData.test,
			title:e.rowData.title
		});
		Titanium.UI.currentTab.open(win,{animated:true});
	}
	if (e.rowData.title == 'Logout') {
		var alertDialog = Titanium.UI.createAlertDialog({
		    message: 'Are you sure?',
		    buttonNames: ['Cancel', 'Log out']
		});
		alertDialog.show();
		alertDialog.addEventListener('click', function(e) {
			if (e.index == 1) {
				Ti.App.Properties.setString("consumerSecret", '');
				Ti.App.Properties.setString("consumerKey", '');
				Ti.UI.createAlertDialog({title:'Logedout', message:'Successfully logged out'}).show();
				redirectTo('../../app.js');
			};
		});
	}
	if (e.rowData.title == 'Clear Search History') {
		var alertDialog = Titanium.UI.createAlertDialog({
		    message: 'Are you sure?',
		    buttonNames: ['Cancel', 'Yes, I am sure']
		});
		alertDialog.show();
		alertDialog.addEventListener('click', function(e) {
			if (e.index == 1) {
				Ti.API.info('deleting history..');
			};
		});
	}
});

// add table view to the window
win.add(tableview);
