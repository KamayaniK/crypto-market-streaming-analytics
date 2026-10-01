import json
import time
from datetime import datetime, timezone

from kafka import KafkaProducer

from api_collector import fetch_market_data, create_events

KAFKA_SERVER = "localhost:9092"
KAFKA_TOPIC = "crypto-market-data"

COLLECTION_INTERVAL = 300  # 5 minutes

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    acks="all"
)


def send_events(events):
    for event in events:
        future = producer.send(
            KAFKA_TOPIC,
            value=event
        )

        metadata = future.get(timeout=10)

        print(
            f"[KAFKA] {event['symbol']:>6} | "
            f"Price: ${event['price_usd']:,.2f} | "
            f"24h Change: {event['price_change_24h_pct']:.2f}% | "
            f"Partition: {metadata.partition} | "
            f"Offset: {metadata.offset}"
        )

    producer.flush()


def main():

    print("=" * 80)
    print("REAL-TIME CRYPTO MARKET STREAM")
    print("=" * 80)
    print("Source: CoinGecko API")
    print("Assets: BTC, ETH, SOL, XRP, DOGE")
    print(f"Kafka Topic: {KAFKA_TOPIC}")
    print("Collection interval: 5 minutes")
    print("Press CTRL+C to stop.")
    print("=" * 80)

    try:

        while True:

            timestamp = datetime.now(timezone.utc).isoformat()

            print(f"\n[{timestamp}] Fetching live market data...")

            market_data = fetch_market_data()

            events = create_events(market_data)

            send_events(events)

            print(
                f"[{timestamp}] "
                f"Successfully streamed {len(events)} events."
            )

            print(
                f"Waiting {COLLECTION_INTERVAL} seconds..."
            )

            time.sleep(COLLECTION_INTERVAL)

    except KeyboardInterrupt:

        print("\nStreaming producer stopped.")

    finally:

        producer.close()


if __name__ == "__main__":
    main()