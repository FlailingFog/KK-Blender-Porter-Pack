'''
This file performs the following operations


'''

import bpy
from .. import common as c

class modify_material(bpy.types.Operator):
    bl_idname = "kkbp.modifymaterial"
    bl_label = bl_idname
    bl_description = bl_idname
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            self.get_body_material_names()


            return {'FINISHED'}
        except Exception as error:
            c.handle_error(self, error)
            return {"CANCELLED"}

    # %% Main functions
    def remove_unused_material_slots(self):
        for object in [o for o in bpy.data.objects if o.type == 'MESH']:
            c.switch(object, 'object')
            bpy.ops.object.material_slot_remove_unused()
    
    # %% Supporting functions

if __name__ == "__main__":
    bpy.utils.register_class(modify_material)

    # test call
    print((bpy.ops.kkbp.modifymaterial('INVOKE_DEFAULT')))
