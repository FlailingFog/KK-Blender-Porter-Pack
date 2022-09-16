### Changes for V6.0.0
Huge feature and usability updates by **MediaMoots**!
* The KKBP exporter now works in Koikatsu Sunshine!
* The KKBP Blender plugin now works in Blender 3.1+!
* All outfits are now exported!
    * These are automatically exported from Koikatsu
    * These are available as hidden objects after the model is imported into Blender. They are parented to the armature
    * If you don't want to use these, you can shorten your import time by deleting the "Outfit ##" folder from the export folder 
* Alternate clothing states (shift / hang state) can now be exported!
    * Export these by checking the "Export Variations" box in Koikatsu
    * These are available as hidden objects after the model is imported into Blender. They are parented to the outfit object
* Hitboxes can now be exported!
    * Export these by checking the "Export Hit Meshes" box in Koikatsu
    * These are placed in their own collection when the model is imported into Blender
* The tears object is now exported and available as new shapekeys on the body object!
    * These are parented to the body
    * The tears material also has settings to allow minor color edits
* The eye gag object for heart eyes, firey eyes, etc is now exported and available as new shapekeys on the body object!
    * These are parented to the body
    * The shapekeys will automatically hide the eyes and eyeline materials when active
    * The swirly eye rotation speed, heart eye pulse speed and cry/fire eye animation speed can be changed in the Eye Gag materials 
* The animated tongue is now exported!
    * This is parented to the body object and hidden by default
    * The rigged tongue doesn't use shapekeys like the rest of the face does
* Shapekeys are more accurate than before!
* The heart and sparkle Eye overlays are now exported
* Eyewhite shapekeys are fixed on the exporter-side now!
    * This means Blender is less likely to crash when importing the model
* Small fangs are now exported!
* Accessories are now automatically linked to the correct limb bone!
* Eye and overlay textures are now scaled automatically!
* Hair shine, eyeshadow, nipple and underhair UVmaps are now exported!
    * Thanks to that, these items no longer need to be set and scaled manually for each character
* Converted Normal Maps for use in Unreal and Unity are now exported
* Separated objects can now be exported with the "Export separated meshes" button
* A lot of character info is now exported
    * Check the .json files in the export folder for info on materials, accessories, objects, renderers and bones
* Exported character heights are 4% more accurate
* Texture suffixes are shortened
    * Image names over 64 characters long would cause blender to cufoff the filename, so this means long texture names are less likely to cause issues during import
* The Koikatsu / BepInEx console will now be print out each mesh being exported. If the exporter is not working for a specific character, accessory or clothing item, you can use this to track down what is causing the exporter to fail.
    * These messages are prefixed with [Info   :   Console]

Rigify armature updates by **an anonymous contributor**!
* Better Penetration bones will now be placed in the "Torso (Tweak)" layer when converting to the Rigify armature
    * You need to use the Better Penetration armature type in Koikatsu for these bones to appear

Unity normal blending and mirrored blush scaling by **poisenbery**!
* Unity normal blending is an alternative normal map detail blending method that can be accessed in the "Raw shading" group
* Mirrored blush scaling is an easier way to scale the blush and eyeshadow if the texture is symmetrical. This can be accessed in the "Blush positioning" group on the Face material

