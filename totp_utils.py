import base64
import pyotp


def hex_to_base32(hex_seed: str) -> str:
    # Convert hex string to bytes
    seed_bytes = bytes.fromhex(hex_seed)
    # Base32 encode, remove padding =
    return base64.b32encode(seed_bytes).decode("utf-8").rstrip("=")


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code from 64-char hex seed.
    SHA-1, 30s period, 6 digits.
    """
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, digest="sha1", interval=30)
    return totp.now()


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance (±valid_window periods).
    """
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=6, digest="sha1", interval=30)
    return totp.verify(code, valid_window=valid_window)
