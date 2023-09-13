[return to wiki home](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md)

# Material


## The KKBP material setup
Below is an overview of the KKBP material template. All textures in the .pmx export folder are loaded to the green textures node group below. The texture positions are set using the sliders in the purple group below. The textures are used in the Shader group in the middle to create light and dark versions of the material. The material knows when to show the light or dark version of the texture by using the Raw toon shading group. Finally, a rim is added to the output if it is enabled.

![Part 2 mov_snapshot_01 05 000](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/21f84c5c-eb33-48bc-9c7d-8f44c99eadd2)

Opening any Shader node group will show two node groups, a dark color group on the top and a light color group on the bottom. These colors are automatically set using the RGB information stored in the KK_MaterialData.json data (this file is located in the .pmx export folder). You can edit any of these colors or sliders for all Hair materials, Clothes materials, Body materials, etc.

![Part 2 mov_snapshot_01 27 833](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/ac3ca502-04cf-4877-8111-2a13866ecb76)

## Plain Maintex vs Colored Maintex
Plain Maintex files are a component that make up the Maintex you see in game. The Plain Maintex is combined with the colors you set in game and the colormask texture. All three combined create the full Colored Maintex. Colored Maintex files from the KKBP Exporter already have the colors applied and also include any additional overlays, so it combines the Plain Maintex + Colormask files + colors + overlay files together. If you want to change the colors on the fly, you can swap to the plain maintex by setting the "Use colored maintex" and "Ignore colormask" sliders below to 0 instead of 1.

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/7f1883f6-210a-4225-9163-9cfb59f22be6)

## Special materials (Outlines)
Outlines have a different material setup. If an alphamask is available for this material, the alphamask's red channel will be used to determine where the outline should be transparent. If it is not available, the maintex will be used instead. If neither are available, the outline will be visible everywhere on the material.

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/98b155ac-6442-4290-806a-741017f6ac5c)

## Special materials (Eyes)
The eye texture is automatically created by the KKBP Exporter. If you want to use the custom eye slider and change the colors of the eye on the fly, you have to extract certain eye textures from the game using SB3Utility, then load them into the green texture group and recreate the eye from scratch. [Here's an example of doing that](https://www.youtube.com/watch?v=XFt12n7ByBI&t=231)

Eyes have a special material setup that allows you to change both of them at once. If you want to change the eyes separately, you can make the eye shader node group unique by clicking on the number next to the node group name:

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/903e3ee6-0ae8-4fa1-b6b1-549b84e21ab2)

## Special materials (Hair)
Hair has a special material setup that allows you to change the like-colored hair materials at the same time.
See the "Special materials (Eyes)" section above for how to give specific pieces of hair different colors.

## Special materials (Tears)
Tears have a special material that uses a gradient to get a look similar to the in-game one. You can make the tears use an HDRI or a flat color instead by using the sliders in the Tears material.

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/fbed381d-e9f3-4e88-b6d8-9ec175f52f80)

## Special materials (Gag eyes)
There are three sets of Gag eyes: Gag00, Gag01 and Gag02  
Gag00 images are displayed in a mirrored fashion (both eyes mirror each other)  
Gag01 images are displayed as is   
Gag02 images are animated by continuosly changing the location of the UV map over time (also used by the Cartoony Wink expression)

Gag eyes use drivers to determine what expression to display. When you activate a gag shapekey on the Body object, certain eye materials are moved back into the head to hide them, the gag eye mesh comes out to the front of the head and an image is displayed depending on which gag shapekey was activated.

The default import comes with settings that make the face area behind the gag eyes look bad. Disabling the face eyeshadow intensity, setting the face rim to "None", and using the features in the "Permanent light / dark settings" or "Smoothing out the look of the face with Generated Face Normals (GFN)" sections below can help with that.

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/dfef8712-c344-413f-9c3c-304d13d6313d)

## Smoothing out the look of the face with Generated Face Normals (GFN)
Some face shapekeys can look pretty bad around the mouth with certain lighting

![Part 2 mov_snapshot_13 55 000](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/83103210-cefa-4af0-a813-9de8c05d83c2)

This can be avoided by changing the "Raw Shading" group in the face material to the "Raw Shading (Face)" group instead
![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/193d1ec9-cc9b-42b7-a089-5e4e1e6e0066)

And shading discontinuities on the neck can be fixed by going to the Body material and sliding the "Use Normals" slider down to zero. Here's the same face again, but with GFN enabled:

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/574a78c1-02c0-42e1-b133-afdcc1edf846)

