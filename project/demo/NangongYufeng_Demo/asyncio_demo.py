import asyncio

import threading

import random





async def fn(name,qu):
    while True:
        print(name,"ready to work")
        r=asyncio.run_coroutine_threadsafe(qu.get(),qu._loop)
        rs=r.result()
        print(name,"get work,working",rs)
        if rs=="over":
            asyncio.run_coroutine_threadsafe(qu.put("over"),qu._loop)
            print(name,"over")

        await asyncio.sleep(random.randint(1,3))
        print(name,"done,sleep")
        await asyncio.sleep(random.randint(1,3))
        print(name,"wake up")
        if rs=="over":            
            break

def t(name,qu):
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(fn(name,qu))
    
loop=asyncio.new_event_loop()  
asyncio.set_event_loop(loop)  
qu=asyncio.Queue()
tl=[threading.Thread(target=t,args=(i,qu)) for i in range(5)]
for i in tl:
    i.setDaemon(True)
    i.start()


async def pt(qu):
    for i in range(20):
        await asyncio.sleep(0.8)
        await qu.put(i)
        print("work need to do",qu)
    await qu.put("over")
    await asyncio.sleep(5)

loop.run_until_complete(pt(qu))

loop.close()
