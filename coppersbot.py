
import discord

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

USERID = '<@!490655530172547073>'
client = discord.Client()

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
    
