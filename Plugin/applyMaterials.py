'''
APPLY MATERIALS FOR ATLAS GENERATION
- Replaces all materials with their baked textures
- This makes the material templates compatible with the Material Combiner feature in CATS.

Usage:
- Select an object that has had its materials baked
- Select the folder that holds the textures in the Output Properties tab
- Run script

Tested in Blender 2.91
'''

import bpy
import os
from pathlib import Path

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

class apply_Materials(bpy.types.Operator):
    bl_idname = "kkb.applymaterials"
    bl_label = "Open baked materials folder"
    bl_description = "Open the folder that contains the baked materials"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory = StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob = StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context):
        def runIt():
            def showError(self, context):
                self.layout.label(text="No object selected")

            def sanitizeMaterialName(text):
                for ch in ['\\','`','*','<','>','.',':','?','|','/','\"']:
                    if ch in text:
                        text = text.replace(ch,'')
                return text

            def renameEyelineGroup(object):
                    try:
                        #KK shader V3.02 or lower has a group called mmd_shader that needs to be renamed to literally anything else
                        object.material_slots['Template Eyeline up'].material.node_tree.nodes['mmd_shader'].name = 'eyelinegroup'
                    except:
                        #that group was already renamed
                        pass

            def replaceOrSwap():
                #Get all files from the exported texture folder
                folderpath = self.directory
                fileList = Path(folderpath).glob('*.*')
                files = [file for file in fileList if file.is_file()]
                
                #Get object
                object = bpy.context.active_object
                
                #test if an object is active and selected. 
                try:
                    #object is active but not selected
                    if not object.select_get():
                        bpy.context.window_manager.popup_menu(showError, title="Error", icon='ERROR')
                        return
                except:
                    #active object is Nonetype
                    bpy.context.window_manager.popup_menu(showError, title="Error", icon='ERROR')
                    return
             
                renameEyelineGroup(object)
                
                for matslot in object.material_slots:
                    material = matslot.material
                    nodes = material.node_tree.nodes
                    links = material.node_tree.links
                    matname = sanitizeMaterialName(material.name)
                    #print(matname)
                    
                    #Then get the image for this material by matching the material name and the lightstate
                    #If there's multiple resolutions, choose the first file in the file list
                    currentImage = [file.name for file in files if (matname in file.name and 'light' in file.name)]
                    try:
                        imageName = currentImage[0]
                        imagePath = folderpath + imageName
                        
                        #If no KK export image node exists, create one.
                        #If a KK export image node already exists, check the type and toggle the state
                        #(ex. light is already loaded in, switch the textures to dark)
                        try:
                            try:
                                transpMix = nodes['KK export light']
                                
                                currentImage = [file.name for file in files if (matname in file.name and 'dark' in file.name)]
                                imageName = currentImage[0]
                                imagePath = folderpath + imageName
                                
                                #swap light textures for dark textures
                                bpy.ops.image.open(filepath=imagePath)
                                bpy.data.images[imageName].pack()
                                
                                imageNode = nodes['KK export light'].inputs[0].links[0].from_node
                                imageNode.image = bpy.data.images[imageName]
                                
                                transpMix.name = 'KK export dark'
                                
                            except:
                                transpMix = nodes['KK export dark']
                                
                                currentImage = [file.name for file in files if (matname in file.name and 'light' in file.name)]
                                imageName = currentImage[0]
                                imagePath = folderpath + imageName
                                
                                #swap dark textures for light textures
                                bpy.ops.image.open(filepath=imagePath)
                                bpy.data.images[imageName].pack()
                                
                                imageNode = nodes['KK export dark'].inputs[0].links[0].from_node
                                imageNode.image = bpy.data.images[imageName]
                                
                                transpMix.name = 'KK export light'
                                
                        except:
                            #get output node
                            outputNode = nodes['Material Output']
                            
                            #make mix node for image transparency and track the state of the image file
                            transpMix = nodes.new('ShaderNodeMixShader')
                            transpMix.location = outputNode.location[0], outputNode.location[1] - 300
                            transpMix.name = 'KK export light'
                            
                            #make transparency node
                            transpNode = nodes.new('ShaderNodeBsdfTransparent')
                            transpNode.location = transpMix.location[0] - 300, transpMix.location[1]
                            
                            #make emissive node
                            emissiveNode = nodes.new('ShaderNodeEmission')
                            emissiveNode.location = transpMix.location[0], transpMix.location[1] - 300
                            #Emissive node must be named 'Emission' or Material Combiner will fail
                            try:
                                nodes['Emission'].name = 'renamed for export'
                                emissiveNode.name = 'Emission'
                            except:
                                #image is the only image in the current view
                                pass
                            
                            #make image node
                            imageNode = nodes.new('ShaderNodeTexImage')
                            imageNode.location = emissiveNode.location[0]-300, emissiveNode.location[1]
                            #Image node must be named 'Image Texture' or Material Combiner will fail
                            try:
                                nodes['Image Texture'].name = 'renamed for export'
                                imageNode.name = 'Image Texture'
                            except:
                                #image is the only image in the current view
                                pass
                            
                            #Load in the image texture for the material
                            bpy.ops.image.open(filepath=imagePath)
                            bpy.data.images[imageName].pack()
                            imageNode.image = bpy.data.images[imageName]
                            
                            #link the image node to the emissive node, and send it through the transparency mix shader
                            links.new(imageNode.outputs[0], emissiveNode.inputs[0])
                            links.new(imageNode.outputs[1], transpMix.inputs[0])
                            
                            links.new(transpNode.outputs[0], transpMix.inputs[1])
                            links.new(emissiveNode.outputs[0], transpMix.inputs[2])

                            #Then send that through the main mix shader
                            mainMix = nodes.new('ShaderNodeMixShader')
                            mainMix.location = outputNode.location
                            outputNode.location = outputNode.location[0] + 300, outputNode.location[1]
                            links.new(transpMix.outputs[0], mainMix.inputs[2])
                            
                            #make the node currently plugged into the output node go through the mix shader
                            links.new(outputNode.inputs[0].links[0].from_node.outputs[0], mainMix.inputs[1])
                            links.new(mainMix.outputs[0], outputNode.inputs[0])
                            
                            #set the mix shader's factor to 1 so the baked image is showing instead of the material
                            mainMix.inputs[0].default_value=1
                    except:
                        print('no image found for this material: ' + matname)
            
            replaceOrSwap()
            
        #the second ultimate lazy move
        runIt()
                 
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

if __name__ == "__main__":
    bpy.utils.register_class(apply_Materials)

    # test call
    print((bpy.ops.kkb.applymaterials('INVOKE_DEFAULT')))
