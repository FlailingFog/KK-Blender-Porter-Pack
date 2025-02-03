import bpy
from ..interface.dictionary_en import t
from .. import common as c

class mat_comb_switch(bpy.types.Operator):
    bl_idname = "kkbp.matcombswitch"
    bl_label = "Material combiner switch"
    bl_description = t('mat_comb_switch_tt')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #toggle textures for the combiner script
        for obj in [o for o in bpy.data.collections[c.get_name() + '.001'].all_objects if not o.hide_get() and o.type == 'MESH']:
            for mat in [mat_slot.material for mat_slot in obj.material_slots if mat_slot.material.get('simple')]:
                nodes = mat.node_tree.nodes
                #find the image node
                image_node = None
                for node in nodes:
                    if node.type == 'TEX_IMAGE':
                        image_node = node
                if image_node:
                    #toggle light / dark state
                    image_node.image = nodes['textures'].node_tree.nodes['dark' if image_node.image == nodes['textures'].node_tree.nodes['light'].image else 'light'].image
            context.view_layer.objects.active = obj
            bpy.ops.object.material_slot_remove_unused()

        return {'FINISHED'}
