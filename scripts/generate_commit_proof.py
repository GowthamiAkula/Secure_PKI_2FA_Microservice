import base64
import subprocess
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from crypto_utils import sign_message, encrypt_with_public_key


def main():
    # 1) Get current commit hash
    commit_hash = subprocess.check_output(
        ["git", "log", "-1", "--format=%H"], text=True
    ).strip()

    # 2) Load student private key
    priv_bytes = Path("student_private.pem").read_bytes()
    private_key = serialization.load_pem_private_key(
        priv_bytes, password=None
    )

    # 3) Sign commit hash
    signature = sign_message(commit_hash, private_key)

    # 4) Load instructor public key
    pub_bytes = Path("instructor_public.pem").read_bytes()
    public_key = serialization.load_pem_public_key(pub_bytes)

    # 5) Encrypt signature
    encrypted_sig = encrypt_with_public_key(signature, public_key)

    # 6) Base64-encode encrypted signature
    encoded = base64.b64encode(encrypted_sig).decode("ascii")

    # Output: two lines
    print(commit_hash)
    print(encoded)


if __name__ == "__main__":
    main()
