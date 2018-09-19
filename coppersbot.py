# Work with Python 3.6
# This vulgar bot is based on sample code provided by devdungeon.
# https://www.devdungeon.com/content/make-discord-bot-python
import discord

USERID = '<@490655530172547073>'

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith(USERID):
        msg = message.content[len(USERID):].lstrip()
        print(msg)
        if msg.startswith('hello'):
            msg = 'IDIOT DETECTED. INITIALIZING STANDARD GREETING PROTOCOL. Hello {0.author.mention}.'.format(message)
            await client.send_message(message.channel, msg)
        elif msg.startswith('piss off'):
            msg = 'pissing off'.format(message)
            await client.send_message(message.channel, msg)
            await client.logout()
        else:
            slang = {'b': ':b:', 's': ':heavy_dollar_sign:', 'a': ':a:', }
            out = ""
            for c in msg:
                if c.lower() in slang:
                    out += slang[c.lower()]
                else:
                    out += c
            await client.send_message(message.channel, out)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

file = open("DiscordToken.txt", "r")
client.run(file.read())
file.close()
