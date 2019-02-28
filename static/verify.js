$(function() {
    $('.verifyForm').on('submit', function(e) {
        e.preventDefault();

        var form = document.getElementById("verifyForm");
        var email = form.elements['email'].value;
        var key = form.elements['key'].value;

        var verificationInfo  = {'email':email, 'key': key};
        console.log(verificationInfo);
        $.ajax({
            url: '/verify',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(verificationInfo),
            type: 'POST',
            success: function(response) {
                console.log(response);

            },
            error: function(error) {
                console.log(error);
            },
            dataType: "json"
        });
    });
});
