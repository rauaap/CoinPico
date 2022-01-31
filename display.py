from LCD import I2C_LCD

class Display(I2C_LCD):
    def __init__(self, i2c, addr, l, c):
        super().__init__(i2c, addr, l, c)
        self.custom_char(0, [4,14,21,4,4,4,4,0]), #UP
        self.custom_char(1, [4,4,4,4,21,14,4,0]), #DOWN
        self.custom_char(2, [4,14,21,4,4,21,14,4]) #UPDOWN
    
    def printrows(self, *strings, startrow=0, clear=True):
        if clear:
            self.clear()
        for s in strings:
            self.move_to(0, startrow)
            if s:
                self.putstr(s)
            startrow+=1
        self.move_to(0,0)
    
    def putlastchars(self, *chars, startrow=0, clear=False):
        if clear:
            self.clear()
        for c in chars:
            self.move_to(16-len(c), startrow)
            if c:
                self.putstr(c)
            else:
                print(c)
            startrow+=1
        self.move_to(0,0)
