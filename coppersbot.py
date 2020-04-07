
import os
import io
import discord

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import matplotlib.pyplot as plt
import numpy as np

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

USERID = '<@!490655530172547073>'
client = discord.Client()

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
    body = {'values': data}
    result = sheet.values().update(spreadsheetId=spreadsheet, range=ssrange,
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
    sheet = getData("Sheet1")
    values = [x[1:] for x in sheet]
    x = values[0][1:]
    fig, ax = plt.subplots()
    for n in range(len(sheet) - 1):
        y = values[n+1][1:]
        if len(y) == 0:
            y = [0]
        y2 = []
        for v in y:
            y2.append(int(v))
        diff = 0
        if len(y2) < len(x):
            diff = len(x) - len(y2)
        for i in range(diff):
            y2.append(y2[-1])
        ax.plot(x,y2)
    fig.canvas.draw()
    return np.array(fig.canvas.renderer.buffer_rgba())

async def checkRegistered(user, sheet):
    data = getData("Sheet1")
    data = list(map(lambda x: x[0], data))[1:]
    if str(message.author.id) not in data:
        newdata = [[str(message.author.id), message.author.display_name]]
        rang = toA1(0,1+len(data)) + ':' + toA1(1,1+len(data))
        setData(rang, data=newdata)
        msg = message.author.display_name + " is now registered"
        print(msg)
        await message.channel.send(msg)
        return
    msg = message.author.display_name + " is in database"
    print(msg)
    await message.channel.send(msg)
    return


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

    args = list(map(lambda s: s.strip(), msg.split()))
    cmd = args[0]
    args = args[1:]
    
    if cmd == "quit":
        await message.channel.send("quitting")
        await client.logout()
        return

    if cmd == "stonk":
        img = getPlotImg()
        buf = io.BytesIO()
        plt.imsave(buf, img, format='png')
        buf.seek(0)
        dimg = discord.File(buf, 'stonk.png')
        await message.channel.send(file=dimg)
        return
    
    if cmd == "set":
        res = setData(toA1(0,1))
        return

    if cmd == "register":
        data = getData("Sheet1")
        data = list(map(lambda x: x[0], data))[1:]
        if str(message.author.id) not in data:
            newdata = [[str(message.author.id), message.author.display_name]]
            rang = toA1(0,1+len(data)) + ':' + toA1(1,1+len(data))
            setData(rang, data=newdata)
            msg = message.author.display_name + " is now registered"
            print(msg)
            await message.channel.send(msg)
            return
        msg = message.author.display_name + " is in database"
        print(msg)
        await message.channel.send(msg)
        return
        
        
		
@client.event
async def on_ready():
    global USERID
    USERID = '<@!' + str(client.user.id) + '>'
    print('Logged in as')
    print(client.user.name)
    print(USERID)
    print('------')

if __name__ == "__main__":
    file = open("DiscordToken.txt", "r")
    client.run(file.read())
    file.close()
    
