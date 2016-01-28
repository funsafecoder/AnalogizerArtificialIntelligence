import requests
import math

file = requests.get("http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz")

f = open("tmp.gz", "wb")

f.write(file.content)
f.close()

file = requests.get("http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz")

f = open("tmp.meta.gz", "wb")

f.write(file.content)
f.close()

file = requests.get("http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz")

f = open("test.gz", "wb")

f.write(file.content)
f.close()

file = requests.get("http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz")

f = open("test.meta.gz", "wb")

f.write(file.content)
f.close()

import gzip
import struct

# Data found here: http://yann.lecun.com/exdb/mnist/

def unt(stuff):
    return struct.unpack(">i", stuff)[0]

def rankPoint(me, test):
    total = 0
    for i in range(len(me.pixels)):
        for j in range(len(me.pixels[i])):
            total = total + pow((me.pixels[i][j] - test.pixels[i][j]), 2)
    return math.sqrt(total)


def unpackImage(image, meta):
    data = dict(
        number = meta.read(1),
        pixels = []#[]
    ))
    
    for row in range(rows):
        
        # gotta initialize the 2nd layer here
        data['pixels'].append([])
        
        data['number'] = meta.read(1)
        
        for col in range(cols):
            data['pixels'][row].append(image.read(1))
    
    return Image(data["pixels"], data["number"])

#This is a good POPO
class Image(object):
    pixels = []
    number = 0

    def __init__(self, pixels, number):
        self.pixels = pixels
        self.number = number

f = gzip.open("tmp.gz", "rb")
meta = gzip.open("tmp.meta.gz", "rb")
test = gzip.open("test.gz", "rb")
testmeta = gzip.open("test.meta.gz", "rb")

print("Magic: " + str(unt(f.read(4))))
print("Meta-magic: " + str(unt(meta.read(4))))
print("Magic Test: " + str(unt(test.read(4))))
print("Meta-magic Test: " + str(unt(testmeta.read(4))))

trainingcount = unt(f.read(4))
meta.read(4) # discard the size
testcount = unt(test.read(4))
testmeta.read(4)

rows = unt(f.read(4))
cols = unt(f.read(4))
unt(test.read(4))
unt(test.read(4))

assert rows == 28


topten = []
testimage = unpackImage(test, testmeta)
for i in range(1000):
    trained = unpackImage(f, meta)
    rank = rankPoint(testimage, trained)
    if len(topten) < 10:
        topten.append(rank)
    else:
        
























