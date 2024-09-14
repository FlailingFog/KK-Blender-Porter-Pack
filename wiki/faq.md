---
layout: default
---

# Frequency asked questions

## I don't know what versions of the programs or addons to use
KKBP has been updated many times to keep up with newer Blender versions and is likely **not** backwards compatible, so the version of KKBP you need to use depends on what your Blender version is. Check the version table below if you are not using Blender 4.2 LTS

|Blender version|Last working KKBP version|PMX Importer dependency version|Koikatsu HF Patch version|Koikatsu Sunshine HF Patch version|Video guide link|
|---|---|---|---|---|---|
4.2.0 LTS|7.0.0|mmd_tools 4.2.2|HF Patch 3.28|HF Patch for KKS 1.17|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuveWvSwKg18l6mDSl5xl4x7o)|
|3.6.9 LTS|6.6.3|mmd_tools 2.9.2|HF Patch 3.22|HF Patch for KKS 1.7|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuvc-wbexi2vwSnVHnZFwkYNP)|
|3.5|6.5.0|mmd_tools 2.9.2|HF Patch 3.22|HF Patch for KKS 1.7|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuvc-wbexi2vwSnVHnZFwkYNP)|
|3.4|6.4.2|mmd_tools 2.9.2|HF Patch 3.22|HF Patch for KKS 1.7|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuvc-wbexi2vwSnVHnZFwkYNP)|
|3.3|6.2.1|mmd_tools 2.9.2|HF Patch 3.17|HF Patch for KKS 1.7|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuvc-wbexi2vwSnVHnZFwkYNP)|
|3.2|5.1.1|CATS Blender Plugin 0.19|HF Patch 3.13|--|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuvdEAbUzJxSqp61fNiPTFfwb)|
|2.93|4.3.0|CATS Blender Plugin 0.18|HF Patch 3.7|--|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuvd5eAOb3Ct1eovFAlgv-iwe)|
|2.91.2|4.2.1|CATS Blender Plugin 0.18|HF Patch 3.7|--|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuvd5eAOb3Ct1eovFAlgv-iwe)|
|2.83.4|3.06|CATS Blender Plugin 0.17|HF Patch 3.0|--|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuvfIJ20QrEzkoFl__F9VaRk2)|
|2.82.7|V2|[This outdated mmd_tools version](https://github.com/powroupi/blender_mmd_tools?tab=readme-ov-file)|--|--|[Here](https://www.youtube.com/playlist?list=PLhiuav2SCuvfx_IJw2TnYmPdWYwIzo7SO)|

## I'm using the right versions but it's still not working
**Some heavily modded characters will not import correctly.** Custom body mods, face mods and other mods that change body material names or shapekey names from the default will likely not work. Try exporting the default character that you get when you startup the character creator **with only the "Export Single Outfit" checkbox checked**, and double check the table for choosing the right version at the top of the page. If that works, try adding back each piece of clothing / hair until the item that causes the issue is found. If even the default character doesn't work, triple check you installed everything in the version table at the top of the page.

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq10.png)

## My top is missing
KKBP applies the alphamask to the body by default. If your character is supposed to be a shirtless guy, you can open the Body Shader on the body material...

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq1.png)

and disable the "Built in transparency toggle" to show the top of the body

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq2.png)

If you're using multiple outfits, the alphamask may change based on the outfit. If you need to change the alphamask you can open up the Body textures node group on the body material...

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq3.png)

and change the alphamask to the body_AM_## file that corresponds to your outfit

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq4.png)

## My clothes are missing
During import, KKBP tries to automatically hide any extra clothes objects. Make sure the object wasn't accidentally hidden by checking the children of the Outfit object in the outliner

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq5.png)

## I'm getting fully white textures after importing my character
The import script failed somewhere. In Blender, click the Scripting tab on the top of the window. Any errors will appear at the bottom of the log. A successful import log will end in "KKBP import finished"

## I'm getting fully white textures, but only in certain places
Some materials are supposed to have overlays, but KKBP cannot tell when that's supposed to happen, so it defaults to enabling overlays. Open the Shader of the clothes material that's showing up as white...

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq6.png)

Then try adjusting the sliders boxed below

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq7.png)

## My hair doesn't look right
Some hairs have "Maintex" textures, so KKBP will automatically make the Maintex active if it finds one. If that wasn't supposed to happen, open the Shader of the hair material...

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq8.png)

Then try adjusting the sliders boxed below

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/faq9.png)

## Blender crashed during import
Try importing again. It does that every once in a while. The import process can take around 1GB of RAM and 2GB of VRAM (or around 4.5GB of RAM and 3GB of VRAM on complex cards with many accessories), so if you're low on either of those it may crash because of that too.

