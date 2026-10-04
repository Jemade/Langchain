# Four weeks of AWS for a software engineer

Start with 2–3 focused hours per day: 40 minutes reading, 70–100 minutes building, 20 minutes explaining what you did without AI assistance. If starting Monday 5 October 2026, finish Sunday 1 November. The goal is a working foundation and one demonstrable deployment, not mastery of AWS or a certification guarantee.

Use the free [W3Schools AWS tutorial](https://www.w3schools.com/aws/index.php) as your first reading source. Its Cloud Practitioner material introduces services; it does not replace hands-on engineering. Some W3Schools course/certificate products are paid. Supplement with [AWS documentation](https://docs.aws.amazon.com/), [AWS training](https://aws.amazon.com/training/digital/) and [LangChain learning resources](https://docs.langchain.com/oss/python/learn). Check each course's access terms before enrolling.

## Week 1: identity, compute and networking

Read: [Cloud introduction](https://www.w3schools.com/aws/aws_cloudessentials_intro.php), [Regions](https://www.w3schools.com/aws/aws_cloudessentials_awsregions.php), [Availability Zones](https://www.w3schools.com/aws/aws_cloudessentials_awsavailabilityzones.php), [Shared responsibility](https://www.w3schools.com/aws/aws_cloudessentials_sec_sharedresponsibilitymodel.php), [User access](https://www.w3schools.com/aws/aws_cloudessentials_sec_userpermissionsandaccess.php), [EC2](https://www.w3schools.com/aws/aws_cloudessentials_ec2intro.php), [Instance types](https://www.w3schools.com/aws/aws_cloudessentials_ec2instancetypes.php), [Networking](https://www.w3schools.com/aws/aws_cloudessentials_awsnetworking.php), [Subnet and access](https://www.w3schools.com/aws/aws_cloudessentials_awssubnetandaccess.php).

| Day | Build or practice | Evidence you should have |
| --- | --- | --- |
| 1 | Read account plans, choose one region, enable root MFA, configure a budget alert if available. Do not create root access keys. | Account safety/cost checklist without secret screenshots |
| 2 | Install AWS CLI, configure SSO or another approved temporary identity, run `aws sts get-caller-identity`. | Explanation of user vs role, policy vs permission, temporary credentials |
| 3 | Draw a VPC, subnet, route table, gateway and security group. Read the supplied template. | Explain why a public subnet does not mean every port is open |
| 4 | Launch the supplied learning stack after cost review, or examine it locally with cfn-lint if no account is ready. | Instance and role IDs; explain vCPU, memory, stop vs terminate |
| 5 | Connect using SSM. Run a Docker container locally or on the instance. | Shell connection and a healthy application |
| 6 | Read EC2 pricing, scaling and load balancing. Explain security groups vs IAM. | A written choice between EC2, Lambda and containers for this app |
| 7 | Run FreightDesk locally, create/review a case and explain each node from code. | One approved export and one rejected request |

Gate: you can explain requests from browser to API, authenticate without hard-coded AWS keys, identify which ports are open and say which resources cost money.

## Week 2: storage and databases

Read: [Storage](https://www.w3schools.com/aws/aws_cloudessentials_storageanddatabases_introduction.php), [S3](https://www.w3schools.com/aws/aws_cloudessentials_amazonsimplestorageservice.php), [EBS](https://www.w3schools.com/aws/aws_cloudessentials_awsebs.php), [EFS](https://www.w3schools.com/aws/aws_cloudessentials_amazonelasticfilesystem.php), [RDS](https://www.w3schools.com/aws/aws_cloudessentials_amazonrds.php), [DynamoDB](https://www.w3schools.com/aws/aws_cloudessentials_amazondynamodb.php), [RDS vs DynamoDB](https://www.w3schools.com/aws/aws_cloudessentials_comparingamazonrdsandamazondynamodb.php).

| Day | Build or practice | Evidence you should have |
| --- | --- | --- |
| 8 | Upload a fictional policy to a private S3 bucket using your temporary identity. | Successful object read; anonymous public access remains blocked |
| 9 | Enable/check versioning, encryption and lifecycle settings. Replace and restore a test object. | Difference between durability, versioning and backup |
| 10 | Explain object storage vs a block volume vs a shared filesystem. Restart the container. | SQLite case persists; understand volume deletion |
| 11 | Stop the API and back up both SQLite files to S3 using the provided adapter. | Backup object versions, no customer documents |
| 12 | Restore both files into a new local runtime directory and resume a pending review. | Tested recovery procedure and observed recovery time |
| 13 | Design a PostgreSQL schema for users, requests, decisions and policy versions. Use local PostgreSQL if avoiding RDS charges. | Index and transaction explanation; migration sketch |
| 14 | Design DynamoDB keys for request lookup and status lists; compare with SQL joins. | Access-pattern table and weekly notes |

Gate: you can select the right storage type and recover a pending review. RDS and DynamoDB are learning exercises; the delivered MVP still uses SQLite.

## Week 3: serverless, queues and reliable workflows

Read: [Lambda](https://www.w3schools.com/aws/aws_cloudessentials_awslambda.php), [Serverless](https://www.w3schools.com/aws/aws_cloudessentials_awsserverless.php), [SQS](https://www.w3schools.com/aws/aws_cloudessentials_awssqs.php), [SNS](https://www.w3schools.com/aws/aws_cloudessentials_awssns.php), [EventBridge](https://www.w3schools.com/aws/aws_cloudessentials_awseventbridge.php), [Containers](https://www.w3schools.com/aws/aws_cloudessentials_awscontainers.php), [ECS](https://www.w3schools.com/aws/aws_cloudessentials_awsecs.php), [Fargate](https://www.w3schools.com/aws/aws_cloudessentials_awsfargate.php).

| Day | Build or practice | Evidence you should have |
| --- | --- | --- |
| 15 | Write a small Lambda handler validating a shipment reference, with unit tests. Deploy only after reviewing account costs. | Valid/invalid input behavior and execution-role explanation |
| 16 | Read API Gateway HTTP API documentation; describe auth, status codes and throttling. | API contract for a future asynchronous request endpoint |
| 17 | Send/receive/delete a fictional message in an SQS lab queue. | Explain visibility timeout, retries and duplicate delivery |
| 18 | Add a dead-letter queue to the lab and force a repeated processing failure. | Failed message inspected and safely redriven |
| 19 | Run LangGraph restart, deduplication and provider-failure tests. | Explain why checkpointing and queue acknowledgements solve different problems |
| 20 | Trace the LangChain prompt/parser pipeline. Try Bedrock only with an enabled model and spending allowance. | Demo/model distinction and a manually checked answer |
| 21 | Compare one EC2 instance with ECS/Fargate. Document migration requirements. | Explicit reason not to put local SQLite on horizontally scaled replicas |

Gate: explain at-least-once delivery, idempotency, human review and how you would move expensive work out of an HTTP request. Queue/Lambda labs are not claimed as integrated product features.

## Week 4: deploy, observe and demonstrate

Read: [CloudFormation](https://www.w3schools.com/aws/aws_cloudessentials_awscloudformation.php), [CloudWatch](https://www.w3schools.com/aws/aws_cloudessentials_ma_cloudwatch.php), [CloudTrail](https://www.w3schools.com/aws/aws_cloudessentials_ma_cloudtrail.php), [Billing](https://www.w3schools.com/aws/aws_cloudessentials_ps_billingservices.php), [Cost optimization](https://www.w3schools.com/aws/aws_cloudessentials_ps_costoptimization.php), [Well-Architected](https://www.w3schools.com/aws/aws_cloudessentials_clo_awswellarchitectedframework.php).

| Day | Build or practice | Evidence you should have |
| --- | --- | --- |
| 22 | Review CI, lockfiles and the Docker image. Run lint/tests/browser checks. | Exact commit and successful checks |
| 23 | Follow the AWS deployment guide. Build the pinned source commit on EC2. | Health endpoint through SSM port forwarding |
| 24 | Enable container logs, find a failed request, inspect the CPU alarm. | Distinguish application logs, metrics and CloudTrail API events |
| 25 | Run the 60 synthetic evaluations, then manually assess a smaller varied model set if using Bedrock. | Honest demo metrics, latency observations, unsupported claims noted |
| 26 | Interview a dispatcher about one recent exception; ask how they resolve it today. | Anonymized notes and a change based on feedback, with consent |
| 27 | Record a 3–5 minute walkthrough: report, evidence, decision, restart and recovery. | Demo, architecture and known limitations |
| 28 | Inspect costs, clean up unused resources and write lessons learned. | Resource inventory and accurate resume bullet |

## What to know by the end

Compute: EC2, Lambda, container images, ECS/Fargate basics. Storage: S3, EBS, EFS selection and backups. Data: SQL/RDS vs DynamoDB access patterns. Network: VPC, routes, security groups, TLS and DNS basics. Security: roles, least privilege, MFA and secrets. Reliability: queues, retries, idempotency and recovery. Delivery: CloudFormation, CI/CD, logs, alarms and costs. AI engineering: LangChain composition, LangGraph state/checkpoints/interrupts, evidence review and evaluation limits.

## Costs and current account plans

Read [AWS Free Tier](https://aws.amazon.com/free/) before starting. As checked on 4 October 2026, eligible new customers can receive $100 initially and earn up to $100 additional credits, with a Free plan lasting up to six months or until credits run out. Existing account eligibility and enabled services may differ. Do not assume the older “12 months free” rules apply to your account. W3Schools reading is separate from AWS resource usage.

[Budget alerts](https://aws.amazon.com/aws-cost-management/aws-budgets/) notify you; they do not universally stop spending. Set alerts before lab deployment. Avoid NAT gateways, load balancers, idle RDS instances and unneeded EKS clusters in this first month. Stopping EC2 does not remove storage charges. Retained S3 backups can still cost money after deleting the stack.

## Honest portfolio wording

After you actually deploy and verify recovery: “Built a logistics exception review MVP with LangChain policy retrieval and durable LangGraph human-review checkpoints; deployed a single-instance AWS learning environment with EC2, encrypted EBS, private S3 backups and CloudWatch logs.” Until then, say “prepared AWS deployment infrastructure,” not “deployed on AWS.”
