$(function() {
    $('.viewCookie').on('submit', function(e) {
        e.preventDefault();
	
	var x = {'cookie' : document.cookie};
	console.log(x);
	console.log("hereeeee");
        $.ajax({
            url: 'http://130.245.170.251/cookieTest',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(x),
            type: 'POST',
            success: function(response) {
                console.log(response);
                document.write(response['newPage']);
            },
            error: function(error) {
                console.log("hello");
                console.log(error);
            },
            dataType: "json"
        });
    });
});

$(function() {
    $('.logout').on('submit', function(e) {
        e.preventDefault();

        var x = {'cookie' : document.cookie};
        console.log(x);
        console.log("hereeeee");
        $.ajax({
            url: 'http://130.245.170.251/logout',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(x),
            type: 'POST',
            success: function(response) {
               	var cookieString = "_id=" + response['cookie'] + ";expires=Thu, 18 Dec 2013 12:00:00 UTC;";
		console.log(cookieString);
		document.cookie = cookieString;
		console.log("document cookie: " + document.cookie);
                window.location.href = "http://130.245.170.251/loggedOut";
	    },
            error: function(error) {
                console.log("hello");
                console.log(error);
            },
            dataType: "json"
        });
    });
});

$(function() {
    $('.tttForm').on('submit', function(e) {
	e.preventDefault();
//	var gridArray = [" ", " ", " ", " ", " ", " ", " ", " ", " "]
        x = document.cookie;
	console.log(x);
  //      $(".X").each(function(item) {
//	    var pos = $(this).val();
//	    gridArray[pos-1] = "X";
//	});
//	$(".O").each(function(item) {
  //          var pos = $(this).val();
    //        gridArray[pos-1] = "O";
      //  });
        var playerMove = $(document.activeElement).val() - 1;
//	gridArray[playerMove-1] = "X";
	var move = {'move':playerMove};
	var jsonMove = JSON.stringify(move);
	console.log(jsonMove);
        $.ajax({
            url: '/ttt/play',
	    contentType: "application/json; charset=utf-8",
            data: jsonMove,
            type: 'POST',
            success: function(response) {
                console.log(response);
		grid = response.grid;
		console.log(grid);
		html = "<table><tr><td>";
		html = html + "<button type=\"submit\" class=\"" + grid[0] + "\" name=\"choice\" value=\"1\">" + grid[0] + "</button></td>";
		html = html + "<td><button type=\"submit\" class=\"" + grid[1] + "\" name=\"choice\" value=\"2\">" + grid[1] + "</button></td>";
		html = html + "<td><button type=\"submit\" class=\"" + grid[2] + "\" name=\"choice\" value=\"3\">" + grid[2] + "</button></td></tr>";
                html = html + "<tr><td><button type=\"submit\" class=\"" + grid[3] + "\" name=\"choice\" value=\"4\">" + grid[3] + "</button></td>";
                html = html + "<td><button type=\"submit\" class=\"" + grid[4] + "\" name=\"choice\" value=\"5\">" + grid[4] + "</button></td>";
                html = html + "<td><button type=\"submit\" class=\"" + grid[5] + "\" name=\"choice\" value=\"6\">" + grid[5] + "</button></td></tr>";
                html = html + "<tr><td><button type=\"submit\" class=\"" + grid[6] + "\" name=\"choice\" value=\"7\">" + grid[6] + "</button></td>";
                html = html + "<td><button type=\"submit\" class=\"" + grid[7] + "\" name=\"choice\" value=\"8\">" + grid[7] + "</button></td>";
                html = html + "<td><button type=\"submit\" class=\"" + grid[8] + "\" name=\"choice\" value=\"9\">" + grid[8] + "</button></td></tr>";
                html = html + "</table>";
                console.log(html);
                nameDate = $(".tagline").text();
	        newNameDate = "<h1 class=\"mb-5\"><span class=\"tagline\" style=\"font-size:90%\"><b>" + nameDate + "</b></h1>"
                console.log(newNameDate);
		$("#col-xl-9 mx-auto").html(newNameDate);
		$("#tictactoe").html(html);

            },
            error: function(error) {
		console.log("hello");
                console.log(error);
            },
            dataType: "json"
        });
    });
});
