---
layout: default
---

# Test cases

1. In Koikatsu, export Chika with all 8 outfits (default exporter settings)
    * Also export with only "Export Single Outfit" enabled
    * Also export with only "Export Variations" and "Export Hit Meshes" checked
    * Also export with a pose selected, an emotion pattern selected and only "Export Single Outfit", "Keep Current Pose" and "Enable Shapekeys" checked
1. In Blender, import the "Export Variations" and "Export Hit Meshes" model
    * Check variations + hitboxes were separated
    * Check eye shapekeys work
    * Check mouth shapekeys work
    * Check Gag eye shapekeys work
1. In another file, import the "Keep Current Pose" and "Enable Shapekeys" model
    * Check armature type was changed to Koikatsu
    * Check pose and shapekeys were applied to base mesh
1. In another file, import the 8 outfits export
    * Check Outfits 0, 1, 2 exist, and have textures + converted colors
    * Check Hair for Outfits 0, 1, 2 exist and have textures + converted colors
1. In another file, import the "Export Single Outfit" export
    * Check Outfit 0 exists
    * Check Hair for Outfit 0 exists
    * Check hand IK, leg IK, hips bone and center bone work
    * Check eye controller works
    * Use the bake material templates button
    * Use the "Prep for target application" button
1. In another file, import the "Export Single Outfit" export with the "Rigify Armature", "Skip modifying shapekeys", "Use Cycles" options. Check "Fix body seams" and enable the "SFW mode" checkbox
    * Check Rigify hand IK, leg IK, hips bone and center bone work
    * Check Rigify eye controller works
    * Check shapekeys were not modified
    * Switch to rendered view and check the model appears in the cycles viewport
    * Go into edit mode and check the seam down the middle of the neck is gone
    * Check the sfw alphamask was applied to the body material
    * Check nsfw meshes were deleted
1. In another file, import the "Export Single Outfit" export with the "Separate every object" option selected
    * Check all outfit objects are separated
