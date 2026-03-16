import secrets
import string

def generate_secure_token(length=32):
    """
    Generate a secure random token using secrets module.
    """
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return token

if __name__ == "__main__":
    token = generate_secure_token()
    print(f"\nGenerated Secure Token:\n{token}\n")
    print("You can use this token for your API_TOKEN environment variable.")
