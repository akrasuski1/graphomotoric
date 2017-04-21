import parse, segment
from PIL import Image, ImageDraw
import math, colorsys

def draw(p, w=1500, h=1000, color_mode="speed", maxt=1e9, vec_len=40, segs=[]):
    packets=p["packets"]
    im=Image.new("RGB", (w, h), (255, 255, 255))
    draw=ImageDraw.Draw(im)

    maxx=20000.0
    maxy=16000.0
    maxs=1024.0
    maxv=5.0
    scale=16.0

    def xy_to_img(x, y):
        return x/scale, y/scale

    def get_color(intensity):
        color=colorsys.hsv_to_rgb(intensity/2.0, 1, 1)
        return (int(color[0]*255), int(color[1]*255), int(color[2]*255))

    last=(0,0,0,0)
    last_v=0
    for num, pack in enumerate(packets):
        x, y, s = pack["x"], pack["y"], pack["strength"]
        lat, lon, t = pack["latitude"], pack["longitude"], pack["time"]
        if t>maxt:
            break
        lx, ly = last[0], last[1]
        dx = x-lx
        dy = y-ly
        dt = t-last[3]

        last = x, y, s, t

        xi, yi = xy_to_img(x, y)
        lxi, lyi = xy_to_img(lx, ly)
        if s==0:
            # No touch. Skip the sample.
            continue
        else:
            if color_mode=="strength":
                color=get_color(1-s/maxs)
            elif color_mode=="speed":
                d=(dx*dx+dy*dy)**0.5
                if dt==0:
                    dt=1
                v=d/dt
                v=v*0.1+last_v*0.9 # Exponential smoothing.
                color=get_color(v/maxv)
                last_v=v;

        draw.line([lxi, lyi, xi, yi], color, width=2)
        if vec_len and num%10==0:
            lat=lat/10./180*math.pi
            lon=lon/10./180*math.pi
            length=vec_len*math.cos(lat)
            cx=length*math.cos(lon)
            cy=length*math.sin(lon)
            draw.line([xi, yi, xi+cx, yi+cy], (0, 0, 255), width=1)

    # TODO: segmentation.
    def dr(a, b, c, d, col=(0, 0, 0)):
        x1, y1 = xy_to_img(a, b)
        x2, y2 = xy_to_img(c, d)
        draw.rectangle([x1, y1, x2, y2], outline=col)

    print len(segs), "segs"
    for seg in segs:
        bbox=segment.bounding_box(seg)
        dr(bbox[0], bbox[1], bbox[2], bbox[3])

    im.show()

if __name__=="__main__":
    import sys
    name=sys.argv[1]
    f=open(name, "rb")
    p=parse.parse(f)
    draw(p)
