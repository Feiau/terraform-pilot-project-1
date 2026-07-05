# Pilot Project: Terraform CI/CD with AWS Lambda

## Solution Architecture

This project deploys a serverless "Hello World" application using AWS Lambda and API Gateway, managed entirely through Terraform with a fully automated CI/CD pipeline via GitHub Actions.

```
┌─────────────────────────────────────────────────────────────┐
│                      GitHub Repository                        │
├─────────────────────────────────────────────────────────────┤
│  Push to main ──► Deploy Dev                                 │
│  Tag v* ────────► Deploy Prod (with manual approval)         │
│  PR ────────────► Validate + Plan                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS Account                                │
├──────────────────────┬──────────────────────────────────────┤
│      Dev Env         │           Prod Env                    │
│  ┌──────────────┐    │    ┌──────────────┐                   │
│  │ API Gateway  │    │    │ API Gateway  │                   │
│  │  (HTTP API)  │    │    │  (HTTP API)  │                   │
│  └──────┬───────┘    │    └──────┬───────┘                   │
│         │            │           │                            │
│  ┌──────▼───────┐    │    ┌──────▼───────┐                   │
│  │   Lambda     │    │    │   Lambda     │                   │
│  │ (Python 3.12)│    │    │ (Python 3.12)│                   │
│  └──────────────┘    │    └──────────────┘                   │
├──────────────────────┴──────────────────────────────────────┤
│  S3 Bucket (state + native lock) — shared backend            │
└─────────────────────────────────────────────────────────────┘
```

## Terraform Structure and Design Decisions

### Directory Layout

```
terraform-pilot-project-1/
├── .github/workflows/       # CI/CD pipeline definitions
│   ├── deploy-dev.yml       # Dev deployment (push to main)
│   ├── deploy-prod.yml      # Prod deployment (git tag)
│   └── terraform-validate.yml # PR validation
├── modules/
│   └── lambda-api/          # Reusable module: Lambda + API Gateway
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── environments/
│   ├── dev/                 # Dev environment root module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── prod/                # Prod environment root module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── bootstrap/               # One-time state backend setup
│   └── main.tf
├── app/                     # Application source code
│   └── lambda_function.py
├── .gitignore
└── README.md
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Modular design** | `modules/lambda-api` is reusable across environments, reducing code duplication |
| **Separate root modules per env** | Each environment has its own state file, preventing blast radius across environments |
| **S3 backend with native lock** | Terraform 1.15+ supports `use_lockfile = true` — no DynamoDB needed |
| **AWS Provider ~> 5.0** | Latest stable major version with broad feature support |
| **Python 3.12 Lambda** | Simple, no build step required, fast cold starts |
| **HTTP API Gateway (v2)** | Lower cost and latency than REST API for simple use cases |

## Environment Separation Strategy

Environments are **fully isolated** through:

1. **Separate Terraform state files** — Each environment uses a different S3 key (`dev/terraform.tfstate` vs `prod/terraform.tfstate`)
2. **Separate AWS IAM roles** — CI/CD uses different OIDC roles per environment (`AWS_ROLE_ARN_DEV` vs `AWS_ROLE_ARN_PROD`)
3. **Resource naming** — All resources include the environment name (e.g., `feitenga01-pilot-hello-world-dev`)
4. **GitHub Environments** — Prod uses a separate GitHub environment with tag-based trigger isolation
5. **Different triggers** — Dev deploys on push to main; Prod deploys only on version tags

## CI/CD Workflow Design

### Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `terraform-validate.yml` | PR (*.tf changes) | Format check + validate |
| `deploy-dev.yml` | Push to main / PR | Plan on PR, Apply on merge |
| `deploy-prod.yml` | Git tag `v*` | Plan + Apply (tag-gated) |

### Pipeline Flow

```
PR Created ──► terraform-validate (fmt + validate)
           ──► deploy-dev / terraform-plan (generates plan artifact)

PR Merged to main ──► deploy-dev / terraform-apply (auto-deploys to dev)

Git Tag v1.0.0 ──► deploy-prod / terraform-plan
               ──► deploy-prod / terraform-apply
