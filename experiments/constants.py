import string

BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
WHITE = 255, 255, 255
GRAY = 180, 180, 180

ALPHA = set(string.ascii_uppercase)
ALPHANUM = ALPHA.union(string.digits)
VOWELS = set('AEIOUY')
CONSONANTS = ALPHA.difference(VOWELS)

UNLIMITED_DURATION = float('inf')
