import { processFiles, readDirectory } from "./TextFormatter";

const basedir = "/Users/jamesglenn/Downloads/answerhub_data";
const questionsdir = `${basedir}/questions/`;
const commentsdir = `${basedir}/comments/`;
const questionsout = `${basedir}/questions.txt`;
const commentsout = `${basedir}/comments.txt`;

const questions = readDirectory(questionsdir);
const comments = readDirectory(commentsdir);

console.log(questions);

processFiles(questionsdir, questions, "question", questionsout);
processFiles(commentsdir, comments, "comment", commentsout);

console.log("All done <3");
