import bpy
from ..interface.dictionary_en import t
from .. import common as c

class reset_materials(bpy.types.Operator):
    bl_idname = "kkbp.resetmaterials"
    bl_label = "Reset KKBP materials"
    bl_description = t('reset_mats_tt')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #setup materials for the combiner script
        for obj in [o for o in bpy.data.collections[c.get_name()].all_objects if not o.hide_get() and o.type == 'MESH']:
            for mat in [mat_slot.material for mat_slot in obj.material_slots if mat_slot.material.get('simple')]:
                if bpy.data.materials.get(mat.name + '-ORG'):
                    org_mat = bpy.data.materials.get(mat.name + '-ORG')
                    mat.user_remap(org_mat)
        return {'FINISHED'}
