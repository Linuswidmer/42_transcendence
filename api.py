import asyncio
import websockets
import sys
import aioconsole
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
import ssl
import getpass

async def receive_message(websocket, queue):
	while True:
		try:
			message = await websocket.recv()
			print(message)
			await queue.put(message)
		except ConnectionClosedOK:
			print("Connection closed.")
			break
		except ConnectionAbortedError:
			print("Connection closed by the server.")
			break

async def send_message(uri):
	ssl_context = ssl.create_default_context()
	ssl_context.check_hostname = False
	ssl_context.verify_mode = ssl.CERT_NONE

	try:
		async with websockets.connect(uri, ssl=ssl_context) as websocket:
			queue = asyncio.Queue()
			asyncio.create_task(receive_message(websocket, queue))

			try:
				while True:
					password = getpass.getpass("Enter the admin password: ")
					await websocket.send(password)

					response = await queue.get()
					if response == "Authentication successful":
						break
					else:
						print("Invalid password, please try again.")

				while True:
					await asyncio.sleep(0.05)
					message = await aioconsole.ainput(":> ")
					await websocket.send(message)
					if message == "exit":
						break
			except KeyboardInterrupt:
				print("\nProgram interrupted by user.")
				await websocket.close()
				sys.exit(0)

	except ConnectionRefusedError:
		print("Could not connect to the server. Please make sure the server is running and accepting connections.")


if len(sys.argv) != 2:
	print(f"Usage: {sys.argv[0]} <websocket-url>")

else:
	asyncio.run(send_message(sys.argv[1]))