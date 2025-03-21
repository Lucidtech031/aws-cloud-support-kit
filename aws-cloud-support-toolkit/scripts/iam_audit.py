import boto3
from datatime import datetime, timedelta

# AWS clients
iam = boto3.client("iam")

# Define inactive period threshold (90 days)
INACTIVE_DAYS = 90
THRESHOLD_DATE = datetime.utcnow() - timedelta(days-INACTIVE_DAYS)

def list_iam_users():
    response = iam.list_users()
    return response.get("Users", [])

def check_user_last_activity(user):
    username = user["UserName"]
    last_login = user.get("PasswordLastUsed")

    if last_login:
        last_login = last_login.replace(tzinfo=None)
        inactive_days = (datetime.utcnow() - last_login).days
        if inactive_days > INACTIVE_DAYS:
            print(f"ALERT: User {username} is inactive for {inactive_days} days!")
        else:
            print(f"ALERT: User {username} has never logged in!")

def check_access_keys(user):
    username = user["Username"]
    response = iam.list_access_keys(UserName=username)

    for key in response.get("AccessKeyMetadata", []):
        last_used = iam.get_access_key_last_used(AccessKeyId=key["AccessKeyId"])
        key_last_used = last_used["AccessKeyLastUsed"].get("LastUsedDate")

        if key_last_used:
            key_last_used = key_last_used.replace(tzinfo=None)
            inactive_days = (datetime.utcnow() - key_last_used).days
            if inactive_days > INACTIVE_DAYS:
                print(f"ALERT: Access key {key['AccessKeyId']} for {username} is inactive for {inactive_days} days!")
            else:
                print(f"ALERT: Access key {key['AccessKeyId']} for {username} has never been used!")

def check_iam_roles():
    response = iam.list_roles()
    roles = response.get("Roles", {})
    for role in roles:
        role_name = role["RoleName"]
        last_used = role.get("RoleLastUsed", {}).get("LastUsedDate")

        if not last_used or last_used.replace(tzinfo=None) < THRESHOLD_DATE:
            print(f"ALERT: IAM Role {role_name} has not been used for 90+ days!")

def check_policies():
    response = iam.list_policies(Scope="Local")
    policies = response.get("Policies", [])

    for policy in policies:
        policy_name = policy["PolicyName"]
        policy_arn = policy["Arn"]

        policy_version = iam.get_policy(PolicyArn=policy_arn)["Policy"]["DefaultVersionId"]
        policy_document = iam.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)["PolicyVersion"]["Document"]

        if "Statement" in policy_document:
            for statement in policy_document["Statement"]:
                if statement.get("Effect") == "Allow" and statement.get("Action") == "*":
                    print(f"ALERT: Overly permissive policy detected - {policy_name}!")

def audit_iam():
    # Run IAM security audit.
    print("Auditing IAM users...")
    users = list_iam_users()
    for user in users:
        check_user_last_activity(user)
        check_access_keys(user)

    print("\n Auditing IAM roles...")
    check_iam_roles()

    print("\n Auditing IAM policies...")
    check_policies()

if __name__ == "__main__":
    audit_iam()