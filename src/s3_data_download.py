"""Script to process data from Kafka"""
import os
import boto3
import argparse


def get_aws_session():
    """Create and return AWS session"""
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    return boto3.Session(
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )


def get_buckets(client):
    """List all S3 buckets"""
    response = client.list_buckets()

    print('\nBuckets: ')
    for bucket in response['Buckets']:
        print(bucket['Name'])


def get_files_in_bucket(client, bucket_name):
    """List all the files in a given bucket"""
    response = client.list_objects_v2(Bucket=bucket_name)
    return response.get('Contents', [])


def download_files(client, bucket_name, files):
    """Download selected files from bucket and return CSV files"""

    csv_files = []

    print('\nDownloaded files: ')
    for obj in files:
        key = obj['Key']
        if key.startswith('lmnh') and key.endswith(('.csv', '.json')):
            if key.endswith('.csv'):
                csv_files.append(f"./data/raw/{key}")
            client.download_file(bucket_name, key, f"./data/raw/{key}")
            print(key)

    return csv_files


def combine_csv_files(csv_files, output_file='./data/processed/combined_exhibitions.csv'):
    """Combine multiple CSV files into a single output file"""

    with open(output_file, 'w', encoding='utf-8') as out_f:
        first_file = True
        for file in csv_files:
            with open(file, 'r', encoding='utf-8') as f:
                if first_file:
                    out_f.write(f.read())
                    first_file = False
                else:
                    next(f)
                    out_f.write(f.read())

    for file in csv_files:
        os.remove(file)


def get_args():
    """Handle command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bucket", "-b", required=True, help="Specify the name of the S3 bucket")
    arguments = parser.parse_args()
    return arguments


def main(bucket_name):
    """Main function to run extraction"""
    session = get_aws_session()
    client = session.client('s3')

    get_buckets(client)

    all_files = get_files_in_bucket(client, bucket_name)
    csv_files = download_files(client, bucket_name, all_files)

    combine_csv_files(csv_files)


if __name__ == "__main__":
    args = get_args()
    main(args.bucket)
