import AnswerHub, {Question} from "./AnswerHub";
import fs = require("fs");
import fetch from "node-fetch";

const MINIMUM_CONFIDENCE = 0; // TODO set this
const LAST_QUESTION_FILE = `${__dirname}/../data/last_question_timestamp.txt`;
const CONFIG_FILE = `${__dirname}/../config.json`;
/** How often to check the forums (in seconds) */
const CHECK_INTERVAL = 5;
const ANSWER_URL = "http://localhost:41170/autoguru/answer-stub";
const config = JSON.parse(fs.readFileSync(CONFIG_FILE).toString());

const answerHub = new AnswerHub(
	"https://discussion.developer.riotgames.com/",
	config.answerhub_credentials.username,
	config.answerhub_credentials.password
);

const answerQuestion = async (question: Question) => {
	const response = await fetch(ANSWER_URL, {
		method: "POST",
		headers: {
			"Content-Type": "application/json"
		},
		body: JSON.stringify({question: question.body})
	});
	if (response.status !== 200) {
		console.error(`Received ${response.status} code from question anwering server`);
		return;
	}

	const body = await response.json();
	if (body.confidence > MINIMUM_CONFIDENCE) {
		await answerHub.answerQuestion(question.id, body.content);
	}
};

setInterval(async () => {
	let lastQuestionTime: number = 0;
	if (fs.existsSync(LAST_QUESTION_FILE)) {
		lastQuestionTime = +fs.readFileSync(LAST_QUESTION_FILE).toString();
	}

	try {
		const questions = await answerHub.getQuestions(0, "newest");
		for (const question of questions.list) {
			try {
				if (question.creationDate > lastQuestionTime) {
					console.log("Found a question that needs to be answered");
					await answerQuestion(question);
				}
			} catch (ex) {
				console.error(`Error occurred while responding to question ${question.id}: ${ex}`);
			}
			if (lastQuestionTime < question.creationDate) {
				lastQuestionTime = question.creationDate;
			}
		}
	} catch (ex) {
		console.error(`Error checking questions: ${ex}`);
	}
	fs.writeFileSync(LAST_QUESTION_FILE, lastQuestionTime);
}, CHECK_INTERVAL * 1000);
