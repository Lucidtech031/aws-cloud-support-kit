# AWS Cloud Support Toolkit

## Overview
The **AWS Cloud Support Toolkit** is a Python-based automation suite designed to help diagnose and resolve common AWS issues. It includes monitoring scripts, security audits, cost tracking, and a web dashboard for real-time insights. This project is designed for aspiring Cloud Support Engineers and stays within the AWS Free Tier.

## Features
### ✅ AWS Service Health Monitoring
- Tracks EC2, S3, and RDS status using **CloudWatch** and **Boto3**.
- Sends alerts when issues arise.

### ✅ Automated Troubleshooting Scripts
- **EC2 Diagnosis**: Checks instance state, CPU usage, and restarts unhealthy instances.
- **S3 Security Check**: Identifies public/unsecured buckets and fixes policies.
- **RDS Monitoring**: Ensures database connectivity and logs slow queries.
- **IAM Audit**: Detects unused roles and enforces best practices.
- **Cost Optimization**: Analyzes AWS Free Tier usage and sends alerts.

### ✅ Web Dashboard (Flask-based)
- Displays real-time AWS service health and logs.
- Provides a user-friendly interface for troubleshooting insights.
- Hosted on AWS EC2 with **Nginx & Gunicorn** for production.

### ✅ CloudWatch Alarms & Auto-Remediation
- Monitors EC2 CPU utilization and disk space.
- Automatically restarts EC2 instances when CPU usage exceeds thresholds.
- Logs alerts to CloudWatch for historical tracking.

## Tech Stack
- **AWS Services**: EC2, S3, RDS, IAM, Lambda, CloudWatch, Cost Explorer API
- **Python Libraries**: Boto3, Flask, Paramiko, Pandas, Matplotlib
- **Infrastructure**: Nginx, Gunicorn, Supervisor (for production)

## Setup Instructions
### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/aws-cloud-support-toolkit.git
cd aws-cloud-support-toolkit
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Configure AWS Credentials**
```bash
aws configure
```
Enter your **Access Key, Secret Key, Region**, and output format.

### **4. Run Individual Scripts for Troubleshooting**
- **EC2 Monitoring**
  ```bash
  python scripts/ec2_diagnosis.py
  ```
- **S3 Security Check**
  ```bash
  python scripts/s3_security_check.py
  ```
- **RDS Monitoring**
  ```bash
  python scripts/rds_monitoring.py
  ```
- **IAM Audit**
  ```bash
  python scripts/iam_audit.py
  ```
- **Cost Optimization**
  ```bash
  python scripts/cost_optimization.py
  ```

### **5. Run the Web Dashboard**
```bash
python web_dashboard/app.py
```
Visit **http://127.0.0.1:5000/** to access the dashboard.

### **6. Deploy the Flask Dashboard on AWS EC2**
1. Launch an EC2 instance (Amazon Linux 2/Ubuntu)
2. Install dependencies:
   ```bash
   sudo apt update -y && sudo apt install python3-pip nginx -y
   pip install flask gunicorn boto3
   ```
3. Transfer files to EC2:
   ```bash
   scp -i your-key.pem -r web_dashboard ec2-user@your-ec2-ip:~
   ```
4. Run Flask with Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:5000 app:app
   ```
5. Configure **Nginx** as a reverse proxy for production.

## Future Enhancements
- Add AI-based anomaly detection for AWS monitoring.
- Deploy the web dashboard on AWS Lambda for serverless hosting.
- Implement automated cost-saving recommendations.

## Contribution
Contributions are welcome! Feel free to submit issues and pull requests.

## License
This project is licensed under the MIT License.

