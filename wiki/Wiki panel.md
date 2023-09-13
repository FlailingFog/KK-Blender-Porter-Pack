[return to wiki home](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md)

# Panel options

You can mouse over most panel options to get an explanation of each item.  
This page will only cover things that are not immediately obvious from the explanations built into the panel, so be sure to check those.

## Default panel settings
If you expand KKBP in Blender's addon menu, you can set default settings for the panel (so you don't have to set them each time you import a character). 
![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/33682523-016e-41a2-bb4c-0bb043ee55cd)

## Importing panel
* Changing the "Automatically categorize" option to "Separate by SMR data" will not load any materials onto the model
* Changing the "Use KKBP Armature" option to anything else will break full compatibility with the "Prep for target application" button in the Exporting panel.
    * It's still possible to export the model, but you'll have to figure out how yourself.
* Changing the "Use KKBP Armature" option to "Koikatsu Armature" or "PMX Armature" will not create IK bones or an Eye Controller bone during import (results in an FK-only armature)

## Exporting panel
* The "Very Simple (SLOW)" option and "Unity - VRM / VRChat Compatible" options will only work with the KKBP Armature. If you're not using the KKBP Armature then make the options "No changes" and "Generic FBX" or you'll get an error.
* The Export FBX button is just a shortcut to the .fbx file export in File > Export > .fbx with these preset options
    * object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
    * use_mesh_modifiers=False,
    * add_leaf_bones=False,
    * bake_anim=False,
    * apply_scale_options='FBX_SCALE_ALL',
    * path_mode='COPY',
    * embed_textures=True,
    * mesh_smooth_type='OFF'

## Extras panel
* Instructions for exporting studio objects from the game and importing them using the button in the panel [can be found here](https://www.youtube.com/watch?v=PeryYTsAN6E)
* Instructions for exporting animations from the game and importing them using the button in the panel can be found [here if you prefer text](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/extras/animationlibrary/createanimationlibrary.py) or [here if you prefer video](https://www.youtube.com/watch?v=Ezsy6kwgBE0)
* Instructions for exporting maps from the game and importing them using the button in the panel [can be found here](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/extras/animationlibrary/createmapassetlibrary.py) 
* The optimize materials button will replace the KKBP materials with a simple toon shader. This gives a massive boost in animation playback performance. You need to bake KKBP materials using the button in the exporting panel, then use the "Switch baked templates" button after setting the option to "Light" and "Dark" (both sets of images need to be loaded into your current file before the materials can be optimized.)
* If the "Use KKBP Armature" option was selected during import but you now want to swap to a Rigify armature, you can click the "Convert for Rigify" button to permanentally convert the KKBP one to a Rigify one.
* The "Separate Eyes and Eyebrows" button will separate the eyes and eyebrows into separate objects, then link their shapekeys to the Body object's shapekeys. This can be combined with the Cryptomatte compositor features to make the Eyes and Eyebrows show through the hair. See [this video for an example of selecting objects with Cryptomatte](https://www.youtube.com/watch?v=3UR4eXxMlsU). Cryptomatte does not work well with materials set to Alpha Blend, so you'll need to change the Face material, Body material and others to Alpha Clip before it will work.

[return to wiki home](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md)