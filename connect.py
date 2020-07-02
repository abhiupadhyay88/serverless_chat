import json
import boto3

#update websocket connection id for user_id
def update_websocket_user_mapping(websocket_id,user_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('websocket_user_mapping')
    table.put_item(
        Item={
            'user_id':user_id,
            'websocket_id':websocket_id
        }    
    )
    table = dynamodb.Table('reverse_user_websocket_mapping')
    table.put_item(
        Item={
            'websocket_id':websocket_id,
            'user_id':user_id
        }    
    )

# pull offline messages for the user_id and push it to sqs
def pull_offline_messages(user_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('unsent_chat')
    items = table.get_item(
        Key={
            'user_id': user_id,
        }
    )
    messages = items.get('Item',[])
    
    #delete unsent chat from the table
    table.delete_item(
        Key={
            'user_id': user_id,
        }
    )
    return messages
    
#push message to sqs 
def push_to_sqs(message):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/581010750309/chat_message'
    msg = sqs.send_message(QueueUrl=queue_url,
                                      MessageBody=json.dumps(message))
                                      

def lambda_handler(event, context):
    websocket_id = event.requestContext.connectionId
    payload = json.loads(event.body)
    user_id = payload.get('user_id')
    
    # update connection ids in dynamodb table
    update_websocket_user_mapping(websocket_id,user_id)
    
    #pull offline messages
    messages = pull_offline_messages(user_id)
    
    #Sending offline messages
    if messages:
        for message in messages:
            push_to_sqs(message) 
    
    return {
        'statusCode': 200
    }

