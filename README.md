
---

## 🚀 **Friendbook Backend - Docker Setup Guide**

This guide will help you set up the **Friendbook Backend** locally using **Docker** and **Docker Compose**.

---

## 📦 **Step 1: Install Docker**

### ✅ For Windows & Mac:

* Download and install Docker Desktop from the official Docker website:
  👉 [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

> Make sure **Docker Desktop** is running after installation.

---

### ✅ For Linux (Ubuntu Example):

```bash
sudo apt update
sudo apt install -y docker.io docker-compose

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Optional: Run Docker without sudo
sudo usermod -aG docker $USER
newgrp docker
```

> 👉 Verify Docker installation:

```bash
docker --version
docker-compose --version
```

---

## 🔥 **Step 2: Clone the Repository**

```bash
git clone https://github.com/codewithjoe-tech/socal-backend.git
cd socal-backend
```

---

## ⚙️ **Step 3: Run Docker Compose**

> This will build the Docker images and start the services (e.g., backend server, database).

```bash
docker-compose up --build
```

✅ Once complete, the backend server will be running at:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🛑 **Step 4: Stop the Server**

To stop the running containers, press `Ctrl + C` in the terminal, then run:

```bash
docker-compose down
```

---

## 🗂️ **Project Structure Example:**

```plaintext
socal-backend/
├── backend/           # Django or FastAPI app (example)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
```

---

## 🚀 **Quick Commands:**

| Command                     | Description                  |
| --------------------------- | ---------------------------- |
| `docker-compose up --build` | Build and run the containers |
| `docker-compose up`         | Run without rebuilding       |
| `docker-compose down`       | Stop and remove containers   |
| `docker ps`                 | Check running containers     |

---

## 🚩 **Common Issues:**

* **Port Already in Use:**
  Stop previous containers:

  ```bash
  docker-compose down
  ```

* **Permission Denied:**
  If on Linux, run with `sudo` or add user to Docker group (see step 1).

---

## 📑 **Conclusion:**

You are now ready to develop and test the **Socal Backend** locally using Docker!

---

