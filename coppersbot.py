# Work with Python 3.6
# This vulgar bot is based on sample code provided by devdungeon.
# https://www.devdungeon.com/content/make-discord-bot-python
import os
import discord
import GoogleDriveApiTest
import json

USERID = '<@490655530172547073>'

client = discord.Client()

database = dict()

async def cmd_hello(message):
    msg = 'IDIOT DETECTED. INITIALIZING STANDARD GREETING PROTOCOL. Hello {0.author.mention}.'.format(message)
    await message.channel.send(msg)

async def cmd_looksharp(message):
    success, spreadsheet = GoogleDriveApiTest.FetchFile()
    if not success:
        await message.channel.send("I can't do that")
    else:
        colsheet = [list(x) for x in [*zip(*spreadsheet)] if x is not ''] # transpose spreadsheet
        out = "All done, found "
        for n in colsheet:
            database[n[0]] = n[1:]
            out += n[0] + ", "
        await message.channel.send(out)

async def cmd_showme(message):
    msg = message.content
    if msg.split(' ')[1] != 'me':
        return
    word = msg[len('show me'):].strip()
    out = "I don't know what " + word + " is"
    if word in database:
        out = ""
        for n in database[word]:
            out += n + '\n'
        out = out[:-1]
    await message.channel.send(out)

async def cmd_pleasego(message):
    msg = 'gamer time'.format(message)
    await message.channel.send(msg)
    await client.logout()

async def cmd_client(message):
    await message.channel.send(discord.ClientUser.id)

async def cmd_gamer(message):
    activity = discord.Game(name=message.content[len('gamer'):], url='https://twitter.com', type=1)
    await client.change_presence(activity=activity)

database['commands'] = {
    'hello' : cmd_hello,
    'look_sharp' : cmd_looksharp,
    'show' : cmd_showme,
    'shoo' : cmd_pleasego,
    'client' : cmd_client,
    'gamer' : cmd_gamer
}

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if not message.content.startswith(USERID):
        return
    
    message.content = message.content[len(USERID):].lstrip()
    msg = message.content
    print(msg)
        
    if msg.split()[0] in database['commands'].keys():
        await database['commands'][msg.split()[0]](message)
    else:
        slang = {'b': ':b:', 's': ':heavy_dollar_sign:', 'a': ':a:', }
        out = ""
        for c in msg:
            if c.lower() in slang:
                out += slang[c.lower()]
            else:
                out += c
        await message.channel.send(out)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

if __name__ == "__main__":
    #load extra databases
    jsdb = json.load(open("database.json", "r"))
    for key in jsdb.keys():
        database[key] = jsdb[key]
    
    #filter python files from a folder
    directory = "Modules"
    mods = [x[:-3] for x in os.listdir(directory) if x.endswith('.py')]

    #import filtered files
    modules = __import__(directory, globals(), locals(), mods, 0)
    for m in mods:
        name, func = getattr(modules, m).register()
        database['commands'][name] = func
        globals()[name] = func

    file = open("DiscordToken.txt", "r")
    client.run(file.read())
    file.close()
    
