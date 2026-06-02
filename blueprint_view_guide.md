# Blueprint View Setup Guide

This guide explains how to set up and use the 2D architectural blueprint view system in Blender for the Kaka Forest Retreat project.

## Overview

The `setup_blueprint_view.py` script creates a professional architectural floor plan view with:
- Flat white shading with edge highlighting
- Multiple orthographic cameras for different floor levels
- Automatic clipping planes to reveal interior layouts
- Easy switching between ground floor, first floor, and roof views

## Running the Script

### Method 1: From Blender's Python Console (Recommended)
1. Open Blender and switch to the **Scripting** workspace (top menu bar)
2. In the Python Console at the bottom, paste and run:
   ```python
   exec(open(r"c:\KakaForestRetreat\setup_blueprint_view.py").read())
   ```

### Method 2: From Blender's Text Editor
1. In Blender, switch to the **Scripting** workspace
2. Click **Open** in the Text Editor panel
3. Navigate to and open `setup_blueprint_view.py`
4. Click the **▶️ Run Script** button or press **Alt+P**

## What Gets Created

The script creates 4 orthographic cameras for different views:

| Camera Name | Cut Height | Purpose | View Scale |
|-------------|------------|---------|------------|
| **BP_Ground_Floor** | 1.2m | Ground floor interior plan | 30m × 30m |
| **BP_First_Floor** | 4.0m | First floor interior plan | 30m × 30m |
| **BP_Roof_Plan** | 7.0m | Roof structure plan | 30m × 30m |
| **BP_Site_Plan** | No cut | Full site overview | 50m × 50m |

The viewport is automatically configured with:
- White background (SINGLE color shading)
- Cavity edge highlighting (WORLD mode)
- Maximum ridge/valley settings for clear line work
- Camera view activated by default

## Switching Between Views

### Quick Switch Commands
After running the setup, use these commands in Blender's Python Console to switch cameras:

```python
# Ground floor plan (default)
switch_to_camera('BP_Ground_Floor')

# First floor plan
switch_to_camera('BP_First_Floor')

# Roof plan
switch_to_camera('BP_Roof_Plan')

# Full site overview
switch_to_camera('BP_Site_Plan')
```

### Alternative: Manual Camera Selection
1. In the **Outliner** panel, find the camera you want (e.g., "BP_First_Floor")
2. Select the camera object
3. Press **Ctrl+Numpad 0** to make it the active camera
4. Press **Numpad 0** to view through it

## Customizing the View

### Adjusting Camera Position
To recenter cameras on your site, edit the `main()` function parameters:
```python
cameras = create_floor_plan_cameras(
    center_x=5,    # X coordinate of site center
    center_y=-5    # Y coordinate of site center
)
```

### Changing Cut Heights
To section at different heights, edit `create_floor_plan_cameras()`:
```python
# Example: Cut ground floor at 1.5m instead of 1.2m
cameras['ground'] = create_blueprint_camera(
    name="BP_Ground_Floor",
    location=(center_x, center_y, 20),
    clip_height=1.5,  # Changed from 1.2
    ortho_scale=30.0
)
```

### Adjusting Zoom Level
To zoom in/out, change the `ortho_scale` parameter:
- **Smaller value** = zoomed in (e.g., 20.0 for tighter view)
- **Larger value** = zoomed out (e.g., 40.0 for wider view)

Or adjust in the UI:
1. Select the camera in the Outliner
2. Open **Object Data Properties** (camera icon in properties panel)
3. Adjust **Orthographic Scale** slider

## Rendering Blueprint Images

To export clean blueprint images:

1. Switch to the desired camera view:
   ```python
   switch_to_camera('BP_Ground_Floor')
   ```

2. Set render settings (optional):
   - Open **Render Properties** panel
   - Set resolution (e.g., 3840 × 2160 for high quality)
   - Choose PNG or JPEG format

3. Render the view:
   - Press **F12** to render
   - Press **F3** then type "Save Image" to export

## Tips & Tricks

### Viewport Navigation
- **Numpad 0**: Toggle in/out of camera view
- **Home**: Frame all objects
- **Middle Mouse + Drag**: Pan view
- **Scroll**: Zoom in/out (even in camera view)

### Fine-tuning Edge Display
If lines are too thick or thin:
1. Open **Shading** panel in the 3D viewport header
2. Adjust **Cavity** sliders:
   - **Ridge**: Controls convex edge visibility
   - **Valley**: Controls concave edge visibility

### Working with Multiple Buildings
The cameras capture everything in the scene. To isolate a specific building:
- Use **Collections** to organize buildings
- Toggle collection visibility in the Outliner
- Or use **Local View** (Numpad `/`) to isolate selected objects

### Rerunning the Script
You can safely rerun the script multiple times. It will:
- Remove existing blueprint cameras
- Create fresh cameras with current settings
- Preserve your scene geometry

## Troubleshooting

**Problem**: Camera view shows nothing or wrong area
- **Solution**: Adjust `center_x` and `center_y` in `create_floor_plan_cameras()` to match your site center

**Problem**: Can't see interior (walls block view)
- **Solution**: Lower the `clip_height` value for that camera (e.g., 0.8m instead of 1.2m)

**Problem**: Edges not visible enough
- **Solution**: Increase ridge/valley factors in viewport shading settings, or enable **Backface Culling**

**Problem**: View is too zoomed in/out
- **Solution**: Adjust the camera's `ortho_scale` value (select camera → Object Data Properties → Orthographic Scale)

## Coordinate Reference

For Kaka Forest Retreat project:
- **Origin**: (0, 0, 0) at ground level
- **X-axis**: East (-X) / West (+X)
- **Y-axis**: North (-Y) / South (+Y)
- **Z-axis**: Up (+Z) / Down (-Z)
- **Red Cottage (Björken)**: ~X=0
- **Wet Wing**: ~X=11

Default camera center is set to (5, -5, 20) to frame the entire site.

## Advanced: Section Plane Method

The script includes an alternative cutting method using boolean operations. To use it:

1. Uncomment in `main()`:
   ```python
   setup_section_plane_method(clip_height=1.2)
   ```

2. Manually add **Boolean** modifiers to building objects:
   - Select building object
   - Add Modifier → Boolean → Difference
   - Set Object to "Section_Plane"

This gives cleaner cuts but requires manual setup per object.
