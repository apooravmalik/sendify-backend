import random
import string

def generate_code(length=6):
    """Generates a random alphanumeric code of given length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
