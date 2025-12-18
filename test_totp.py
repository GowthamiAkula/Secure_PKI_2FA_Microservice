from totp_utils import generate_totp_code, verify_totp_code

HEX_SEED = "4e46f141570475506cc36a9e681c9fd3fafd9145b9b0ef9e218a98ae56484f39"

code = generate_totp_code(HEX_SEED)
print("Current TOTP code:", code)
print("Is valid:", verify_totp_code(HEX_SEED, code))

