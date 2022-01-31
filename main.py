from uos import mount, umount
from sdcard import SDCard
from machine import I2C, Pin, SPI
from display import Display
from buttons import Buttons
from eeprom import Eeprom
from wallet import Wallet
from bitcoin import address

i2c = I2C( 1, sda=machine.Pin(14), scl=machine.Pin(15) )
lcd = Display(i2c, 0x27, 2, 16)
e = Eeprom(i2c)
spi = SPI(0, miso=Pin(16), mosi=Pin(19), sck=Pin(18))
buttons = Buttons(2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)

def startmenu():
    lcd.printrows('load seed', 'new seed')
    lcd.putlastchars(chr(0), chr(1))
    action = buttons.wait_press(buttons.TWO, buttons.EIGHT)
    if action.id == 8:
        dice_sides = enter_dice_sides()
        required_rolls = get_required_rolls(dice_sides)
        dicerolls = [r-1 for r in roll_dice(dice_sides, required_rolls)]
        newseed(dicerolls, dice_sides)

def enter_dice_sides():
    lcd.printrows('enter the number', 'of dice sides')
    lcd.putlastchars('>', startrow=1)
    buttons.wait_press(buttons.RIGHT)

    def sides_validation():
        dice_sides = enter_digits(2, clear=True)
        if dice_sides < 2:
            lcd.printrows('need at least', '2 sides')
            lcd.putlastchars('>', startrow=1)
            buttons.wait_press(buttons.RIGHT)
            return sides_validation()
        return dice_sides

    return sides_validation()

"""
division doesnt work with huge numbers in micropython
so we cant do log(2**128)/log(x)
"""
def get_required_rolls(dice_sides):
    t = 2**128
    s = 1
    c = 0
    while s<t:
        s = s*dice_sides
        c += 1
    return c

def newseed(r, b):
    bigint = sum([ n*b**i for i,n in enumerate(r) ])
    data = bigint.to_bytes(16, 'big')
    e.write(0, data)

def sumdigits(digits):
    digits.reverse()
    return sum( [ n * 10 ** i for i,n in enumerate(digits) ] )

def enter_digits(amount, clear=False):
    digits = []
    lcd.printrows(' '*3 , '< clear', clear=clear)
    lcd.putlastchars('OK >', startrow=1)
    for i in range(amount):
        digit = buttons.wait_press(*buttons.allbuttons).id
        if digit == 10:
            return enter_digits(amount)
        elif digit == 11 and digits:
            return sumdigits(digits)
        lcd.putstr( str(digit) )
        digits.append(digit)
    if buttons.wait_press(buttons.LEFT, buttons.RIGHT).id == 10:
        return enter_digits(amount)
    else:
        return sumdigits(digits)

def enter_roll(n, dice_sides, required_rolls, clear=True):
    if clear:
        lcd.clear()
    lcd.putlastchars( f'{n+1}/{required_rolls}' )
    roll = enter_digits(2)
    if roll > dice_sides or roll == 0:
        return enter_roll(n, dice_sides, required_rolls, clear=False)
    return roll

def roll_dice(dice_sides, required_rolls):
    rolls = []
    n = 0
    while True:
        rolls.append( enter_roll(n, dice_sides, required_rolls) )
        n+=1
        if n >= required_rolls:
            lcd.printrows('< done ', startrow=1, clear=False)
            lcd.putlastchars('roll >', startrow=1)
            if buttons.wait_press(buttons.RIGHT, buttons.LEFT).id == 10:
                break
            else:
                continue
    return rolls

def displaymnem():
    mnem = wallet.mnemonic
    mnem = mnem.split(' ')
    pos = 0
    while True:
        lcd.clear()
        pos %= len(mnem)
        lcd.printrows(mnem[pos], mnem[pos+1])
        lcd.putlastchars( str(pos+1), str(pos+2) )
        action = buttons.wait_press(buttons.TWO, buttons.EIGHT, buttons.LEFT)
        if action.id == 2:
            pos -= 2
        elif action.id == 8:
            pos += 2
        elif action.id == 10:
            return

def displayaddresses(i=None):
    if i is None:
        lcd.putlastchars('start #', clear=True)
        i = enter_digits(3)
    i %= 1000
    pos = 0
    lcd.printrows( str(i), startrow=1 )
    while True:
        pos %= 3
        addr = address.p2wpkh( wallet.account.derive('m/0/{}'.format(i)).pubkey )
        addr_slice = addr[pos*16:pos*16+16]
        lcd.putlastchars( '{}/3'.format(pos+1) + chr((pos+1)%3), startrow=1 )
        lcd.putstr( '{: <16}'.format(addr_slice) )
        action = buttons.wait_press(buttons.TWO, buttons.EIGHT, buttons.FOUR, buttons.SIX, buttons.LEFT)
        if action.id == 2:
            pos -= 1
        elif action.id == 8:
            pos += 1
        elif action.id == 4 or action.id == 6 :
            i += action.id - 5
            return displayaddresses(i)
        else:
            return

def export_xpub():
    lcd.printrows('Writing xpub', 'to xpub.txt...')
    try:
        sd = SDCard(spi, Pin(17))
    except OSError:
        lcd.printrows('No SD card', 'found')
        lcd.putlastchars('OK >', startrow=1)
        buttons.wait_press(buttons.RIGHT)
        return
    try:
        mount(sd, '/sd')
    except OSError:
        mount(sd, '/sd')
    with open('/sd/xpub.txt', 'a') as f:
        f.write(wallet.xpub + '\n')
    umount('/sd')
    lcd.printrows('Xpub saved', 'to SD card')
    lcd.putlastchars('OK >', startrow=1)
    buttons.wait_press(buttons.RIGHT)

def mainmenu():
    notimplemented = lambda: None
    menuitems = [(['show seed', 'words'], displaymnem),
                 (['display', 'addresses'], displayaddresses),
                 (['write xpub', 'to SD card'], export_xpub),
                 (['sign transaction', 'on SD card'], notimplemented)]
    pos = 0
    while True:
        lcd.clear()
        pos %= len(menuitems)
        menutext, func = menuitems[pos]
        lcd.printrows(*menutext)
        lcd.putlastchars('>', startrow=1)
        action = buttons.wait_press(buttons.TWO, buttons.EIGHT, buttons.RIGHT)
        if action.id == 2:
            pos -= 1
        elif action.id == 8:
            pos += 1
        elif action.id == 11:
            func()

def main():
    global wallet
    startmenu()
    lcd.printrows('loading...')
    bytes = e.read(0, 16)
    wallet = Wallet(bytes)
    while True:
        mainmenu()

main()
