# Textures Directory

## Setting up Floor Textures

To use the laminate floor texture from PolyHaven:

1. **Download** the texture from https://polyhaven.com/a/laminate_floor_02
   - Choose the 1K or 4K resolution (4K recommended for better quality)
   - Download the JPG format

2. **Create folder structure:**
   ```
   c:\KakaForestRetreat\textures\laminate_floor_02\
   ```

3. **Place these files** in the folder:
   - `laminate_floor_02_diff_1k.jpg` (Color/Diffuse map) - **Required**
   - `laminate_floor_02_rough_1k.exr` (Roughness map) - **Required**
   - `laminate_floor_02_nor_gl_1k.exr` (Normal map) - Optional
   - `laminate_floor_02_disp_1k.png` (Displacement map) - Optional
   
   Note: The roughness and normal maps are .exr format, not .jpg

## Setting up Roof Textures

To use the box profile metal sheet texture from PolyHaven:

1. **Download** the texture from https://polyhaven.com/a/box_profile_metal_sheet
   - Choose the 1K or 4K resolution
   - Download the JPG format for diffuse, EXR for roughness

2. **Create folder structure:**
   ```
   c:\KakaForestRetreat\textures\box_profile_metal_sheet\
   ```

3. **Place the files** in the folder:
   - `*_diff_*.jpg` (Color/Diffuse map) - **Required**
   - `*_rough_*.exr` (Roughness map) - **Required**
   - Any other maps (normal, displacement) - Optional

## Current Setup

- **Floors**: If textures are found, realistic laminate texture with UV mapping (scale 4.0)
- **Roof**: If textures are found, realistic corrugated metal texture with UV mapping (scale 2.0)
- If textures are not found, both will fall back to simple colors
- Texture scales can be adjusted in `materials.py` if needed

## Other Textures

You can add other textures from PolyHaven or other sources in this directory following a similar structure.
