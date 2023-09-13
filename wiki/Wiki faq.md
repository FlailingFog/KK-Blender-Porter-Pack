[return to wiki home](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md)

# Frequency asked questions

## My top is missing
KKBP applies the alphamask to the body by default. If your character is supposed to be a shirtless guy, you can open the Body Shader on the body material...

![image](https://user-images.githubusercontent.com/65811931/219536304-6d61fada-5f98-4001-a201-e46ed18a828f.png)

and disable the "Built in transparency toggle" to show the top of the body

![image](https://user-images.githubusercontent.com/65811931/219537294-e03c95fe-b328-476d-bb6c-05cb2ca636de.png)

If you're using multiple outfits, the alphamask may change based on the outfit. If you need to change the alphamask you can open up the Body textures node group on the body material...

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/dfbee2e0-2d59-42d5-8360-aeb5cee78ba8)

and change the alphamask to the body_AM_## file that corresponds to your outfit

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/3c891836-d420-4a36-b791-b617cb44a316)

## My clothes are missing
During import, KKBP tries to automatically hide any extra clothes objects. Make sure the object wasn't accidentally hidden by checking the children of the Outfit object in the outliner

![image](https://user-images.githubusercontent.com/65811931/219535179-28f30c3e-85a8-462f-be06-a22463e3e4c5.png)

## I'm getting fully white textures after importing my character
The import script failed somewhere. In Blender, click the Scripting tab on the top of the window. Any errors will appear at the bottom of the log. A successful import log will end in "KKBP import finished"

## I'm getting fully white textures, but only in certain places after importing my character
Some materials are supposed to have overlays, but KKBP cannot tell when that's supposed to happen, so it defaults to enabling overlays. Open the Shader of the clothes material that's showing up as white...

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/337ed901-0033-4f5a-8395-cf03f7797590)

Then try adjusting the sliders boxed below

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/7f1883f6-210a-4225-9163-9cfb59f22be6)

## My hair doesn't look right
Some hairs have "Maintex" textures, so KKBP will automatically make the Maintex active if it finds one. If that wasn't supposed to happen, open the Shader of the hair material...

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/77f99caf-df75-43ac-b8c2-d66c079d6357)

Then try adjusting the sliders boxed below

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/4eeb8e10-d3a2-4195-aa3a-0488a86f3c72)

## I got a "cf_pv_foot_L" / "cf_j_leg03_R" error during import
You accidentally chose the .pmx file inside of the "Outfit ##" folder instead of the .pmx file in the base export folder. Choose the correct .pmx file in the base export folder, or upgrade to KKBP 6.6+ (this version automagically makes sure you choose the right .pmx file).

## I upgraded to KKBP 6.6+ and still got a "cf_pv_foot_L" / "cf_j_leg03_R" error during import
Try importing again. It does that every once in a while.

## Blender crashed during import
Try importing again. It does that every once in a while.

## I don't know what versions of the programs or addons to use
KKBP has been updated many times to keep up with newer Blender versions, so the version of KKBP you need to use depends on what your Blender version is. [Check this table](https://github.com/FlailingFog/KK-Blender-Porter-Pack#required-software) for info on what versions to use.

## I'm using the right versions but it's still not working
Some heavily modded characters will not import correctly. Try exporting the default character that you get when you startup the character creator **with only the "Export Single Outfit" checkbox checked**, and [double check the table for choosing the right version](https://github.com/FlailingFog/KK-Blender-Porter-Pack#required-software). If that works, try adding back each piece of clothing / hair until the item that causes the issue is found. If that didn't work, [triple check you installed everything in the version table.](https://github.com/FlailingFog/KK-Blender-Porter-Pack#required-software)

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/7dbe96e1-b402-4ae8-b854-e18e2ee55273)

[return to wiki home](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md)