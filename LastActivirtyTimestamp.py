import boto3
import json
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserActivity')

def lambda_handler(event, context):
    # Get the CloudTrail log records from the event
    records = event['Records']
    
    for record in records:
        # Parse the CloudTrail log
        message = json.loads(record['Sns']['Message'])
        for trail_event in message['Records']:
            user_name = trail_event.get('userIdentity', {}).get('userName')
            group_name = trail_event.get('userIdentity', {}).get('groupName')
            if user_name and group_name:
                # Update the DynamoDB table with the latest activity timestamp
                table.update_item(
                    Key={'UserName': user_name, 'GroupName': group_name},
                    UpdateExpression='SET LastActivityTimestamp = :timestamp',
                    ExpressionAttributeValues={
                        ':timestamp': datetime.utcnow().isoformat()
                    }
                )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Activity timestamps updated successfully')
    }
