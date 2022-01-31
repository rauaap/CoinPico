import time

class Eeprom:
    def __init__(self, i2c, address=0x50):
        self.i2c = i2c
        self.address = address
        
    def write(self, memloc, data):
        data = [data[i:i+16] for i in range(0, len(data), 16)]
        for chunk in data:
            self.i2c.writeto_mem(self.address, memloc, chunk)
            memloc += 16
            time.sleep(0.05)
            
    def read(self, memloc, nbytes):
        return self.i2c.readfrom_mem(self.address, memloc, nbytes)
