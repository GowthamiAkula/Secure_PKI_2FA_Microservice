import base64
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from totp_utils import generate_totp_code, verify_totp_code

app = FastAPI()

DATA_DIR = Path("/data")
SEED_FILE = DATA_DIR / "seed.txt"
PRIVATE_KEY_PATH = Path("student_private.pem")


class DecryptSeedRequest(BaseModel):
    encrypted_seed: str


class Verify2FARequest(BaseModel):
    code: str


def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        pem_data = f.read()
    return serialization.load_pem_private_key(pem_data, password=None)


def decrypt_seed_bytes(encrypted_seed_b64: str, private_key) -> str:
    encrypted_bytes = base64.b64decode(encrypted_seed_b64)

    decrypted_bytes = private_key.decrypt(
        encrypted_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    hex_seed = decrypted_bytes.decode("utf-8")
    if len(hex_seed) != 64:
        raise ValueError("Seed must be 64 characters")
    if any(c not in "0123456789abcdef" for c in hex_seed):
        raise ValueError("Seed not valid hex")
    return hex_seed


@app.post("/decrypt-seed")
def decrypt_seed_endpoint(body: DecryptSeedRequest):
    try:
        private_key = load_private_key()
        hex_seed = decrypt_seed_bytes(body.encrypted_seed, private_key)

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        SEED_FILE.write_text(hex_seed, encoding="utf-8")
        return {"status": "ok"}
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


@app.get("/generate-2fa")
def generate_2fa():
    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_FILE.read_text(encoding="utf-8").strip()
    try:
        code = generate_totp_code(hex_seed)
    except Exception:
        raise HTTPException(status_code=500, detail="TOTP generation failed")

    now = int(time.time())
    remaining = 30 - (now % 30)
    return {"code": code, "valid_for": remaining}


@app.post("/verify-2fa")
def verify_2fa(body: Verify2FARequest | None = None):
    if body is None or not body.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not SEED_FILE.exists():
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    hex_seed = SEED_FILE.read_text(encoding="utf-8").strip()
    is_valid = verify_totp_code(hex_seed, body.code, valid_window=1)
    return {"valid": is_valid}
