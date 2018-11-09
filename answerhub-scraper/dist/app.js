"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const AnswerHub_1 = require("./AnswerHub");
const fs = require("fs");
const LAST_QUESTION_PAGE_FILE = `${__dirname}/../data/last_question_page.txt`;
const LAST_COMMENT_PAGE_FILE = `${__dirname}/../data/last_comment_page.txt`;
const CONFIG_FILE = `${__dirname}/../config.json`;
const config = JSON.parse(fs.readFileSync(CONFIG_FILE).toString());
const answerHub = new AnswerHub_1.default("http://discussion.developer.riotgames.com/", config.answerhub_credentials.username, config.answerhub_credentials.password);
const downloadQuestions = async () => {
    let lastPage = 0;
    if (fs.existsSync(LAST_QUESTION_PAGE_FILE)) {
        const contents = fs.readFileSync(LAST_QUESTION_PAGE_FILE).toString();
        lastPage = +contents;
    }
    // Determine how many pages of questions there are because AnswerHub doesn't let you sort by oldest questions first
    const pageCount = (await answerHub.getQuestions(0, "newest")).pageCount;
    for (let page = pageCount - lastPage; page >= 0; page--) {
        await downloadQuestionPage(page);
        fs.writeFileSync(LAST_QUESTION_PAGE_FILE, page);
    }
};
const downloadComments = async () => {
    let lastPage = 0;
    if (fs.existsSync(LAST_COMMENT_PAGE_FILE)) {
        const contents = fs.readFileSync(LAST_COMMENT_PAGE_FILE).toString();
        lastPage = +contents;
    }
    // Determine how many pages of questions there are because AnswerHub doesn't let you sort by oldest comments first
    const pageCount = (await answerHub.getComments(0, "newest")).pageCount;
    for (let page = pageCount - lastPage; page >= 0; page--) {
        await downloadCommentPage(page);
        fs.writeFileSync(LAST_COMMENT_PAGE_FILE, page);
    }
};
const downloadQuestionPage = async (page) => {
    console.log("Downloading question page " + page);
    const questionList = await answerHub.getQuestions(page, "newest");
    for (const question of questionList.list) {
        try {
            console.log(`Downloading question ${question.id}...`);
            const contents = {
                id: question.id,
                body: answerHub.formatQuestionBody(question.body),
                answers: []
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
        }
        catch (ex) {
            console.error(`An error occurred while downloading question ${question.id}: ${ex}`);
        }
    }
};
const downloadCommentPage = async (page) => {
    console.log("Downloading comment page " + page);
    const commentList = await answerHub.getComments(page, "newest");
    for (const comment of commentList.list) {
        try {
            console.log(`Downloading comment ${comment.id}...`);
            const contents = {
                id: comment.id,
                body: answerHub.formatQuestionBody(comment.body)
            };
            fs.writeFileSync(`${__dirname}/../data/comments/${comment.id}.json`, JSON.stringify(contents));
        }
        catch (ex) {
            console.error(`An error occurred while downloading comment ${comment.id}: ${ex}`);
        }
    }
};
Promise.all([
    downloadQuestions(),
    downloadComments()
]).then(() => {
    console.log("Done!");
}, (ex) => {
    console.error(ex);
});
//# sourceMappingURL=app.js.map