# %%

from build123d import *
from ocp_vscode import *
from defs import *
# from photointerrupter import * // fdjkjfdk f
import copy
import math
# %%

with BuildPart() as gp1:
    with BuildSketch(Plane.front) as sk1:
        Rectangle(5.5,4.8,align=CENMIN)
        with Locations((0,1.8)):
            Rectangle(3,3,align=CENMIN,mode=Mode.SUBTRACT)
        chamfer(sk1.edges().group_by(Axis.Y)[1].vertices(),length=0.3)
    extrude(amount=2.6)
    chamfer(gp1.edges().group_by(Axis.Z)[-1].group_by(Axis.Y)[0],length=0.4)
    with Locations((0,-2.05)):
        Cylinder(0.5,0.8,align=CENCENMAX)
    chamfer(gp1.edges().group_by(Axis.Z)[0],0.2)
show(gp1)
# %%
def keycap(w=18,r=40):
    with BuildPart() as pt:
        with BuildSketch(Plane.top) as sk1:
            RectangleRounded(w,w,2)
        with BuildSketch(Plane.top.offset(5)):
            RectangleRounded(w-2,w-2,3)
        loft()
        with Locations((0,0,r+2.5)):
            Sphere(r,mode=Mode.SUBTRACT)
        fillet(pt.edges().group_by(Axis.Z)[-1],1)
    return pt.part
show(keycap())
# %%
show(make_face(Polyline((0,0),(0,1),(1,0))))
# %%
def flexure(l,h,r,flat_corner=False):
    l, h = l/2, h/2
    lines = Line((0,h+r),(0,0)) + TangentArc((0,r+h),(r,h),tangent=(0,-1)) + Line((r,h),(l,h))
    p = Plane.right.offset(l)
    profile = lines + mirror(lines) + mirror(lines,about=p) + (Polyline((l,-h),(2*l,-h),(2*l,0)) if flat_corner else mirror(mirror(lines, about=p)))
    sketch = make_face(profile)
    return sketch

show(flexure(10,1,1,flat_corner=True))

# %%
def arm1():
    sk1 = Plane.right*(flexure(2,0.4,0.5) + Pos((2,0))*Rectangle(25,4,align=MINCEN) + Pos((27,0))*flexure(2,0.4,0.5))
    pt1 = extrude(sk1,amount=8)

    pt2 = extrude(Plane.left*Trapezoid(2,10,84,90,align=MINMIN),amount=-9)
    pt3 = extrude(Plane.left*Trapezoid(4,12,96,align=MINMIN),amount=-8)
    pt4 = extrude(Plane.left*Trapezoid(3,10,90,84,align=MINMIN),amount=-9)
    bb = Rotation(about_x=6)*(Pos(0.5,0,2)*pt1 + Pos(0.5,0,8)*pt1) + pt2 + Pos((0.5,34.15,2.5))*pt3
    return Pos((0,2,0))*bb

show(arm1())
# %%
def keycut(l=6,w=3,h=6,cut=False):
    if cut:
        l += 0.3
        w += 0.3
        h += 0.3
    with BuildPart() as pt:
        with BuildSketch(Plane.top):
            Trapezoid(l,w,70,rotation=-90,align=CENMAX)
        with BuildSketch(Plane.top.offset(-h)):
            Trapezoid(l-1,w,70,rotation=-90,align=CENMAX)
        loft()
    return pt.part
show(keycut())
# %%
def base1():
    h=7
    l = 19
    w = 19
    ln = 3
    wn = 5
    wall = 2
    base_h = 2
    u = Box(l,w,h+base_h,align=MINMINMIN) - Pos((wall,0,base_h))*Box(l-2*wall,w,base_h+h,align=MINMINMIN) - Pos((wall,10,h+base_h))*keycut(cut=True)
    mu = mirror(u,about=Plane.right.offset(w/2))
    col = u + Pos((0,19,0))*mu + Pos((0,19*2,0))*u
    grid = Part() + GridLocations(19,0,wn,1,align=MINMINMIN)*col
    surround = extrude(Rectangle(w*wn+2*wall,l*ln + l + 2*wall,align=MINMIN) - Pos((wall,wall))*Rectangle(w*wn,l*ln+l,align=MINMIN),amount=h+base_h)
    return Pos((wall,wall,0))*grid + surround

