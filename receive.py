import json
import boto3
import json
from time import time

#put data in chat table
def insert_chat_item(payload):
    chatroom_id = payload.get(chatroom_id,None)
    if chatroom_id:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('chat')
        payload['chatroom_id'] = chatroom_id
        payload['receive_timestamp'] = int(time.time())
        table.put_item(
            Item=payload
        )
    
#fetch user ids from chatroom user ids
def fetch_user_ids(chatroom_id):
    user_ids = []
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('chatroom_users')
    try:
        response = table.get_item(
            Key={
                'chatroom_id': chatroom_id,
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        user_ids = item.user_ids
        
    return user_ids
    
#push message to sqs 
def push_to_sqs(message):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/581010750309/chat_message'
    msg = sqs.send_message(QueueUrl=queue_url,
                                      MessageBody=json.dumps(message))
                                      

def lambda_handler(event, context):
    websocket_id = event.requestContext.connectionId
    payload = json.loads(event.body)
    
    #insert chat item for future reference
    response = insert_chat_item(payload)
    
    #create message for sqs queue
    message = {
        'message_type':payload.get('message_type'),
        'message_content':payload.get('message_content'),
        'chatroom_id':payload.get('chatroom_id')
    }
    chatroom_id = payload.get('chatroom_id')
    user_ids = fetch_user_ids(chatroom_id)
    for user_id in user_ids:
        message['user_id'] = user_id
        #push to sqs queue
        push_to_sqs(message)
        
    return {
        'statusCode': 200
    }
    

