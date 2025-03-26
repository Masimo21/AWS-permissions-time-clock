import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('LastActivityTimestamp')

def update_last_activity(user):
    table.put_item(
        Item={
            'Username': user,
            'LastActivity': datetime.utcnow().isoformat()
        }
    )
