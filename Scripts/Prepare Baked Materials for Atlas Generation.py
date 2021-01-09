'''
PREPARE MATERIALS FOR ATLAS GENERATION
- Replaces all materials with their baked textures
- This makes the material templates compatible with the Material Combiner feature in CATS.

Usage:
- Select an object that has had its materials baked in the 3D viewport
- Select the folder that holds the textures in the Output Properties tab
- Run script

Tested in Blender 2.91
'''

import bpy
from pathlib import Path

#Get all files from the exported texture folder
folderpath = bpy.context.scene.render.filepath
fileList = Path(folderpath).glob('*.*')
files = [file for file in fileList if file.is_file()]

#Get object
object = bpy.context.active_object
    
for matslot in object.material_slots:
    material = matslot.material
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    
    #Then get the image for this material by matching the material name and the lightstate
    #If there's multiple resolutions, choose the first file in the file list
    currentImage = [file.name for file in files if (material.name in file.name and 'light' in file.name)]
    imageName = currentImage[0]
    imagePath = folderpath + imageName
    
    if currentImage:
        #If no KK export image node exists, create one.
        #If a KK export image node already exists, check the type and toggle the state
        #(ex. light is already loaded in, switch the textures to dark)
        try:
            try:
                imageNode = nodes['KK export light']
                currentImage = [file.name for file in files if (material.name in file.name and 'dark' in file.name)]
                imageName = currentImage[0]
                imagePath = folderpath + imageName
                
                #Load the dark image texture
                bpy.ops.image.open(filepath=imagePath)
                bpy.data.images[imageName].pack()
                imageNode.image = bpy.data.images[imageName]
                imageNode.name = 'KK export dark'
            except:
                imageNode = nodes['KK export dark']
                currentImage = [file.name for file in files if (material.name in file.name and 'light' in file.name)]
                imageName = currentImage[0]
                imagePath = folderpath + imageName
                
                #Load the dark image texture
                bpy.ops.image.open(filepath=imagePath)
                bpy.data.images[imageName].pack()
                imageNode.image = bpy.data.images[imageName]
                imageNode.name = 'KK export light'
                
        except:
            #get output node
            outputNode = nodes['Material Output']
            
            #make emissive node
            emissiveNode = nodes.new('ShaderNodeEmission')
            emissiveNode.location = outputNode.location[0], outputNode.location[1] - 300
            
            #make image node
            imageNode = nodes.new('ShaderNodeTexImage')
            imageNode.location = emissiveNode.location[0]-300, emissiveNode.location[1]
            imageNode.name = 'KK export light'
            
            #Load in the image texture for the material
            bpy.ops.image.open(filepath=imagePath)
            bpy.data.images[imageName].pack()
            imageNode.image = bpy.data.images[imageName]
            
            #link the image node to the emissive node, and send it through a mix shader
            links.new(imageNode.outputs[0], emissiveNode.inputs[0])
            mixShader = nodes.new('ShaderNodeMixShader')
            mixShader.location = outputNode.location
            outputNode.location = outputNode.location[0] + 300, outputNode.location[1]
            links.new(emissiveNode.outputs[0], mixShader.inputs[2])
            
            #make the node currently plugged into the output node go through the mix shader
            links.new(outputNode.inputs[0].links[0].from_node.outputs[0], mixShader.inputs[1])
            links.new(mixShader.outputs[0], outputNode.inputs[0])
            
            #set the mix shader's factor to 1 so the image is showing instead of the material
            mixShader.inputs[0].default_value=1
    else:
        print('no image found for this material: ' + material)
        
print({'FINISHED'})