show(base1()+gp1.part)
# %%
def arm2(l,h,w,fl,fh,gap):
    shoulder = 8
    wrist = 3
    gap_side = 0.5
    gap_front = 1
    bar_l = l -2*fl - shoulder - wrist - gap_front
    f = flexure(fl,fh,fh,flat_corner=True)
    a = Plane.right*(f + Pos((fl,-fh/2))*Rectangle(bar_l,h+fh/2,align=MINMIN) + Pos((bar_l +2*fl,0))*mirror(f,about=Plane.right))
    b = a + Pos((0,0,2*h+gap))*mirror(a, about=Plane.bottom)
    # b = Plane.right*(flexure(l,0.5,.5) + Pos((0,2*h))*flexure(l,0.5,.5))
    c = extrude(b,amount=w-1)
    th = h*2 + gap*2 + fh*3
    trap_b = extrude(Plane.right*Trapezoid(shoulder,th,84,84,align=MINMIN),amount=w)
    trap_k = Rotation(about_x=-6)*(extrude(Plane.right*Trapezoid(wrist,th,96,96,align=MINMAX),amount=w-1) +Pos((7.5,0,0))*keycap())
    arm = trap_b + Pos((1,shoulder))*Rotation(about_x=6)*(Pos((0,0,1))*c + Pos((0,bar_l+2*fl,th))*trap_k)

    return arm
r = arm2(38,3,7,2,0.4,.5)
show(r + Pos((0,38,0))*r)
r.export_stl('arm.stl')

# %% 

a = arm2(30,4,9,2,0.4,1.5,'half')
b = Part() + copy.copy(a) + Pos((0,20))*mirror(copy.copy(a),about=Plane.right)
c = Part() + GridLocations(11,40,10,2)*copy.copy(a)
show(b)
# b2 = arm1() +  Pos((0,-2,0))*Box(.5,40,10,align=MAXMINMIN) + Pos((9.5,-2,0))*Box(.5,40,10,align=MAXMINMIN) + Pos((0,38,0))*arm1()
# b2 = Pos((0.5,2,0))*b2
# bl = b2 + Pos((0.5,20,14.5))*Box(19,19,2,align=MINMINMIN)
# br = b2 + Pos((-9.5,20,14.5))*Box(19,19,2,align=MINMINMIN)

# rl = Box(10,20,10,align=MINMINMIN) + Pos((0,20,0))*bl + Pos((0,60,0))*bl + Pos((0,100,0))*bl 
# rr = Pos((10,0,0))*br + Pos((10,40,0))*br + Pos((10,80,0))*br + Pos((10,120,0))*Box(10,20,10,align=MINMINMIN)
# r1 = b2+ Pos((0,40,0))*b2 + Pos((-.5,78,0))*Box(10,20,10,align=MINMINMIN)
# r2 = Pos((0,20,0))*b2+ Pos((0,60,0))*b2 + Pos((-.5,-2,0))*Box(10,20,10,align=MINMINMIN)
# rc = r1 + Pos((10,0,0))*r2


# show(Part() + Locations((0,0,0),(20,0,0),(40,0,0),(60,0,0))*(rl + rr))

# show(rc + Pos((20,0,0))*rc + Pos((40,0,0))*rc + Pos((60,0,0))*rc + Pos((10,10,10))*keys )
# %%
gap = 0.5
b_w = 2
b_h = 8
b_t = 6
b_gap = 0.5
b_f = flexure(20-2*b_w -1,0.4,0.5)
b = extrude(Plane.right*(Rectangle(b_w,b_h,align=MINMIN) + Pos((b_w,1))*b_f + Pos((b_w,b_h-1))*b_f+ Pos((20-b_w-1))*Rectangle(b_w,b_h,align=MINMIN)),amount=b_t)
show(b)

