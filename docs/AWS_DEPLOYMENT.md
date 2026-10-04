# AWS learning deployment

This is an operator-access learning lab, not a public production service. The CloudFormation template is statically validated in CI; creating resources and testing AWS recovery require your account. Review current prices and your account plan first. No resources are created by merely cloning this repository.

## 1. Prerequisites and cost review

Install Docker locally, AWS CLI and the Session Manager plugin. Authenticate using an approved temporary identity. Choose a region supporting Amazon Linux 2023 and the instance type. Check `aws sts get-caller-identity`. Configure budget notifications. The stack provisions EC2, public IPv4, 20 GB encrypted EBS, a private versioned S3 bucket and CloudWatch resources. It can incur charges. `t3.small` is the practical default for building the image; `t3.micro` may run out of memory during builds.

## 2. Create the stack deliberately

```bash
aws cloudformation validate-template --template-body file://infra/learning-stack.yaml
aws cloudformation deploy --template-file infra/learning-stack.yaml \
  --stack-name freightdesk-learning --capabilities CAPABILITY_IAM
aws cloudformation describe-stacks --stack-name freightdesk-learning \
  --query 'Stacks[0].Outputs' --output table
```

Copy InstanceId, BackupBucket and LogGroupName from the outputs. AWS deployment identity needs CloudFormation and the permissions to create these resources, including passing the instance role. Do not solve denied permissions by casually granting AdministratorAccess to the application.

## 3. Build on EC2 through SSM

Start `aws ssm start-session --target YOUR_INSTANCE_ID`. On the instance:

```bash
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo mkdir -p /opt/freightdesk/runtime
sudo chown 10001:10001 /opt/freightdesk/runtime
git clone https://github.com/Jemade/Langchain.git
cd Langchain
git checkout YOUR_REVIEWED_COMMIT_SHA
sudo docker build -t freightdesk:lab .
```

Generate a reviewer token locally with Python `secrets.token_urlsafe(32)`, keep a copy in your password manager and create `/opt/freightdesk/env` on the instance using `sudoedit`. Put `FREIGHTDESK_TOKEN=YOUR_VALUE` on one line. Then `sudo chmod 600 /opt/freightdesk/env`. Do not put tokens in Git, screenshots or logs.

Replace the region and log group below with the stack's actual values:

```bash
sudo docker run -d --name freightdesk --restart unless-stopped \
  --env-file /opt/freightdesk/env -p 127.0.0.1:8000:8000 \
  -v /opt/freightdesk/runtime:/app/runtime \
  --log-driver awslogs --log-opt awslogs-region=YOUR_REGION \
  --log-opt awslogs-group=YOUR_LOG_GROUP --log-opt awslogs-stream=application \
  freightdesk:lab
curl http://127.0.0.1:8000/health
```

The instance role supplies credentials to the Docker logging driver. The application runs as UID 10001. The API binds only to host loopback and the security group has no inbound rules.

## 4. Open the interface locally

In a separate terminal on your own computer:

```bash
aws ssm start-session --target YOUR_INSTANCE_ID \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["8000"],"localPortNumber":["8000"]}'
```

Open http://127.0.0.1:8000 and paste your reviewer token. AWS documentation: [Session Manager and port forwarding](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-sessions-start.html). This tunnel is for your own access; it is not a public recruiter URL.

## 5. Backup and restore drill

Stop the application before backing up so request metadata and graph checkpoints represent the same maintenance point. The adapter uses SQLite's backup API, but the two database copies are not one atomic transaction.

```bash
sudo docker stop freightdesk
sudo docker run --rm --network host \
  -v /opt/freightdesk/runtime:/app/runtime freightdesk:lab \
  python -m freightdesk.backup --bucket YOUR_BACKUP_BUCKET
sudo docker start freightdesk
```

The instance profile permits writes only under `backups/`. S3 object encryption is requested and bucket versioning is enabled. The AWS SDK uses the instance role, not a static key. The host-network backup command allows EC2 metadata credentials to be obtained; metadata requires IMDSv2.

To restore, stop the service; preserve the current runtime files elsewhere; download `backups/requests.sqlite` and `backups/checkpoints.sqlite` into an empty recovery directory using your authorized operator identity; set ownership to UID 10001; start the service pointing at that directory. Review source object versions and ensure both files are from the same backup maintenance window. Test a pending review and an approved export before accepting recovery. Never replace active SQLite files under a running process.

## 6. Observe and clean up

CloudWatch Logs contains access/error logs; persisted workflow traces are in the application state. Inspect the CPU alarm in CloudWatch; it has no SNS notification action. Avoid adding shipment text to access logs. CloudTrail is a separate service for AWS API auditing and is not provisioned here.

Export your learning evidence and verify backups, then:

```bash
aws cloudformation delete-stack --stack-name freightdesk-learning
aws cloudformation wait stack-delete-complete --stack-name freightdesk-learning
```

The S3 bucket is deliberately retained and can continue to incur storage charges. To remove it, first decide whether to preserve backup data, then delete all object versions and delete markers before deleting the bucket. Verify EC2 termination, volume deletion and leftover resources in the console. Root EBS is deleted with the instance, so do not treat it as a durable backup.

Production next steps: individual identity/roles, public TLS endpoint, authorization boundaries, rate limits, shared database/checkpointer, redacted observability and tested recovery. Do not expose this shared-token MVP directly to the internet.
