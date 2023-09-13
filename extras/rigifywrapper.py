'''
Wrapper for the rigifyscripts folder
'''
import bpy, traceback
from .. import common as c
from ..importing.postoperations import post_operations

class rigify_convert(bpy.types.Operator):
    bl_idname = "kkbp.rigifyconvert"
    bl_label = "Convert for rigify"
    bl_description = """Runs several scripts to convert a KKBP armature to be Rigify compatible"""
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            p = post_operations()
            p.retreive_stored_tags()
            p.apply_rigify()
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(rigify_convert)

    # test call
    print((bpy.ops.kkbp.rigifyconvert('INVOKE_DEFAULT')))

