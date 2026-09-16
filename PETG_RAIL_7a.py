# ----------------------------------------------------------------------------
# Parametric Corner Rail System (Inward-Pivoting Split Wings with Aligned Reliefs)
# Copyright (c) 2026 - MIT License
# ----------------------------------------------------------------------------
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

import FreeCAD as App
import Part
import Mesh
import math
import os
import PySide2.QtWidgets as QtWidgets
from collections import namedtuple 

doc_name = "PETG_Corner_Rail_WarpSplit"
App.closeDocument(doc_name) if App.getDocument(doc_name) else None
doc = App.newDocument(doc_name)

RailConfig = namedtuple('RailConfig', [
    'upper_slot_width',  
    'lower_slot_width',  
    'slot_depth',        
    'rail_length',       
    'coupler_length',    
    'screw_dia',         
    'screw_angle'        
])

MaterialSpec = namedtuple(
    "MaterialSpec", ["thickness", "slot_width", "description"]
)

MATERIAL_SPECS = { 
    "16ga_aluminum": MaterialSpec(1.29, 1.45, "Lightweight aluminum covers"),
    "12ga_aluminum": MaterialSpec(2.05, 2.25, "Heavy-duty aluminum cover sheet; excellent thermal transfer"),
    "12ga_steel":  MaterialSpec(2.66, 2.85, "Heavy structural steel frame/chassis; maximum rigidity"),
    "14ga_aluminum": MaterialSpec(1.63, 1.80, "Medium aluminum enclosure walls"),
    "14ga_steel": MaterialSpec(1.90, 2.10, "Standard steel paneling"),
    "16ga_steel": MaterialSpec(1.52, 1.70, "Standard thin-gauge steel (~0.060 in)"),
    "18ga_aluminum": MaterialSpec(1.02, 1.20, "Thin aluminum trim or interior shrouds"),
    "18ga_steel": MaterialSpec(1.21, 1.38, "Lightweight steel brackets (~0.048 in)"),
    "metric_1.5mm": MaterialSpec(1.50, 1.68, "Standard 1.5mm metric sheet stock"),
    "metric_2.0mm": MaterialSpec(2.00, 2.18, "Standard 2.0mm metric plate stock"),
    "plate_1_8in": MaterialSpec(3.18, 3.35, "1/8 inch heavy structural plate"),
    "frp_09": MaterialSpec(2.25, 2.40, "0.09 inch fiberglass (FRP) structural panels; high electrical insulation"),
}

slot_width_list = list(MATERIAL_SPECS.keys()) 

input_len, ok = QtWidgets.QInputDialog.getDouble(
    None, "Custom Rail Length", "Enter target rail length (mm):", 250.0, 110.0, 500.0, 2
)
RAIL_LENGTH = input_len if ok else 250.0

dialog_lower = QtWidgets.QInputDialog()
dialog_lower.setWindowTitle("Lower Rail Setup")
dialog_lower.setLabelText("Select sheet gauge for lower slots:")
dialog_lower.setComboBoxItems(slot_width_list)
dialog_lower.setComboBoxEditable(False)
dialog_lower.resize(350, 150)

ok_lower = dialog_lower.exec_()
selected_text_lower = dialog_lower.textValue() if ok_lower else "16ga_aluminum"
ACTIVE_MATERIAL = selected_text_lower

current_mat_lower = MATERIAL_SPECS.get(ACTIVE_MATERIAL, MATERIAL_SPECS["16ga_aluminum"])
MATERIAL_THICKNESS_LOWER = current_mat_lower.thickness
DYNAMIC_SLOT_WIDTH_LOWER = current_mat_lower.slot_width
  
dialog_upper = QtWidgets.QInputDialog()
dialog_upper.setWindowTitle("Upper Rail Setup")
dialog_upper.setLabelText("Select sheet gauge for upper slots:")
dialog_upper.setComboBoxItems(slot_width_list)
dialog_upper.setComboBoxEditable(False)
dialog_upper.resize(350, 150)

ok_upper = dialog_upper.exec_()
selected_text_upper = dialog_upper.textValue() if ok_upper else "16ga_aluminum"
ACTIVE_MATERIAL1 = selected_text_upper

