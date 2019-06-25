
print("module 1 loaded")

async def Mod1func(message):
    await message.channel.send("module 1 function")
    

def register():
    print("module 1 registered")
    return Mod1func.__name__, Mod1func
