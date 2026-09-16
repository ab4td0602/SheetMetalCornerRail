# MIT License
#
# Copyright (c) 2026 James E. Smith,  Smith Machine Control LLC 
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import FreeCAD as App, FreeCADGui, Part, Mesh, math, os

doc_name = "Coupler_70mm_10mmFlat_PrintReady"
App.closeDocument(doc_name) if App.getDocument(doc_name) else None
doc = App.newDocument(doc_name)

COUPLER_LENGTH      = 74.0
CORE_SIZE           = 9.80   # Rail's inner core boundary
MAX_ENVELOPE        = 18.0   # 18mm under-cover limit
REDUCTION_SZ        = 0.0    # Reduce body width by 1.5mm (~0.060")
FLAT_WIDTH_BOTTOM   = 4.0    # Bottom landing for inner core slot fit
FLAT_WIDTH_TOP      = 10.0   # Expanded to 10mm flat landing for 5mm screw head
FIT_TOLERANCE       = 0.15
CLEARANCE_HOLE_DIA  = 3.2
CLEARANCE_HOLE_DIA_5M = 5.2
COUNTER_BORE_5MM = 9.6
COUNTER_BORE_DEPTH_5MM = 4.5

# Print/Slicing Parameters
WARP_FACTOR         = 1.2
DRAFT_ANGLE_DEG     = 0.0

c_outer      = MAX_ENVELOPE - FIT_TOLERANCE
reduced_outer = c_outer - REDUCTION_SZ
boundary_max = c_outer / 2.0  # Original outer edge/face boundary reference=

bottom_offset = FLAT_WIDTH_BOTTOM / math.sqrt(2.0)
top_offset    = FLAT_WIDTH_TOP / math.sqrt(2.0)

p_bottom_start = App.Vector(0, FLAT_WIDTH_BOTTOM / 2.0, 0)
p_bottom_end   = App.Vector(0, 0, FLAT_WIDTH_BOTTOM / 2.0)
p_top_start    = App.Vector(0, reduced_outer - top_offset, reduced_outer)
p_top_end      = App.Vector(0, reduced_outer, reduced_outer - top_offset)

pts = [
    p_bottom_start, App.Vector(0, reduced_outer, 0),
    p_top_end, p_top_start, App.Vector(0, 0, reduced_outer),
    p_bottom_end, p_bottom_start
]

shift_y = boundary_max
shift_z = boundary_max
shifted_pts = [App.Vector(p.x, p.y - shift_y, p.z - shift_z) for p in pts]

edges = [Part.makeLine(shifted_pts[i], shifted_pts[i+1]) for i in range(len(shifted_pts)-1)]
profile_wire = Part.Wire(edges)
profile_face = Part.Face(profile_wire)
coupler_solid = profile_face.extrude(App.Vector(COUPLER_LENGTH, 0, 0))

# Centered face coordinates for cutting tools
face_center_y = boundary_max - (bottom_offset / 2.0)
face_center_z = boundary_max - (bottom_offset / 2.0)
face_center_cb_y = top_offset
face_center_cb_z = top_offset 

# 45-degree through holes at stations 18.0 and 52.0 (adjusted for reduced profile)
drill_dir = App.Vector(0, -1, -1).normalize()
for cx in [ 7.0, 19.5, 54.5, 67.0 ]:
    start_pt = App.Vector(cx, face_center_y + 2.0, face_center_z + 2.0)
    thru = Part.makeCylinder(CLEARANCE_HOLE_DIA_5M / 2.0, 50.0, start_pt, drill_dir)
    coupler_solid = coupler_solid.cut(thru)

# 45 degree counter bores for 5mm screw  
for cx in [ 7.0, 19.5, 54.5, 67.0 ]:
    start_pt1 = App.Vector(cx, face_center_cb_y, face_center_cb_z)
    counter_bore = Part.makeCylinder(COUNTER_BORE_5MM / 2 , COUNTER_BORE_DEPTH_5MM + (FLAT_WIDTH_TOP / 2 ), start_pt1, App.Vector(0, -1, -1) )
    coupler_solid = coupler_solid.cut(counter_bore)

# Primary fastener stations (10.0 and 60.0 mm) on Top and Front faces (Coversheet mounting)
PRIMARY_STATIONS = [12.0, 62.0]
for cx in PRIMARY_STATIONS:
     top_hole = Part.makeCylinder(2.7 / 2.0, 12, App.Vector(cx, boundary_max -12 , boundary_max ), App.Vector(0, 0, -1))
     front_hole = Part.makeCylinder(2.7 / 2.0, 12.0, App.Vector(cx, boundary_max, boundary_max - 12), App.Vector(0, -1, 0))
     coupler_solid = coupler_solid.cut(top_hole).cut(front_hole)

# Secondary fastener stations (13.0, 23.0, 47.0, and 57.0 mm) 
NEW_STATIONS = [ 25.0, 49.0]
offset_from_edge = 4.5
target_coordinate_opposite = boundary_max - offset_from_edge

for cx in NEW_STATIONS:
    bottom_hole_new = Part.makeCylinder(2.7 / 2.0, 8.0, App.Vector(cx, target_coordinate_opposite, -boundary_max), App.Vector(0, 0, 1))
    rear_hole_new = Part.makeCylinder(2.7 / 2.0, 8.0, App.Vector(cx, -boundary_max, target_coordinate_opposite), App.Vector(0, 1, 0))
    
    coupler_solid = coupler_solid.cut(bottom_hole_new).cut(rear_hole_new)

obj = doc.addObject("Part::Feature", "Coupler_74mm_10mmFlat_PrintReady")
obj.Shape = coupler_solid
doc.recompute()

# Styling view properties
if App.GuiUp:
    gui = FreeCADGui.getDocument(doc.Name).getObject(obj.Name)
    gui.ShapeColor = (0.1, 0.6, 0.8)
    gui.LineColor = (0.0, 0.0, 0.0)
    gui.LineWidth = 1.8
    gui.DisplayMode = "Flat Lines"
    gui.Transparency = 50

# Export STL mesh
stl_path = os.path.join(os.path.expanduser("~"), "Coupler_74mm_10mmFlat_PrintReady.stl")
Mesh.Mesh(obj.Shape.tessellate(0.01)).write(stl_path)

# Force-refresh viewport rendering via temporary save/reopen
temp_fcstd = os.path.join(os.path.expanduser("~"), "Coupler_74mm_Temp.FCStd")
doc.saveAs(temp_fcstd)
App.closeDocument(doc.Name)
App.openDocument(temp_fcstd)

print(f"SUCCESS: 70mm Coupler generated with 1.5mm width reduction and 10mm top flat. STL exported.")