current_mat_upper = MATERIAL_SPECS.get(ACTIVE_MATERIAL1, MATERIAL_SPECS["16ga_aluminum"])
MATERIAL_THICKNESS_UPPER = current_mat_upper.thickness
DYNAMIC_SLOT_WIDTH_UPPER  = current_mat_upper.slot_width

RailConfig = namedtuple("RailConfig", ["height", "slot_depth"])

RAIL_CONFIGS = {
    "10mm": RailConfig(height=28.0, slot_depth=10.0),
    "16mm": RailConfig(height=34.0, slot_depth=16.0)
}

dialog_config = QtWidgets.QInputDialog()
dialog_config.setWindowTitle("Slot depth")
dialog_config.setLabelText("Select slot depth")
dialog_config.setComboBoxItems(list(RAIL_CONFIGS.keys()))
dialog_config.setComboBoxEditable(False)
dialog_config.resize(350, 150)

ok_config = dialog_config.exec()
selected_config_text = dialog_config.textValue() if ok_config else "10mm" 

config = RAIL_CONFIGS.get(selected_config_text, RAIL_CONFIGS["10mm"])

OUTER_DIM = config.height
SLOT_D = config.slot_depth

current_warp_factor, ok = QtWidgets.QInputDialog.getDouble(
    None, "Active WARP 0 - 10 degrees", "Enter target WARP degree correction (deg):", 0.0, 0.0, 10.01, 2
)
ACTIVE_WARP_DEGREE_FACTOR = current_warp_factor if ok else 0.0
HALF_WARP_DEG = ACTIVE_WARP_DEGREE_FACTOR / 2.0

DRAFT_ANGLE_DEG   = 0.0    
TOTAL_NOTCH_DEPTH = 0.50   
DRAFT_RAD         = math.radians(abs(DRAFT_ANGLE_DEG))
DRAFT_OFFSET      = OUTER_DIM * math.tan(DRAFT_RAD)

LOWER_WING_EXTENSION = (MATERIAL_THICKNESS_LOWER / 2.0) if ACTIVE_MATERIAL == "plate_1_8in" else max(0.0, DYNAMIC_SLOT_WIDTH_LOWER - 1.70)
UPPER_WING_EXTENSION = (MATERIAL_THICKNESS_UPPER / 2.0) if ACTIVE_MATERIAL1 == "plate_1_8in" else max(0.0, DYNAMIC_SLOT_WIDTH_UPPER - 1.70)

LOWER_OUTER_DIM      = OUTER_DIM + LOWER_WING_EXTENSION
UPPER_OUTER_DIM      = OUTER_DIM + UPPER_WING_EXTENSION

SLOT_W_UPPER      = DYNAMIC_SLOT_WIDTH_UPPER  
SLOT_W_LOWER      = DYNAMIC_SLOT_WIDTH_LOWER  
OUTER_WALL        = 3.5    
CORE_SIZE         = 11.0    
FLAT_WIDTH        = 8.0    

END_HOLE_DIAM     = 4.5
HOLE_DEPTH        = 15.0
END_TAP_Y         = 6.0     
END_TAP_Z         = 6.0     

HOLE_OFFSET         = 12.0
OUTER_CLEARANCE_DIA = 3.2
INNER_PILOT_DIA     = 2.7

WING_HOLE_POS_Y     = (LOWER_OUTER_DIM - SLOT_D) + 5.0  
WING_HOLE_POS_Z     = (UPPER_OUTER_DIM - SLOT_D) + 5.0  

side_hole_offsets_x = [HOLE_OFFSET, RAIL_LENGTH - HOLE_OFFSET]

DIAGONAL_HOLE_DIA = 4.6
DIAGONAL_DIR      = App.Vector(0, 1, 1)

diag_hole_stations_x = [
    17.5, 30.0, 52.5,
    (RAIL_LENGTH / 2.0) - 17.5,
    (RAIL_LENGTH / 2.0) + 17.5,
    RAIL_LENGTH - 52.5,
    RAIL_LENGTH - 30.0, 
    RAIL_LENGTH - 17.5
]

# ----------------------------------------------------------------------------
# 1. THREE-WAY SECTION PROFILE SETUP (YZ Plane)
# ----------------------------------------------------------------------------

