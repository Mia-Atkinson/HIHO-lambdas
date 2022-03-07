import json
import urllib.parse
import boto3
import logging
import sys
import time
from botocore.exceptions import ClientError
import requests
import os

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')
transcribe_client = boto3.client('transcribe')
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content_type = response['ContentType']
        print("CONTENT TYPE: " + response['ContentType'])
        if content_type == "video/mp4":
            content_type = "mp4"
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    file_name = os.path.basename(key)
    job_name = os.path.splitext(file_name)[0]
    print(f"key={job_name}")
    #job_name = f'{filename}-{time.time_ns()}'
    print(f"Starting transcription job {job_name}.")
    start_job(
        job_name, \
        f's3://{bucket}/{key}', \
        content_type, \
        'en-US', \
        transcribe_client)
        
def start_job(
        job_name, media_uri, media_format, language_code, transcribe_client,
        vocabulary_name=None):
    """
    Starts a transcription job. This function returns as soon as the job is started.
    To get the current status of the job, call get_transcription_job. The job is
    successfully completed when the job status is 'COMPLETED'.

    :param job_name: The name of the transcription job. This must be unique for
                     your AWS account.
    :param media_uri: The URI where the audio file is stored. This is typically
                      in an Amazon S3 bucket.
    :param media_format: The format of the audio file. For example, mp3 or wav.
    :param language_code: The language code of the audio file.
                          For example, en-US or ja-JP
    :param transcribe_client: The Boto3 Transcribe client.
    :param vocabulary_name: The name of a custom vocabulary to use when transcribing
                            the audio file.
    :return: Data about the job.
    """
    print(job_name)
    try:
        job_args = {
            'TranscriptionJobName': f'{job_name}-{time.time()}',
            'Media': {'MediaFileUri': media_uri},
            'MediaFormat': media_format,
            'LanguageCode': language_code,
            'OutputBucketName': 'hiho-transcription',
            'OutputKey': f'output/{job_name}.json'
            }
        if vocabulary_name is not None:
            job_args['Settings'] = {
                'VocabularyName': vocabulary_name,
                "ShowSpeakerLabels": True,
                "MaxSpeakerLabels": 6
            }
        response = transcribe_client.start_transcription_job(**job_args)
        job = response['TranscriptionJob']
        logger.info("Started transcription job %s.", job_name)
    except ClientError:
        logger.exception("Couldn't start transcription job %s.", job_name)
        raise
    else:
        return job

def get_job(job_name, transcribe_client):
    """
    Gets details about a transcription job.

    :param job_name: The name of the job to retrieve.
    :param transcribe_client: The Boto3 Transcribe client.
    :return: The retrieved transcription job.
    """
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name)
        job = response['TranscriptionJob']
        logger.info("Got job %s.", job['TranscriptionJobName'])
    except ClientError:
        logger.exception("Couldn't get job %s.", job_name)
        raise
    else:
        return job
