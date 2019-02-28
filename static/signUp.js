$(function() {
    $('.signUpForm').on('submit', function(e) {
        e.preventDefault();
	
	var form = document.getElementById("signUpForm");
	var username = form.elements['username'].value;
	var password = form.elements['password'].value;
	var email = form.elements['email'].value;

        var userInfo  = {'username':username, 'password':password, 'email':email};
	console.log(userInfo);	
        $.ajax({
            url: '/adduser',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(userInfo),
            type: 'POST',
            success: function(response) {
                console.log(response);

            },
            error: function(error) {
                console.log("hello");
                console.log(error);
            },
            dataType: "json"
        });
    });
});

