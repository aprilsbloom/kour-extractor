import hashlib
import random
import string

CHAR_LIST = string.ascii_letters + string.digits

def hash_file(bytes):
	return hashlib.sha256(bytes).hexdigest()

def random_string(length=5):
	return "".join([random.choice(CHAR_LIST) for i in range(length)]).upper()

def remove_wrapped_quotes(str):
	if str[0] == '"':
		str = str[1:]

	if str[-1] == '"':
		str = str[:-1]

	return str

def remove_empty_items(arr):
	return [str(x).strip() for x in arr if str(x).strip() != '']

def remove_arr_duplicates(arr):
	return list(set(arr))