# Work with Python 3.6
# This vulgar bot is based on sample code provided by devdungeon.
# https://www.devdungeon.com/content/make-discord-bot-python
import discord
import GoogleDriveApiTest

USERID = '<@490655530172547073>'

client = discord.Client()

database = dict([("the big man", [":tophat:",":eyes:",":nose:",":lips:",":shirt:",":eggplant:",":jeans:",":mans_shoe:"])])

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
        elif msg.startswith('look sharp'):
            success, spreadsheet = GoogleDriveApiTest.FetchFile()
            if not success:
                await client.send_message(message.channel, "I can't do that")
            else:
                colsheet = [list(x) for x in [*zip(*spreadsheet)] if x is not ''] # transpose spreadsheet
                out = "All done, found "
                for n in colsheet:
                    database[n[0]] = n[1:]
                    out += n[0] + ", "
                await client.send_message(message.channel, out)

        elif msg.startswith('show me'):
            word = msg[len('show me'):].strip()
            out = "I don't know what " + word + " is"
            if word in database:
                out = ""
                for n in database[word]:
                    out += n + '\n'
                out = out[:-1]
            await client.send_message(message.channel, out)
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
