### Changes for V5.0.1
* Bugfixes (see [#106](https://github.com/FlailingFog/KK-Blender-Porter-Pack/pull/106), [#95](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/95))

### Changes for V5.0.0
* New export plugin, image saturation functions, and automated color setting by **MediaMoots**!
* Rigify compatible armature conversion by an anonymous contributor!
* Better joint correction bones!
    * Taken from **johnbbob_la_petite** on the Koikatsu Discord
* Better viewport performance using preview quality normal nodes!
    * Taken from **pcanback** [on blenderartists](https://blenderartists.org/t/way-faster-normal-map-node-for-realtime-animation-playback-with-tangent-space-normals/1175379)
* In-game animation imports!
* New base armature!
    * Bones are now organized by type through armature layers!
    * Toggle for keeping the stock KK armature!
    * Accessory bones show up automatically now!
* Upgrades to the export process!
    * Added a button for exporting prep!
    * Smarter baking script!
    * Rebaking materials at higher resolutions is easier now!
    * Support for baking and atlasing normal maps!
* KK shader.blend is now integrated into the plugin!
* Easy slots for forcing light and dark colors!
* Easy slots for makeup and body paint!
* Easy slots for patterns!
* Support for colorized normal maps!
* Automatic separation of Eyes and Eyebrow materials!
    * This allows you to make the Eyes and Eyebrows show through the hair using Cryptomatte and other compositor features
* Shader-to-RGB nodes added to clothing color inputs!
    * This allows you to plug metal and other types of materials into clothing colormask inputs

### Changes for V4.3.1:
* Renamed the spine bones during the "1) Run right after importing" script
    * CATS was not detecting the Spine, Chest and Upper Chest bones correctly. This resulted in the spine and chest bones being merged into one bone with awkward spine bends. Renaming the bones lets CATS detect the three bones correctly.

### Changes for V4.3.0:
* Added a new button to the KK Panel: **Import Studio Object**
    * This script speeds up the import process for an accessory, studio object, or studio map that has been exported as an fbx file with SB3U
    * Example usage video: https://www.youtube.com/watch?v=PeryYTsAN6E
    * The shader applied to the object can be left as the default, changed to an emission shader, changed to the KK Shader, or changed to a custom user-defined node group
* Added a new button to the KK Panel: **Link Shapekeys**
    * If the Eyebrows material is separated from the body object, this script will allow you to link the shapekeys values on the Body object to the Eyebrows object
    * Example usage video: https://www.youtube.com/watch?v=sqEBau1enWE
        * (click this button instead of running the script in the editor as shown)
    * This can be used for the Eyes and Eyeline materials as well
    * Script source: https://blender.stackexchange.com/questions/86757/
* Added a Center bone back to the armature
    * This bone lets you move all the bones on the armature without moving the armature's object location
* Added a Pelvis bone back to the armature
    * This bone lets you move the pelvis and legs without moving the upper spine
* Edited the armature bone tree a little
* Changed the bone widget shapes in the KK shader to be slightly more rigify-like
* Fixed the orientation of the top skirt bones
* Gave the face material a separate outline
* The "Select unused bones" button now unparents the Hips bone from the new Center bone
    * Leaving the Hips bone parented caused import issues in Unity

### Changes for V4.2.3:
* Made eyewhite operations for the shapekeys optional through a toggle
* Fixed the Basis shapekey being deleted when not set to English

### Changes for V4.2.2:
* The plugin now works in Blender 2.93
* The plugin should now work when Blender's interface is set to any language
* Added lazy crash prevention to the shapekeys button

### Changes for V4.2.1:
* Bake button wasn't assigned correctly in the new panel layout

### Changes for V4.2:
* The eyewhites shapekeys are now used when generating the KK shapekeys
    * This will prevent gaps between the eyewhite and the lower eyelash for certain expressions
* The plugin will now recognize the *KK Better Penetration* body type
    * Toes are placed on armature layer 2
    * BP bones are placed on armature layer 3
* Materials without an image texture should properly bake now
    * This will ensure fully transparent materials and materials that are a solid color (but still use the KK Shader) are baked
* The Separate Body button will now attempt to separate the shadowcast and bonelyfans meshes automatically, then shove them into a collection
* The Import Textures button will now check if the user has actually selected the Textures folder and will abort if they chose the wrong folder
    * This was done to prevent texture loading issues
    * This check can be disabled with a toggle
* Adjusted panel layout
* Added better joint correction for the hip bone
    * In order to use them, the "Enable hip drivers" toggle needs to be enabled before pressing the "5 Add bone drivers" button
* Better descriptions of what each toggle does
* Made using multiple outlines optional through a toggle
* The hair object can now be named either "hair" or "Hair"

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
