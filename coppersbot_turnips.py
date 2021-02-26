
import os
import io
from datetime import datetime
import discord

import pickle
#from googleapiclient.discovery import build
#from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import Request

import matplotlib.pyplot as plt
import numpy as np

import time

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

USERID = ['<@!490655530172547073>', '<@490655530172547073>']
stalkchannel = None
SHEET = "Sheet2"
client = discord.Client()

async def echo(msg, message):
    print(msg)
    await message.channel.send(msg)

def initSheets(spreadsheet):
    creds = None
    print("creds")
    picklepath = 'token.pickle'
    if os.path.exists(picklepath):
        with open(picklepath, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(picklepath, 'wb') as token:
            pickle.dump(creds, token)
    print("service")
    service = build('sheets', 'v4', credentials=creds)
    print("sheet")
    sheet = service.spreadsheets()
    return sheet

def getData(ssrange):
    spreadsheet = "10zcHJfs8IV1IiN2JWEyPDluZhxsD7HNp0KU1WMfHRvw"
    sheet = initSheets(spreadsheet)
    print("get")
    result = sheet.values().get(spreadsheetId=spreadsheet, range=ssrange).execute()
    return result.get('values', [])

def setData(ssrange, data=[["12"]]):
    spreadsheet = "10zcHJfs8IV1IiN2JWEyPDluZhxsD7HNp0KU1WMfHRvw"
    sheet = initSheets(spreadsheet)
    print("set")
    newrange = SHEET + '!' + ssrange
    body = {'values': data}
    result = sheet.values().update(spreadsheetId=spreadsheet, range=newrange,
                                   valueInputOption="RAW", body=body).execute()
    print(result.get('updatedCells'))
    return result.get('updatedCells')

def toA1(c, r):
    c += 1
    out = ''
    while 0 < c:
        c, rem = divmod(c - 1, 26)
        out = chr(ord('A') + rem) + out
    out += str(r + 1)
    return out

def getPlotImg():
    sheet = getData(SHEET)
    values = [x[1:] for x in sheet]
    fig, ax = plt.subplots()
    ax.set_title(values[0][0])
    for r in range(1, len(sheet)):
        x = []
        y = []
        for i in range(2, len(sheet[r])):
            if sheet[r][i] != '':
                x.append(sheet[0][i])
                y.append(int(sheet[r][i]))
        ax.plot(x,y)
        ax.annotate(s=sheet[r][1], xy=(x[-1],y[-1]), xytext=(5,0), textcoords='offset points')
    fig.canvas.draw()
    return np.array(fig.canvas.renderer.buffer_rgba())

async def checkAndRegister(message, data):
    data = list(map(lambda x: x[0], data))[1:]
    #if the user isn't registered, give them a new row
    if str(message.author.id) not in data: 
        newdata = [[str(message.author.id), message.author.display_name]]
        datarange = toA1(0,1+len(data)) + ':' + toA1(1,1+len(data))
        setData(datarange, data=newdata)
        msg = message.author.display_name + " is now registered"
        await echo(msg, message)
        return len(data)
    #msg = message.author.display_name + " is in database"
    #await echo(msg, message)
    return data.index(str(message.author.id))

def getColumnFromCurrentTime(sheet):
    date = datetime.date(datetime.strptime(sheet[0][1], '%Y-%m-%d'))
    now = datetime.date(datetime.now())
    diff = (now - date).days - 1
    hour = datetime.time(datetime.now()).hour
    print('date', diff)
    print('hour', hour)
    n = 2 * diff
    if 12 <= hour:
        n += 1
    return n

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    #global stalkchannel
    #if stalkchannel == message.channel.id:
    #    word = message.content.strip().split()[0].strip()
    #    filtered = ''.join(list(filter(lambda c: c.isdigit(), word)))
    #    if len(filtered) != 0:
    #        await message.add_reaction(697974246059671552)
    #        return
    
    if not (message.content.startswith(USERID[0]) or message.content.startswith(USERID[1])):
        return

    cut = len(USERID[0])
    if message.content.startswith(USERID[1]):
        cut = len(USERID[1])
    
    message.content = message.content[cut:].lstrip()
    msg = message.content
    print(msg)

    args = list(map(lambda s: s.strip(), msg.split()))
    cmd = args[0]
    args = args[1:]

    stonkshort = all(map(str.isdigit, cmd))
    
    if cmd == "stonk" or stonkshort:
        data = getData(SHEET)
        row = 1 + await checkAndRegister(message, data)
        col = 2 + getColumnFromCurrentTime(data)
        
        if stonkshort:
            value = cmd
        else:
            value = args[0]
        print(value)
        print('row', row)
        print('col', col)
        setData(toA1(col, row), [[value]])
        await message.add_reaction("\U0001F360")
        return

    if cmd == "register":
        data = getData(SHEET)
        print(data)
        await checkAndRegister(message, data)
        return

    if cmd == "graph":
        img = getPlotImg()
        buf = io.BytesIO()
        plt.imsave(buf, img, format='png')
        buf.seek(0)
        dimg = discord.File(buf, 'stonk.png')
        await message.channel.send(file=dimg)
        return
    
    if message.author.id != 133719771702099968:
        return
    
    if cmd == "quit":
        await message.channel.send("quitting")
        await client.logout()
        return

    if cmd == "usechannel":
        stalkchannel = message.channel.id
        await echo("using this channel for stalk market", message)
        return

    if cmd == "getids":
        count = 0
        async for m in message.channel.history(limit=int(args[0])):
            print(m.author.id, m.author.display_name)
            count += 1
        await message.channel.send(":eyes:")
        return

    if cmd == "woah":
        channels = message.guild.text_channels
        msg = ""
        for c in channels:
            msg += c.name + ' '
        await message.channel.send(msg)
        return

    if cmd == "getHistory":
        absstarttime = time.time()
        for c in message.guild.text_channels:
            starttime = time.time()
            messages = await c.history(limit=None).flatten()
            endtime = time.time()
            i = len(messages)
            print(i)
            msg = "parsed " + str(i) + " messages"
            msg += " from " + c.name
            msg += " in " + str(endtime-starttime) + " seconds."
            await message.channel.send(msg)
        absendtime = time.time()
        await message.channel.send("completed in " + str(absendtime-absstarttime) + ' seconds.')
        return
    
@client.event
async def on_ready():
    global USERID
    USERID[0] = '<@!' + str(client.user.id) + '>'
    USERID[1] = '<@' + str(client.user.id) + '>'
    print('Logged in as')
    print(client.user.name)
    print(USERID[1])
    print('------')

if __name__ == "__main__":
    file = open("DiscordToken.txt", "r")
    client.run(file.read())
    file.close()
    
