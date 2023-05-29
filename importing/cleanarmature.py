'''
AFTER CATS (CLEAN ARMATURE) SCRIPT
- Hides all bones that aren't in the bonelists
- Connects the finger bones that CATS sometimes misses for koikatsu imports
- Corrects the toe bones on the better penetration armature
Usage:
- Run the script
'''

import bpy, time, traceback
from .finalizepmx import survey_vertexes
from .. import common as c



class clean_armature(bpy.types.Operator):
    bl_idname = "kkbp.cleanarmature"
    bl_label = "Clean armature"
    bl_description = "Makes the armature less of an eyesore"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            last_step = time.time()

            c.kklog('\nCategorizing bones into armature layers...', 'timed')

            reorganize_armature_layers()
            if bpy.context.scene.kkbp.categorize_dropdown in ['A', 'B']:
                visually_connect_bones()
            move_accessory_bones(context)
            
            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')

            return {'FINISHED'}
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
if __name__ == "__main__":
    bpy.utils.register_class(clean_armature)

    # test call
    print((bpy.ops.kkbp.cleanarmature('INVOKE_DEFAULT')))
