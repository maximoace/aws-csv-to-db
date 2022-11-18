import json
import boto3

from modules.model.session import Session
from modules.files.csv_file import CsvFile
from modules.files import forms

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    csv_file = s3.get_object(Bucket=bucket_name, Key=object_key)
    file = CsvFile(csv_file)
    file.filter_data(forms.get_field_names())
    file.format_data()
    Session.objects.insert_no_duplicate(file.data)
    return {
        'statusCode': 200,
        'body': json.dumps('Csv content successfully stored in the database')
    }
