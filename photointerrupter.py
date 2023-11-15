from build123d import *
from ocp_vscode import *
from defs import *
## GP1S094HCZ0F

with BuildPart() as gp1:
    with BuildSketch(Plane.front) as sk1:
        Rectangle(5.5,4.8,align=CENMIN)
        with Locations((0,1.8)):
            Rectangle(3,3,align=CENMIN,mode=Mode.SUBTRACT)
        chamfer(sk1.edges().group_by(Axis.Y)[1].faces(),length=0.3)
    extrude(amount=20.6)

