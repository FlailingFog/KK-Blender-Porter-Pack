---
layout: default
---

# Mesh

## Face shapekeys
Shapekeys from koikatsu are preserved when importing. Only the Body object will have shapekeys.  
The Face shapekeys originally come from the game as partial shapekeys; For example, if you wanted to activate the "Angry" mouth shapekey you would need to activate the angry lips shapekey, the angry tongue shapekey, the angry teeth shapekey and the angry nose shapekey to get the full expression. KKBP combines these shapekeys into a single shapekey called "KK Mouth Angry" for convienience. The same is done for the eye shapekeys. No modifications are made to the Eyebrow shapekeys. Once all shapekeys are combined, the partial shapekeys are deleted to clean up the shapekey list. If you want to preserve the partial shapekeys, or stop the plugin from editing the shapekeys at all you can do that by changing the Shapekey settings in the KKBP panel.  

Shapekeys are generated using the shapekey names of the base Type 1 head. Compatibility for different headmods can vary because different headmods can have different names for the shapekeys (such as the Yelan headmod). These differently named headmod shapekeys can be added to the translate_shapekeys list in [modifymesh.py](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/importing/modifymesh.py) to allow them to work. If a headmod has not been added to the list, no KK shapekeys will be created and the original headmod shapekeys will be preserved.

All shapekeys can be found by selecting the Body object and going to the Data tab:  

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/mesh1.png)

## Tear and gag eye shapekeys
The gag eye and tear meshes are separated from the Body. Their shapekeys are automatically linked to the Body's shapekeys through drivers. This way you don't have to find the small tears object to change the shapekey, you can just click on the body and change the tear shapekey that way. The tear and gag eye meshes shrink into the head when not active. If your character has a really small head, you may have to [edit the shapekeys as shown in this issue](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/338).

Tears and gag eyes can be activated in the shapekey panel

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/mat6p1.png)

## Body seams
The Body has seams in several places (middle of neck, middle of chest, around mouth). These are visible in some situations, so a "merge by distance" operation can performed on the body to remove the seams. This unfortunately [modifies some bone weights as seen in this issue](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/69). It will also screw up the uv map on the material atlas near the neck. The "merge by distance" operation will only occur if you enable the "Fix body seams" option on the Import panel. 
Clothes also have seams, but these seams are not automatically merged when this option is enabled.

## Object organization
This is the default object organization you'll get after importing. Some objects like the variations will be missing if you didn't enable them in the Koikatsu KKBP Exporter panel.

![image](https://raw.githubusercontent.com/FlailingFog/flailingfog.github.io/master/assets/images/mesh2.png)