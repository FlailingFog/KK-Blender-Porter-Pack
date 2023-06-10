'''
SHAPEKEYS SCRIPT
- Renames the face shapekeys to english
- Creates new, full shapekeys using the existing partial shapekeys
- Deletes the partial shapekeys if keep_partial_shapekeys is not set to True
'''

import bpy, time,traceback
from .. import common as c

class shape_keys(bpy.types.Operator):
    bl_idname = "kkbp.shapekeys"
    bl_label = "The shapekeys script"
    bl_description = "Fixes the shapekeys"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:

            return {'FINISHED'}
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(shape_keys)

    # test call
    print((bpy.ops.kkbp.shapekeys('INVOKE_DEFAULT')))
