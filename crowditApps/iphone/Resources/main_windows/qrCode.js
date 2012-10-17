var win = Titanium.UI.currentWindow;

var qrCodeURL = Titanium.UI.createTextField({
	color:'#336699',
	top:10,
	left:10,
	width:300,
	height:40,
	hintText:'QR-Code-URL',
	keyboardType:Titanium.UI.KEYBOARD_DEFAULT,
	returnKeyType:Titanium.UI.RETURNKEY_DEFAULT,
	borderStyle:Titanium.UI.INPUT_BORDERSTYLE_ROUNDED
});
win.add(qrCodeURL);

var qrCodeGenerateBtn = Titanium.UI.createButton({
	title:'Generate QR Code',
	top:110,
	width:90,
	height:35,
	borderRadius:1,
	font:{fontFamily:'Arial',fontWeight:'bold',fontSize:14}
});
win.add(qrCodeGenerateBtn);

var qrCode = Titanium.UI.createImageView({
	top:300,
	width:300,
	height:'auto'
});

win.add(qrCode);

qrCodeGenerateBtn.addEventListener('click',function(e)
{
	if (qrCodeURL.value)
	{
		var decodedUrl = Ti.Network.encodeURIComponent("http://127.0.0.1:8000/api/crowdit/invite/validate?invitationID=" + qrCodeURL.value + "&format=json");
		qrCode.image = "http://qrcode.kaywa.com/img.php?d=" + decodedUrl;
	}
	else
	{
		alert("QR Code URL is required");
	}
});


