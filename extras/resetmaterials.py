import bpy
from ..interface.dictionary_en import t

class reset_materials(bpy.types.Operator):
    bl_idname = "kkbp.resetmaterials"
    bl_label = "Reset KKBP materials"
    bl_description = t('reset_mats_tt')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #setup materials for the combiner script
        for obj in [o for o in bpy.data.collections['Collection'].all_objects if not o.hide_get() and o.type == 'MESH']:
            for mat in [mat_slot.material for mat_slot in obj.material_slots if 'KK ' in mat_slot.material.name and 'Outline ' not in mat_slot.material.name and ' Outline' not in mat_slot.material.name and ' Atlas' not in mat_slot.material.name]:
                if bpy.data.materials.get(mat.name + '-ORG'):
                    org_mat = bpy.data.materials.get(mat.name + '-ORG')
                    org_mat.node_tree.nodes['baked_group'].inputs[3].default_value = 0
                    mat.user_remap(org_mat)
        return {'FINISHED'}