Better face normals using shader nodes!
* The face now uses a bastardized version of the Generated Face Normals setup [described in this post by **aVersionOfReality**](https://www.aversionofreality.com/blog/2021/9/5/clean-toon-shading)
* This setup is disabled by default for performance reasons. Enable it by going to the face material > swap the "Raw Shading" node group to "Raw Shading (face)"
* This setup only works in Blender
* The GFN Empty position and scale can be edited by unhiding it. It's parented to the armature
* The GFN options can be edited in the node group called "Generated Face Normals" inside of the the "Raw shading (face)" group

Plus some misc changes to the Blender plugin:
* Added a one-click option for importing models!
    * Hair is now separated from the model automatically, so the entire import process has been reduced to a single button
    * The behaviour from V5.0 (where you can separate objects as you please) can still be accessed by changing the "Don't pause to categorize" option on the upper right to "Pause to categorize", then pressing the "Finish categorization" button when you're done.
* The main plugin UI can now be fully translated!
    * Current languages: English, Japanese (日本語)
* Material baking is now done [through the use of Geometry Nodes!](https://blender.stackexchange.com/questions/231662/)
    * This works with multiple UV maps, so you no longer need to create a new mesh for hair highlights or anything that uses a separate uv map
    * You can also speed up the baking process by skipping the dark and normal bakes if you don't want them
* Exporting can now be done without installing the CATS addon
    * Material Combiner is still required if you want a material atlas
* Added a simplification choices menu to the export prep button
* Removed the vanilla armature type toggle in favor of a menu
    * There's four options to choose from. Check the tooltip for a brief description of each option
    * The ability to switch between armature types after import was removed
* Shapekeys on clothes and hair objects are now deleted
    * Shapekeys only affect the face, so these weren't needed anyway
* The Eye, Eyebrow, Eyewhite, Eyeline and Nose materials are now marked as freestyle faces by default (for freestyle exclusion)
* Lipstick and Flush textures are now loaded into the face material
* Added a safe for work mode toggle that probably works
* The permalight/permadark texture has been merged into one file
* Python errors are now copied to the KK Log in the Scripting tab on the top
* The import directory string listed in the KK Log is now censored if it detects your Windows username
* The plugin now uses an HDRI from polyhaven
* All KKBP panel options are now visible by default
* The KKBP panel will now gray out some buttons after a model is imported  

And many bugfixes

### Changes for V5.1.0
* Added per-character light linking to the KK shader
    * If you have multiple characters in a scene, this allows you to "link" a light to a character, so you can achieve ideal lighting for each character and not have to fiddle with a global lighting setup that affects all characters at once. This works for up to three characters / light sources. It's enabled by default and can be found inside of the Raw Shading group.
    * Usage: Make sure the "Light linking options (open me)" group framed in pink has it's slider set to 1, and any red lights will light your character. Import a second character, return to the ""Light linking options (open me)" group, and open it. Change the output of the pink "Match RGB output and sunlight color for light linking" frame from R to G. Any green lights will light the second character, but not the first character. Using a yellow light will light both R and G characters. Using a white light will light all characters.
* Added reaction to colored light to the KK shader
    * When you use a light that isn't pure white, the colors on the model will become affected by the color of the light. This is disabled by default and can be found inside of the Raw Shading group. Colored lights and light linking can't be used at the same time.
    * Usage: Make sure the "Light linking options (open me)" group framed in pink has it's slider set to 0, and any colored lights will add additional color to your character. Any white lights will light the model like normal.
* Updated Rigify scripts to the latest version (Feb 24th)
* Overlay masks for Body and Face shaders now retain their original color.
    * The "Overlay color" inputs on the body/face shader that used to set the overlay color have been changed to "Overlay color multiplier" inputs. Keep this as a white color to preserve the overlay mask's original color. If the overlay is pure white itself, the color on the multiplier will just set the color of the overlay.
* Added an image slot for the "plain" version of the maintex for clothing items.
    * This can be accessed by going into the clothing shader group and setting the "Use colored maintex?" slider to zero
    * If there's no plain version available, you'll get a pink placeholder texture as a warning
* The permanant light and dark image masks in the raw shading group have been moved to the green texture group
    * This removes the need to create a unique raw shading group for every material.
* Bugfixes ([#94](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/94), [#90](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/90), [#105](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/105), [#114](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/114))

### Changes for V5.0.1
* Bugfixes (see [#106](https://github.com/FlailingFog/KK-Blender-Porter-Pack/pull/106), [#95](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/95))

### Changes for V5.0.0
* New export plugin, image saturation functions, and automated color setting by **MediaMoots**!
    * These make the import process more than twice as fast as the previous version!
    * Color data from the game is now extracted and applied to the shaders automatically during the import process
    * Textures are now automatically saturated to replicate the look of the in-game saturation filter
    * More textures are extracted than before
    * The new export plugin fixes common bugs involving broken charamaker functionality, shapekeys and accessories
* Rigify compatible armature conversion by an anonymous contributor!
    * Requires Rigify and the "auto-execute scripts" setting to be enabled
    * Adds IK toggles for fingers, skirts, and accessories
    * Improves the eye controls with extra features like single eye manipulation and eye target tracking
    * Adds FK <-> IK switches to limb bones
    * Makes more armature controls accessible
* Better joint correction bones!
    * Taken from **johnbbob_la_petite** on the Koikatsu Discord
* Better viewport performance using preview quality normal nodes!
    * Taken from **pcanback** [on blenderartists](https://blenderartists.org/t/way-faster-normal-map-node-for-realtime-animation-playback-with-tangent-space-normals/1175379)
* Extracted in-game animation files can now be imported automatically!
* New base armature!
    * Bones are now organized by type through armature layers
    * Toggle for keeping the stock KK armature
    * Accessory bones show up automatically now
* Upgrades to the export process!
    * Added a button for exporting prep
    * Smarter baking script
    * Rebaking materials at higher resolutions is easier now
    * Support for baking and atlasing normal maps
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
