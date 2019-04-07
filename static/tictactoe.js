$(function() {
	$("a").click(function(e) {
	    if ($(e.target).attr("id") == "listGames"){
            	$.ajax({
                	type: "POST",
                	url: '/listgames',
                	success: function(response) {
                    		console.log(response);
                		window.location.href = "http://130.245.170.251/listGamesView?games=" + response;
                	}
            	});
	    }
	    if ($(e.target).attr("id") == "viewGameScore"){
                $.ajax({
                        type: "POST",
                        url: '/getscore',
                        success: function(response) {
                                console.log(response);
                                window.location.href = "http://130.245.170.251/gameScoreView?response=" + response;
                        }
                });
	    }
	    if ($(e.target).attr("id") == "home"){
        	e.preventDefault();
       		x = document.cookie;
        	console.log(x);
        	var playerMove = null;;
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
	    }
        });
});

$(function() {
    $('.searchUserForm').on('submit', function(e) {
	e.preventDefault();
	
	var form = document.getElementById("searchUserForm");
	var username = form.elements['username'].value;
	var searchType = $("#searchType").val();
	console.log(searchType);

	var urlPath = "/user/" + username;
	if (searchType != "userInfo"){
		urlPath += "/" + searchType
	}
	console.log(urlPath);
	$.ajax({
		url: urlPath,
		type: 'GET',
		success: function(response) {
			console.log(response);
			status = response['status'];
			console.log(status);
	                document.getElementById('results').innerHTML = '';
			var h1 = document.createElement('h1');
			var h2 = document.createElement('h2');
			if (status != "OK"){
				h1.innerHTML = "Search failed: " + response['error'];
			}
			else if (searchType == "userInfo"){
				h1.innerHTML = "User info for user " + username; 
				h2.innerHTML = "Email: " + response['user']['email'];
				h2.innerHTML += "<p>Reputation: " + response['user']['reputation'] + "</p>";
				h1.appendChild(h2);
			}
			else {
				h1.innerHTML = "IDs of " + searchType + " posted by user " + username;
				IdArray = response[searchType];
				for (var i = 0; i < IdArray.length; i++){
                                	var Id = IdArray[i];
					if (i == IdArray.length-1){
						h2.innerHTML += Id;
					}
					else {
						h2.innerHTML += Id + ", ";
					}
				}
				h1.appendChild(h2);
			}
			document.getElementById('results').appendChild(h1);
		},
		error: function(error) {
                console.log(error);
            	},
                dataType: "json"
	});
    });
});


$(function() {
    $('.addQuestionForm').on('submit', function(e) {
        e.preventDefault();
	console.log("in add question function");
        var form = document.getElementById("addQuestionForm");
        var title = form.elements['title'].value;
        var body = form.elements['body'].value;
        var tags = form.elements['tags'].value;
	var media = form.elements['media'].value;
	
	var tagsArray = tags.split(",");

        var json = {'title':title, 'body':body,'tags':tagsArray}
	var jsonData = JSON.stringify(json);
	console.log(jsonData);
	$.ajax({
            url: '/questions/add',
            contentType: "application/json; charset=utf-8",
            type: 'POST',
            data: jsonData,
	    success: function(response) {
		document.getElementById('results').innerHTML = '';
		var h1 = document.createElement('h1');
		status = response['status'];
		if (status == "OK"){
			qID = response['id'];
			h1.innerHTML = "Question Add Successful<p>Question ID: " + qID + "</p>";
		}
		else{
			h1.innerHTML = "Question Add Failed, " + response['error'];
		}
		document.getElementById('results').appendChild(h1)
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            },
            dataType: "json"
        });
    });
});

$(function() {
    $('.addAnswerForm').on('submit', function(e) {
        e.preventDefault();
        var form = document.getElementById("addAnswerForm");
	var questionID = form.elements['questionID'].value;
	var body = form.elements['body'].value;

	var json = {'body':body};
	var jsonData = JSON.stringify(json);
	var urlString = "/questions/" + questionID + "/answers/add"
        console.log(urlString);
	$.ajax({
            url: urlString,
            contentType: "application/json; charset=utf-8",
            type: 'POST',
            data: jsonData,
            success: function(response) {
                document.getElementById('results').innerHTML = '';
                var h1 = document.createElement('h1');
                status = response['status'];
                if (status == "OK"){
                        qID = response['id'];
                        h1.innerHTML = "Answer Add Successful<p> ID: " + qID + "</p>";
                }
                else{
                        h1.innerHTML = "Question Add Failed, " + response['error'];
                }
                document.getElementById('results').appendChild(h1)
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            },
            dataType: "json"
        });
    });
});

