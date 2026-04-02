#this is overcomplicated and scuffed but it works most of the time
import asyncio
from bleak import BleakClient, BleakScanner
import matplotlib.pyplot as plt
from collections import deque
import threading

DATA_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb" #DO NOT CHANGE

data = deque([0]*200, maxlen=200)
plt.ion()
fig, ax = plt.subplots()

#BLE scan 
async def ble_task():
    devices = await BleakScanner.discover()
    esp32 = next((d for d in devices if d.name == "ESP32_EMG"), None)
    if not esp32:
        print("no esp32 connection")
        return

    async with BleakClient(esp32) as client:
        print("connected to esp32")

        def callback(sender, value):  
            try:
                val = float(value.decode())
                data.append(val)
            except Exception as e:
                print("value decode error:", e)

        await client.start_notify(DATA_UUID, callback)

        #upd
        while True:
            await asyncio.sleep(1)

#run BLE in a separate MTA thread so i can actually use matlib 
def run_ble_loop():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(ble_task())

ble_thread = threading.Thread(target=run_ble_loop)
ble_thread.start()

#plotting in main thread (STA)
while True:
    ax.clear()
    ax.plot(data)
    ax.set_ylim(0, 3000)
    plt.pause(0.01)
