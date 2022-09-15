'''
APPLY MATERIALS FOR ATLAS GENERATION
- Replaces all materials with their baked textures
- This allows the Material Combiner feature in CATS to recognize the baked textures

Usage:
- Select an object that has had its materials baked
- Select the folder that holds the textures in the Output Properties tab
- Run script
'''

import bpy, os, traceback
from ..importing.importbuttons import kklog
from pathlib import Path
from.bakematerials import sanitizeMaterialName, showError

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

#load plugin language
from bpy.app.translations import locale
if locale == 'ja_JP':
    from ..interface.dictionary_jp import t
else:
    from ..interface.dictionary_en import t

def create_atlas_helpers():
    object = bpy.context.active_object
    for matslot in object.material_slots:
        
        material = matslot.material
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        #print(matname)
        if not nodes.get('KK export'):
            #get output node
            outputNode = nodes['Material Output']

            #make mix node for image transparency and track the state of the image file
            transpMix = nodes.new('ShaderNodeMixShader')
            transpMix.location = outputNode.location[0], outputNode.location[1] - 300
            transpMix.name = 'KK export'

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

            #link the image node to the emissive node, and send it through the transparency mix shader
            links.new(imageNode.outputs[0], emissiveNode.inputs[0])
            links.new(imageNode.outputs[1], transpMix.inputs[0])

            links.new(transpNode.outputs[0], transpMix.inputs[1])
            links.new(emissiveNode.outputs[0], transpMix.inputs[2])

            #Then send that through the main mix shader
            mainMix = nodes.new('ShaderNodeMixShader')
            mainMix.name = 'KK Mix'
            mainMix.location = outputNode.location
            outputNode.location = outputNode.location[0] + 300, outputNode.location[1]
            links.new(transpMix.outputs[0], mainMix.inputs[2])

            #make the node currently plugged into the output node go through the mix shader
            links.new(outputNode.inputs[0].links[0].from_node.outputs[0], mainMix.inputs[1])
            links.new(mainMix.outputs[0], outputNode.inputs[0])

            #set the mix shader's factor to 1 so the baked image is showing instead of the material
            mainMix.inputs[0].default_value=1

def replace_images(folderpath, apply_type):
    fileList = Path(folderpath).glob('*.*')
    files = [file for file in fileList if file.is_file()]
    
    object = bpy.context.active_object
    for matslot in object.material_slots:
        material = matslot.material
        nodes = material.node_tree.nodes
        matname = sanitizeMaterialName(material.name)
        #print(matname)
        
        #Check if there's any images for this material
        #if there's no matching images, skip to the next material
        if apply_type == 'A':
            currentImage = [file.name for file in files if (matname in file.name and 'light' in file.name)]
        elif apply_type == 'B':
            currentImage = [file.name for file in files if (matname in file.name and 'dark' in file.name)]
        else:
            currentImage = [file.name for file in files if (matname in file.name and 'normal' in file.name)]
        if not currentImage:
            kklog("No {} baked image found for {}".format('light' if apply_type == 'A' else 'dark' if apply_type == 'B' else 'normal', matname))
            continue

        imageName = currentImage[0]
        imagePath = folderpath + imageName

        #load the image into the image node
        transpMix = nodes['KK export']
        imageName = currentImage[0]
        imagePath = folderpath + imageName

        bpy.ops.image.open(filepath=imagePath, use_udim_detecting=False)
        bpy.data.images[imageName].pack()
        
        imageNode = transpMix.inputs[0].links[0].from_node
        imageNode.image = bpy.data.images[imageName]

        nodes['KK Mix'].inputs[0].default_value = 1

class apply_materials(bpy.types.Operator):
    bl_idname = "kkb.applymaterials"
    bl_label = "Open baked materials folder"
    bl_description = t('apply_mats_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context):
        try:
            scene = context.scene.kkbp
            apply_type = scene.atlas_dropdown

            #Get all files from the exported texture folder
            folderpath = scene.import_dir if scene.import_dir != 'cleared' else self.directory #if applymaterials is run right after bake, use import dir as a temp directory holder
            scene.import_dir == 'cleared'

            for ob in [obj for obj in bpy.context.view_layer.objects if obj.type == 'MESH']:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = ob
                ob.select_set(True)
                create_atlas_helpers()
                replace_images(folderpath, apply_type)
            
            return {'FINISHED'}
        
        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

if __name__ == "__main__":
    bpy.utils.register_class(apply_materials)

    # test call
    print((bpy.ops.kkb.applymaterials('INVOKE_DEFAULT')))
