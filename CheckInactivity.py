import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
iam = boto3.client('iam')
table = dynamodb.Table('LastActivityTimestamp')

INACTIVITY_THRESHOLD_PERMISSIONS = timedelta(days=30)
INACTIVITY_THRESHOLD_DELETE = timedelta(days=60)

def lambda_handler(event, context):
    response = table.scan()
    for item in response['Items']:
        username = item['Username']
        last_activity = datetime.fromisoformat(item['LastActivity'])
        current_time = datetime.utcnow()
        
        if current_time - last_activity > INACTIVITY_THRESHOLD_DELETE:
            delete_user(username)
        elif current_time - last_activity > INACTIVITY_THRESHOLD_PERMISSIONS:
            remove_permissions(username)

def remove_permissions(username):
    # Example: Detach all policies from the user
    attached_policies = iam.list_attached_user_policies(UserName=username)
    for policy in attached_policies['AttachedPolicies']:
        iam.detach_user_policy(UserName=username, PolicyArn=policy['PolicyArn'])
    print(f"Removed permissions for user {username}")

def delete_user(username):
    # Delete the user after removing permissions
    remove_permissions(username)
    iam.delete_user(UserName=username)
    print(f"Deleted user {username}")
