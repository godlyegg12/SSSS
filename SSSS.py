
# Shamir's Secret Sharing System

import secrets
import math
import numpy
import argparse
import os


def encode(data,numReq,numGen=None):

    # Default to gererating only as many keys as required
    if numGen == None:
        numGen = numReq

    # Generate random coefficients of a polynomial
    coeff = []
    for i in range(1,numReq):
        coeff += [secrets.randbelow(math.floor((100/numReq)/(i*3)))+1]

    keys = []
    xs = []
    for _ in range(0,numGen):
        
        # Get a new random x value
        x = secrets.randbelow(255)+1
        while x in xs:
            x = secrets.randbelow(255)+1
        xs += [x]
        
        # Evaluate polynomial at x coordinate
        y = int(data)
        for i in range(1,numReq):
            y += (x**i) * coeff[i-1]
        keys += [(x,y)]
        
    return keys


def decode(numReq,points):

    arr = numpy.zeros((numReq,numReq),dtype=int)
    points = numpy.asarray(points,dtype=int)

    for i in range(0,numReq):
        arr[:,i] = points[:,0]**i

    d = numpy.linalg.det(arr)
    arr[:,0] = points[:,1]

    return int(round(numpy.linalg.det(arr)/d))


def encodeFile(numReq,numGen,file):

    file = file.replace("\\","/")
    try:
        f = open(file,mode="rb")
    except FileNotFoundError:
        print("Error: %s doesn't exist"%(file))
        return
    dr = file[0:file.rfind("/")]

    outF = []
    for i in range(0,numGen):
        t = open(dr+"/Key-"+str(i+1)+".shm",mode="wb")
        outF += [t]

    f.seek(0,2)
    length = f.tell()
    f.seek(0,0)

    print("Making "+str(numGen)+" keys...")

    keys = encode(int(code,base=2),numReq,numGen)
    for i in range(0,numGen):
        outF[i].write(keys[i][0].to_bytes(1,byteorder="big"))
        outF[i].write(keys[i][1].to_bytes(3,byteorder="big"))

    name = file[file.rfind("/")+1:len(file)] + "*"
    for ch in name:
        keys = encode(ord(ch),numReq,numGen)
        for i in range(0,numGen):
            outF[i].write(keys[i][0].to_bytes(1,byteorder="big"))
            outF[i].write(keys[i][1].to_bytes(3,byteorder="big"))

    while f.tell() < length:
        keys = encode(int.from_bytes(f.read(1),byteorder="big"),numReq,numGen)
        for i in range(0,numGen):
            outF[i].write(keys[i][0].to_bytes(1,byteorder="big"))
            outF[i].write(keys[i][1].to_bytes(3,byteorder="big"))
    f.close()
    for o in outF:
        o.close()

    print("Done!")


def decodeFile(outPath,keyPath):

    keyF = []

    files = os.listdir(keyPath)
    for f in files:
        if f[-4:len(f)] == ".shm":
            keyF += [open(keyPath+"/"+f,mode="rb")]

    if len(keyF) == 0:
        print("Error: No keys in "+keyPath)
        return
    
    numKeys = 0
    for i in range(2,len(keyF)+1):
        key = []
        for j in range(0,i):
            keyF[j].seek(0,0)
            x = keyF[j].read(1)
            y = keyF[j].read(3)
            key += [(int.from_bytes(x,byteorder="big"),int.from_bytes(y,byteorder="big"))]
        if decode(i,key) == int(code,base=2):
            numKeys = i
            break

    print("Using "+str(numKeys)+" keys...")

    for k in keyF:
        k.seek(4,0)

    c = ""
    name = ""
    while True:
        key = []
        for k in keyF:
            x = k.read(1)
            y = k.read(3)
            key += [(int.from_bytes(x,byteorder="big"),int.from_bytes(y,byteorder="big"))]
        c = chr(decode(numKeys,key))
        if c == "*":
            break
        else:
            name += c

    while os.path.exists(outPath+"/"+name):
        if name.find(".") == -1:
            name = name + "_"
        else:
            name = name[0:name.find(".")] + "_" + name[name.find("."):len(name)]
    o = open(outPath+"/"+name,mode="wb")

    done = False
    while True:
        key = []
        for k in keyF:
            x = k.read(1)
            if x == b"":
                done = True
                break
            y = k.read(3)
            key += [(int.from_bytes(x,byteorder="big"),int.from_bytes(y,byteorder="big"))]
        if not(done):
            o.write(int.to_bytes(decode(numKeys,key),length=1,byteorder="big"))
        else:
            break

    o.close()
    for f in keyF:
        f.close()
    print("Done!")


global code
code = b"11010011"

parser = argparse.ArgumentParser(add_help=False)
g = parser.add_mutually_exclusive_group()
g.add_argument("--encode",nargs=3,metavar=("numReq","numGen","filePath"),help="Encode 'filePath' into 'numGen' keys, needing 'numReq' keys to decode it")
g.add_argument("--decode",nargs=1,metavar=("keyPath"),help="Use keys in 'keyPath' to try to decode a file")
args = parser.parse_args()

if args.encode != None:
    numReq = int(args.encode[0])
    numGen = int(args.encode[1])
    file = str(args.encode[2])
    encodeFile(numReq,numGen,file)
elif args.decode != None:
    outPath = str(args.decode[0])
    keyPath = str(args.decode[0])
    decodeFile(outPath,keyPath)
else:
    parser.print_help()

parser.exit()





