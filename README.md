```markdown
# Secure PKI-Based 2FA Microservice

A containerized microservice that implements secure two-factor authentication (2FA) using public-key cryptography (RSA) and TOTP codes, built with FastAPI and Docker.

## Features

- Decrypts a 64‑character hex seed using RSA‑OAEP (SHA‑256) and stores it securely on a Docker volume.
- Generates standard 6‑digit TOTP codes (SHA‑1, 30‑second window) from the stored seed.
- Verifies user‑submitted 2FA codes with a configurable time window (±1 step).
- Runs as a Docker container with a cron job that logs the latest 2FA code every minute in UTC.
- Persists the decrypted seed and cron output across container restarts using named Docker volumes.

## Architecture

- **Backend framework:** FastAPI (`main.py`).
- **Crypto:** `cryptography` for RSA‑OAEP decryption and key handling, `pyotp` for TOTP.
- **Containerization:** Multi‑stage Dockerfile (builder + slim runtime image).
- **Orchestration:** `docker-compose.yml` to run the app with mounted volumes and PEM keys.
- **Cron:** `scripts/log_2fa_cron.py` scheduled via `/etc/cron.d/2fa-cron` inside the container.

### Key Files

- `main.py` – FastAPI app exposing the 2FA API endpoints.
- `totp_utils.py` – Helpers to convert the hex seed to Base32 and generate/verify TOTP codes.
- `decrypt_seed.py` – Local helper script to test RSA decryption of `encrypted_seed.txt`.
- `scripts/log_2fa_cron.py` – Cron script that logs the current TOTP code every minute.
- `Dockerfile` – Multi‑stage build that installs dependencies, configures cron, and starts Uvicorn.
- `docker-compose.yml` – Defines the `app` service, volumes (`/data`, `/cron`), and PEM key mounts.
- `student_private.pem` / `student_public.pem` / `instructor_public.pem` – RSA keys used for decryption and commit proof.
- `crypto_utils.py` – Helper functions for `sign_message` (RSA‑PSS) and `encrypt_with_public_key` (RSA‑OAEP).
- `scripts/generate_commit_proof.py` – Script to create the cryptographic commit proof for evaluation.

## API Endpoints

All endpoints are served over HTTP on port `8080`.

### POST `/decrypt-seed`

Decrypts the encrypted seed using the student private key and stores it in `/data/seed.txt`.

**Request body:**

```
{
  "encrypted_seed": "<base64 encrypted seed>"
}
```

**Successful response:**

```
{
  "status": "ok"
}
```

If decryption fails or the seed is not a valid 64‑character hex string, the endpoint returns HTTP 500.

### GET `/generate-2fa`

Generates the current 6‑digit TOTP code from the stored seed.

**Response (200):**

```
{
  "code": "123456",
  "valid_for": 23
}
```

- `code` is the current TOTP.
- `valid_for` is the number of seconds the code remains valid in the current 30‑second window.

If the seed has not been decrypted yet (`/data/seed.txt` missing), the endpoint returns HTTP 500 with `Seed not decrypted yet`.

### POST `/verify-2fa`

Verifies a submitted 2FA code against the current seed.

**Request body:**

```
{
  "code": "123456"
}
```

**Response:**

```
{
  "valid": true
}
```

- `valid` is `true` if the code is within the allowed time window (±1 step), otherwise `false`.

If no code is provided, the endpoint returns HTTP 400. If the seed has not been decrypted, it returns HTTP 500.

## Cron Job and Persistence

Inside the running container:

- The decrypted seed is stored at `/data/seed.txt` on a named Docker volume.
- The cron job runs `scripts/log_2fa_cron.py` every minute.
- Each run appends a line to `/cron/last_code.txt`:

```
YYYY-MM-DD HH:MM:SS - 2FA Code: XXXXXX
```

Timestamps are in UTC using `datetime.utcnow()` and are truncated to seconds.

### Volumes

`docker-compose.yml` defines two named volumes:

- `seed-data` → mounted at `/data` (stores `seed.txt`).
- `cron-output` → mounted at `/cron` (stores `last_code.txt`).

Because these are named volumes, `seed.txt` and `last_code.txt` survive container restarts.

## Running the Project Locally

### Prerequisites

- Python 3.11 (for local scripts / tests).
- Docker and Docker Compose installed and running.

### 1. (Optional) Install Python dependencies locally

```
python -m venv .venv
# On Linux/macOS:
source .venv/bin/activate
# On Windows (PowerShell or Git Bash):
.venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Build and start the container

From the project root:

```
docker compose build
docker compose up -d
```

Check the container:

```
docker compose ps
```

You should see the `pki-2fa-container` service `Up` with port `0.0.0.0:8080->8080/tcp`.

### 3. Decrypt and store the seed

Use the provided `encrypted_seed.txt`:

```
curl -X POST http://localhost:8080/decrypt-seed \
  -H "Content-Type: application/json" \
  -d "{\"encrypted_seed\": \"$(cat encrypted_seed.txt)\"}"
```

A successful response:

```
{"status": "ok"}
```

Now `/data/seed.txt` exists inside the container.

### 4. Generate a 2FA code

```
curl http://localhost:8080/generate-2fa
```

Example:

```
{"code":"666699","valid_for":27}
```

### 5. Verify a 2FA code

First get a fresh code from `/generate-2fa`, then:

```
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "666699"}'
```

Expected:

```
{"valid": true}
```

If you send an obviously wrong code:

```
curl -X POST http://localhost:8080/verify-2fa \
  -H "Content-Type: application/json" \
  -d '{"code": "000000"}'
```

you should see:

```
{"valid": false}
```

### 6. Inspect cron output

To check that the cron job is running inside the container:

```
docker exec -it pki-2fa-container sh -c "tail -n 5 /cron/last_code.txt"
```

You should see several lines with timestamps one minute apart and different `2FA Code` values.

## Commit Proof (Step 13)

The project includes:

- `crypto_utils.py` with:
  - `sign_message(message: str, private_key) -> bytes` – signs the ASCII commit hash using RSA‑PSS with SHA‑256 and maximum salt length.
  - `encrypt_with_public_key(data: bytes, public_key) -> bytes` – encrypts data using RSA‑OAEP with SHA‑256.

- `scripts/generate_commit_proof.py` which:
  1. Reads the latest Git commit hash (`git log -1 --format=%H`).
  2. Loads `student_private.pem` and signs the commit hash string.
  3. Loads `instructor_public.pem` and encrypts the signature.
  4. Base64‑encodes the encrypted signature.
  5. Prints:
     - Line 1: commit hash (40‑character hex).
     - Line 2: encrypted signature (Base64 string).

Run:

```
python scripts/generate_commit_proof.py
```

Use the two printed lines as the commit proof in the evaluation portal.

## Notes

- Timezone inside the container is set to UTC via `TZ=UTC` and `tzdata`.
- The service listens on `0.0.0.0:8080` so it is reachable from the host and from the evaluation environment.
- This project is designed for educational use as part of a secure PKI‑based 2FA assignment.
```