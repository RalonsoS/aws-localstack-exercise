import boto3
import csv
import os

def lambda_handler(event, context):
    if 'Records' not in event:
        return {"statusCode": 400, "body": "Event does not contain 'Records'"}

    s3 = boto3.client('s3', endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:{os.environ['EDGE_PORT']}")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read().decode('utf-8').splitlines()
    
    # Process CSV
    reader = csv.reader(data)
    processed_data = []
    for row in reader:
        row[2] = max(0, int(row[2]))  # Replace negative age with 0
        processed_data.append(row)
    
    # Save processed file back to S3
    processed_csv = '\n'.join([','.join(map(str, row)) for row in processed_data])
    s3.put_object(Bucket=bucket, Key="processed_test_input.csv", Body=processed_csv)
    
    return {"statusCode": 200, "body": "CSV processed"}
