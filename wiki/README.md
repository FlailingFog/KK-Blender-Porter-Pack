## How to use the exporter

1. Install the <a style="font-weight:bold" href="https://github.com/ManlyMarco/KK-HF_Patch"> HF Patch for Koikatsu</a>, or the <a style="font-weight:bold" href="https://github.com/ManlyMarco/KKS-HF_Patch"> HF Patch for Koikatsu Sunshine</a>.  
**Pre-modded repacks will not work** unless you update with the repack's auto-updater or install the HF patch.  
[Click here for repack workaround #1.](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/465#issuecomment-2602969013)  
[Click here for repack workaround #2.](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/523)  
[Click here for repack workaround #3.](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/560)

1. Find your Koikatsu install directory and drag the <a style="font-weight:bold" href="https://github.com/FlailingFog/KK-Blender-Porter-Pack/releases">KKBP exporter</a> into the /bepinex/plugins/ folder

1. Start Koikatsu and open the Character Maker
   
1. Enable the KKBP Exporter window.  
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/exportpanel2.png)

1. Change your export options. [See this page for an explanation of all export options](export_panel).
   
1. Click the "Export Model for KKBP" button at the top of the screen. This may take a few minutes depending on your computer hardware.
   
3. A folder in your Koikatsu install directory will popup when the export is finished

## How to use the importer
1. Open Blender 4.2 LTS. **Other versions are not guaranteed to work.** [Click here if you are not using Blender 4.2](faq)
   
1. Install <a style="font-weight:bold" href="https://extensions.blender.org/add-ons/mmd-tools/">mmd_tools</a> in Blender
   
1. Install <a style="font-weight:bold" href="https://github.com/FlailingFog/KK-Blender-Porter-Pack/releases">KKBP Importer 8.0.0</a> in Blender
   
1. After you install both addons, you can click the "Import model" button in the KKBP panel. [An explanation of all import options can be found here](import_panel)   
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/importpanel2.png)

1. Choose the .pmx file from the export folder 
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/importpanel3.png)

1. The blender console will appear and begin importing the model. This may take a few minutes depending on your computer hardware  
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/importpanel4.png)

1. Check there were no errors during import in the scripting tab. A successful import will end in "KKBP import finished in XX minutes"  
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/importpanel5.png)

## Editing the model in Blender
1. If there were no errors, you can start using the model as is by activating the material preview on the top right. If your computer is taking a long time to compile all the shaders (longer than 60 seconds), it is recommended to finalize the materials by clicking the button in the KKBP panel. If you finalize the materials then the shaders will compile very quickly. Finalizing the materials can take anywhere from 5 to 30 minutes depending on your hardware and model.  
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/importpanel6.png)

1. If there were no errors but something doesn't look right, check the [FAQ](faq) or the [material breakdown](material_breakdown) page for information on how to edit the materials. 

1. If you got an error during import, check the [FAQ](faq), or search [the issues page on the Github repo](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues) to see if anyone else had the same issue as you.

## Exporting from Blender to fbx:

1. Enable the Atlas option, then click the Finalize Materials button in the KKBP panel  
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/atlasoption.png)
   
1. This does three things
    * Finalizes all of the materials to png files and saves them to the baked_files folder in the export folder
    * Creates an atlas file for your body / hair / clothes and saves them to the atlas_files folder in your export folder
    * Creates a new collection that uses the atlas
   
1. Hide the original collection in the outliner and show the new collection
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/importpanel7.png)

1. If you want to reduce the bone count, or convert the model's armature for VRM / VRChat / Unreal Engine, click the "Prep for target application" button.   
   
1. Click the export button in the collection tab to export an fbx file to the atlas_files folder in the export folder
![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/importpanel8.png)
