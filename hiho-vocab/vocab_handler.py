#!/usr/bin/env python3
import logging
import os
import boto3
import io
import json
from os.path import exists
from botocore.exceptions import ClientError
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload


s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')
logging.getLogger().setLevel(logging.INFO)
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = os.environ['FOLDER_ID']
FILE_ID = os.environ['FILE_ID']
transcribe_client = boto3.client('transcribe')

def lambda_handler(event, context):
	get_secret()
	if os.path.exists('/tmp/credentials.json'):
		creds = Credentials.from_authorized_user_file('/tmp/credentials.json', SCOPES)
		os.remove('/tmp/credentials.json')
	else:
		raise Exception("credentials not stored in /tmp/credentials.json")

	try:
		drive_service = build('drive', 'v3', credentials=creds)
	except HttpError as error:
		logging.error("An error occurred: {}".format(error))

	get_csv_from_drive(drive_service)
	upload_to_s3()
	update_vocab()
	os.remove('/tmp/vocab.csv')

	return {
		'statusCode': 200,
		'body': json.dumps('File Uploaded')
	}

def get_csv_from_drive(drive_service):
	logging.info("Pulling file from Drive ...")
	file_id = FILE_ID

	# mimeType='application/vnd.google-apps.spreadsheet'
	request = drive_service.files().export_media(fileId=file_id,
												mimeType='text/plain')
	fh = io.BytesIO()
	downloader = MediaIoBaseDownload(fh, request)
	done = False
	while done is False:
		status, done = downloader.next_chunk()
		logging.info("Download %d%%." % int(status.progress() * 100))
	#file_name = os.path.join(path, name)

	f = open('/tmp/vocab.csv', 'wb')
	f.write(fh.getvalue())

def update_vocab():
	logging.info("Updating Vocab")
	try:
		vocab_args = {'VocabularyName': 'Gymnastics', 'LanguageCode': 'en-US'}
		vocab_args['VocabularyFileUri'] = 's3://hiho-transcription/HIHO-vocab.csv'
		response = transcribe_client.update_vocabulary(**vocab_args)
		logging.info(
			"Updated custom vocabulary %s.", response['VocabularyName'])
	except ClientError:
		logging.exception("Couldn't update custom vocabulary Gymnastics.")
		raise

def upload_to_s3():
	logging.info("Uploading to S3")
	filename = "/tmp/vocab.csv"
	with open(filename) as f:
		string = f.read()

	encoded_string = string.encode("utf-8")
	encoded_string.replace(b',',bytes(	))
	logging.info(encoded_string)
	s3_path = "HIHO-vocab.csv"
	s3.put_object(Bucket="hiho-transcription",
					Key=s3_path,
					Body=encoded_string)
	logging.info("Uploading CSV to S3")

def get_secret():
	secret_name_user = "arn:aws:secretsmanager:us-east-1:161219206179:secret:HIHO/gauth-6xMdBe"
	region_name = "us-east-1"

	session = boto3.session.Session()
	client = session.client(
		service_name='secretsmanager',
		region_name=region_name
	)

	try:
		get_secret_value_response = client.get_secret_value(
			SecretId=secret_name_user
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
