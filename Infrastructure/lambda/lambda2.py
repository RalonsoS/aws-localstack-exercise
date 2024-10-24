def lambda_handler(event, context):
    s3 = boto3.client('s3', endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:{os.environ['EDGE_PORT']}")
    bucket = "input-bucket"
    key = "processed_test_input.csv"
    
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read().decode('utf-8').splitlines()
    
    # Process CSV
    reader = csv.reader(data)
    processed_data = []
    for row in reader:
        age_group = 0 if int(row[2]) < 5 else 1
        row.append(age_group)
        processed_data.append(row)
    
    # Save processed file to output-bucket
    processed_csv = '\n'.join([','.join(map(str, row)) for row in processed_data])
    s3.put_object(Bucket="output-bucket", Key="processed_test_input.csv", Body=processed_csv)
    
    return {"statusCode": 200, "body": "CSV processed with AgeGroup"}
