import json
import urllib.parse
import boto3
import logging
import sys
from botocore.exceptions import ClientError
import requests
import os

s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')
transcribe_client = boto3.client('transcribe')
logging.getLogger().setLevel(logging.INFO)

def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content_type = response['ContentType']
        logging.info("CONTENT TYPE: " + response['ContentType'])
        if content_type == "video/mp4" or content_type == "audio/x-m4a":
            content_type = "mp4"
        elif content_type=="audio/mp3":
            content_type = "mp3"
        else:
            raise Exception("S3 Audio File: Invalid format")
    except Exception as e:
        logging.error('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    file_name = os.path.basename(key)
    job_name = os.path.splitext(file_name)[0]
    logging.info(f"key={job_name}")
    logging.info(f"Starting transcription job {job_name}.")
    start_job(
        job_name, \
        f's3://{bucket}/{key}', \
        content_type, \
        'en-US', \
        transcribe_client)

def start_job(
        job_name, media_uri, media_format, language_code, transcribe_client):
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
    try:
        job_args = {
            'TranscriptionJobName': f'{job_name}',
            'Media': {'MediaFileUri': media_uri},
            'MediaFormat': media_format,
            'LanguageCode': language_code,
            'OutputBucketName': 'hiho-transcription',
            'OutputKey': f'output/{job_name}.json'
            }

        job_args['Settings'] = {
            'VocabularyName': "Gymnastics",
            "ShowSpeakerLabels": True,
            "MaxSpeakerLabels": 6
        }
        response = transcribe_client.start_transcription_job(**job_args)
        job = response['TranscriptionJob']
        logging.info("Started transcription job %s.", job_name)
    except ClientError as e:
        logging.error("Couldn't start transcription job %s.", job_name)
        raise e
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
        logging.info("Got job %s.", job['TranscriptionJobName'])
    except ClientError:
        logging.exception("Couldn't get job %s.", job_name)
        raise
    else:
        return job