```

### Security

- **OIDC authentication** — No long-lived AWS credentials stored in GitHub
- **Least privilege** — Separate roles per environment
- **Plan artifacts** — Reviewable before apply
- **Tag-gated production** — Only explicit version tags trigger prod deployment

## Deployment Instructions

### Prerequisites

- AWS Account with appropriate permissions
- GitHub repository
- Terraform ~> 1.15 (1.15.7 used in CI)
- AWS CLI configured locally

### Step 1: Bootstrap State Backend

```bash
cd bootstrap
terraform init
terraform apply
```

This creates the S3 bucket for Terraform state management (native S3 locking via `use_lockfile = true`, no DynamoDB needed).

### Step 2: Configure GitHub OIDC

Create an IAM OIDC identity provider for GitHub Actions in your AWS account, then create two IAM roles:

1. **Dev role** — Allows GitHub Actions to deploy to dev
2. **Prod role** — Allows GitHub Actions to deploy to prod

Both roles need permissions for: Lambda, API Gateway, IAM (for Lambda execution role), CloudWatch Logs, S3 (for state bucket `terraform-state-feitenga01-pilot`).

### Step 3: Configure GitHub Repository

Add the following secrets to your GitHub repository:

| Secret | Description |
|--------|-------------|
| `AWS_ROLE_ARN_DEV` | ARN of the IAM role for dev deployments |
| `AWS_ROLE_ARN_PROD` | ARN of the IAM role for prod deployments |

Create two GitHub Environments:
- `dev` — No protection rules
- `prod` — Enable "Required reviewers" protection rule (requires GitHub Pro/Team plan; optional)

### Step 4: Deploy

```bash
# Deploy to dev (push to main)
git add .
git commit -m "Initial deployment"
git push origin main

# Deploy to prod (create a tag)
git tag v1.0.0
git push origin v1.0.0
```

### Local Development

```bash
# Package the Lambda function
cd app && zip -r lambda.zip lambda_function.py && cd ..

# Plan changes for dev
cd environments/dev
terraform init
terraform plan

# Apply changes (dev only)
terraform apply
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `Error: No valid credential sources found` | OIDC not configured | Verify IAM OIDC provider and role trust policy include your GitHub repo |
| `Error acquiring state lock` | Previous run crashed or concurrent run | Delete the `.tflock` file from the S3 state path |
| `Error: S3 bucket does not exist` | Bootstrap not run | Run `terraform apply` in `bootstrap/` directory first |
| `AccessDenied` on terraform apply | IAM role lacks permissions | Check role has Lambda, API Gateway, IAM, and CloudWatch Logs permissions |
| `terraform fmt` fails in CI | Unformatted code | Run `terraform fmt -recursive` locally before committing |
| Lambda returns 500 | Code error | Check CloudWatch Logs at `/aws/lambda/feitenga01-pilot-hello-world-<env>` |

### Useful Commands

```bash
# Check deployed API endpoint
cd environments/dev && terraform output api_endpoint

# View Lambda logs
aws logs tail /aws/lambda/feitenga01-pilot-hello-world-dev --follow

# Destroy environment (caution!)
cd environments/dev && terraform destroy
```

## FAQ

**Q: Why Lambda instead of ECS or EC2?**
A: Lambda is the simplest serverless option — no infrastructure to manage, minimal code, and stays within AWS free tier for this demo.

**Q: Why separate directories per environment instead of workspaces?**
A: Separate directories provide stronger isolation — each has its own backend config, provider config, and can diverge independently. Workspaces share backend configuration which can be risky for production.

**Q: Can I add more environments?**
A: Yes. Copy an existing environment directory, update the backend key and environment name, and create a new workflow file with the appropriate trigger.

**Q: Why OIDC instead of IAM access keys?**
A: OIDC eliminates the need for long-lived credentials. GitHub generates short-lived tokens that AWS verifies, reducing the risk of credential leakage.

**Q: How do I roll back a deployment?**
A: Revert the commit on main (for dev) or create a new tag pointing to the previous good commit (for prod). The pipeline will redeploy the previous state.

**Q: What are the known limitations?**
A: See the section below.

## Known Limitations and Future Improvements

### Limitations
- Single AWS region deployment (no multi-region)
- No custom domain name for API Gateway
- No automated testing of the Lambda function in CI
- State bucket name is hardcoded as `terraform-state-feitenga01-pilot` (must be globally unique)

### Assumptions
- Single AWS account for both environments (resource isolation via naming only)
- GitHub Actions has network access to AWS APIs
- The S3 bucket name `terraform-state-feitenga01-pilot` is available

### Future Improvements
- Add `terraform-docs` generation to CI
- Add integration tests (invoke API endpoint after deploy, validate response)
- Add cost estimation with Infracost
- Multi-region deployment with Route53 failover
- Custom domain with ACM certificate
- Add monitoring/alerting with CloudWatch alarms
