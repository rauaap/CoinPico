from machine import Pin

class ButtonPin(Pin):
    def __init__(self, pin, mode, pull, id):
        super().__init__(pin, mode, pull)
        self.id = id
        self.pressed = self.value
        
class Buttons:
    def __init__(self, one, two, three, four, five, six, seven, eight, nine, left, zero, right):
        self.ONE = ButtonPin(one, Pin.IN, Pin.PULL_DOWN, 1)
        self.TWO = ButtonPin(two, Pin.IN, Pin.PULL_DOWN, 2)
        self.THREE = ButtonPin(three, Pin.IN, Pin.PULL_DOWN, 3)
        self.FOUR = ButtonPin(four, Pin.IN, Pin.PULL_DOWN, 4)
        self.FIVE = ButtonPin(five, Pin.IN, Pin.PULL_DOWN, 5)
        self.SIX = ButtonPin(six, Pin.IN, Pin.PULL_DOWN, 6)
        self.SEVEN = ButtonPin(seven, Pin.IN, Pin.PULL_DOWN, 7)
        self.EIGHT = ButtonPin(eight, Pin.IN, Pin.PULL_DOWN, 8)
        self.NINE = ButtonPin(nine, Pin.IN, Pin.PULL_DOWN, 9)
        self.LEFT = ButtonPin(left, Pin.IN, Pin.PULL_DOWN, 10)
        self.ZERO = ButtonPin(zero, Pin.IN, Pin.PULL_DOWN, 0)
        self.RIGHT = ButtonPin(right, Pin.IN, Pin.PULL_DOWN, 11)
        self.button_names = ['ZERO', 'ONE', 'TWO', 'THREE', 
                             'FOUR', 'FIVE', 'SIX', 
                             'SEVEN', 'EIGHT', 'NINE', 
                             'LEFT', 'RIGHT']
        self.allbuttons = [self.__dict__[b] for b in self.button_names]
        
    class StatusList:
        def __init__(self, statuslist):
            self.statuslist = [ self.StatusObj(s) for s in statuslist ]
        def __repr__(self):
            return 'StatusList({})'.format( str( self.statuslist) )
        def __iter__(self):
            return iter(self.statuslist)
        def __len__(self):
            return len(self.statuslist)
        def __getitem__(self, k):
            return self.statuslist[k]
        def __delitem__(self, k):
            del self.statuslist[k]
        def filter(self, f=True):
            return Buttons.StatusList ( list( filter(lambda x: x[1]==f, self.statuslist) ) )
        class StatusObj:
            def __init__(self, status):
                self.status = status
            @property
            def pin(self):
                return self.status[0]
            def __repr__(self):
                return 'StatusObj{}'.format( str(self.status) )
            def __iter__(self):
                return iter(self.status)
            def __getitem__(self, k):
                return self.status[k]
            def __eq__(self, other):
                return self.status[1] == other
            def __bool__(self):
                return self.status[1]
    
    @classmethod        
    def status(cls, *buttons):
        vals = [ ( b, b.pressed() ) for b in buttons ]
        return cls.StatusList(vals)
            
    @staticmethod
    def all_pressed(*buttons):
        return False not in [b.pressed() for b in buttons]
            
    @staticmethod
    def none_pressed(*buttons):
        return True not in [b.pressed() for b in buttons]
        
    @classmethod
    def wait_press(cls, *buttons):
        while cls.none_pressed(*buttons):
            pass
        button = cls.status(*buttons).filter()[0].pin
        while button.pressed():
            pass
        return button
        
    @classmethod
    def action_hold(cls, *buttons, toggle=False):
        def decor(callback):
            def wrapper(*args, **kwargs):
                res = callback(*args, **kwargs)
                while not cls.none_pressed(*buttons):
                    pass
                while toggle == cls.none_pressed(*buttons):
                    pass
                return res
            return wrapper
        return decor        
