import boto3
import paramiko
from datetime import datetime, timedelta

# AWS clients
ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')
logs = boto3.client('logs')

# Define thresholds
CPU_THRESHOLD = 70 
DISK_THRESHOLD = 20
LOG_GROUP = "EC2MonitoringLogs"
LOG_STREAM = "EC2Alerts"

def create_log_group():
    try:
        logs.create_log_group(logGroupName=LOG_GROUP)
        print(f"Create CloudWatch Log Group: {LOG_GROUP}")
    except logs.exceptions.ResourceAlreadyExistsException:
        pass # Log group already exists

def log_to_cloudwatch(message):
    timestamp = int(datetime.utcnow().timestamp() * 1000)

    try: 
        logs.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
    except log.exceptions.ResourceAlreadyExistsExpection:
        pass # Log stream already exists

    logs.put_log_events(
        logGroupName=LOG_GROUP,
        logStreamName=LOG_STREAM,
        logEvents=[{"timestamp": timestamp, "message": message}]
    )
# Function to check EC2 instance status
def check_instance_status():
    
    response = ec2.describe_instances()

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            state = instance['State']['Name']

            print(f"Instance ID: {instance_id}, State: {state}")

            # Restart the instance if it's stopped
            if state == 'stopped': 
                print(f"Restarting instance: {instance_id}")
                ec2.start_instances(InstanceIds=[instance_id])

def check_cpu_utilization(instance_id):
    
    response = cloudwatch.get_metric_statistics(
        Namespace = 'AWS/EC2',
        MetricName = 'CPUUtilization',
        Dimensions = [{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime = datetime.utcnow() - timedelta(minutes=10),
        EndTime = datetime.utcnow(),
        Period = 300,
        Statistics = ['Average']
    )

    if response['Datapoints']:
        avg_cpu = response['Datapoints'][0]['Average']
        print(f"Instance {instance_id} CPU Usage: {avg_cpu}%")

        if avg_cpu > CPU_THRESHOLD:
            print(f"ALERT: High CPU usage detected on {instance_id}!")

    def check_disk_space(instance_ip, key_path, username="ec2-user"):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(instance_ip, username=username, key_filename=key_path)

            stdin, stdout, stderr = ssh.exec_command("df -h / awk 'NR==2 {print $5}")
            disk_usage = stdout.read().decode().strip().replace('%', '')

            print(f"Instance {instance_id} Disk Usage: {disk_usage}% used")

            if int(disk_usage) > DISK_THRESHOLD:
                print(f"ALERT: High disk usage detected on {instance_id}!")

            ssh.close()
        except Exception as e:
            print(f"Error checking disk space: {e}")
            
if __name__ == "__main__":
    check_instance_status()
