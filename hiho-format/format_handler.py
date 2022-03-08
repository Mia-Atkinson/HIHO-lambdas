#!/usr/bin/env python3
import json
import boto3
import os
import sys
import datetime
import logging
import urllib
from os.path import exists
from botocore.exceptions import ClientError
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from apiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = os.environ['FOLDER_ID']
INTRO = """\n[Intro Music Plays: Din Daa Daa (Dub), Song by George Kranz]
Din Daa Daa, Doe Doe Doe
(Bah!) Din Daa Daa, Doe Doe
(Bah!) Din Daa Daa, Doe Doe Doe
(Bah!) Din Daa Daa, Doe Doe"""
OUTRO = """\n[Outro Music Plays: Din Daa Daa (Dub), Song by George Kranz]
Din Daa Daa, Doe Doe Doe
(Bah!) Din Daa Daa, Doe Doe
(Bah!) Din Daa Daa, Doe Doe Doe
(Bah!) Din Daa Daa, Doe Doe"""

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')
logging.getLogger(__name__).setLevel(logging.INFO)
logging.basicConfig(format='%(levelname)s: %(message)s')

def lambda_handler(event, context):
	# Get the object from the event and show its content type
	bucket = event['Records'][0]['s3']['bucket']['name']
	key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
	logging.info(f'Key: {key}')
	try:
		response = s3.get_object(Bucket=bucket, Key=key)
		data = response["Body"].read().decode('utf-8')
		data_dict = json.loads(data)
	except Exception as e:
		logging.error('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
		raise e
	s3_file_name = os.path.basename(key)
	job_name = os.path.splitext(s3_file_name)[0]

	get_secret()

	if os.path.exists('/tmp/credentials.json'):
		creds = Credentials.from_authorized_user_file('/tmp/credentials.json', SCOPES)
		os.remove('/tmp/credentials.json')
	else:
		raise Exception("credentials not stored in /tmp/credentials.json")
	try:
		service = build('drive', 'v3', credentials=creds)
	except HttpError as error:
		logging.error(f'An error occurred: {error}')

	# Format File
	logging.info("Filename: ", job_name)
	format_file(data_dict, job_name)

	upload_file(job_name, service)
	upload_to_s3(job_name, bucket)
	delete_me = '/tmp/'+job_name+'.txt'
	os.remove(delete_me)

	return {
		'statusCode': 200,
		'body': json.dumps('File Uploaded')
	}

def upload_to_s3(job_name, bucket):
	filename = "/tmp/{}.txt".format(job_name)
	with open(filename) as f:
		string = f.read()
	encoded_string = string.encode("utf-8")
	s3_path = "text_output/{}.txt".format(job_name)
	s3.put_object(Bucket=bucket, Key=s3_path, Body=encoded_string)
	logging.info("Uploading {} to S3".format(s3_path))

def format_file(input_json, job_name):
	with open('/tmp/'+job_name+'.txt', "w") as w:
		data = input_json
		labels = data['results']['speaker_labels']['segments']
		speaker_start_times={}
		for label in labels:
			for item in label['items']:
				speaker_start_times[item['start_time']] =item['speaker_label']
		items = data['results']['items']
		lines=[]
		line=''
		time=0
		speaker='null'
		i=0
		replace_words=[" Uh ", " uh ", " Um ", " um "," like "," Like "," um, "," uh, "]
		for item in items:
			i=i+1
			content = item['alternatives'][0]['content']
			if item.get('start_time'):
				current_speaker=speaker_start_times[item['start_time']]
			elif item['type'] == 'punctuation':
				line = line+content
			if current_speaker != speaker:
				if speaker:
					lines.append({'speaker':speaker, 'line':line, 'time':time})
				line=content
				speaker=current_speaker
				time=item['start_time']
			elif item['type'] != 'punctuation':
				line = line + ' ' + content
		lines.append({'speaker':speaker, 'line':line,'time':time})
		sorted_lines = sorted(lines,key=lambda k: float(k['time']))
		w.write(job_name)
		w.write("\n\n")
		w.write(INTRO)
		w.write("\n\n\n")
		for line_data in sorted_lines[1:]:
			line=line_data.get('speaker') + ': ' + line_data.get('line')
			for word in replace_words:
				line=line.replace(word,' ')
			w.write(line + '\n\n')
		w.write(OUTRO)
	w.close()

def upload_file(job_name, service):
	logging.info("Uploading {} to Google Drive".format(job_name))
	file_metadata = {
		'name': job_name,
		'mimeType': 'application/vnd.google-apps.document',
		'parents':[FOLDER_ID]
	}
	upload_location = '/tmp/'+job_name+'.txt'
	media = MediaFileUpload(upload_location, mimetype='text/plain')

	file = service.files().create(body=file_metadata,
									media_body=media,
									fields='id').execute()

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
