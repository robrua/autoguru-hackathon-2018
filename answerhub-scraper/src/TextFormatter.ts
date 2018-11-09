import * as fs from "fs";

interface Question {
  id: number;
  title: string;
  body: string;
  answers: Answer[];
}

interface Answer {
  id: number;
  body: string;
  accepted: boolean;
}

interface Comment {
  id: number;
  body: string;
}

export const readDirectory = (dirname: string): string[] => {
  try {
    return fs.readdirSync(dirname);
  } catch (error) {
    console.error(error);
    return [];
  }
};

const writeToFile = (lines: string[], filePath: string) => {
  const file = fs.createWriteStream(filePath);
  file.on("error", (err: Error) => {
    /* error handling */
    console.error(err);
  });
  for (const line of lines) {
    file.write(line + "\n");
  }
  file.end();
};

export const processFiles = (
  basepath: string,
  filenames: string[],
  objectType: string,
  outFilePath: string
): void => {
  const lines = [];
  for (const filename of filenames) {
    const file = JSON.parse(fs.readFileSync(`${basepath}/${filename}`, "utf8"));
    if (objectType.toLowerCase() === "question") {
      lines.push(...formatQuestion(file));
    } else if (objectType.toLowerCase() === "comment") {
      lines.push(...formatComment(file));
    }
  }

  writeToFile(lines, outFilePath);
};

const formatQuestion = (question: Question): string[] => {
  const lines: string[] = [];

  lines.push(question.title);
  lines.push(question.body);

  for (const answer of question.answers) {
    lines.push(...formatAnswer(answer));
  }

  return lines;
};

const formatAnswer = (answer: Answer): string[] => {
  const lines = [answer.body];
  return lines;
};

const formatComment = (comment: Comment): string[] => {
  const lines = [comment.body];
  return lines;
};
