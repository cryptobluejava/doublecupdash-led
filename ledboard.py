# ledboard.py
import asyncio
import struct
from bleak import BleakClient, BleakScanner

WRITE_UUID = ""
client = None
queue = asyncio.Queue(maxsize=1)
ledboard_id = ""


async def led_loop(ledboard_id):
    # Main loop to handle LED board connection and pixel updates
    await connect_to_ledboard(ledboard_id)
    while True:
        try:
            matrix = await queue.get()
            await send_pixels_to_ledboard(matrix)
        except Exception as e:
            print("Erro no envio para LED:", e)
            await asyncio.sleep(1)
            try:
                await connect_to_ledboard(ledboard_id)
            except Exception as e:
                print("Erro ao reconectar:", e)
                await asyncio.sleep(2)


async def connect_to_ledboard(ledboard_id):
    # Connect to the LED board using its Bluetooth address
    global client
    client = BleakClient(ledboard_id)
    await client.connect()
    await client.get_services()
    await client.write_gatt_char(WRITE_UUID, bytearray([5, 0, 4, 1, 1]))
    await asyncio.sleep(0.05)


async def enable_diy_mode():
    # Enable DIY mode on the LED board
    if client:
        await client.write_gatt_char(WRITE_UUID, bytearray([5, 0, 4, 1, 1]))
        await asyncio.sleep(0.05)


async def send_pixels_to_ledboard(matrix):
    # Send pixel data to the LED board
    if client:
        rgb_data = bytearray()
        for row in matrix:
            for r, g, b in row:
                rgb_data += bytes([r % 256, g % 256, b % 256])
        data_len = len(rgb_data)
        header = bytearray()
        header += struct.pack("<H", data_len + 9)
        header += b'\x00\x00'
        header += b'\x00'
        header += struct.pack("<I", data_len)
        payload = header + rgb_data
        await client.write_gatt_char(WRITE_UUID, payload)


async def disconnect_ledboard():
    # Disconnect from the LED board
    global client
    if client:
        await client.disconnect()
        client = None


async def renew_connection(ledboard_id):
    # Renew connection to the LED board
    await disconnect_ledboard()
    await led_loop(ledboard_id)


async def scan():
    # Scan for BLE devices and print their names and addresses
    devices = await BleakScanner.discover()
    for d in devices:
        print(f"{d.name} - {d.address}")


async def explore(client: BleakClient):
    # Show all services and characteristics
    for service in client.services:
        print(f"Service: {service.uuid}")
        for char in service.characteristics:
            print(f"  Characteristic: {char.uuid} (props: {char.properties})")