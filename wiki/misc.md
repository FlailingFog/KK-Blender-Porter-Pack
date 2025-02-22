## Misc

## Getting info from the Koikatsu console
The Bepinex debug console can be enabled by opening InitSetting.exe in your Koikatsu install folder and checking the Console box

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/misc1.png)

After you click the KKBP export button, the exporter will start logging it's progress in the console window. These will begin with ```[Info : Console]```

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/misc2.png)

## Getting info from the Blender console
On Windows, the Blender console is automatically opened when you import a model or bake a material. If an error occurs, the console will stay open so the user can read the error message. The console will automatically close when a model is successfully imported without errors. This log is also saved to Blender's Scripting tab on the top.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/misc3.png)

## Importing multiple characters
The KKBP importer can't import more than one character into the same file. You have to import characters separately, then merge them into one file by using File > Append, then append the character collection from the second character's .blend file.

## Finalizing materials
Using the "Finalize materials" button in the Export panel will convert all KKBP materials into PNG files. This is done by applying a geometry nodes modifier that flattens each mesh into a flat plane, then a picture is taken of the flat plane. The entire mesh is folded, so some very small gaps are left if there are transparent parts of the mesh. Because of this, a second filler plane is placed right under the folded mesh to fill in those gaps.

Because the mesh is folded, Z-fighting sometimes occurs and leads to a corrupt-looking image. This can be avoided by enabling the "Use old baker" checkbox in the KKBP panel. Using this option wil remove the folded mesh and only use the filler plane to bake images. The filler plane does not contain extra UV maps, so materials that rely on multiple UV maps like Hair will not bake properly with the old baker (for example the hair shine will not show up). Most other materials will bake properly with the old baker.

Only visible objects will be finalized, so if you have alternate outfit pieces or other outfits you want to bake, make sure they're visible in the Outliner before clicking the Finalize button.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/misc4.png)

## Working with Freestyle outlines
Mark any faces you don't want to be freestyled as freestyle faces, enable Freestyle in Blender, and disable the outline modifier on the body object. Try using these freestyle settings if you don't want to experiment

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/misc6.png)

Then try these compositor settings if you don't want to experiment

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/misc7.png)


## Armatures in Unity
The "Very Simple (SLOW)", "Simple" and "Unity - VRM / VRChat Compatible" options in the Export panel will make changes to the armature that allow Unity to automatically identify the bones needed for the Humanoid armature.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/misc8.png)

## Springbones in Unity
After the Koikatsu model is imported into Unity, springbones from the [UniVRM Unity package](https://github.com/vrm-c/UniVRM/releases) can be added to get realtime hair, skirt and accessory movement.

In the below example, the right twintail is given springbones. The springbone script is added to the twintail bone at the end of the chain. The twintail chain has four bones in the chain: Joint2_002 > Joint3 > Joint4 > Joint5, so the springbone script is added to Joint5. The root bones along the chain are then added to the "Root bone elements" section on the right. There are three remaining bones, so the size is set to 3.

![image](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/misc9.jpg)

[return to wiki home](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md)