# Combined Pipeline and Kafka Consumer Project

This project consists of two primary scripts:

1. **Pipeline (`s3_data_download.py`)** - This script downloads specific files (CSV and JSON) from an Amazon S3 bucket, processes them, and combines multiple CSV files into a single output file. It uses `boto3` to interact with AWS S3 and manages environment variables using `python-dotenv`.

2. **Kafka Consumer (`kafka_data_processor.py`)** - This script consumes messages from a Kafka topic and updates an Amazon RDS database based on the consumed data, processing interactions like ratings and requests and logging errors for invalid messages.

---

## Features

### Pipeline

- Lists all S3 buckets in your AWS account.
- Downloads files from a specified bucket that match a set naming pattern.
- Combines multiple CSV files into one output CSV file.

### Kafka Consumer

- Connects to a Kafka topic and processes messages.
- Updates tables in Amazon RDS with exhibition interaction data.
- Logs processed messages, including validation errors for invalid messages.

---

## Prerequisites

### 1. AWS, Database, and Kafka Configurations

- Ensure you have access to an Amazon S3 bucket, an Amazon RDS database, and Kafka server details.

### 2. Environment Variables

- Store all necessary credentials and configurations in a single `.env` file with the following structure:

```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
DATABASE_USERNAME=your_db_username
DATABASE_PASSWORD=your_db_password
DATABASE_IP=your_db_host
DATABASE_PORT=your_db_port
DATABASE_NAME=your_db_name
BOOTSTRAP_SERVERS=your_kafka_servers
SECURITY_PROTOCOL=your_security_protocol
SASL_MECHANISM=your_sasl_mechanism
USERNAME=your_kafka_username
PASSWORD=your_kafka_password
GROUP_ID=your_kafka_group_id
```

---

## Installation

### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Project Directory Setup
- Create a data folder to store downloaded files for the Pipeline.
```bash
mkdir data
```

---

## Usage

### Running the Pipeline Script

1. **Run the Script**
```bash
python3 s3_data_download.py --bucket <your-bucket-name>
```

- Lists all S3 buckets, filters files in the specified bucket starting with `lmnh` and ending with .csv or .json
- Downloads these files and combines CSV files into `combined_exhibitions.csv` in the data folder.

### Running the Kafka Consumer Script
1. **Reset the database**
```bash
sh reset_db.sh
```

2. **Execute the Consumer**
- The following command includes optional arguments:
```bash
python kafka_data_processor.py --logs --max-messages 5000
```

- `--logs, -l`: Enables logging of processed messages and errors.
- `--max-messages, -m`: Sets the maximum number of messages to process (default is 100,000).

---

## Outputs
- **Pipeline Output:** The combined CSV file, `combined_exhibitions.csv`, is stored in the data folder.

- **Kafka Consumer Logs:** If logging is enabled, processed messages and validation errors are saved to `error_messages.txt`.

