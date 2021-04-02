import json
import boto3
import requests
from requests_aws4auth import AWS4Auth
from stemming.porter2 import stem
import inflect
p = inflect.engine()

def create_presigned_url(bucket_name, object_name, expiration=3600):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    return response


def lambda_handler(event, context):
    client = boto3.client('lex-runtime')
    # TODO
    print(event)
    print("Test to see if this line is updated via Code pipleline")
    input_text = event['q']

    input_text = input_text.lower()
    # input_text = 'hen and sam'
    s = ' '
    words = input_text.split()
    print(words)
    print(stem('animals'))
    for idx, val in enumerate(words):
        words[idx] = p.singular_noun(words[idx])
    s = s.join(words)
    print(s)
    response = client.post_text(
        botName='Label_disambiguator',
        botAlias='Label_disambiguator',
        userId='x1',
        inputText=s)
    # print (response)
    labels = []
    if 'intentName' not in response:
        labels = []
    elif response["intentName"] == "SearchIntent":
        for slot in response["slots"]:
            e = response["slots"][slot]
            if e is not None:
                labels.append(e)

    print(labels)
    # labels=['Sally']
    query_string = ''
    if len(labels) == 1:
        query_string = '(' + labels[0] + ')'
    elif len(labels) > 1:
        query_string = '(' + labels[0] + ')'
        for i in range(len(labels) - 1):
            query_string = query_string + ' OR (' + labels[i + 1] + ')'
    print(query_string)

    query = {
        "size": 20,
        "query": {
            "query_string": {
                "default_field": "labels",
                "query": query_string
            }
        }
    }

    region = 'us-east-2'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    host = 'search-photos-7ka2227iannxvqedwmlx62ft7u.us-east-1.es.amazonaws.com'
    index = 'photos'
    url = 'https://search-photos-4thhlt7eispnjuszan4xthlhxa.us-east-2.es.amazonaws.com/photos/_search'
    headers = {"Content-Type": "application/json"}

    request = requests.get(url, auth=awsauth, headers=headers, data=json.dumps(query)).json()
    print(request)

    result = request["hits"]["hits"]

    result_locations = []

    for res in result:
        key = res["_source"]["objectKey"]
        bucket_name = res["_source"]["bucket"]
        labels = res["_source"]["labels"]
        s3_url = create_presigned_url(bucket_name, key)
        # s3_url='https://'+bucket_name+'.s3.amazonaws.com/' + key

        result_locations.append((s3_url, labels))

    print(result_locations)
    response_results_json_list = []
    for result in result_locations:
        response_results_json = {
            "url": result[0],
            "labels": result[1]
        }
        response_results_json_list.append(response_results_json)
    response = {
        "results": response_results_json_list
    }

    print(json.dumps(response))
    # return json.dumps(response)
    return response