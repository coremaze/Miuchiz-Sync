def readshittyint(intfrompacket): #base 10 from hex
    intlist = "".join("%02x " % b for b in intfrompacket)
    intlist = intlist.split()
    newint = 0
    for i, e in enumerate(intlist):
        newint += int(e) * (100**i)
    return newint

characters = ["Cloe",
              "Yasmin",
              "Spike",
              "Dash",
              "Roc",
              "Creeper",
              "Inferno"]

class Character():
    def __init__(self, char_data):
        if char_data.startswith(b'\x00\x00\x04\x00\x30\x13\x00\x00\x00'):
            char_data = char_data[8:]
        self.char_data = char_data
        self.unit = char_data[0x48]
        self.creditz = readshittyint(char_data[0x4A : 0x4E])
    def Info(self):
        print('Type: %s' % characters[self.unit])
        print('Creditz: %s' % self.creditz)

            
