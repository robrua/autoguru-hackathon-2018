import os
import discord

TOKEN = os.environ['BOTTOKEN']

MESSAGE_TOKEN = "? "

client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------\n')

    #for channel in client.get_all_channels():
    #    print(channel, channel.id)

    with open("text.txt", 'w') as of:
        pass

    nmessages = 'inf'
    count = 0
    limit = 100
    for channel in client.get_all_channels():
        last_message = None
        with open("text.txt", 'a') as of:
            while count <= nmessages:
                logs = client.logs_from(
                    channel=channel,
                    limit=limit,
                    reverse=False,
                    before=last_message,
                )
                _count = 0
                async for message in logs:
                    print(message.content, file=of)
                    last_message = message
                    count += 1
                    _count += 1
                if count % 1000:
                    print(count)
                if _count != limit:
                    break
    print("Finished!!!")


client.run(TOKEN)
