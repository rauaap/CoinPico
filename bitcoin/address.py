import binascii, hashlib, sys
from . import bech32

base58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def hashpubkey(pubkey):
    a=hashlib.sha256(pubkey).digest()
    ripemd160=hashlib.new('ripemd160', a)
    return ripemd160.digest()

def preparepayload(pubkey, prefix=b'\x00'):
    prefix_pubkeyb=prefix+pubkey
    checksum=hashlib.sha256(
        hashlib.sha256(prefix_pubkeyb).digest()
        ).digest()

    prefix_pubkeyb_check=prefix_pubkeyb+checksum[:4]
    return prefix_pubkeyb_check

def base58encode(payload):
    n=int(binascii.hexlify(payload), 16)
    res=''
    while n>0:
        n, r=divmod(n, 58)
        res+=base58[r]
    padding = 0
    for c in payload:
        if c == 0:
            padding += 1
        else:
            break
    res=list(res)
    res.reverse()
    res=''.join(res)
    return base58[0]*padding+res

def p2wpkh(pubkey):
    return bech32.encode( 'bc', 0, hashpubkey(pubkey) )
