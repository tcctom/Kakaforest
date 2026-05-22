# Kaka forest main dwelling
Simple, modern, fitting, strong, eco, 

## Location
60 meters north of Björken (red cottage), elevation 5 meters lower.
(these measurements should be configurable so we can update when we get more accurate measurements)

## Base size and style
### Main shell
A full two storey rectangular box, 6 meters by 8 meters. The 8 meter length runs east to west. We expect the external shell to be built using the potius residential system. https://www.potius.co.nz/potius-residential/

- Exterior wall thinkness is 200mm or as per potius specs.
- Ground floor ceiling height should be 2.5 meters
- First floor ceiling height should be 2.4 meters

### Roof
- A gable roof
- 35 degree pitch
- Ridge line running east to west the 8 meter length 
- Want to be able to explore 2 different roof option. Flush Gable and Traditional Gable 
- Industry standard overhangs on all sides for the Traditional Gable
- on the north side we want the roof to continue down for another meter to proved some shading for a north facing balcony across the full length


**Technical Note for Blender Implementation:**
When creating the gable roof in Blender, use a custom mesh with vertices positioned at exact locations (eaves and ridge), rather than rotating flat panels. This is the same approach used in the Björken module. Create vertices at:
- North and south eave edges (at `eave_height = top of walls`)
- Ridge line at center (at `ridge_height = eave_height + (WIDTH/2) * tan(pitch)`)
Then define two faces for the north and south slopes. This avoids complex rotation math and positioning errors.

### Entrance / Porch
Sticking out to the west of the west wall we have a small porch. 
- floor area 2.5 meters wide by 2.5 meters deep 
- should be covered by a 35 degree gable roof with the ridge line running east to west like the main roof.
- aligned centrally on the west wall
- external wall should wrap the 2.5 meter width and 1.5 meters of the depth
- remaining 1 meter is outside but still covered by the porch roof.
- An entrance door will be on the west side of the porch.

Option 2
can you also create another entrance porch option for me? same witdth along the west face as existing but only coming our 1.5 meters and not enclosed, i.e. just a roof and a deck. roof would be simple monopitch rather than gable. main entrance door would be on the main structure west  wall. 

### Windows 

- Ground floor north wall - 3 large windows / patio doors. 2 meters height. 1.5, 2.0, 1.5 meter widths respectively, evenly spaced aling the wall.
- First floor north wall - 3 windows. width and placement matching ground floor but height only 1.2 meters.
- Ground floor east wall - 2 small windows
- First floor east wall - 2 small windows
- Ground floor west wall - 2 very small windows taking into account of porch
- First floor west wall - 2 small windows
- Ground floor south wall - 3 medium windows evenly spaced
- First floor south wall - 3 medium windows evenly spaced

### Exterior cladding
For our location on a mountain spur at 800m elevation surrounded by native beech forest, we want cladding that is durable in exposed conditions and blends harmoniously with the beech forest setting.

**Recommended Options:**

1. **Vertical Cedar Weatherboards** (Primary recommendation)
   - Natural Western Red Cedar or NZ-grown Macrocarpa
   - Vertical orientation with 150mm spacing shadowclad grooves
   - Oiled or stained in dark natural tones (charcoal grey, dark brown, or black stain)
   - Allows building to recede visually into forest backdrop
   - Excellent weather resistance for mountain conditions
   - Natural oils provide protection against moisture and UV

2. **Dark Stained Timber (Alternative)**
   - Treated pine or cedar horizontal weatherboards
   - Dark stain colors: Resene "Ironsand", "Bokara Grey", or similar
   - Creates shadow effect that minimizes building presence in clearing
   - Cost-effective if cedar is unavailable

3. **Mixed Cladding (Feature option)**
   - Vertical dark-stained cedar on main walls
   - Natural unstained cedar or lighter tone on gable ends for accent
   - Creates subtle architectural interest while maintaining forest harmony

**Color Palette:**
- Walls: Dark charcoal, graphite grey, or deep brown (to blend with tree trunks and shadows)
- Window frames: Off-white or soft cream (contrast for definition)
- Roof: Dark grey or black corrugated iron (recessive, traditional NZ rural)

**Weather Considerations:**
- All cladding must handle high moisture, wind exposure, and potential snow load
- Minimum 150mm ground clearance for splash protection
- Proper flashing and drip edges critical at 800m elevation

## Interior
- Internal wall thickness 110mm. 
### Master bedroom
This will be on the east side of the first floor. east west width 4 meters. north south length the full 6 meters. ensuit in south east corner, walk in wardrobe to the west of that.
