import requests
import math
import pathlib
import multiprocessing
import queue
import sys

p = pathlib.Path('tmp.gz')
if not p.is_file():
    file = requests.get("http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz")
    
    f = open("tmp.gz", "wb")

    f.write(file.content)
    f.close()

p = pathlib.Path('tmp.meta.gz')
if not p.is_file():
    file = requests.get("http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz")

    f = open("tmp.meta.gz", "wb")

    f.write(file.content)
    f.close()

p = pathlib.Path('test.gz')
if not p.is_file():
    file = requests.get("http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz")

    f = open("test.gz", "wb")

    f.write(file.content)
    f.close()

p = pathlib.Path('test.meta.gz')
if not p.is_file():
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


def unpackImage(image, meta, rows, cols):
    data = dict(
        number = int.from_bytes(meta.read(1), byteorder='little'),
        pixels = []#[]
    )
    
    for row in range(rows):
        
        # gotta initialize the 2nd layer here
        data['pixels'].append([])
        
        for col in range(cols):
            data['pixels'][row].append(int.from_bytes(image.read(1), byteorder='little'))
    
    return Image(data["pixels"], data["number"])

#This is a good POPO
class Image(object):
    pixels = []
    number = 0

    def __init__(self, pixels, number):
        self.pixels = pixels
        self.number = number

class Rank(object):
    image = None
    ranking = 0
    
    def __init__(self, image, rank):
        self.image = image
        self.rank = rank

def getPreparedFileHandle(path):
    file = gzip.open(path, "rb")
    file.read(4) # magic!
    count = unt(file.read(4)) # count
    rows = unt(file.read(4))
    cols = unt(file.read(4))
    return (file, count, rows, cols)
    
def getPreparedMetaHandle(path):
	file = gzip.open(path, "rb")
	file.read(4) # magic!
	count = unt(file.read(4)) # num of items
	return (file, count)
	
def findBestMatch(testimage):
    topten = [] 
    f, trainingcount, rows, cols = getPreparedFileHandle("tmp.gz")
    meta, _ = getPreparedMetaHandle("tmp.meta.gz")
    for i in range(trainingcount):
        trained = unpackImage(f, meta, rows, cols)
        rank = rankPoint(testimage, trained)
        rank = Rank(trained, rank)
        
        if len(topten) == 0:
            topten.append(rank)
        else:
            for x in range(len(topten)):
                if topten[x].rank > rank.rank:
                    topten.insert(x, rank)
                    break
        
        if len(topten) > 10:
            topten.pop()
    return topten
    
def printResults(results, actual):

    for x in range(len(results)):
        print(str(x) + ": " + str(results[x].image.number) + " at distance " + str(results[x].rank))
    
    print()
    
    print("The actual number was " + str(actual.number))
    sys.stdout.flush()

meta = gzip.open("tmp.meta.gz", "rb")
test = gzip.open("test.gz", "rb")
testmeta = gzip.open("test.meta.gz", "rb")

#print("Magic: " + str(unt(f.read(4))))
print("Meta-magic: " + str(unt(meta.read(4))))
print("Magic Test: " + str(unt(test.read(4))))
print("Meta-magic Test: " + str(unt(testmeta.read(4))))

#trainingcount = unt(f.read(4))
meta.read(4) # discard the size
testcount = unt(test.read(4))
testmeta.read(4)

#rows = unt(f.read(4))
#cols = unt(f.read(4))
rows = unt(test.read(4))
cols = unt(test.read(4))

def run(work_queue, lock):

    while True:
        data = work_queue.get(True, None)
        results = findBestMatch(data)
        with lock:
            printResults(results, data)

threads = 7
work_queue = multiprocessing.Queue(10)
lock = multiprocessing.Lock()
for i in range(threads):
	p = multiprocessing.Process(target=run, args=(work_queue, lock))
	p.daemon = True
	p.start()

for testnum in range(testcount):
    testimage = unpackImage(test, testmeta, rows, cols)
    work_queue.put(testimage)

for testnum in range(testcount):
    topten = []
    f, trainingcount, rows, cols = getPreparedFileHandle("tmp.gz")
    meta, _ = getPreparedMetaHandle("tmp.meta.gz")
    testimage = unpackImage(test, testmeta)
    for i in range(trainingcount):
        trained = unpackImage(f, meta)
        rank = rankPoint(testimage, trained)
        rank = Rank(trained, rank)
        
        if len(topten) == 0:
            topten.append(rank)
        else:
            for x in range(len(topten)):
                if topten[x].rank > rank.rank:
                    topten.insert(x, rank)
                    break
        
        if len(topten) > 10:
            topten.pop()
        
        numfreq[trained.number]+=1

    for x in range(len(topten)):
        print(str(x) + ": " + str(topten[x].image.number) + " at distance " + str(topten[x].rank))

    print()

    print("The actual number was " + str(testimage.number))
    print(numfreq)












