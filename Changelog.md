### Changes for V4.1.2:
* Added an easier way to scale and move UVs with the "Scale Vector" node group.
    * This replaces the mapping node setup used for the eyes, blush, etc
* Materials that have a maintex or alphamask will now get their own outline material
    * This should prevent transparency issues with the outline
* Added a heel controller to the armature
    * This is for rotating the foot bone while keeping the toes in place; a "tip toe" bone.
* Added HSV sliders for the maintex of general/clothes materials
* Fixed the nsfw texture parser node group in the body shader
* The Bone Widgets collection is now hidden automatically
* Fix bake script to account for world lighting
* Fixed the foot IK
* Moved the "MouthCavity" bone to the secondary layer
* Moved supporting bones to their own armature layers instead of hiding them(layers 17, 18, and 19)
* Relocated bone scaling and armature layer script operations to different buttons
* Moved debug mode toggles to the shapekeys/drivers buttons

### Changes for V4.0.6:
* Fix male body material not being recognized by the scripts
* Added sliders to the body shader to control optional genital textures
    * The genital texture can be loaded into the "NSFW Textures" node group in the body template
    * The file location of the genital texture (cf_body_00_t) depends on what body mod you're using
* Added an example for materials that are partially metal to the KK Shader.blend

### Changes for V4.0.5:
* Quick fix for an issue with the Import Textures button
    * If the body alpha mask did not exist in the "Textures" folder, the script would not handle it correctly

### Changes for V4.0.4:
* Put all the scripts into a blender plugin so the user can press a button instead of having to copy paste scripts
* Added a button that applies the material templates to the model automatically
    * These templates can be edited in the KK Shader.blend
* Added a button that applies the textures to the model automatically
    * *Grey's Mesh Exporter plugin for Koikatsu* is required in order for this to work
    * Colors still need to be set manually
    * This works 90% of the time, so a handful of textures might need to be loaded in manually
* Added custom shapes for the armature to make the important bones more obvious
    * These shapes can be edited in the KK Shader.blend
    * These can be disabled in the armature tab (Armature tab > Viewport Display > Shapes)
* Added second bone layer on the armature for skirt, face and eyebrow bones
    * Multiple bone layers can be made visible at once by shift selecting the layer in the Armature > Skeleton section
