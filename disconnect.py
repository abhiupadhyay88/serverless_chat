import json
import boto3

#delete db entries for websocket and userid
def delete_websocket_userid_entries(websocket_id):
    dynamodb = boto3.resource('dynamodb')
    
    #delete entry from reverse mapping
    table = dynamodb.Table('reverse_user_websocket_mapping')
    response = table.get_item(
        Key={
            'chatroom_id': websocket_id,
        }
    )
    user_id = response['Item'].user_id
    table.delete_item(
        Key={
            'websocket_id':websocket_id
        }
    )
    # delete entry from websocket mapping
    table = dynamodb.Table('websocket_user_mapping')
    table.delete_item(
        Key={
            'user_id':user_id
        }
    )
    
def lambda_handler(event, context):
    websocket_id = event.requestContext.connectionId
    delete_websocket_userid_entries(websocket_id)
    return {
        'statusCode': 200,
    }
