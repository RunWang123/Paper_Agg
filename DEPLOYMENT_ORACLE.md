# Deploying CosmosPaper on Oracle Cloud (Docker)

This guide walks you through deploying the Paper Aggregator (Next.js Frontend + FastAPI Backend + PostgreSQL) on an Oracle Cloud VM using Docker Compose.

## Prerequisites

1.  **Oracle Cloud VM**: An Ubuntu Aarch64 (ARM) instance (e.g., VM.Standard.A1.Flex) is recommended for cost/performance, but AMD64 works too.
2.  **Docker & Docker Compose**: Installed on the VM.
3.  **Git**: Installed on the VM.

## 1. Prepare the Server

SSH into your Oracle VM:

```bash
ssh ubuntu@YOUR_VM_IP
```

Install Docker and Git (if not already installed):

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git
sudo usermod -aG docker $USER
# Log out and log back in for group changes to take effect
exit
ssh ubuntu@YOUR_VM_IP
```

## 2. Clone the Repository

Clone your project (replace with your repo URL):

```bash
git clone https://github.com/RunWang123/Paper_Agg.git
cd Paper_Agg
# Switch to the version2 branch
git checkout version2
```

## 3. Configure Environment Variables

Create the `.env` file from the example:

```bash
cp .env.example .env
nano .env
```

**Crucial Steps:**

1.  **ALLOWED_ORIGINS**: Add your VM's IP address.
    ```env
    ALLOWED_ORIGINS=http://localhost:3000,http://YOUR_ORACLE_VM_IP:3000
    ```
2.  **Database URL**: Ensure it matches the docker-compose service name (`db`).
    ```env
    DATABASE_URL=postgresql://paper_user:paper_password@db:5432/paper_agg
    ```

## 4. Configure Docker Compose

Edit `docker-compose.yml` to set your Public IP:

```bash
nano docker-compose.yml
```

Find `YOUR_ORACLE_VM_IP` and replace it with your actual Oracle VM Public IP in **two places**:
1.  Backend `ALLOWED_ORIGINS`
2.  Frontend `NEXT_PUBLIC_API_URL`

```yaml
    environment:
      - ALLOWED_ORIGINS=http://localhost:3000,http://123.45.67.89:3000
...
    environment:
      - NEXT_PUBLIC_API_URL=http://123.45.67.89:8000
```

## 5. Build and Run

Start the services in the background:

```bash
docker-compose up -d --build
```

Check logs to ensure everything started correctly:

```bash
docker-compose logs -f
```

## 6. Configure Oracle Cloud Firewall (Ingress Rules)

By default, Oracle Cloud blocks most ports. You need to allow traffic on ports **3000** (Frontend) and **8000** (Backend).

1.  Go to your **VCN (Virtual Cloud Network)** in Oracle Cloud Console.
2.  Navigate to **Security Lists** > **Default Security List**.
3.  Click **Add Ingress Rules**.
4.  Add a rule for Port 3000:
    *   **Source CIDR**: `0.0.0.0/0`
    *   **Destination Port Range**: `3000`
5.  Add a rule for Port 8000:
    *   **Source CIDR**: `0.0.0.0/0`
    *   **Destination Port Range**: `8000`

## 7. Access the App

Open your browser and visit:

*   **Frontend**: `http://YOUR_ORACLE_VM_IP:3000`
*   **Backend API**: `http://YOUR_ORACLE_VM_IP:8000/docs`

## Extensions (Optional)

### Using Nginx (Recommended for Production)
For a cleaner URL (e.g., just the IP or a domain name) and HTTPS support, set up Nginx as a reverse proxy.

1.  Install Nginx: `sudo apt install nginx`
2.  Configure `/etc/nginx/sites-available/default` to proxy port 80 to 3000 and `/api` to 8000.
3.  Use Certbot for free SSL certificates.