$(function() {
    $('.searchQuestionAdvancedForm').on('submit', function(e) {
	e.preventDefault();
	var form = document.getElementById("searchQuestionAdvancedForm");
	var timestamp = form.elements['timestamp'].value;
	var limit = form.elements['limit'].value;
	var searchPhrase = form.elements['searchPhrase'].value;

	console.log("timestamp:" + timestamp);
	console.log("limit: " + limit);
	console.log("searchPhrase: " + searchPhrase);
	
	jsonData = {};

	if (timestamp != ""){
		jsonData['timestamp'] = parseInt(timestamp);
	}
	if (limit != ""){
		jsonData['limit'] = parseInt(limit);
	}
	if (searchPhrase != ""){
		jsonData['q'] = searchPhrase;
	}
	json = JSON.stringify(jsonData);
	console.log(json);
	$.ajax({
		url: "/search",
            	contentType: "application/json; charset=utf-8",
            	type: 'POST',
		data: json,
           	success: function(response) {
			document.getElementById('results').innerHTML = "";
			var h1 = document.createElement('h1');
			status = response['status'];
			if (status == "OK") {
				h1.innerHTML = "Details of Questions from Search Results<hr>"
				h2 = document.createElement('h2');
				questions = response['questions'];
				for (var i = 0; i < questions.length; i++){
					question = questions[i];
		                        id = question['id'];
                        		user = question['user'];
                       	 		username = user['username'];
                        		userRep = user['reputation'];
                        		title = question['title'];
                        		score = question['score'];
                        		view_count = question['view_count'];
                        		answer_count = question['answer_count'];
                        		timestamp = question['timestamp'];
                        		body = question['body'];
                        		accepted_answer_id = question['accepted_answer_id'];
                        		h2.innerHTML += "id: " + id + "<p>Username of poster: " + username + "</p><p>Reputation of poster: " + userRep + "</p><p>Title: " + title + "</p><p>Body: " + body + "</p><p>timestamp: " + timestamp + "</p><p>score: " + score + "</p><p>View Count: " + view_count + "</p><p>Answer Count: " + answer_count + "</p><p>Accepted Answer ID: " + accepted_answer_id + "</p><hr>";
				}
				h1.appendChild(h2);
			}
			else {
				h1.innerHTML = "Search failed: " + response['error'];
			}
			document.getElementById('results').appendChild(h1);
		},
            	error: function(error) {
                	console.log(error);
            	},
            	dataType: "json"
	});
    });
});
	

$(function() {
    $('.searchQuestionIDForm').on('submit', function(e) {
        e.preventDefault();
        var form = document.getElementById("searchQuestionIDForm");
        var questionID = form.elements['questionID'].value;

	var urlString = "/questions/" + questionID;
        console.log(urlString);
        $.ajax({
            url: urlString,
            contentType: "application/json; charset=utf-8",
            type: 'GET',
            success: function(response) {
                document.getElementById('results').innerHTML = '';
                var h1 = document.createElement('h1');
                status = response['status'];
                if (status == "OK"){
                        question = response['question']
                        h1.innerHTML = "Details of Question " + questionID + "<hr>";
                        h2 = document.createElement('h2');
                        id = question['id'];
                        user = question['user'];
			username = user['username'];
			userRep = user['reputation'];
                        title = question['title'];
                        score = question['score'];
                	view_count = question['view_count'];
			answer_count = question['answer_count'];
			timestamp = question['timestamp'];
			body = question['body'];
			accepted_answer_id = question['accepted_answer_id'];        
		        h2.innerHTML += "id: " + id + "<p>Username of poster: " + username + "</p><p>Reputation of poster: " + userRep + "</p><p>Title: " + title + "</p><p>Body: " + body + "</p><p>timestamp: " + timestamp + "</p><p>score: " + score + "</p><p>View Count: " + view_count + "</p><p>Answer Count: " + answer_count + "</p><p>Accepted Answer ID: " + accepted_answer_id + "</p><hr>";
                        h1.appendChild(h2);
                }
                else{
                        h1.innerHTML = "Question Add Failed, " + response['error'];
                }
                document.getElementById('results').appendChild(h1)
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            },
            dataType: "json"
        });
    });
});
$(function() {
    $('.searchAnswerForm').on('submit', function(e) {
        e.preventDefault();
        var form = document.getElementById("searchAnswerForm");
        var questionID = form.elements['questionID'].value;

        var urlString = "/questions/" + questionID + "/answers"
        console.log(urlString);
        $.ajax({
            url: urlString,
            contentType: "application/json; charset=utf-8",
            type: 'GET',
            success: function(response) {
                document.getElementById('results').innerHTML = '';
                var h1 = document.createElement('h1');
                status = response['status'];
                if (status == "OK"){
			answers = response['answers']
			h1.innerHTML = "Answers to question " + questionID + "<hr>";
			h2 = document.createElement('h2');
			for (var i = 0; i < answers.length; i++){
				var answer = answers[i];
				console.log(answer.id);
				id = answer.id;
				user = answer['user'];
				body = answer['body'];
				score = answer['score'];
				is_accepted = answer['is_accepted'];
				timestamp = answer['timestamp'];
				h2.innerHTML += "id: " + id + "<p>user: " + user + "</p><p>body: " + body + "</p><p>score: " + score + "</p><p>accepted: " + is_accepted + "</p><p>timestamp: " + timestamp + "</p><hr>";
			}
			h1.appendChild(h2);
                }
                else{
                        h1.innerHTML = "Question Add Failed, " + response['error'];
                }
                document.getElementById('results').appendChild(h1)
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            },
            dataType: "json"
        });
    });
});


$(function() {
    $('.listGames').on('click', function(e) {
        e.preventDefault();

        var x = {'cookie' : document.cookie};
        console.log(x);
        $.ajax({
            url: '/listgames',
            contentType: "application/json; charset=utf-8",
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
