"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const fs = require("fs");
const JSONStream = require("JSONStream");
const es = require("event-stream");
const writeStream = fs.createWriteStream("/Users/jamesglenn/gensim-data/wiki-english-20171001/lineified.txt", { flags: "a" });
const getStream = () => {
    const jsonData = "/Users/jamesglenn/gensim-data/wiki-english-20171001/wiki-english-20171001", stream = fs.createReadStream(jsonData, { encoding: "utf8" }), parser = JSONStream.parse("section_texts.*");
    return stream.pipe(parser);
};
console.log("Starting streaming");
getStream().pipe(es.mapSync((data) => {
    console.log(`Writing ${data.length} lines of text`);
    for (const line of data) {
        writeStream.write(line);
    }
    console.log(`Successfully wrote ${data.length} lines of text`);
}));
//# sourceMappingURL=WikipediaFormatter.js.map