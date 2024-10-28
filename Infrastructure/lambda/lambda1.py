import boto3
import csv
import os

def lambda_handler(event, context):
    # Crear cliente de S3
    s3 = boto3.client('s3', endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:{os.environ['EDGE_PORT']}")
    
    # Simular un evento de prueba si 'Records' no está presente
    if 'Records' not in event:
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'input-bucket'},
                    'object': {'key': 'test_input.csv'}
                }
            }]
        }
    
    try:
        # Obtener el bucket y key del archivo a procesar
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        # Descargar el archivo desde S3
        response = s3.get_object(Bucket=bucket, Key=key)
        data = response['Body'].read().decode('utf-8').splitlines()
        
        # Procesar el archivo CSV
        reader = csv.reader(data)
        processed_data = []
        for row in reader:
            # Validar que la columna de edad esté en el índice esperado
            try:
                row[2] = str(max(0, int(row[2])))  # Reemplaza valores negativos de edad con 0
            except (ValueError, IndexError):
                row.append("0")  # Añade una edad predeterminada si no es válida
            processed_data.append(row)
        
        # Generar el CSV procesado como texto
        processed_csv = '\n'.join([','.join(row) for row in processed_data])
        
        # Guardar el CSV procesado en S3
        processed_key = "processed_" + key
        s3.put_object(Bucket=bucket, Key=processed_key, Body=processed_csv)
        
        return {
            "statusCode": 200,
            "body": f"CSV procesado y guardado como {processed_key} en el bucket {bucket}."
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error procesando CSV: {str(e)}"
        }
