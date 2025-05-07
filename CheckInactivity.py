import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
iam = boto3.client('iam')
table = dynamodb.Table('UserActivity')

INACTIVITY_THRESHOLD_GROUP = timedelta(days=1)
INACTIVITY_THRESHOLD_PERMISSIONS = timedelta(days=7)
INACTIVITY_THRESHOLD_DELETE = timedelta(days=14)

def lambda_handler(event, context):
    response = table.scan()
    for item in response['Items']:
        username = item['UserName']
        group_name = item['GroupName']
        last_activity = datetime.fromisoformat(item['LastActivityTimestamp'])
        current_time = datetime.utcnow()
        
        if current_time - last_activity > INACTIVITY_THRESHOLD_DELETE:
            delete_user(username)
        elif current_time - last_activity > INACTIVITY_THRESHOLD_PERMISSIONS:
            remove_permissions(username)
        elif current_time - last_activity > INACTIVITY_THRESHOLD_GROUP:
            remove_group(username, group_name)

def remove_permissions(username):
    # Example: Detach all policies from the user
    attached_policies = iam.list_attached_user_policies(UserName=username)
    for policy in attached_policies['AttachedPolicies']:
        iam.detach_user_policy(UserName=username, PolicyArn=policy['PolicyArn'])
    print(f"Removed permissions for user {username}")

def remove_group(username, group_name):
    # Remove the user from the specified group
    iam.remove_user_from_group(UserName=username, GroupName=group_name)
    print(f"Removed user {username} from group {group_name}")

def delete_user(username):
    # Delete the user after removing permissions
    remove_permissions(username)
    iam.delete_user(UserName=username)
    print(f"Deleted user {username}")
