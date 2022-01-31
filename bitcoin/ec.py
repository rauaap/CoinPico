import secp256k1

def compressedpubk(key):
    pubk = secp256k1.ec_pubkey_create(key)
    cpubk = secp256k1.ec_pubkey_serialize(pubk, secp256k1.EC_COMPRESSED)
    return cpubk
