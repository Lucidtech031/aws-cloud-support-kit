from flask import Flask, render_template
import boto3

app = Flask(__name__)

# AWS clients
ec2 = boto3.client("ec2")
s3 = boto3.client("s3")
iam = boto3.client("iam")
logs = boto3.client("logs")
ce = boto3.client("ce")

LOG_GROUP = "EC2MonitoringLogs"

def get_ec2_instances():
    instances = []
    response = ec2.describe_instances()
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append({
                "id": instance["InstanceId"],
                "state": instance["State"]["Name"],
                "type": instance["InstanceType"],
                "launch_time": instance["LaunchTime"].strftime("%Y-%m-%d %H:%M:%S")
            })
    return instances

def get_s3_buckets():
    response = s3.list_buckets()
    return [bucket["Name"] for bucket in response["Buckets"]]

def get_iam_users():
    response = iam.list_users()
    return [{"username": user["UserName"], "created": user["CreateDate"].strftime("%Y-%m-%d")} for user in response["Users"]]

def get_cloudwatch_logs():
    try:
        response = logs.describe_log_streams(logGroupName=LOG_GROUP, orderBy="LastEventTime", descending=True)
        if response["logStreams"]:
            stream_name = response["logStreams"][0]["logStreamName"]
            log_events = logs.get_log_events(logGroupName=LOG_GROUP, logStreamName=stream_name, limit=10)
            return [event["message"] for event in log_events["events"]]
    except Exception as e:
        return [f"Error fetching logs: {e}"]
    return ["No logs found."]

@app.route("/")
def dashboard():
    return render_template("index.html",
                           ec2_instances=get_ec2_instances(),
                           s3_buckets=get_s3_buckets(),
                           iam_users=get_iam_users(),
                           cloudwatch_logs=get_cloudwatch_logs())

if __name__ == "__main__":
    app.run(debug=True)
