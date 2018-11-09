"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const fs = require("fs");
exports.readDirectory = (dirname) => {
    try {
        return fs.readdirSync(dirname);
    }
    catch (error) {
        console.error(error);
        return [];
    }
};
const writeToFile = (lines, filePath) => {
    const file = fs.createWriteStream(filePath);
    file.on("error", (err) => {
        /* error handling */
        console.error(err);
    });
    for (const line of lines) {
        file.write(line + "\n");
    }
    file.end();
};
exports.processFiles = (basepath, filenames, objectType, outFilePath) => {
    const lines = [];
    for (const filename of filenames) {
        const file = JSON.parse(fs.readFileSync(`${basepath}/${filename}`, "utf8"));
        if (objectType.toLowerCase() === "question") {
            lines.push(...formatQuestion(file));
        }
        else if (objectType.toLowerCase() === "comment") {
            lines.push(...formatComment(file));
        }
    }
    writeToFile(lines, outFilePath);
};
const formatQuestion = (question) => {
    const lines = [];
    lines.push(question.title);
    lines.push(question.body);
    for (const answer of question.answers) {
        lines.push(...formatAnswer(answer));
    }
    return lines;
};
const formatAnswer = (answer) => {
    const lines = [answer.body];
    return lines;
};
const formatComment = (comment) => {
    const lines = [comment.body];
    return lines;
};
//# sourceMappingURL=TextFormatter.js.map