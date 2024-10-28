import boto3
import csv
import os

def lambda_handler(event, context):
    # Crear cliente de S3
    s3 = boto3.client('s3', endpoint_url=f"http://{os.environ['LOCALSTACK_HOSTNAME']}:{os.environ['EDGE_PORT']}")

    # Simulación de evento si 'Records' no está presente
    if 'Records' not in event:
        event = {
            'Records': [{
                's3': {
                    'bucket': {'name': 'input-bucket'},
                    'object': {'key': 'processed_test_input.csv'}
                }
            }]
        }

    try:
        # Obtener el bucket de origen y la clave del archivo a procesar
        input_bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
        
        # Descargar el archivo procesado desde input-bucket
        response = s3.get_object(Bucket=input_bucket, Key=key)
        data = response['Body'].read().decode('utf-8').splitlines()
        
        # Leer y añadir la nueva columna AgeGroup
        reader = csv.reader(data)
        header = next(reader)  # Leer la primera fila como encabezado
        header.append("AgeGroup")  # Añadir la columna AgeGroup al encabezado

        updated_data = [header]  # Iniciar el archivo procesado con el encabezado actualizado
        for row in reader:
            age = int(row[2])  # Supone que la edad está en la tercera columna
            age_group = 0 if age < 5 else 1  # Asignar AgeGroup según la edad
            row.append(str(age_group))  # Añadir la nueva columna al registro
            updated_data.append(row)
        
        # Generar el nuevo CSV como texto
        updated_csv = '\n'.join([','.join(row) for row in updated_data])
        
        # Guardar el archivo con la columna añadida en output-bucket
        output_bucket = "output-bucket"  # Nombre del bucket de salida
        new_key = "updated_" + key
        s3.put_object(Bucket=output_bucket, Key=new_key, Body=updated_csv)
        
        return {
            "statusCode": 200,
            "body": f"Columna AgeGroup añadida y archivo guardado como {new_key} en el bucket {output_bucket}."
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error al añadir columna AgeGroup: {str(e)}"
        }
