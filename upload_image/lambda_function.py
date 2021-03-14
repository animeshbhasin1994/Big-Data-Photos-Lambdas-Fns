import boto3
import base64
import json

def lambda_handler(event, context):
    
    '''
    return {"Event" :event["body"],
        "headers": {
            "my_header": "my_value"
        }, 
        'status': 'True',
       'statusCode': 200,
       'body': 'Image Uploaded'
       }
    '''
    
    print(event)
    
    body = json.loads(event["body"])
    #body = event["body"]
    
    s3 = boto3.resource(u's3')
    bucket = s3.Bucket(u'coms6998-bucket2')
    #bucket = s3.Bucket(u'testbucketb2')
    
    path_test = '/tmp/output'         # temp path in lambda.
    key = body['ImageName']          # assign filename to 'key' variable
    data = body['img64'].split(',')[1]         # assign base64 of an image to data variable 
    data1 = data
    img = base64.b64decode(data1+ "===")     # decode the encoded image data (base64)
    
    metadata = {"customLabels": body["x-amz-meta-customLabels"]}
    #bucket.put_object(Body=)
    
    
    with open(path_test, 'wb') as data:
        #data.write(data1)
        data.write(img)
        #bucket.upload_file(path_test, key)   # Upload image directly inside bucket
    
    with open(path_test, 'rb') as data:
        
        bucket.put_object(Body=data, Key=key, Metadata= metadata)
        
        #bucket.upload_file(path_test, 'FOLDERNAME-IN-YOUR-BUCKET /{}'.format(key))    # Upload image inside folder of your s3 bucket.
    
    
    print('res---------------->',path_test)
    print('key---------------->',key)

    return {
        "headers": {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
       'statusCode': 200,
       'body': 'Image Uploaded',
       "isBase64Encoded": False
      }