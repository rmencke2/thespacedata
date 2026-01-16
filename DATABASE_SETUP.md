# Persistent Database Setup for influzer.ai

## The Problem

AWS App Runner containers are **ephemeral** - when they restart or scale, any local data (including SQLite in `/tmp`) is lost. For production, you need an external database.

## Solution: AWS RDS PostgreSQL

### Step 1: Create an RDS PostgreSQL Instance

**Via AWS Console:**
1. Go to AWS RDS → Create database
2. Choose **PostgreSQL**
3. Select **Free tier** (for testing) or **Production**
4. Settings:
   - DB instance identifier: `influzer-db`
   - Master username: `postgres`
   - Master password: (save this securely)
5. Connectivity:
   - VPC: Default VPC
   - Public access: **Yes** (for App Runner access, or use VPC connector)
   - Security group: Create new, allow inbound PostgreSQL (port 5432)
6. Database name: `influzer`

**Via AWS CLI:**
```bash
aws rds create-db-instance \
  --db-instance-identifier influzer-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15 \
  --master-username postgres \
  --master-user-password YOUR_SECURE_PASSWORD \
  --allocated-storage 20 \
  --db-name influzer \
  --publicly-accessible \
  --vpc-security-group-ids sg-xxxxxxxx
```

### Step 2: Get Database Connection URL

After creation, get the endpoint from RDS console. Your DATABASE_URL will be:

```
postgres://postgres:YOUR_PASSWORD@influzer-db.xxxxxx.us-east-1.rds.amazonaws.com:5432/influzer
```

### Step 3: Add DATABASE_URL to App Runner

**Option A: Via AWS Console**
1. Go to App Runner → Your service → Configuration
2. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: `postgres://postgres:PASSWORD@your-rds-endpoint:5432/influzer`

**Option B: Via GitHub Secrets + Workflow**

1. Add secret to GitHub repo:
   - Go to Settings → Secrets and variables → Actions
   - Add `DATABASE_URL` secret

2. Update deploy workflow (see updated deploy.yml below)

### Step 4: Security Group Configuration

Ensure your RDS security group allows inbound traffic from App Runner:

```bash
# Get App Runner's outbound IP or use VPC connector
aws ec2 authorize-security-group-ingress \
  --group-id sg-your-rds-security-group \
  --protocol tcp \
  --port 5432 \
  --cidr 0.0.0.0/0  # For testing only! Use VPC connector in production
```

**For production:** Use an App Runner VPC connector to keep database private.

## Alternative: Use Neon or Supabase (Simpler)

For a simpler setup, use a managed PostgreSQL service:

### Neon (Recommended - Free tier available)
1. Sign up at https://neon.tech
2. Create a project
3. Copy the connection string
4. Add to App Runner as `DATABASE_URL`

### Supabase
1. Sign up at https://supabase.com
2. Create a project
3. Go to Settings → Database → Connection string
4. Add to App Runner as `DATABASE_URL`

## Verification

After deploying with DATABASE_URL set, check the logs:

```bash
aws apprunner list-operations --service-arn YOUR_SERVICE_ARN
```

You should see:
```
[entrypoint] DATABASE_URL=<set>
[entrypoint] Running migrations...
```

## Environment Variables Summary

For production, set these in App Runner:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `DJANGO_SECRET_KEY` | Random secret key |
| `DJANGO_SETTINGS_MODULE` | `myproject.settings` |
| `ALLOWED_HOSTS` | Your domain(s) |
| `USE_S3` | `true` for S3 media storage |
| `AWS_STORAGE_BUCKET_NAME` | Your S3 bucket |
| `OPENAI_API_KEY` | OpenAI API key |
