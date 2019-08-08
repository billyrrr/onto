import random
import string


# Generate a random string
# with 32 characters.
# https://www.geeksforgeeks.org/generating-random-ids-python/
def random_id():
    random_id_str = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    return random_id_str
