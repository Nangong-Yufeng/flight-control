import asyncio
import threading
 
def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
    print('asyncio.Task.all_tasks().pop().result()', asyncio.Task.all_tasks().pop().result())
    
    
async def do_some_work(name):
    for i in range(5):
        print(f"{name}: is working")
        await asyncio.sleep(1)
    return True
        
loop = asyncio.new_event_loop()
 
threading.Thread(target=start_loop, args=(loop,)).start()
 
task = loop.create_task(do_some_work("Lili"))
 
loop._csock.send(b'\0')
 
while True:
    if task.done():
        loop.stop()
        loop._csock.send(b'\0')
        break