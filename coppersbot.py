
import os
import discord

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import matplotlib.pyplot as plt
import numpy as np

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

USERID = '<@!490655530172547073>'
client = discord.Client()

def getData():
    spreadsheet = "10zcHJfs8IV1IiN2JWEyPDluZhxsD7HNp0KU1WMfHRvw"
    ssrange = "B1:N2"
    creds = None
    print("creds")
    picklepath = r'token.pickle'
    if os.path.exists(picklepath):
        with open(picklepath, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(r'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(picklepath, 'wb') as token:
            pickle.dump(creds, token)
    print("service")
    service = build('sheets', 'v4', credentials=creds)
    print("sheet")
    sheet = service.spreadsheets()
    print("get")
    result = sheet.values().get(spreadsheetId=spreadsheet, range=ssrange).execute()
    return result.get('values', [])

def getPlotImg():
    values = getData()
    x = values[0][1:]
    y = values[1][1:]
    if len(y) == 0:
        y = [0]
    y2 = []
    for v in y:
        y2.append(int(v))
    if len(y2) < len(x):
        diff = len(x) - len(y2)
    for i in range(diff):
        y2.append(y2[-1])
    fig, ax = plt.subplots()
    ax.plot(x,y2)
    fig.canvas.draw()
    plt.imsave('plot.png', np.array(fig.canvas.renderer.buffer_rgba()))

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

    cmd = msg.split()[0].strip()

    if cmd == "quit":
        await message.channel.send("quitting")
        await client.logout()
        return

    if cmd == "get":
        getPlotImg()
        await message.channel.send("Image generated")
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
    
