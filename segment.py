

def bounding_box(packets):
    minx=packets[0]["x"]
    maxx=minx
    miny=packets[0]["y"]
    maxy=miny
    for pack in packets:
        if pack["x"]<minx: minx=pack["x"]
        if pack["x"]>maxx: maxx=pack["x"]
        if pack["y"]<miny: miny=pack["y"]
        if pack["y"]>maxy: maxy=pack["y"]
    return (minx, miny, maxx, maxy)

def segments_cross(l1, r1, l2, r2, eps=0):
    if l1>r2+eps: return False
    if l2>r1+eps: return False
    return True

def bbox_similar(bb1, bb2):
    return segments_cross(bb1[0], bb1[2], bb2[0], bb2[2]
            ) and segments_cross(bb1[1], bb1[3], bb2[1], bb2[3])

def segmentate(packets, delta=250, minsamples=25):
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
    bboxes=[]
    for r in groups:
        bboxes.append(bounding_box(r))
    similarity=range(len(bboxes))
    for i in range(len(bboxes)):
        for j in range(len(bboxes)):
            if bbox_similar(bboxes[i], bboxes[j]):
                similarity[j]=similarity[i]
    result=[[] for i in range(len(bboxes))]
    for i in range(len(bboxes)):
        for p in groups[i]:
            result[similarity[i]].append(p)

    ret=[]
    for g in result:
        if len(g)>minsamples:
            ret.append(g)
    return ret

if __name__=="__main__":
    import parse, sys, show

    p=parse.parse(open(sys.argv[1], "rb"))
    segs=segmentate(p["packets"])
    show.draw(p, w=1500, h=1000, color_mode="speed", maxt=1e9, vec_len=0, segs=segs)
