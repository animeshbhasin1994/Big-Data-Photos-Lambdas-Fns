import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection


def lambda_handler(event, context):
    # TODO implement
    print(event)
    print("Test to see if this line is updated via Code pipleline")
    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    image_key = event["Records"][0]["s3"]["object"]["key"]

    head_object = boto3.client("s3").head_object(Bucket=bucket_name, Key=image_key)

    print(bucket_name, image_key, head_object)

    timestamp = head_object["LastModified"]
    timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S")

    client = boto3.client('rekognition')

    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket_name, 'Name': image_key}},
                                    MaxLabels=100)
    custom_labels=[]
    rekognition_labels = []
    
    # rekognition_labels
    for label in response["Labels"]:
        rekognition_labels.append(label['Name'])

    # custom_labels
    
    custom_label_string=head_object['Metadata']['customlabels']
    # custom_label_string='peter,hen'
    
    for i in custom_label_string.split(','):
        custom_labels.append(i.strip())
    
    print ("Custom Labels : " + str(custom_labels))
    labels= custom_labels+rekognition_labels+['snake']
    print(labels)

    elastic_search_json_object = {
        "objectKey": image_key,
        "bucket": bucket_name,
        "createdTimestamp": timestamp_str,
        "labels": labels
        }
        
    print(elastic_search_json_object)
    
    region = 'us-east-2'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    
    host = "search-photos-4thhlt7eispnjuszan4xthlhxa.us-east-2.es.amazonaws.com"
    
    elastic_search = Elasticsearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )
    

    elastic_search.index(index="photos", id=elastic_search_json_object["objectKey"], body=elastic_search_json_object)
    
    
    print(elastic_search.get(index="photos", id=elastic_search_json_object["objectKey"]))
    
    print ("done")