## Koikatsu color conversion
The colors you see in Koikatsu are not the real colors being used, they're being saturated. In order to replicate the colors shown in koikatsu, all colors and images are run through the color_to_KK and image_to_KK functions in [modifymaterial.py](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/importing/modifymaterial.py) to convert the base colors to the "real" colors seen visually in the game. This process is also run on all Maintex images.

Here's an example of a material before and after color saturation

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/01a8a67d-289c-4f60-9204-334dc4382772)

## Koikatsu dark color conversion
The game uses a second color conversion process to automatically get dark colors for every light color. The skin_dark_color and clothes_dark_color functions in [modifymaterial.py](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/importing/modifymaterial.py) are used to automatically obtain dark colors for every piece of clothing and create dark Maintex images. 

## Cycles support
Basic Cycles support is available by selecting "Use Cycles" in the panel. This will replace the Rim node group in the KK shaders with a Toon-like shader compatible with Cycles. The outline is disabled in the mode.

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/f5aaaa16-36f3-422e-ad7d-de6811c28091)

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/1515d432-1421-4176-99ea-8444771ed1dd)

## Lightning Boy Shader support
Basic [Lightning Boy Shader support](https://lightningboystudio.gumroad.com/l/aYbiH) is available by selecting "Use LBS" in the panel. This will replace the Rim node group in the KK shaders with a group that contains an LBS setup. KKBP does not contain any LBS nodes, so LBS must be installed for this mode to work. Ambient occlusion and bloom are enabled in this mode.

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/4f8cce43-6dfe-4521-ba66-ad5890ce18db)

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/bc290384-bfbd-4b28-8694-1953dc7cee8d)

## Normal blending methods
A different normal blending method is available in the Raw Shading group. Enter it and find the node to use the Unity tech demo blending method. These blending methods [were taken from this page](https://blog.selfshadow.com/publications/blending-in-detail/)

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/f727e9f9-acc6-4106-aa39-9f79f4d59e50)


## Normal quality settings
Normals are set to lower quality by default to increase animation playback performance. To change to higher quality normals, just enter the Raw Shading group, connect the higher quality output node and unmute the node by selecting it and pressing the M key.
This is done automatically when baking materials.

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/0ff6d4cf-fdd9-402e-b4da-4902be8d21da)


## Toon shading settings
Toon shading is created by the color ramps in the Raw Shading group. You can edit the color ramps in this section to increase or decrease the amount of light needed to show the light or dark version of the materials.

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/f377ef56-b0b9-41a2-96e1-8a28ea861b73)


## Permanent light / dark settings
Parts of each material can be made permanently light or dark using the Permalight image in the texture node group. The red channel of the image is used for permalight and the blue channel is used for permadark 

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/90b21355-8fa2-4b92-b8d7-06d7ed3ae700)

## Per-character light linking settings
If you have multiple characters in a scene, this allows you to "link" a light to a character, so you can achieve ideal lighting for each character and not have to fiddle with a global lighting setup that affects all characters at once. This works for up to three characters / light sources. It's enabled by default and can be found inside of the Raw Shading group.

Usage: Enter the Raw Shading group then make sure the "Light linking options (open me)" group framed in pink has it's slider set to 1, and any red lights will light your character. Import a second character, return to the ""Light linking options (open me)" group, and open it. Change the output of the pink "Match RGB output and sunlight color for light linking" frame from R to G. Any green lights will light the second character, but not the first character. Using a yellow light will light both R and G characters. Using a white light will light all characters.

![](https://user-images.githubusercontent.com/65811931/156895424-fa80054b-d4c2-4c50-a4e1-4df653140200.png)

## Light color influence
When you use a light that isn't pure white, the colors on the model will become affected by the color of the light. This is disabled by default and can be found inside of the Raw Shading group. Colored lights and light linking can't be used at the same time.

Usage: Make sure the "Light linking options (open me)" group framed in pink has it's slider set to 0, and any colored lights will add additional color to your character. Any white lights will light the model like normal.

![](https://user-images.githubusercontent.com/65811931/156895644-6139b803-57f9-46a5-8ed3-035eb1087439.png)


## Shader to RGB support
Many color inputs on the KK shader have a "Shader to RGB" node on the inside, so they can accept shaders like the principled BSDF as an input.

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/21f633be-d215-4547-805e-5ff59af32450)

[return to wiki home](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md)

## Editing the KKBP shader
The KKBP library file can be edited if you want to use a custom material or node setup for all imported models. Keep in mind the import scripts will error out if certain things are missing, so don't delete anything already in the file. The library file is usually located here: ```C:\Users\[your username]\AppData\Roaming\Blender Foundation\Blender\[your blender version]\scripts\addons\KK-Blender-Porter-Pack\KK Shader.blend```