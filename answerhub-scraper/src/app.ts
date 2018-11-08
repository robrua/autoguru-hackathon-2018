import AnswerHub from "./AnswerHub";
import fs = require("fs");

const LAST_PAGE_FILE = `${__dirname}/../data/last_question.txt`;
const CONFIG_FILE = `${__dirname}/../config.json`;
const config = JSON.parse(fs.readFileSync(CONFIG_FILE).toString());

const answerHub = new AnswerHub(
	"http://discussion.developer.riotgames.com/",
	config.answerhub_credentials.username,
	config.answerhub_credentials.password
);

const downloadQuestions = async () => {
	let lastPage: number = 0;
	if (fs.existsSync(LAST_PAGE_FILE)) {
		const contents: string = fs.readFileSync(LAST_PAGE_FILE).toString();
		lastPage = +contents;
	}
	// Determine how many pages of questions there are because AnswerHub doesn't let you sort by oldest questions first
	const pageCount = (await answerHub.getQuestions(0, "newest")).pageCount;
	for (let page = pageCount - lastPage; page >= 0; page--) {
		await downloadPage(page);
		fs.writeFileSync(LAST_PAGE_FILE, page);
	}
};


const downloadPage = async (page: number) => {
	console.log("Downloading page " + page);
	const questionList = await answerHub.getQuestions(page, "newest");
	for (const question of questionList.list) {
		try {
			console.log(`Downloading question ${question.id}...`);
			const contents = {
				id: question.id,
				body: answerHub.formatQuestionBody(question.body),
				answers: [] as any[]
			};
			for (const answerId of question.answers) {
				const answer = await answerHub.getAnswer(answerId);
				contents.answers.push({
					id: answer.id,
					body: answerHub.formatQuestionBody(answer.body),
					accepted: answer.marked
				});
			}
			fs.writeFileSync(`${__dirname}/../data/questions/${question.id}.json`, JSON.stringify(contents));
		} catch (ex) {
			console.error(`An error occurred while downloading question ${question.id}: ${ex}`);
		}
	}
};

downloadQuestions();
