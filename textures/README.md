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

## Current Setup

- If textures are found, the floor will use realistic laminate texture with proper UV mapping
- If textures are not found, it will fall back to a simple brown color
- The texture scale is set to 4.0 - adjust in `materials.py` if needed

## Other Textures

You can add other textures from PolyHaven or other sources in this directory following a similar structure.
