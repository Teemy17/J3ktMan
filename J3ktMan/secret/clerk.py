import dotenv
import os

dotenv.load_dotenv(dotenv.find_dotenv())

__publishable_key = os.getenv("CLERK_PUBLISHABLE_KEY")
__secret_key = os.getenv("CLERK_SECRET_KEY")

assert __publishable_key is not None
assert __secret_key is not None

PUBLISHABLE_KEY: str = __publishable_key
SECRET_KEY: str = __secret_key
