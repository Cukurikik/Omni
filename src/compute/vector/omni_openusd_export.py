import sys
from pxr import Usd, UsdGeom, Gf

# OMNI Vector & Embedding Layer
# OpenUSD Export Script: Converts GAMBA Gaussian Splatting states into Pixar's Universal Scene Description

def export_splats_to_usd(splat_data: list, output_filepath: str):
    """
    Takes simulated memory structures from the Zig GAMBA engine 
    and translates them into a robust OpenUSD stage for Omniverse rendering.
    """
    stage = Usd.Stage.CreateNew(output_filepath)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

    root_prim = UsdGeom.Xform.Define(stage, '/OmniGambaScene')
    stage.SetDefaultPrim(root_prim.GetPrim())

    points_prim = UsdGeom.Points.Define(stage, '/OmniGambaScene/GaussianSplats')
    
    positions = []
    widths = []
    colors = []
    opacities = []

    for idx, splat in enumerate(splat_data):
        positions.append(Gf.Vec3f(splat['x'], splat['y'], splat['z']))
        
        # USD Points use width; we average the scale tensor
        avg_scale = (splat['scale_x'] + splat['scale_y'] + splat['scale_z']) / 3.0
        widths.append(avg_scale)
        
        # Spherical harmonics mapped to RGB for USD preview
        colors.append(Gf.Vec3f(splat['sh_r'], splat['sh_g'], splat['sh_b']))
        opacities.append(splat['opacity'])

    # Bind attributes to the USD Prim
    points_prim.CreatePointsAttr(positions)
    points_prim.CreateWidthsAttr(widths)
    points_prim.CreateDisplayColorAttr(colors)
    points_prim.CreateDisplayOpacityAttr(opacities)

    # Save the USD file
    stage.GetRootLayer().Save()
    print(f"OMNI OpenUSD export successful: {output_filepath}")

if __name__ == "__main__":
    # Simulated data bridge from standard input or FFI
    mock_splats = [
        {'x': 0.0, 'y': 1.0, 'z': 0.0, 'scale_x': 0.1, 'scale_y': 0.1, 'scale_z': 0.1, 'sh_r': 1.0, 'sh_g': 0.0, 'sh_b': 0.0, 'opacity': 0.9},
        {'x': 1.0, 'y': 0.0, 'z': 0.0, 'scale_x': 0.2, 'scale_y': 0.2, 'scale_z': 0.2, 'sh_r': 0.0, 'sh_g': 1.0, 'sh_b': 0.0, 'opacity': 0.5}
    ]
    export_splats_to_usd(mock_splats, "omni_gamba_scene.usda")
