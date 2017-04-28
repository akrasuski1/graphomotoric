

def bounding_box(packets):
    minx=packets[0]["x"]
    maxx=minx
    miny=packets[0]["y"]
    maxy=miny
    for pack in packets:
        if pack["strength"]==0: continue
        if pack["x"]<minx: minx=pack["x"]
        if pack["x"]>maxx: maxx=pack["x"]
        if pack["y"]<miny: miny=pack["y"]
        if pack["y"]>maxy: maxy=pack["y"]
    return (minx, miny, maxx, maxy)

def segments_cross(l1, r1, l2, r2):
    if l1>r2: return False
    if l2>r1: return False
    return True

def bbox_overlap(bb1, bb2):
    return segments_cross(bb1[0], bb1[2], bb2[0], bb2[2]
            ) and segments_cross(bb1[1], bb1[3], bb2[1], bb2[3])

def segmentate(packets, delta=250, minsamples=25):
    # Group drawn segments by distance to last sample (short gap is OK).
    groups=[]
    last_packet={"x":-1e9, "y":-1e9}
    for pack in packets:
        s=pack["strength"]
        if s==0:
            continue
        else:
            lx=last_packet["x"]
            ly=last_packet["y"]
            x=pack["x"]
            y=pack["y"]
            dx=lx-x
            dy=ly-y
            d=(dx*dx+dy*dy)**0.5
            if d<delta:
                groups[-1].append(pack)
            else:
                groups.append([pack])
            last_packet=pack
    # The expected locations of the segments.
    expected={
            "ZIGZAG":     (2500,  2000, 4500,  12300),
            "CIRCLERIGHT":(6000,  3000, 8000,  7000),
            "CIRCLELEFT": (6000,  8500, 8000,  12000),
            "FIRSTLINE":  (9200,  2000, 10000, 13000),
            "SECONDLINE": (10400, 2000, 11000, 13000),
            "BROKENLINE": (11700, 2000, 12700, 13000),
            "SPIRALOUT":  (13500, 2000, 18000, 6500),
            "SPIRALIN":   (13500, 8200, 18000, 13000),
    }
    # Calculate bounding boxes of the segments.
    bboxes=[]
    for i, r in enumerate(groups):
        bboxes.append(bounding_box(r))
    #for e in expected:
    #    bboxes[e]=expected[e]
    # Calculate which bounding boxes overlap.
    similarity=range(len(bboxes))
    for i in range(len(bboxes)):
        for j in range(i+1, len(bboxes)):
            if bbox_overlap(bboxes[i], bboxes[j]):
                similarity[j]=similarity[i]
    # Merge those that overlap.
    result={}
    for i in range(len(bboxes)):
        if similarity[i] not in result:
            result[similarity[i]]=[]
        result[similarity[i]]+=groups[i]
    # Filter out very short segments.
    ret=[]
    for g in result:
        r=result[g]
        if len(r)>minsamples:
            ret.append(r)
    return ret

if __name__=="__main__":
    import parse, sys, show

    p=parse.parse(open(sys.argv[1], "rb"))
    segs=segmentate(p["packets"])
    show.draw(p, w=1500, h=1000, color_mode="speed", maxt=1e9, vec_len=0, segs=segs)
