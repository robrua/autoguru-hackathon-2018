import os
import discord
import requests
import json
import random


TOKEN = os.environ['BOTTOKEN']

MESSAGE_TOKEN = "? "
I_DUNNO_ANSWER = "I don't have an answer in my database that sufficiently answers your question."
MEME_CHANCE = 0.2

client = discord.Client()


def ask_for_wisdom(question: str = ""):
    url = "http://localhost:41170/autoguru/answer-stub"
    data = {"question": question[2:]}
    headers = {"Content-Type": "application/json"}

    data = json.dumps(data)
    req = requests.post(url=url, data=data, headers=headers, stream=True)
    response = req.content.decode()
    answer = json.loads(response)['content']
    confidence = abs(json.loads(response)['confidence'])
    return answer


def ask_question(question: str = ""):
    url = "http://localhost:41170/autoguru/answer"
    data = {"question": question[2:]}
    headers = {"Content-Type": "application/json"}

    data = json.dumps(data)
    req = requests.post(url=url, data=data, headers=headers, stream=True)
    response = req.content.decode()
    answer = json.loads(response)['content']
    confidence = abs(json.loads(response)['confidence'])
    answer += f'\n\n(Confidence: {confidence})'
    return answer


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith(MESSAGE_TOKEN):
        if message.content.startswith(MESSAGE_TOKEN + "wizdom"):
            answer = ask_for_wisdom()
        else:
            question = message.content
            answer = ask_question(question)
            if answer.startswith(I_DUNNO_ANSWER) and random.random() < MEME_CHANCE:
                answer += "\n\nhttps://i.imgur.com/zKeatPl.png"
        sent_message = await client.send_message(message.channel, answer)
        if not answer.startswith(I_DUNNO_ANSWER):
            await client.add_reaction(sent_message, "👍")
            await client.add_reaction(sent_message, "👎")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------\n')


client.run(TOKEN)
