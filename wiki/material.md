## Material

## Before you begin...
**There's a lot of information on the [material breakdown](material_breakdown) if you're having issues with a material or want to know how a typical KKBP material works.**

## Updating a finalized material
If you want to go back to the original material to edit it again, you can set the material back to the -ORG version of the material.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat2p3.png)

Here I have updated the hair color on the original shader

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat2p5.png)

To finalize the material again, just click the "Finalize Materials" button on the KKBP panel. The material will be re-finalized and the lightweight shader + atlas model will be updated.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat2p6.png)

## Special materials (Outlines)
Outlines have a different material setup. If an alphamask is available for this material, the alphamask's red channel will be used to determine where the outline should be transparent. If it is not available, the maintex alpha channel will be used for determining transparency instead. If neither are available, the outline will be visible everywhere on the material. The outline materials will not be converted to png files when you click the Finalize Materials button.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat4.png)

## Special materials (Eyes)
The eye texture is automatically created by the KKBP Exporter. If you want to use the custom eye slider and change the colors of the eye on the fly, you have to extract certain eye textures from the game using SB3Utility, then load them into the green texture group and recreate the eye from scratch. [Here's an example of doing that](https://www.youtube.com/watch?v=XFt12n7ByBI&t=231)

## Special materials (Body)
The body has a transparency mask to prevent it from clipping through some clothes [Check here for making the body visible](https://flailingfog.github.io/faq). 

If you are finding that the body is still transparent in the wrong areas, you can either edit the body alpha mask (location shown below), or load a different body_AM file from your pmx export folder. The first body alpha mask for the first outfit is automatically loaded in (cf_m_body_AM.png), so if you switch to a different outfit you'll have to switch the body mask to the right one (ex. body_AM_01 for outfit 01, 02 for outfit 02, etc).

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat5p4.png)

## Special materials (Hair)
Hair materials are not linked. If you modify one hair material and then click the update hair materials button, the rest of the hair materials on this object will be updated using the settings of the current hair material.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat5p5.png)

## Special materials (Tears)
Tears have a special material that uses a gradient to get a look similar to the in-game one. You can make the tears use an HDRI or a flat color instead by using the sliders in the Tears material.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat6.png)

Tears can be activated in the shapekey panel

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat6p1.png)


## Special materials (Gag eyes)
There are three sets of Gag eyes: Gag00, Gag01 and Gag02  
Gag00 images are displayed in a mirrored fashion (both eyes mirror each other)  
Gag01 images are displayed as is   
Gag02 images are animated by continuosly changing the location of the UV map over time (also used by the Cartoony Wink expression)

Gag eyes use drivers to determine what expression to display. When you activate a gag shapekey on the Body object, certain eye materials are moved back into the head to hide them, the gag eye mesh comes out to the front of the head and an image is displayed depending on which gag shapekey was activated.

The default import comes with settings that make the face area behind the gag eyes look bad. Disabling the face eyeshadow intensity, setting the face rim to "None", and using the features in the "Permanent light / dark settings" section below can help with that.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat7.png)

Gag eyes can be activated in the shapekey panel

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat6p1.png)

## Koikatsu color conversion
The colors you see in Koikatsu are not the real colors being used; they're actually being saturated. In order to replicate the colors shown in koikatsu, all colors and images are run through the color_to_KK and image_to_KK functions in [converttextures.py](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/importing/converttextures.py) to convert the base colors to the "real" colors seen visually in the game. This process is also run on all Maintex images.

Here's an example of a material before and after color saturation

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat11.png)

## Koikatsu dark color conversion
The game uses a second color conversion process to automatically get dark colors for every light color. The skin_dark_color and clothes_dark_color functions in [modifymaterial.py](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/importing/modifymaterial.py) are used to replicate this process in Blender and to automatically obtain dark colors for every piece of clothing and create dark Maintex images. If this is disabled in the panel, you'll only get the light colors.

## Cycles support
Basic Cycles support is available by selecting "Use Cycles" in the panel. This will replace the Rim node group in the KK shaders with a Toon-like shader compatible with Cycles. The outline is disabled in the mode.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat12.png)

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat13.png)

## Normal blending methods
A different normal blending method is available in the Toon Shading group. Enter it and find the node to use the Unity tech demo blending method. These blending methods [were taken from this page](https://blog.selfshadow.com/publications/blending-in-detail/) and [also this page](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/166)

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat16.png)


## Normal quality settings
Normals are set to lower quality by default to increase animation playback performance. To change to higher quality normals, just enter the Toon Shading group, connect the higher quality output node and unmute the node by selecting it and pressing the M key.
This is done automatically when baking materials so you don't need to worry about it if you plan on exporting the model from blender.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat17.png)


## Toon shading settings
Toon shading is created by the color ramps in the Toon Shading group. You can edit the color ramps in this section to increase or decrease the amount of light needed to show the light or dark version of the materials.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat18.png)


## Permanent light / dark settings
Parts of each material can be made permanently light or dark using the Permalight image in the texture node group. The red channel of the image is used for permalight and the blue channel is used for permadark 

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/mat19.png)

## Editing the KKBP shader
The KKBP library file can be edited if you want to use a custom material or node setup for all imported models. Keep in mind the import scripts will error out if certain things are missing, so don't delete anything already in the file. The library file is usually located here: ```C:\Users\[your username]\AppData\Roaming\Blender Foundation\Blender\[your blender version]\scripts\addons\KK-Blender-Porter-Pack\KK Shader.blend```