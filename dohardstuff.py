import requests

file = requests.get("http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz")

f = open("tmp.gz", "wb")

f.write(file.content)
f.close()

file = requests.get("http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz")

f = open("tmp.meta.gz", "wb")

f.write(file.content)
f.close()

import gzip
import struct

# Data found here: http://yann.lecun.com/exdb/mnist/

def unt(stuff):
    return struct.unpack(">i", stuff)[0]

f = gzip.open("tmp.gz", "rb")
meta = gzip.open("tmp.meta.gz", "rb")
print("Magic: " + str(unt(f.read(4))))
print("Meta-magic: " + str(unt(meta.read(4))))

count = unt(f.read(4))
meta.read(4) # discard the size

data = []

for i in range(count):
    rows = unt(f.read(4))
    cols = unt(f.read(4))
    
    data.append(dict(
        number = meta.read(1),
        pixels = []#[]
    ))
    
    for row in range(rows):
        
        # gotta initialize the 2nd layer here
        data[i]['pixels'].append([])
        
        data[i]['number'] = meta.read(1)
        
        for col in range(cols):
            data[i]['pixels'][row].append(f.read(1))

print(len(data[0]))
