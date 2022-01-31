import binascii, hashlib

with open('bitcoin/wordlist.txt', 'r') as f:
    wordlist=f.read().split('\n')

def to_words(entropy):
    size = len(entropy)
    assert size in [16, 20, 24, 28, 32]
    checksumlen = int(size/4)
    checksum=hashlib.sha256(entropy).digest()[0] >> (8-checksumlen)
    checked = (int.from_bytes(entropy, 'big') << checksumlen) | checksum
    words = []
    for i in range( int( (size*8+checksumlen)/11 ) ):
        checked, r = divmod(checked, 2048)
        words.append(wordlist[r])
    words.reverse()
    return ' '.join(words)

def to_seed(words, passphrase=''):
    words=words.encode('utf8')
    salt=('mnemonic'+passphrase).encode('utf8')
    seed=hashlib.pbkdf2_hmac('sha512', words, salt, 2048, 64)
    return seed[:64]
    
