
import os
import discord

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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
        data = getData()
        msg = ""
        for row in data:
            for col in row:
                msg += str(col) + ' '
            msg += '\n'
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
    
