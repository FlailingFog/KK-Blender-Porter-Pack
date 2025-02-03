#This script takes a source hair material and copies all of it's attributes to all target hair materials on the same object
# so you don't have to manually change every single hair material yourself

import bpy
from ..interface.dictionary_en import t

class link_hair(bpy.types.Operator):
    bl_idname = "kkbp.linkhair"
    bl_label = "Link hair"
    bl_description = t('link_hair_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #get the currently selected hair material
        object = bpy.context.object
        source_material = object.active_material
        for type in ['light', 'dark']:
            if source_material.node_tree.nodes.get(type):
                for target_material in [s.material for s in object.material_slots if s.material.get('hair')]:
                    if target_material.node_tree.nodes.get(type):
                        #copy all of the hair settings for this node group to the target material
                        for index, input in enumerate(target_material.node_tree.nodes[type].inputs):
                            input.default_value = source_material.node_tree.nodes[type].inputs[index].default_value

        return {'FINISHED'}

