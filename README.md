# KK Blender Porter
A plugin and a shader to get you started with setting up an exported Koikatsu character in Blender.  

The plugin is a Blender addon that automates various actions, and the KK Shader is a .blend file that contains the shader, some material templates and some custom bone widgets.  
The changelog for the pack [can be found here.](https://github.com/FlailingFog/KK-Blender-Shader-Pack/blob/master/Changelog.md)
The [wiki also shows](https://github.com/FlailingFog/KK-Blender-Shader-Pack/wiki) some stuff

# Usage Instructions for V5
### Video instructions (with shading instructions)
The pack has a video tutorial series below: (*click for playlist*)


### Text instructions (without shading instructions)
The usage instructions are different based on what plugin you're using to export the model from Koikatsu.
#### If you're using the PMX plugin...
1a. Export the model with the pmx exporter  
1b. Export the textures with grey's mesh exporter  
1c. Import the pmx file into Blender using the big "Import Model" button in CATS  
1d. Finalize the pmx file with the Finalize PMX button  
#### If you're using Grey's Mesh Exporter...
1a. Open studio and load your character  
1b. Open the Grey's Mesh Exporter window  
1c. Enable the generic shader/materials option  
1d. Export the model and textures  
1e. Import the model into Blender with the Import FBX button  
1f. Scale the armature to the correct height  
1g. Scale the hand bones to the correct size using active element scaling mode on the Left/Right wrist bones 
1h. Scale the eyebrow and eye bones to the correct height using active element scaling mode on one of the mouth bones  
1i. Manually correct accessory positions by clicking on the object, finding it's N_move empty parent and then finding the N_move's ca_slot## empty parent. Scale down the ca_slot## empty until the accessory is the correct size  
1j.  FInalize the fbx file with the Finalize FBX button  
#### Then, for either type of export...
2. Manually combine the materials as shown in Part 1 of the current video series
3. Separate the hair object and rename it as shown in Part 2 of the current video series
4. Drag the face mc and body mc image files into the Textures folder (This folder is in the same directory as the fbx file is in) as shown in Part 2 of the current video series
5. Drag the KK shader.blend from this repository into the Textures folder
6. Click the Import KK Shader and Textures button and open the Textures folder
7. Manually shade everything as shown in Parts 3-8 of the current video series
