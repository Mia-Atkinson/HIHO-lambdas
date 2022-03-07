#!/usr/bin/env python3
import json
import boto3
import os
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive']
logger = logging.getLogger(__name__)
SECRET_ARN = "arn:aws:secretsmanager:us-east-1:161219206179:secret:HIHO/gauth-6xMdBe"
REGION_NAME = "us-east-1"

def lambda_handler(event, context):
    get_secret()

    creds = None
    if os.path.exists('/tmp/credentials.json'):
        creds = Credentials.from_authorized_user_file('/tmp/credentials.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing Token")
            creds.refresh(Request())
        else:
            print("No valid tokens available")
            exit()
        write_secret(creds)

    return {
        'statusCode': 200,
        'body': json.dumps('Credentials updated in Secret Manager')
    }

def write_secret(creds):
    session = boto3.session.Session()
    client = session.client(
    	service_name='secretsmanager',
    	region_name=REGION_NAME
    )
    try:
        client.put_secret_value(
        SecretId=SECRET_ARN,
        SecretString=creds.to_json()
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e

def get_secret():
	session = boto3.session.Session()
	client = session.client(
		service_name='secretsmanager',
		region_name=REGION_NAME
	)

	try:
		get_secret_value_response = client.get_secret_value(
			SecretId=SECRET_ARN
		)
	except ClientError as e:
		if e.response['Error']['Code'] == 'DecryptionFailureException':
			raise e
		elif e.response['Error']['Code'] == 'InternalServiceErrorException':
			raise e
		elif e.response['Error']['Code'] == 'InvalidParameterException':
			raise e
		elif e.response['Error']['Code'] == 'InvalidRequestException':
			raise e
		elif e.response['Error']['Code'] == 'ResourceNotFoundException':
			raise e

	else:
		if 'SecretString' in get_secret_value_response:
			secret = get_secret_value_response['SecretString']
			f = open('/tmp/credentials.json', "w")
			f.write(secret)
			f.close()
			return(json.loads(secret))
