import random
import string


def generate_password():
    """Generate a 10-digit random password."""
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    return password
