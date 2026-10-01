import json

from kafka import KafkaConsumer
import mysql.connector


KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "crypto-market-data"

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3307
MYSQL_USER = "root"
MYSQL_PASSWORD = "admin"
MYSQL_DATABASE = "crypto_analytics"


# Connect to MySQL
db = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

cursor = db.cursor()

print("MySQL connection successful!")


# Connect to Kafka
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="crypto-mysql-consumer",
    value_deserializer=lambda value: json.loads(
        value.decode("utf-8")
    )
)


print("=" * 80)
print("CRYPTO MARKET KAFKA → MYSQL CONSUMER")
print("=" * 80)
print(f"Kafka Topic: {KAFKA_TOPIC}")
print(f"MySQL Database: {MYSQL_DATABASE}")
print("Waiting for live cryptocurrency events...")
print("Press CTRL+C to stop.")
print("=" * 80)


insert_query = """
INSERT INTO crypto_market_data (
    timestamp,
    coin_id,
    symbol,
    name,
    price_usd,
    market_cap_usd,
    volume_24h_usd,
    price_change_24h_pct,
    market_cap_rank
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""


try:

    for message in consumer:

        event = message.value

        data = (
            event["timestamp"],
            event["coin_id"],
            event["symbol"],
            event["name"],
            event["price_usd"],
            event["market_cap_usd"],
            event["volume_24h_usd"],
            event["price_change_24h_pct"],
            event["market_cap_rank"]
        )

        cursor.execute(insert_query, data)

        db.commit()

        print(
            f"[MYSQL] {event['symbol']:>6} | "
            f"Price: ${event['price_usd']:,.2f} | "
            f"24h Change: "
            f"{event['price_change_24h_pct']:.2f}% | "
            f"Saved to database"
        )


except KeyboardInterrupt:

    print("\nConsumer stopped.")


finally:

    cursor.close()
    db.close()
    consumer.close()