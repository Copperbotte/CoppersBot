
import numpy as np
print("Numpy module loaded")

async def Numpyfunc(message, msg, client):
    out = "Numpy sine: " +  str(np.sin(10.0))
    await client.send_message(message.channel, out)

def register():
    print("Numpy module registered") 
    return Numpyfunc.__name__, Numpyfunc
