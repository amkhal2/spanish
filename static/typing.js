// Declaring General-Scope Variables

var question = document.getElementById('question'); // question 
var startButton = document.getElementById('start');	// 'start quiz' button
var checkButton = document.getElementById('check'); // 'check answer' button
var questionID, answerID, answer;	// question and answer IDs
var count = [];	
var IDs = [];
var message = document.getElementById('message'); // feedback message
var searchBox = document.getElementById('searchDB'); // search box
var searchResult = document.getElementById('searchResult'); // search results div
var answerBox = document.getElementById('answer'); // search box


// When the user clicks 'start quiz', get the selected category and search database
// to get a random question with answers

startButton.addEventListener('click', function(){
	var toServer = JSON.stringify({
	'IDs': IDs });
	
	message.innerHTML = '';
	answerBox.value = '';
	
	// Make POST request and send IDs list to server and search db for a random question and answers
	var xhr = new XMLHttpRequest();
	xhr.open('POST', '/get_typing', true);
	xhr.setRequestHeader('Content-type', 'application/json');
	xhr.send(toServer);

	
	// Process the response
			xhr.onload = function(){
			if (xhr.status === 200) {
				data = JSON.parse(xhr.responseText);
				IDs = data.IDs;
				console.log(IDs);
				question.innerHTML = data.question;
				
				question.scrollIntoView();
				
				questionID = data.questionID;
							
			}
		}
});

// When the user clicks 'Check Answer' button, verify the selected answer

checkButton.addEventListener('click', function(){
	
	// get the text from Answer Box
	answer = answerBox.value.trim();
	
	// console.log(answer);
	// console.log(question);
		
	
	// check if the selected value is correct
	if (answer === question.innerText) {
		
		// check if 'questionID' is in 'count' array
		if (!count.includes(questionID)) {
			count.push(questionID);
		};
		
		// console.log(count.length);
		message.innerHTML = '<p class="success">Well Done! You have ' + count.length + ' correct answer(s)...</p>';
		
		// check if the user got 20 correct answers
		if (count.length == 20) {
			message.innerHTML = '<p class="nail">Congratulations! You nailed it...</p>';
					
			count = [];
		}
		
	} else {
		count = [];
		message.innerHTML = '<p class="fail">Wrong answer, please try again...</p>';
	}
	
	
	
}, false);

// Search box feature, searching while you type

searchBox.addEventListener('keyup', function(){
	var toServer = JSON.stringify({
		'userInput': searchBox.value, 'page':'home'	});
	
	// Make the request
	var xhr = new XMLHttpRequest();
	xhr.open('POST', '/search_Database', true);
	xhr.setRequestHeader('Content-type', 'application/json');
	xhr.send(toServer);
	
	// Process the response
	xhr.onload = function(){
		if (xhr.status === 200){
			data = JSON.parse(xhr.responseText);
			
			if (data['status'] === 'success') {
				var content = '';
				content += '<p class="results-num">' + data['res'].length + ' result(s) found...</p>';
				content += '<table><tr> <th>id</th> <th>Spanish</th> <th>Sound</th> <th>Meaning</th></tr>';
				
				for (var i=0; i < data['res'].length; i++){
					content += '<tr><td>' + data['res'][i][0] + '</td><td>' + data['res'][i][1] + '</td><td>' + data['res'][i][2] + '</td>';
					content += '<td>' + data['res'][i][3] + '</td></tr>';
					
				}
				content += '</table>';
				searchResult.innerHTML = content;

			} else {
				searchResult.innerHTML = '<p class="results-num">' + data['res'] + '</p>';
				
			}
		}
	}
}, false);