# Lower Wing Profile (Pivots at y=4, z=0)
lower_wing_pts = [
    App.Vector(0, 4.0, 0.0),
    App.Vector(0, LOWER_OUTER_DIM - DRAFT_OFFSET, 0.0),
    App.Vector(0, LOWER_OUTER_DIM, OUTER_WALL),
    App.Vector(0, LOWER_OUTER_DIM - SLOT_D, OUTER_WALL),
    App.Vector(0, LOWER_OUTER_DIM - SLOT_D, OUTER_WALL + SLOT_W_LOWER),
    App.Vector(0, LOWER_OUTER_DIM, OUTER_WALL + SLOT_W_LOWER),
    App.Vector(0, LOWER_OUTER_DIM, CORE_SIZE),
    App.Vector(0, 15.0, CORE_SIZE),  
    App.Vector(0, 4.0, 0.0)
]
lower_wire = Part.Wire([Part.makeLine(lower_wing_pts[i], lower_wing_pts[i+1]) for i in range(len(lower_wing_pts)-1)])
lower_face = Part.Face(lower_wire)

# Upper Wing Profile (Pivots at y=0, z=4)
upper_wing_pts = [
    App.Vector(0, 0.0, 4.0),
    App.Vector(0, 0.0, UPPER_OUTER_DIM - DRAFT_OFFSET),
    App.Vector(0, OUTER_WALL, UPPER_OUTER_DIM),
    App.Vector(0, OUTER_WALL, UPPER_OUTER_DIM - SLOT_D),
    App.Vector(0, OUTER_WALL + SLOT_W_UPPER, UPPER_OUTER_DIM - SLOT_D),
    App.Vector(0, OUTER_WALL + SLOT_W_UPPER, UPPER_OUTER_DIM),
    App.Vector(0, CORE_SIZE, UPPER_OUTER_DIM),
    App.Vector(0, CORE_SIZE, 15.0),  
    App.Vector(0, 0.0, 4.0)
]
upper_wire = Part.Wire([Part.makeLine(upper_wing_pts[i], upper_wing_pts[i+1]) for i in range(len(upper_wing_pts)-1)])
upper_face = Part.Face(upper_wire)

# Middle Section Profile (Anchored to flat face and interfaces)
middle_pts = [
    App.Vector(0, 4.0, 0.0),
    App.Vector(0, 15.0, CORE_SIZE),
    App.Vector(0, CORE_SIZE + 0.8, CORE_SIZE),
    App.Vector(0, CORE_SIZE - TOTAL_NOTCH_DEPTH, CORE_SIZE - TOTAL_NOTCH_DEPTH),
    App.Vector(0, CORE_SIZE, CORE_SIZE + 0.8),
    App.Vector(0, CORE_SIZE, 15.0),
    App.Vector(0, 0.0, 4.0),
    App.Vector(0, 4.0, 0.0)
]
middle_wire = Part.Wire([Part.makeLine(middle_pts[i], middle_pts[i+1]) for i in range(len(middle_pts)-1)])
middle_face = Part.Face(middle_wire)

# Apply inward warp rotations around pivot points
pivot_lower = App.Vector(0, 4.0, 0.0)
pivot_upper = App.Vector(0, 0.0, 4.0)

lower_face.rotate(pivot_lower, App.Vector(1, 0, 0), HALF_WARP_DEG)
upper_face.rotate(pivot_upper, App.Vector(1, 0, 0), -HALF_WARP_DEG)

# Extrude sections along +X Axis
lower_solid = lower_face.extrude(App.Vector(RAIL_LENGTH, 0, 0))
upper_solid = upper_face.extrude(App.Vector(RAIL_LENGTH, 0, 0))
middle_solid = middle_face.extrude(App.Vector(RAIL_LENGTH, 0, 0))

# Fuse into a single solid
rail_solid = middle_solid.fuse([lower_solid, upper_solid])

# 2. Longitudinal End Holes
cyl_start = Part.makeCylinder(END_HOLE_DIAM / 2.0, HOLE_DEPTH, App.Vector(0, END_TAP_Y, END_TAP_Z), App.Vector(1, 0, 0))
cyl_end   = Part.makeCylinder(END_HOLE_DIAM / 2.0, HOLE_DEPTH, App.Vector(RAIL_LENGTH - HOLE_DEPTH, END_TAP_Y, END_TAP_Z), App.Vector(1, 0, 0))
rail_solid = rail_solid.cut(cyl_start).cut(cyl_end)

