import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization

def load_private_key(path: str = "student_private.pem"):
    with open(path, "rb") as f:
        pem_data = f.read()
    private_key = serialization.load_pem_private_key(
        pem_data,
        password=None,
    )
    return private_key


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP.
    Returns 64-character hex string.
    """
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
        raise ValueError(f"Seed length is {len(hex_seed)}, expected 64")

    valid_chars = set("0123456789abcdef")
    if any(c not in valid_chars for c in hex_seed):
        raise ValueError("Seed contains non-hex characters")

    return hex_seed


def main():
    with open("encrypted_seed.txt", "r", encoding="utf-8") as f:
        encrypted_seed_b64 = f.read().strip()

    private_key = load_private_key()
    hex_seed = decrypt_seed(encrypted_seed_b64, private_key)

    print("Decrypted hex seed:", hex_seed)


if __name__ == "__main__":
    main()
