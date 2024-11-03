"""Main ETL pipeline script"""
import csv
from os import environ
import logging
import argparse
from datetime import datetime
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from s3_data_download import main


def get_connection():
    """Connect to database"""
    return psycopg2.connect(
        user=environ["DATABASE_USERNAME"],
        password=environ["DATABASE_PASSWORD"],
        host=environ["DATABASE_IP"],
        port=environ["DATABASE_PORT"],
        database=environ["DATABASE_NAME"]
    )


def get_cursor(connection):
    """Retrieve cursor"""
    return connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


def insert_rating_interaction(exhibition_id, val, event_at):
    """Add to rating interaction table"""
    cursor.execute(
        "SELECT rating_id FROM rating WHERE rating_value = %s", (int(val),))
    rating_id = cursor.fetchone()

    cursor.execute("""
        INSERT INTO rating_interaction (exhibition_id, rating_id, event_at)
        VALUES (%s, %s, %s)""", (exhibition_id, rating_id[0], event_at))
    conn.commit()


def insert_request_interaction(exhibition_id, type_val, event_at):
    """Add to request interaction table"""
    cursor.execute("""
    SELECT request_id FROM request WHERE request_value = %s
    """, (int(type_val),))
    request_id = cursor.fetchone()
    cursor.execute("""
        INSERT INTO request_interaction (exhibition_id, request_id, event_at)
        VALUES (%s, %s, %s)""", (exhibition_id, request_id[0], event_at))
    conn.commit()


def process_csv(csv_file, rows):
    """Read CSV and update database"""
    logging.info("Reading CSV File")
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= rows:
                break
            event_at = datetime.strptime(row['at'], '%Y-%m-%d %H:%M:%S')
            site = 1+int(row['site'])
            val = int(row['val'])
            type_val = float(row['type']) if row['type'] else None

            if val == -1 and type_val is not None:
                insert_request_interaction(site, type_val, event_at)
            else:
                insert_rating_interaction(site, val, event_at)


def config_log_file():
    """File logs configuration"""
    logging.basicConfig(
        filename="pipeline.log",
        encoding="utf-8",
        filemode="a",
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.INFO,
    )


def config_log_terminal():
    """Terminal logs configuration"""
    logging.basicConfig(
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.INFO,
    )


def get_args():
    """Handle command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bucket", "-b", required=True, help="Specify the name of the S3 bucket")
    parser.add_argument(
        "--rows", "-r", type=int, required=True, help="Number of rows to upload to database")
    parser.add_argument("--logs", "-l", action="store_true",
                        help="Enable file logging")

    arguments = parser.parse_args()
    return arguments


if __name__ == "__main__":
    load_dotenv('.env')

    args = get_args()
    if args.logs:
        config_log_file()
    else:
        config_log_terminal()

    logging.info("Starting Resources Download")
    main(args.bucket)
    logging.info("Download Complete")

    logging.info("Establishing Database Connection")
    conn = get_connection()
    logging.info("Connected to %s", environ["DATABASE_NAME"])
    cursor = get_cursor(conn)
    logging.info("Connection Established")

    CSV_PATH = './data/processed/combined_exhibitions.csv'
    logging.info("Adding Data to Database")
    process_csv(CSV_PATH, args.rows)
    logging.info("Database Populated")

    cursor.close()
    conn.close()
