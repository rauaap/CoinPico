from bitcoin import mnemonic, bip32

class Wallet:
    def __init__(self, bytes):
        self._bytes = bytes
        self.mnemonic = mnemonic.to_words(self._bytes)
        self._seed = mnemonic.to_seed(self.mnemonic)
        self.root = bip32.HDKey.bip32root(self._seed)
        self.account = self.root.derive('m/84h/0h/0h')
        self.xpub = self.account.extended()
        
