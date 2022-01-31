import binascii, sys
from hashlib import sha512, sha256, new
import hashlib
from .address import base58encode
if sys.implementation.name=='micropython':
    from .ec import compressedpubk
else:
    from .testsecp256k1 import compressedpubk
if sys.implementation.name=='cpython':
    from .testhashlib import hmac_sha512
    hashlib.__dict__['hmac_sha512']=hmac_sha512

n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

class HDKey:
    def __init__(self, bytes, fingerprint = None, path = ''):
        self.key = bytes[:32]
        self.chain = bytes[32:]
        self.parent_fingerprint = fingerprint if fingerprint else (0).to_bytes(4, 'big')
        self.path = ''
    
    @property
    def depth(self):
        return len( self.parsepath(self.path) ) - 1
        
    @property
    def number(self):
        return (self.parsepath(self.path)[-1]).to_bytes(4, 'big')
        
    @property
    def pubkey(self):
        return compressedpubk(self.key)
    
    @classmethod    
    def bip32root(cls, bytes):
        bytes = hashlib.hmac_sha512(b'Bitcoin seed', bytes)
        return cls( bytes )

    def ckdpriv(self, index):
        index = index.to_bytes(4, 'big')
        if index[0]>=128:
            ckey=b'\x00' + self.key
        else:
            ckey = compressedpubk(self.key)
        pkeyhash = hashlib.hmac_sha512(self.chain, ckey+index)
        chain = pkeyhash[32:]
        key = ( int.from_bytes(pkeyhash[:32], 'big') + int.from_bytes(self.key, 'big') ) % n
        fingerprint = self.fingerprint
        return HDKey( key.to_bytes(32, 'big') + chain, fingerprint )

    @property
    def fingerprint(self):
        pub=compressedpubk(self.key)
        rip=hashlib.new('ripemd160')
        rip.update(sha256(pub).digest())
        fingerprint=rip.digest()[:4]
        return fingerprint

    @staticmethod
    def parsepath(path):
        path = path.split('/')
        path[0] = '0'
        path = [ int(p[:-1])+2147483648 if 'h' in p else int(p) for p in path]
        return path

    def derive(self, path):
        parsedpath = self.parsepath(path)
        child = self
        fingerprints = [self.fingerprint]
        for p in parsedpath[1:]:
            child = child.ckdpriv(p)
            fingerprints.append( child.fingerprint )
        child.path = path
        child.parent_fingerprint = fingerprints[-2]
        return child
        
    def extended(self, private=False):
        prefix = binascii.unhexlify('04b2430c') if private else binascii.unhexlify('04b24746')
        key = b'\x00'+self.key if private else compressedpubk(self.key)
        depth = (self.depth).to_bytes(1, 'big')
        concat = prefix + depth + self.parent_fingerprint + self.number + self.chain + key
        checksum=sha256( sha256(concat).digest() ).digest()[:4]
        xpub = base58encode(concat + checksum)
        return xpub
        
        
