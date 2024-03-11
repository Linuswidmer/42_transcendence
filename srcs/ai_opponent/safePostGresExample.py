#Example to store data to PostGres SQL with 
# pip install psycopg2

import psycopg2

class GameStatsCollector:
	def __init__(self):
		# Initialize your variables for collecting data
		self.score = 0
		self.duration = 0
	
	def collect_data(self, score, duration):
		# Collect data during the game
		self.score = score
		self.duration = duration
	
	def store_data_to_database(self):
		# Connect to the PostgreSQL database
		conn = psycopg2.connect(
			dbname="your_database_name",
			user="your_username",
			password="your_password",
			host="your_host",
			port="your_port"
		)

		# Create a cursor object
		cursor = conn.cursor()

		# Create a table if it doesn't exist
		cursor.execute("""
			CREATE TABLE IF NOT EXISTS game_stats (
				id SERIAL PRIMARY KEY,
				score INTEGER,
				duration INTEGER
			)
		""")

		# Insert data into the table
		cursor.execute("""
			INSERT INTO game_stats (score, duration)
			VALUES (%s, %s)
		""", (self.score, self.duration))

		# Commit the transaction
		conn.commit()

		# Close the cursor and the connection
		cursor.close()
		conn.close()

# Example usage
collector = GameStatsCollector()
# Assuming you have collected some data during the game
collector.collect_data(score=100, duration=120)
collector.store_data_to_database()