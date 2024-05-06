import asyncio

import websockets

import sys

import aioconsole

from websockets.exceptions import ConnectionClosedOK

import ssl



async def receive_message(websocket):

	while True:

		try:

			response = await websocket.recv()

			print(f"Response from server: {response}")

			#await asyncio.sleep(2)

		except ConnectionClosedOK:

			print("Connection closed by the server.")

			break


async def send_message(uri):

	ssl_context = ssl.create_default_context()

	ssl_context.check_hostname = False

	ssl_context.verify_mode = ssl.CERT_NONE



	# csrf_token = get_csrf_token("127.0.0.1:8443", "/home/")

	#print("csrf:", csrf_token)

	# headers = {

	# 	'Cookie': f'csrftoken={csrf_token}',

	# 	# other headers...

	# }



	async with websockets.connect(uri, ssl=ssl_context) as websocket:

		asyncio.create_task(receive_message(websocket))



		while True:

			message = await aioconsole.ainput("")

			await websocket.send(message)

			if message == "exit":

				break


if len(sys.argv) != 2:

	print(f"Usage: {sys.argv[0]} <websocket-url>")

else:

	asyncio.run(send_message(sys.argv[1]))