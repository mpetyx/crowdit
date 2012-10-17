var win = Titanium.UI.currentWindow;

if (Ti.Platform.name == 'android') 
{
	win.backgroundColor = '#4e5c4d';
}
else
{
	win.backgroundColor = '#aebcad';
}

// create table view data object
var data = [
	{title:'Help Desk', hasChild:true, test:'support/helpDesk.js', header:''},
	{title:'Crowdit.com', header:''},
	{title:'Terms Of Service', hasChild:true, test:'support/termsOfService.js'},
	{title:'Privacy Policy', hasChild:true, test:'support/privacyPolicy.js'},
	{title:'Libraries', hasChild:true, test:'support/libraries.js'}
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
	if (e.rowData.title == 'Crowdit.com') {
		Ti.Platform.openURL('http://crowdit.herokuapp.com');
	}
});

// add table view to the window
win.add(tableview);
