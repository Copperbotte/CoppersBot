
import os
import io
from datetime import datetime
import discord

import pickle

import matplotlib.pyplot as plt
import numpy as np

import time
import wand
import wand.image
#import requests
#requests.get(url)

USERID = ['<@!490655530172547073>', '<@490655530172547073>']
stalkchannel = None
SHEET = "Sheet2"
client = discord.Client()

commands = dict()

async def echo(msg, message):
    print(msg)
    await message.channel.send(msg)

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

#def download_img(url):
#    try:
#        img = requests.get(url)
#        buff = io.BytesIO()

################################################################################
################################### commands ###################################
################################################################################

async def cmd_quit(message, cmd, args):
    await message.channel.send("quitting")
    await client.logout()
    return
commands['quit'] = cmd_quit

async def cmd_help(message, cmd, args):
    await message.channel.send("<@133719771702099968> Help!!")
    return
commands['help'] = cmd_help

async def cmd_woah(message, cmd, args):
    channels = message.guild.text_channels
    msg = ""
    for c in channels:
        msg += c.name + ' '
    await message.channel.send(msg)
    return
commands['woah'] = cmd_woah

def centerCommentBlock(comment, block=80):
    off = (block - len(comment)) // 2
    out = '#'*(off-1) + ' ' + comment + ' '
    out += '#' * (80-len(out))
    out = '#'*80 + '\n' + out + '\n' + '#'*80
    return out

async def cmd_centerCommentBlock(message, cmd, args):
    block = centerCommentBlock(args[0])
    await message.channel.send(block)
    return
commands['centerCommentBlock'] = cmd_centerCommentBlock

async def cmd_plot(message, cmd, args):
    x = np.arange(-1,1+0.01,0.01)
    y = x**3 - 3*x**2

    fig, ax = plt.subplots()
    ax.set_title("Test graph")
    ax.plot(x,y)
    fig.canvas.draw()
    img = np.array(fig.canvas.renderer.buffer_rgba())

    buf = io.BytesIO()
    plt.imsave(buf, img, format='png')
    buf.seek(0)

    file = discord.File(buf, "Test graph.png")
    await message.channel.send(file=file)
    return
commands['plot'] = cmd_plot

_Test_ = None

async def cmd_beads(message, cmd, args):
    global _Test_
    #find image within 500 messages
    img = None
    async for msg in message.channel.history(limit=500):
        print(msg.content)
        if not msg.attachments:
            print('no attachments')
            continue
        print('yes attachment')
        img = msg.attachments[-1]
        break
    if not img:
        await message.channel.send("no images found in the last 500 messages")
        return
    
    buf = await img.to_file()
    _Test_ = buf
    
    i = wand.image.Image(file=buf.fp)
    i.resize(198,148)
    i.border(color=wand.color.Color('transparent'), width=200, height=150)
    i.gaussian_blur(sigma=1)

    background = open(r'beads.png', 'rb')
    template = wand.image.Image(file=background)
    background.close()
    
    #template.composite(i, 537, 33)
    template.composite(i, 534 - 200, 31 - 150)

    buf2 = io.BytesIO(template.make_blob('PNG'))
    name = img.filename[:img.filename.rfind('.')]
    
    file = discord.File(buf2, name +" beads.png")
    await message.channel.send(file=file)
    return
commands['beads'] = cmd_beads
    
#async def cmd_buildDatabase(message, cmd, args):
    

################################################################################
################################## main loop ###################################
################################################################################

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    conds = [message.content.startswith(USERID[0]), message.content.startswith(USERID[1]),
             message.content.lstrip()[0] == '>', message.content.lstrip()[0] == '!']
    
    if not any(conds):
        return
    
    cut = len(USERID[0])
    if conds[1]:
        cut = len(USERID[1])
    if conds[2] or conds[3]:
        cut = 1
    
    message.content = message.content[cut:].lstrip()
    msg = message.content
    print(msg)

    args = list(map(lambda s: s.strip(), msg.split()))
    cmd = args[0]
    args = args[1:]

    #if cmd == "graph":
    #    img = getPlotImg()
    #    buf = io.BytesIO()
    #    plt.imsave(buf, img, format='png')
    #    buf.seek(0)
    #    dimg = discord.File(buf, 'stonk.png')
    #    await message.channel.send(file=dimg)
    #    return
    
    if message.author.id != 133719771702099968: #me
        return

    if cmd in commands.keys():
        return await commands[cmd](message, cmd, args)

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
    
