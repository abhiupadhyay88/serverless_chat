import json
import boto3
from time import time
import requests

#push message in db for offline users
def offline_user(message):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('unsent_chat')
    table.put_item(
        Item=message
    )
    
#fetch websocket connection id for a user_id
def fetch_websocket_id(user_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('websocket_user_mapping')
    websocket_id = None
    try:
        response = table.get_item(
            Key={
                'user_id': user_id,
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        websocket_id = item.websocket_id
        
    return websocket_id
    
def create_chat_entry(message):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('chat_sent')
    message['sent_timestamp'] = int(time())
    table.put_item(
        Item=message    
    )
        
def lambda_handler(event, context):
    message = json.loads(event)
    user_id = message.get('user_id')
    websocket_id = fetch_websocket_id(user_id)
    if not websocket_id:
        offline_user(message)
    else:
        callback_url = message['callback_url']+websocket_id
        requests.post(callback_url,data=message)
        
        #create a chat entry for each chat sent to a user for future reference
        create_chat_entry(message)
        
    return {
        'statusCode': 200
    }

