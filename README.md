Got it 👍
Your content is **already very close to proper Markdown**, but it looks like GitHub is interpreting some parts as plain text (showing `*`, `#`, etc.) because of **missing formatting for code blocks, lists, and headings**.

Below is a **clean, GitHub-ready `README.md` version** of what you shared. You can **copy–paste this directly** into your `README.md` file and it will render nicely.

---

```markdown
# 🔐 Secure PKI-Based 2FA Microservice

A containerized microservice that implements **secure two-factor authentication (2FA)** using **public-key cryptography (RSA)** and **TOTP codes**, built with **FastAPI** and **Docker**.

---

## ✨ Features

- Decrypts a **64-character hex seed** using **RSA-OAEP (SHA-256)** and stores it securely on a Docker volume
- Generates standard **6-digit TOTP codes** (SHA-1, 30-second window)
- Verifies user-submitted 2FA codes with a configurable time window (±1 step)
- Runs as a Docker container with a **cron job** that logs the latest 2FA code every minute (UTC)
- Persists the decrypted seed and cron output across container restarts using **named Docker volumes**

---

## 🏗 Architecture

- **Backend Framework:** FastAPI (`main.py`)
- **Cryptography:**
  - `cryptography` → RSA-OAEP decryption & key handling
  - `pyotp` → TOTP generation & verification
- **Containerization:** Multi-stage Dockerfile (builder + slim runtime)
- **Orchestration:** `docker-compose.yml`
- **Cron Job:**  
  `scripts/log_2fa_cron.py` scheduled via `/etc/cron.d/2fa-cron`

---

## 📁 Key Files

| File | Description |
|----|----|
| `main.py` | FastAPI app exposing 2FA API endpoints |
| `totp_utils.py` | Converts hex seed to Base32 and handles TOTP |
| `decrypt_seed.py` | Local helper to test RSA seed decryption |
| `scripts/log_2fa_cron.py` | Cron script logging TOTP every minute |
| `Dockerfile` | Multi-stage build with cron & Uvicorn |
| `docker-compose.yml` | App service, volumes, and PEM key mounts |
| `crypto_utils.py` | RSA-PSS signing & RSA-OAEP encryption helpers |
| `scripts/generate_commit_proof.py` | Generates cryptographic commit proof |
| `*.pem` files | RSA keys for encryption, decryption & verification |

---

## 🌐 API Endpoints

All endpoints are served over **HTTP** on port **`8080`**.

---

### 🔓 POST `/decrypt-seed`

Decrypts the encrypted seed using the **student private key** and stores it securely at:

```

/data/seed.txt

````

#### Request Body

```json
{
  "encrypted_seed": "hex-encoded-encrypted-seed"
}
````

#### Response

```json
{
  "status": "success",
  "message": "Seed decrypted and stored securely"
}
```

---

## 🐳 Running the Service

```bash
docker-compose up --build
```

The service will be available at:

```
http://localhost:8080
```

---

## 🛡 Security Notes

* RSA-OAEP with SHA-256 is used for secure seed decryption
* TOTP follows RFC 6238 standards
* Private keys are **never committed**
* Sensitive data is persisted using Docker volumes

---

## ✅ Tech Stack

* Python 3.11
* FastAPI
* Cryptography
* PyOTP
* Docker & Docker Compose
* Cron (Linux)

---

## 📌 Author

**Student Project – Secure Authentication Systems**

````
