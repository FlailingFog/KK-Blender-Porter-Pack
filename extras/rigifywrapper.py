'''
Wrapper for the rigifyscripts folder
'''
import bpy, traceback
from .. import common as c
from ..importing.postoperations import post_operations
from ..interface.dictionary_en import t

class rigify_convert(bpy.types.Operator):
    bl_idname = "kkbp.rigifyconvert"
    bl_label = "Convert for rigify"
    bl_description = t('rigify_convert_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            bpy.context.scene.kkbp.armature_dropdown = 'B'
            post_operations.retreive_stored_tags()
            post_operations.apply_rigify()
            return {'FINISHED'}
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}


