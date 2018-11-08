import os
import discord
import requests
import json


TOKEN = os.environ['BOTTOKEN']

MESSAGE_TOKEN = "? "

client = discord.Client()


def ask_for_wisdom(question: str = ""):
    url = "http://localhost:41170/autoguru/answer-stub"
    data = {"question": question}
    headers = {"Content-Type": "application/json"}

    data = json.dumps(data)
    req = requests.post(url=url, data=data, headers=headers, stream=True)
    response = req.content.decode()
    answer = json.loads(response)['content']
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
            answer = ask_for_wisdom(question)
        await client.send_message(message.channel, answer)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------\n')


client.run(TOKEN)
