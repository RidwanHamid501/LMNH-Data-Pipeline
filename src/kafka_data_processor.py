'''Script to process data from Kafka'''
from os import environ
import argparse
import json
import logging
from datetime import datetime, timezone, time
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from confluent_kafka import Consumer


TOPIC = "lmnh"


def get_connection() -> psycopg2.extensions.connection:
    """Connect to database"""
    return psycopg2.connect(
        user=environ["DATABASE_USERNAME"],
        password=environ["DATABASE_PASSWORD"],
        host=environ["DATABASE_IP"],
        port=environ["DATABASE_PORT"],
        database=environ["DATABASE_NAME"]
    )


def get_cursor(connection: psycopg2.extensions.connection) -> psycopg2.extras.DictCursor:
    """Retrieve cursor"""
    return connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


def insert_rating_interaction(cursor, conn, exhibition_id: int, val: int, event_at: str) -> None:
    """Add to rating interaction table"""
    cursor.execute(
        "SELECT rating_id FROM rating WHERE rating_value = %s", (int(val),))
    rating_id = cursor.fetchone()

    cursor.execute("""
        INSERT INTO rating_interaction (exhibition_id, rating_id, event_at)
        VALUES (%s, %s, %s)""", (exhibition_id, rating_id[0], event_at))
    conn.commit()


def insert_request_interaction(cursor, conn, exhibition_id: int,
                               type_val: float, event_at: str) -> None:
    """Add to request interaction table"""
    cursor.execute("""
    SELECT request_id FROM request WHERE request_value = %s
    """, (int(type_val),))
    request_id = cursor.fetchone()
    cursor.execute("""
        INSERT INTO request_interaction (exhibition_id, request_id, event_at)
        VALUES (%s, %s, %s)""", (exhibition_id, request_id[0], event_at))
    conn.commit()


def process_message(message: dict, cursor, conn) -> None:
    """Process a single Kafka message and update the database"""
    logging.info("Processing Kafka message")

    event_at = datetime.fromisoformat(message['at'])
    event_at_utc = event_at.astimezone(timezone.utc)
    formatted_event_at = event_at_utc.strftime('%Y-%m-%d %H:%M:%S')

    site = 1 + int(message['site'])
    val = int(message['val'])
    type_val = float(
        message['type']) if 'type' in message else None

    if val == -1 and type_val is not None:
        insert_request_interaction(
            cursor, conn, site, type_val, formatted_event_at)
    else:
        insert_rating_interaction(cursor, conn, site, val, formatted_event_at)


def validate_message(message: dict) -> list[str]:
    """Validate messages"""
    errors = []

    def validate_time(at):
        try:
            timestamp = datetime.strptime(at, "%Y-%m-%d %H:%M:%S")
            if not (time(8, 45) <= timestamp.time() <= time(18, 15)):
                return False
            return True
        except (ValueError, TypeError):
            return False

    required_keys = {
        'at': validate_time,
        'site': lambda x: isinstance(x, int) and 0 <= x <= 4,
        'val': lambda x: isinstance(x, int) and -1 <= x <= 4,
        'type': lambda x: isinstance(x, int) and x in {0, 1},
    }

    for key, rule in required_keys.items():
        if key not in message:
            if key == 'type' and message.get('val') != -1:
                continue
            errors.append(f"missing '{key}' key")
        elif rule and not rule(message[key]):
            if key == 'at':
                errors.append(
                    f"'{key}' must be in 'YYYY-MM-DD HH:MM:SS' format and between 8:45 AM and 6:15 PM")
            else:
                errors.append(f"'{key}' is invalid")

    if message.get('val') == -1 and 'type' not in message:
        errors.append("missing 'type' key when 'val' is -1")

    return errors


def get_args() -> argparse.Namespace:
    """Handle command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", "-l", action="store_true",
                        help="Enable file logging")
    parser.add_argument("--max-messages", "-m", type=int, default=100000,
                        help="Maximum number of messages to process (default: 100000)")
    arguments = parser.parse_args()
    return arguments


def config_loggers(enable_file_logging=False):
    """Configure loggers for errors and successful messages."""
    if enable_file_logging:
        logging.basicConfig(
            filename="error_messages.txt",
            encoding="utf-8",
            filemode="a",
            format="{asctime} - {levelname} - {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M",
            level=logging.INFO,
        )
    else:
        logging.disable(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("{message}", style="{"))
    logging.getLogger().addHandler(console_handler)


if __name__ == "__main__":
    load_dotenv()

    args = get_args()
    config_loggers(enable_file_logging=args.logs)

    conns = get_connection()
    cursors = get_cursor(conns)

    kafka_config = {
        'bootstrap.servers': environ["BOOTSTRAP_SERVERS"],
        'security.protocol': environ["SECURITY_PROTOCOL"],
        'sasl.mechanisms': environ["SASL_MECHANISM"],
        'sasl.username': environ["USERNAME"],
        'sasl.password': environ["PASSWORD"],
        'group.id': environ["GROUP_ID"],
        'auto.offset.reset': 'latest'
    }

    consumer = Consumer(kafka_config)
    consumer.subscribe([TOPIC])

    MESSAGE_COUNT = 0
    max_messages = args.max_messages

    while MESSAGE_COUNT < max_messages:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            logging.error(f"ERROR: {msg.error()}")
        else:
            MESSAGE_COUNT += 1

            message_value = json.loads(msg.value().decode('utf-8'))
            errors_new = validate_message(message_value)
            if errors_new:
                logging.info(f"""Message {MESSAGE_COUNT}: {
                             message_value} -- Invalid: {', '.join(errors_new)}""")
            else:
                logging.info(f"Message {MESSAGE_COUNT}: {message_value}")
                process_message(message_value, cursors, conns)
