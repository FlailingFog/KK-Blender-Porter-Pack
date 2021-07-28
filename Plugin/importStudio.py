import bpy
import os
from pathlib import Path

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

class import_studio(bpy.types.Operator):
    bl_idname = "kkb.importstudio"
    bl_label = "Import studio object"
    bl_description = "Open the folder containing the fbx files"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context):        
        def runIt():
            
            scene = context.scene.placeholder
            shader_type = scene.dropdown_box 
            shadow_type = scene.shadows_dropdown 
            blend_type = scene.blend_dropdown 
            
            #shader_dict = {"A": "principled", "B": "emission", "C": "kkshader", "D": "custom"}
            shadow_dict = {"A": "NONE", "B": "OPAQUE", "C": "CLIP", "D": "HASHED"}
            blend_dict = {"A": "OPAQUE", "B": "CLIP", "C": "HASHED", "D": "BLEND"}
            
            path = Path(self.directory).rglob('*')
            fileList = []
            for item in path:
                if '.fbx' in str(item):
                    fileList.append(item)
            
            for fbx in fileList:
                bpy.ops.import_scene.fbx(filepath=str(fbx))
                bpy.ops.object.mode_set(mode='OBJECT')
                for object in bpy.context.selected_objects:
                    if object.type == 'ARMATURE':
                        object.scale = [1, 1, 1]
                        if len(object.data.bones) == 1:
                            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                            bpy.data.objects.remove(object)
                            
                    elif object.type == 'MESH':
                        object.scale = [1, 1, 1]
                        for material_slot in object.material_slots:
                            material = material_slot.material
                            nodes = material.node_tree.nodes
                            
                            material.use_backface_culling = True
                            material.show_transparent_back = False
                            material.blend_method = blend_dict[blend_type]
                            material.shadow_method = shadow_dict[shadow_type]
                            
                            try:
                                    image_alpha = nodes['Principled BSDF'].inputs[19].links[0].from_node
                            except:
                                    #there was no image attached to the alpha node
                                    image_alpha = 'noalpha'
                            
                            try:
                                image = nodes['Principled BSDF'].inputs[0].links[0].from_node
                            except:
                                image = 'noimage'
                            
                            if image_alpha != 'noalpha':
                                material.node_tree.links.new(image_alpha.outputs[1], nodes['Principled BSDF'].inputs[19])
                            
                            #if set to emission
                            if shader_type == 'B': 
                                nodes.remove(nodes['Principled BSDF'])
                                output_node = nodes['Material Output']
                                transparency_mix = nodes.new('ShaderNodeMixShader')
                                transparency_mix.location = output_node.location[0], output_node.location[1] - 300
                                transparency_node = nodes.new('ShaderNodeBsdfTransparent')
                                transparency_node.location = transparency_mix.location[0] - 300, transparency_mix.location[1]
                                emissive_node = nodes.new('ShaderNodeEmission')
                                emissive_node.location = transparency_node.location[0], transparency_node.location[1] + 300
                                output_node.location = transparency_mix.location[0] + 300, transparency_mix.location[1]
                                
                                if image != 'noimage':
                                    material.node_tree.links.new(image.outputs[0], emissive_node.inputs[0])
                                material.node_tree.links.new(emissive_node.outputs[0], transparency_mix.inputs[2])
                                material.node_tree.links.new(transparency_node.outputs[0], transparency_mix.inputs[1])
                                if image_alpha != 'noalpha':
                                    material.node_tree.links.new(image_alpha.outputs[1], transparency_mix.inputs[0])
                                elif image != 'noimage':
                                    material.node_tree.links.new(image.outputs[1], transparency_mix.inputs[0])
                                                                    
                                material.node_tree.links.new(output_node.inputs[0], transparency_mix.outputs[0])
                            
                            elif shader_type == 'C':
                            #if set to KK shader
                                if image_alpha != 'noalpha':
                                    image_alpha = image_alpha.image
                                if image != 'noimage':
                                    image = image.image
                                if nodes['Normal Map'].inputs[1].links != ():
                                    normal = nodes['Normal Map'].inputs[1].links[0].from_node.image
                                else:
                                    normal = 'nonormal'

                                template = bpy.data.materials['Template General'].copy()
                                template.name = 'Template ' + material.name
                                material_slot.material = bpy.data.materials[template.name]
                                material = material_slot.material
                                nodes = material.node_tree.nodes

                                def imageLoad(group, node, image, raw = False):
                                    try:
                                        nodes[group].node_tree.nodes[node].image = bpy.data.images[image]
                                        if raw:
                                            currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image.colorspace_settings.name = 'Raw'
                                    except:
                                        print('Image not found, skipping: ' + image)

                                gen_type = material_slot.name.replace('Template ','')

                                #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique texture group
                                new_node = material_slot.material.node_tree.nodes['Gentex'].node_tree.copy()
                                material_slot.material.node_tree.nodes['Gentex'].node_tree = new_node
                                new_node.name = gen_type + ' Textures'
                                
                                if image != 'noimage':
                                    imageLoad('Gentex', 'Maintex', image.name, True)
                                if normal != 'nonormal':
                                    imageLoad('Gentex', 'MainNorm', image.name, True)

                                #Also, make a copy of the General shader node group, as it's unlikely everything using it will be the same color
                                new_node = material_slot.material.node_tree.nodes['KKShader'].node_tree.copy()
                                material_slot.material.node_tree.nodes['KKShader'].node_tree = new_node
                                new_node.name = gen_type + ' Shader'
                                
                                main_image = material_slot.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                                alpha_image = material_slot.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image

                                #If no main image was loaded in, there's no alpha channel being fed into the KK Shader.
                                #Unlink the input node and make the alpha channel pure white
                                if  main_image == None:
                                    getOut = material_slot.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].links[0]
                                    material_slot.material.node_tree.nodes['KKShader'].node_tree.links.remove(getOut)
                                    material_slot.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].default_value = (1,1,1,1)   

                                material.use_backface_culling = True
                                material.show_transparent_back = False
                                material.blend_method = blend_dict[blend_type]
                                material.shadow_method = shadow_dict[shadow_type]
                            
                            elif shader_type == 'D':
                                
                                if nodes['Normal Map'].inputs[1].links != ():
                                    normal = nodes['Normal Map'].inputs[1].links[0].from_node
                                else:
                                    normal = 'nonormal'
                                    
                                nodes.remove(nodes['Principled BSDF'])
                                output_node = nodes['Material Output']
                                custom_group = nodes.new('ShaderNodeGroup')
                                try:
                                    custom_group.node_tree = bpy.data.node_groups['Custom_studio']
                                except: 
                                    custom_group.node_tree = bpy.data.node_groups['custom_studio']
                                custom_group.location = output_node.location[0], output_node.location[1] - 300
                                
                                if image != 'noimage':
                                    material.node_tree.links.new(image.outputs[0], custom_group.inputs[0])
                                if image_alpha != 'noalpha':
                                    material.node_tree.links.new(image_alpha.outputs[1], custom_group.inputs[1])
                                if normal != 'nonormal':
                                    material.node_tree.links.new(normal.outputs[0], custom_group.inputs[2])
                                material.node_tree.links.new(output_node.inputs[0], custom_group.outputs[0])
            
        #I need a better way to do this
        runIt()
        
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_studio)
    
    # test call
    print((bpy.ops.kkb.importstudio('INVOKE_DEFAULT')))
