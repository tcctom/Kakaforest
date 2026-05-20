# Kaka forest main dwelling

## Location
60 meters north of Björken (red cottage), elevation 5 meters lower.
(these measurements should be configurable so we can update when we get more accurate measurements)

## Base size and style
### Main shell
A full two storey rectangular box, 6 meters by 8 meters. The 8 meter length runs east to west. We expect the external shell to be built using the potius residential system. https://www.potius.co.nz/potius-residential/

- Exterior wall thinkness is 200mm or as per potius specs.
- Ground floor ceiling height should be 2.5 meters
- First floor ceiling height should be 2.4 meters
- Ground floor windows & doors
    - North wall - patio doors and big windows
    - East wall - entrance

### Roof
- A gable roof
- 35 degree pitch
- Ridge line running east to west the 8 meter length 
- Industry standard overhangs on all sides

**Technical Note for Blender Implementation:**
When creating the gable roof in Blender, use a custom mesh with vertices positioned at exact locations (eaves and ridge), rather than rotating flat panels. This is the same approach used in the Björken module. Create vertices at:
- North and south eave edges (at `eave_height = top of walls`)
- Ridge line at center (at `ridge_height = eave_height + (WIDTH/2) * tan(pitch)`)
Then define two faces for the north and south slopes. This avoids complex rotation math and positioning errors.

## Interior
- Internal wall thickness 110mm. 
