$(function() {
    $('.logInForm').on('submit', function(e) {
	e.preventDefault();

        var form = document.getElementById("logInForm");
        var username = form.elements['username'].value;
        var password = form.elements['password'].value;

        var userInfo  = {'username':username, 'password':password};
        console.log(userInfo);
        $.ajax({
            url: '/login',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(userInfo),
            type: 'POST',
            success: function(response) {
                console.log(response)
		var cookieString = "_id=" + response['cookie'] + ";";
		console.log(cookieString);
		document.cookie = cookieString;
            	console.log("document cookie: " + document.cookie);
        	window.location.href = "http://130.245.170.251/ttt";
	    },
            error: function(error) {
                console.log("hello");
                console.log(error);
            },
            dataType: "json"
        });
    });
});

