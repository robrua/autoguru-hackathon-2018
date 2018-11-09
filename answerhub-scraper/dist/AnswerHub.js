"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
// Borrowed from https://github.com/Querijn/BottyMcBotface/blob/master/src/AnswerHub.ts
const node_fetch_1 = require("node-fetch");
const TurndownService = require("turndown");
const gfm = require("turndown-plugin-gfm");
class AnswerHubAPI {
    constructor(url, username, password) {
        this.turndownService = new TurndownService();
        // Add a trailing / if missing
        this.baseURL = url.substr(url.length - 1) === "/" ? url : url + "/";
        this.auth = `Basic ${new Buffer(username + ":" + password, "binary").toString("base64")}`;
        this.turndownService.use(gfm.gfm);
    }
    formatQuestionBody(body) {
        let markdown = this.turndownService.turndown(body);
        // Format code blocks
        markdown = markdown.replace(/<pre>/g, "```").replace(/<\/pre>/g, "```");
        // Replace relative URIs in links with absolute URIs
        markdown = markdown.replace(/\[.*\]\((.*)\)/g, (fullMatch, uri) => {
            if (uri.startsWith("/")) {
                return fullMatch.replace(uri, this.baseURL + uri.slice(1));
            }
            return fullMatch;
        });
        const clamped = markdown.substr(0, Math.min(1021, markdown.length));
        return clamped + (clamped.length === 1021 ? "..." : "");
    }
    getQuestions(page = 1, sort = "active") {
        return this.makeRequest(`question.json?page=${page}&sort=${sort}`);
    }
    getAnswers(page = 1, sort = "active") {
        return this.makeRequest(`answer.json?page=${page}&sort=${sort}`);
    }
    getComments(page = 1, sort = "active") {
        return this.makeRequest(`comment.json?page=${page}&sort=${sort}`);
    }
    getArticles(page = 1, sort = "active") {
        return this.makeRequest(`article.json?page=${page}&sort=${sort}`);
    }
    getQuestion(id) {
        return this.makeRequest(`question/${id}.json`);
    }
    getArticle(id) {
        return this.makeRequest(`article/${id}.json`);
    }
    getAnswer(id) {
        return this.makeRequest(`answer/${id}.json`);
    }
    getComment(id) {
        return this.makeRequest(`comment/${id}.json`);
    }
    getNode(id) {
        // '/services/v2/article/[articleId].json' works for questions, answers, comments, and articles
        return this.makeRequest(`article/${id}.json`);
    }
    /**
     * Makes a request to the AnswerHub AnswerHubAPI
     * @param url The url to make a request to, relative to the base AnswerHubAPI url
     * @async
     * @throws {any} Thrown if an error is received from the AnswerHubAPI
     * @returns The parsed body of the response from the AnswerHubAPI
     */
    async makeRequest(url) {
        const resp = await node_fetch_1.default(`${this.baseURL}services/v2/${url}`, {
            method: "POST",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json",
                Authorization: this.auth
            }
        });
        if (resp.status !== 200) {
            throw new Error(`Received status code ${resp.status}`);
        }
        return resp.json();
    }
}
exports.default = AnswerHubAPI;
//# sourceMappingURL=AnswerHub.js.map