import struct
def readshittyint(intfrompacket): #base 10 from hex
    try:
        intlist = "".join("%02x " % b for b in intfrompacket)
        intlist = intlist.split()
        newint = 0
        for i, e in enumerate(intlist):
            newint += int(e) * (100**i)
    except:
        return -1
    return newint

def makeshittyint(i, size):
    hexlist = ""
    while i > 0:
        hexlist += "%02d " % (i % 100)
        i = i//100
    hexlist = [int(x, base=16) for x in hexlist[:-1].split(" ")]
    hexlist = hexlist + ([0]*(size-len(hexlist)))
    return bytes(hexlist)

def nmap(num, initmin, initmax, newmin, newmax):
    input_range = initmax - initmin
    output_range = newmax - newmin
    output = (num - initmin) * output_range // input_range + newmin
    return output


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
        
        self.happiness = struct.unpack("I", char_data[0x4E : 0x52])[0]
        self.happiness = nmap(self.happiness, 0, 0x80000000, 0, 100)
        
        self.hunger = struct.unpack("I", char_data[0x52 : 0x56])[0]
        self.hunger = nmap(self.hunger, 0, 0x80000000, 0, 100)
        
        self.boredom = struct.unpack("I", char_data[0x56 : 0x5A])[0]
        self.boredom = nmap(self.boredom, 0, 0x80000000, 0, 100)
        
    def Output(self):
        data = self.char_data
        data = list(data)
        data[0x4A : 0x4E] = makeshittyint(self.creditz, 4)

        happiness = nmap(self.happiness, 0, 100, 0, 0x80000000)
        data[0x4E : 0x52] = struct.pack("I", happiness)

        hunger = nmap(self.hunger, 0, 100, 0, 0x80000000)
        data[0x52 : 0x56] = struct.pack("I", hunger)

        boredom = nmap(self.boredom, 0, 100, 0, 0x80000000)
        data[0x56 : 0x5A] = struct.pack("I", boredom)

        data = bytes(data)
        return data
    def Info(self):
        print('Type: %s' % characters[self.unit])
        print('Creditz: %s' % self.creditz)

            
