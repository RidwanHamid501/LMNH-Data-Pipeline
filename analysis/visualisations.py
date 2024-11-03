"""Connects to a database to retrieve exhibition rating data and generates 
visualisations of average ratings and rating counts per hour."""

from os import environ
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import matplotlib.pyplot as plt


def get_connection():
    """Connect to the database."""
    return psycopg2.connect(
        user=environ["DATABASE_USERNAME"],
        password=environ["DATABASE_PASSWORD"],
        host=environ["DATABASE_IP"],
        port=environ["DATABASE_PORT"],
        database=environ["DATABASE_NAME"]
    )


def get_cursor(connection):
    """Retrieve cursor."""
    return connection.cursor(cursor_factory=psycopg2.extras.DictCursor)


def run_query(cursor, query):
    """Run a SQL query and return the result."""
    cursor.execute(query)
    return cursor.fetchall()


def fetch_avg_rating(cursor):
    """Fetch average ratings per exhibition."""
    query = """
        SELECT e.exhibition_name, AVG(r.rating_value) AS avg_rating
        FROM rating_interaction AS ri
        JOIN exhibition AS e ON ri.exhibition_id = e.exhibition_id
        JOIN rating AS r ON ri.rating_id = r.rating_id
        GROUP BY e.exhibition_name
        ORDER BY e.exhibition_name;
    """
    return run_query(cursor, query)


def fetch_ratings_per_hour(cursor):
    """Fetch number of ratings per hour."""
    query = """
        SELECT EXTRACT (HOUR FROM ri.event_at) AS hour, COUNT(*) AS num_ratings
        FROM rating_interaction AS ri
        GROUP BY hour
        ORDER BY hour;
    """
    return run_query(cursor, query)


def visualize_avg_rating(data):
    """Generate bar plot for average ratings per exhibition."""
    exhibition_names = [row['exhibition_name'] for row in data]
    avg_ratings = [row['avg_rating'] for row in data]

    plt.figure(figsize=(10, 6))
    plt.bar(exhibition_names, avg_ratings, color='purple')
    plt.title('Average Rating per Exhibition')
    plt.xlabel('Exhibition')
    plt.ylabel('Average Rating')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('average_exhibition_rating.png')
    plt.close()


def visualize_ratings_per_hour(data):
    """Generate line plot for number of ratings per hour."""
    hours = [row['hour'] for row in data]
    num_ratings = [row['num_ratings'] for row in data]

    plt.figure(figsize=(10, 6))
    plt.plot(hours, num_ratings, marker='o', color='red')
    plt.title('Number of Ratings per Hour')
    plt.xlabel('Hour')
    plt.ylabel('Number of Ratings')
    plt.grid(True)
    plt.savefig('ratings_per_hour.png')
    plt.close()


def generate_visualizations():
    """Fetch data and generate visualizations."""
    conn = get_connection()
    cursor = get_cursor(conn)
    try:
        avg_rating_data = fetch_avg_rating(cursor)
        ratings_per_hour_data = fetch_ratings_per_hour(cursor)

        visualize_avg_rating(avg_rating_data)
        visualize_ratings_per_hour(ratings_per_hour_data)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_dotenv()
    generate_visualizations()
