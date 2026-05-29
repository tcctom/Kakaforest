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

i want to focus on the exterior now and particulary the flush gable roof with shading on the north side. I would prefer to do this by making the the north south length 7 meters rather than 6 and the roof perfectly flush with that. we would then resess the noth facing external wall so it comes back to wher it is now but we have a n extended ground floor going outside (patio), extended first floor going outside (balcony) and a roof covering the balcony.

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
- Interior walls that connect with an exterior wall should sit flush with the inside face of the exterior wall.
### Stairs
Located in the southwest corner; dog-legged staircase with an intermediate landing, configured to provide dedicated enclosure for solar battery storage within the under-stair void.

add a north south internal partition 2.5m long to the ground floor. this should be immediately west if the staircase footprint and starting from the south wall going 2.5 meters north.

#### AI Agent instructions
Act as an expert Python developer scripting 3D geometry in Blender. 
Generate a script to model a staircase according to the following strict spatial constraints:

1. GLOBAL POSITIONING:
- Locate the entire staircase assembly strictly in the SOUTHWEST corner of the floor plan.

2. STAIRCASE TYPE & DIRECTION:
- The staircase must be a 180-degree half-turn (dog-legged) staircase. 
- It consists of two parallel flights traveling in opposite directions, separated by a mid-landing.
- When ascending from the ground floor, the user must turn CLOCKWISE at the landing to reach the upper floor.

3. DIMENSIONS & STAIRWELL OPENING:
- Total floor-to-floor height: 2700mm
- Target a rectangular ceiling opening (stairwell footprint) of roughly 2000mm (width) x 3000mm (length).
- Individual flight width: 900mm (Leaving a 200mm central well gap between flights).
- Mid-Landing geometry: A flat, rectangular platform spanning the full 2000mm width and 1000mm deep at the turning point.

4. LOGICAL FLOW FOR THE SCRIPT:
By "edge" we mean edge if the stairwell footprint.
- Flight 1: Starts at north edge, travels North along the east edge, and meets the Landing.
- Landing: Spans East-West along the south edge.
- Flight 2: Starts at the Landing, turns 180-degrees (clockwise loop), and travels South alson the west edge to meet the upper floor.

Ensure all mesh generation, vertices, and object transformations strictly adhere to this clockwise, 180-degree, Southwest-corner logic.

### Master bedroom
This will be on the east side of the first floor. east west width 4 meters. north south length the full 6 meters. ensuite in south east corner, walk in wardrobe to the west of that.

#### ensuite
Shower in north west corner and stepping in from east. toilet in south west corner with back up against west wall. single vanity in south east corner back up against east wall. entrance is the east side of the north wall.

### Guest bedroom
This will be in the north east corner of the ground floor. east west width 4 meters. north south length 3 meters. built in wardrobe the full 3 meter length on the west side. internal door on the south wall just clear of the wardrobe.
