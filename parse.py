import struct

def read32(f):
    return struct.unpack("<I", f.read(4))[0]

def parse_packet(f):
    pack={}
    pack["time"]=read32(f)
    pack["x"]=read32(f)
    pack["y"]=read32(f)
    pack["strength"]=read32(f)
    pack["longitude"]=read32(f)
    pack["latitude"]=read32(f)
    return pack


def parse(f):
    namelen=read32(f)
    name=f.read(namelen)
    datelen=read32(f)
    date=f.read(datelen)
    notelen=read32(f)
    note=f.read(notelen)
    reserved=f.read(16)
    packlen=read32(f)
    packets=[]
    for i in xrange(packlen):
        packets.append(parse_packet(f))
    return {
        "name": name,
        "date": date,
        "note": note,
        "packets": packets
    }

if __name__=="__main__":
    import sys, json
    name=sys.argv[1]
    f=open(name, "rb")
    p=parse(f)
    print json.dumps(p, indent=4)
