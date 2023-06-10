'''
This file performs the following operations

·	Hide all alternate clothing pieces and indoor shoes and other outfits
    (show only the first outfit if it’s present, if not, count up until the
    first outfit collection is found and use that one)
·	Clean orphaned data as long as users = 0 and fake user = False
'''

import bpy
from .. import common as c

class post_operations(bpy.types.Operator):
    bl_idname = "kkbp.postoperations"
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
    def hide_unused_objects(self):
        if bpy.data.objects.get('Tongue (Rigged)'):
            bpy.data.objects['Tongue (Rigged)'].hide = True
        for object in self.outfit_alternates:
            object.hide = True
    
    # %% Supporting functions

if __name__ == "__main__":
    bpy.utils.register_class(post_operations)

    # test call
    print((bpy.ops.kkbp.postoperations('INVOKE_DEFAULT')))