# c = extrude(Plane.top*(Rectangle(10,24,align=MINMIN)-Pos((2,2))*Rectangle(8,20,align=MINMIN)),amount=10)
c = Box(2,20,10,align=MINMINMIN)
d = c + Pos((2,0.5,2))*(Box(gap,b_w,b_h,align=MINMINMIN) + Pos((gap))*(b + Pos((gap+b_t))*(b) + Pos((b_t,19))*Box(gap,b_w,b_h,align=MINMAXMIN)))
pts = [(0,0),(10,10),(0,10)]
tri = Pos((2+gap*2 + 2*b_t,.5 + b_w,2))*extrude(Plane.right*Polygon(*pts,align=MINMIN),amount=-0.5)
e = d + Pos((3+2*b_t,.5,2))*(Box(1,2,b_h,align=MINMINMIN) + Pos((0,19,0))*Box(1,2,b_h,align=MINMAXMIN)) + Pos((0.5,0.5,12))*Box(9.5,19,1,align=MINMINMIN) + Pos((10,.5,10))*Box(b_t+1,b_w,2,align=MAXMINMIN) + tri
f = e + mirror(e,about=Plane.right.offset(10))
g = Part() + GridLocations(20,20,3,2,align=MINMINMIN)*f + extrude(Pos((-2,-2))*Rectangle(20*3+4,20*2+4,align=MINMIN) - Rectangle(20*3,20*2,align=MINMIN),amount=10)
show(e)
# f.export_stl('b2.stl')


# %%
def parallel(l,w,h,fh,d=0,s=2,filled=False,fl=1,double=False):
    gap = 0.5
    if double:
        w = (w - gap)/2
        d = d/2
    with BuildPart() as pt:
        with BuildSketch(Plane.right) as sk:
            Rectangle(s,h,align=MINMIN)

            rot = math.atan2(d,l-2*s)
            l = l*math.cos(rot)
            rotd = rot*180/math.pi
            with Locations((l,d)):
                Rectangle(s,h,align=MAXMIN)
            v = sk.vertices()

            with Locations((l/2,fh*1.5+d/2),(l/2,h+d/2-fh*1.5)):
                Rectangle(l-s,fh,rotation=rotd)
            
            if filled:
                with Locations((l/2,fh*1.5+d/2)):
                    Trapezoid(l-2*s-2*fl,h/2-fh*2,90-rotd,align=CENMIN,rotation=rotd)
                with Locations((l/2,h+d/2-fh*1.5)):
                    Trapezoid(l-2*s-2*fl,h/2-fh*2,90-rotd,align=CENMIN,rotation=rotd+180)




            fillet([x for x in sk.vertices() if x not in v],fh/2)
        
        extrude(amount=w)
        if double:
            add(Pos((2*w+gap,l,d))*Rotation(about_z=180)*pt.part)
            with Locations((w,l,d)):
                Box(gap,s,h,align=MINMAXMIN)




    
    return pt

show(parallel(20,14,8,0.4,d=4,filled=True,double=True,s=3))

# %%
def doubleflex(ft=0.5,fl=2,d=3,filled=True,iw=14,s=3):
    h = 7
    w = 19
    l = 19
    with BuildPart() as pt:
        Box(2,l,h,align=MINMINMIN)
        with Locations((2,0.5,0)):
            Box(.5,s,h,align=MINMINMIN)
        with Locations((2.5,0.5,0)):
            add(parallel(l-1,iw,h,ft,fl=fl,d=d,double=True,filled=filled,s=s))
        with Locations((17,0,0)):
            Box(2,l,h,align=MINMINMIN)
        with Locations((9.5,8.5,h+d)):
            add(keycap())

    return pt

show(doubleflex())

# %%


with BuildPart() as pt:
    # unfilled
    add(doubleflex(filled=False,ft=0.3))
    with Locations((0,19,0)):
        add(doubleflex(filled=False,iw=10))
    with Locations((0,19*2,0)):
        add(doubleflex(filled=False))
    # fl=2
    with Locations((19,0,0)):
        add(doubleflex(ft=0.3))
    with Locations((19,19,0)):
        add(doubleflex())
    with Locations((19,19*2,0)):
        add(doubleflex(ft=0.7))
    # fl=1
    with Locations((19*2,0,0)):
        add(doubleflex(ft=0.3,fl=1))
    with Locations((19*2,19,0)):
        add(doubleflex(fl=1))
    with Locations((19*2,19*2,0)):
        add(doubleflex(fl=1,ft=0.4,iw=10))
    # filler
    with Locations((19*3,0,0),(19*3,19,0),(19*3,19*2,0)):
        add(doubleflex(d=4))
    with Locations((19*4,0,0),(19*4,19,0),(19*4,19*2,0)):
        add(doubleflex(d=2))
    

    with Locations((0,-4,0),(0,19*3,0)):
        Box(19*5,4,7,align=MINMINMIN)

show(pt)
pt.part.export_stl('double.stl')
# %%