# 3. Drill Wing Fastener Holes
z_drill_dir = App.Vector(0, 0, 1)
y_drill_dir = App.Vector(0, 1, 0)

for x_pos in side_hole_offsets_x:
    y_clear = Part.makeCylinder(OUTER_CLEARANCE_DIA / 2.0, OUTER_WALL + 2.0, App.Vector(x_pos, WING_HOLE_POS_Y, -2.0), z_drill_dir)
    y_pilot = Part.makeCylinder(INNER_PILOT_DIA / 2.0, 3.5 + 4.0, App.Vector(x_pos, WING_HOLE_POS_Y, OUTER_WALL), z_drill_dir)
    z_clear = Part.makeCylinder(OUTER_CLEARANCE_DIA / 2.0, OUTER_WALL + 2.0, App.Vector(x_pos, -2.0, WING_HOLE_POS_Z), y_drill_dir)
    z_pilot = Part.makeCylinder(INNER_PILOT_DIA / 2.0, 3.5 + 4.0, App.Vector(x_pos, OUTER_WALL, WING_HOLE_POS_Z), y_drill_dir)
    rail_solid = rail_solid.cut(y_clear).cut(y_pilot).cut(z_clear).cut(z_pilot)

# 4. Drill 45-Degree Corner Holes
diag_max_dim = max(LOWER_OUTER_DIM, UPPER_OUTER_DIM)
diag_total_len = diag_max_dim * math.sqrt(2.0)
drill_length = diag_total_len - 5.0
invert_dir = DIAGONAL_DIR.normalize().negative() 

for x_pos in diag_hole_stations_x:
    diag_cyl = Part.makeCylinder(DIAGONAL_HOLE_DIA / 2.0, drill_length, App.Vector(x_pos, LOWER_OUTER_DIM, UPPER_OUTER_DIM), invert_dir)
    rail_solid = rail_solid.cut(diag_cyl)

# 5. Slot Stress-Relief Cylinders (Transformed with respective wing warp angles)
relief_radius_lower = SLOT_W_LOWER / 2.0
lower_relief_cyl = Part.makeCylinder(
    relief_radius_lower, 
    RAIL_LENGTH, 
    App.Vector(0, LOWER_OUTER_DIM - SLOT_D, OUTER_WALL + relief_radius_lower), 
    App.Vector(1, 0, 0)
)
lower_relief_cyl.rotate(pivot_lower, App.Vector(1, 0, 0), HALF_WARP_DEG)

relief_radius_upper = SLOT_W_UPPER / 2.0
upper_relief_cyl = Part.makeCylinder(
    relief_radius_upper, 
    RAIL_LENGTH, 
    App.Vector(0, OUTER_WALL + relief_radius_upper, UPPER_OUTER_DIM - SLOT_D), 
    App.Vector(1, 0, 0)
)
upper_relief_cyl.rotate(pivot_upper, App.Vector(1, 0, 0), -HALF_WARP_DEG)

rail_solid = rail_solid.cut(lower_relief_cyl).cut(upper_relief_cyl)

# ----------------------------------------------------------------------------
# 6. NATIVE PLACEMENT & EXPORT
# ----------------------------------------------------------------------------
rail_obj = doc.addObject("Part::Feature", f"Corner_Rail_{int(RAIL_LENGTH)}mm_warp_{ACTIVE_WARP_DEGREE_FACTOR}deg")
rail_obj.Shape = rail_solid
rail_obj.Placement = App.Placement()  
doc.recompute()

if App.GuiUp:
    gui_obj = doc.getObject(rail_obj.Name).ViewObject
    gui_obj.ShapeColor   = (0.0, 0.4, 0.8)
    gui_obj.Transparency = 60
    gui_obj.DisplayMode  = "Shaded"

export_path = os.path.join(os.path.expanduser("~"), f"Corner_Rail_{int(RAIL_LENGTH)}mm_warp_{ACTIVE_WARP_DEGREE_FACTOR}deg.stl")
Mesh.export([rail_obj], export_path)

App.Console.PrintMessage(f"SUCCESS: Rail STL exported to '{export_path}'\n")