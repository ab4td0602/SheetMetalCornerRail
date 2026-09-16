# SheetMetalCornerRail
I have python scripts for FreeCAD that will generate FreeCAD drawings for creating  Corner Rails for sheet material.

The rail has two wings which are at right angles.  The wings are 11mm wide. The wings are 28mm from the top of the wing to the 
corner with a slot depth of 10 mm.  Or if you select 16mm slot depth the wings are 34mm from the top of the wing to the corner.

The part can be used for extruding metal or plastic, but was designed primarily for 3d printing PETG or PETG-CF corner rails.  
The rails have an upper and lower rail slot width size which can be selected separately depending on the type of material being 
used.   This runs from 18ga aluminum, 16ga aluminum, 14ga, aluminum, 12ga aluminum, 16ga steel, 14ga steel, 12ga steel,  1.5 mm, 
2.0mm,  .090 FRP,  and 1/8".   

The first selection to be made is the rail length -  The selection runs from 500mm to 110mm.  Default is 250.00  
The second selection is the type of material to use for the lower wing of the corner rail.  This determines the slot size.
The third selection is the type of material to use for the upper wing of the corner rail.  This allows for a separate choice for slot size.
  The fourth selectin is the slot depth.  To provide for more strength,  there are two sizes of rail.  When a general purpose part is needed  
a 10mm slot depth is provided by default - and the rail being rendered in FreeCAD has 28mm wings.   If you select a 16mm depth slot
the wings will be 34mm.   This takes a lot longer to 3d print. 

The fifth selection is a WAPR factor setting and it is the correction you need for being able to print the part at 45 degrees.  I have a
flat on one corner of the part.  This was created to provide a way to have the part face down on that corner, and eliminate any issues 
where supports are needed inside of the slots and holes of the rail.  By placing the part where the vertical sides are now 45 degrees 
instead of 90,  this eliminates any 3d part slicing support issues.  It does create an interesting effect on the actual part creation 
on the 3d printer.  Warping.  My printer setup will print the PETG/PETG-CF parts at about 91.4 included angle printing this way. 
So on my fifth selection I include a WARP angle correction of 1.40.  That correction in the part rendering, will 3d print a 90 included
angle for my setup and PETG.   If you are not using 3d printing -  the default is 0.00.   

-----------------
There are holes in the slots - at 5mm from the bottom of the slots to put 3mm retaining screws,  These are 12mm from each end of the corner
rail and 5mm from the bottom of the slot.  In each sheet being used -  there should be a 3.2mm clearance hole - placed 12mm from the end
and 5mm from the sheet.   The 3mm screw is a pan head and can be tightened to help squeeze the printed plastic slot.  

There are 4.7mm un tapped 5mm holes in either end of the rails at x=0, y=6, and z=6,  and x=(rail length) y=6, and z=6.  These holes are 
15mm deep, and are arranged to secure  end plates/sheets  to 4 rails -  to finish the box enclosure.  To make this work,  the end plates should 
be 38mm greater than the bottom plate is wide and 38mm greater than the side plate is tall.   I would recommend measuring and cutting to 
size after the top, bottom, and sides of the box has been formed.   You do not have to tap the 3d printed holes, as it can be formed
by the 5mm screw, and holds securely, just use a 5M x 16 or 5M x 12 screw.

There are some additional holes in the rail oriented at 45 degrees.   These are provided to accept a coupler which fits between the 
rails. This coupler has matching holes to the rail. These pull into the V of the Rail - and are designed to align two rails coupled to 
extend the overal length. Since the screws pull into the V, these keep the alignment close enough each slot aligns across the two rails. 
And sheet material can extend between the rails.   For instance,  I have two rails at 240mm  and need to have a box that is 480mm. I place
a sheet of material to align the rails and screw in 4 5M x 16 screws through the couplers into the rail.  Now the rails have 4.7mm holes
in the correct spots to match the couplers - and the 5M threads are formed by the screws,   There is a separate function in the coupler 
which is to hold an intermediate sheet for a mezannine to mount electroncs  and it can span above the bottom of the box, by about 9mm.  
There are mounting screws holes for 3mm  on top of the coupler.    Now for each rail the holes in the 45 degree orientation - these are
placed at 17.5, 30, 52.5 from either end of the rail. Additional holes in the middle of the rail are at +17.5 and -17.5 from the middle
of each rail.  That allows for coupling on either end of the rails.   And an additional mid rail tie down for a mezannine sheet. 

Now I only have a single 28mm coupler at the moment.  It will work as a coupler for all rails but it isn't setup for a mezzanine sheet for
16mm slot depth/34mm size parts.  

You can email me at jtsmith0050@gmail.com - if you need assistance.   
file names  -  
PETG_RAIL_7a.py 
CornerRail_Coupler_28m_7b.py
