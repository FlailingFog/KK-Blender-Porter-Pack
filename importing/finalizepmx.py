'''
FINALIZE PMX
- Standardizes the armature to match the Koikatsu armature
- Sets rolls for all bones
- Optionally modifies the armature for IK usage
- Runs several other scripts when finished

some code stolen from MediaMoots here https://github.com/FlailingFog/KK-Blender-Shader-Pack/issues/29
'''

import bpy, math, time, traceback
from mathutils import Vector
from .. import common as c
 
        


  



    


class finalize_pmx(bpy.types.Operator):
    bl_idname = "kkbp.finalizepmx"
    bl_label = "Finalize .pmx files"
    bl_description = "Finalize imported .pmx files"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            last_step = time.time()

            scene = context.scene.kkbp
            modify_armature = scene.armature_dropdown

            c.kklog('\nFinalizing PMX file...')
            standardize_armature(modify_armature)
            reset_and_reroll_bones()
            if modify_armature in ['A', 'B']:
                c.kklog('Modifying armature...')
                modify_pmx_armature()
            rename_mmd_bones()
            remove_empty_vertex_groups()
            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            
            return {'FINISHED'}
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(finalize_pmx)
    
    # test call
    print((bpy.ops.kkbp.finalizepmx('INVOKE_DEFAULT')))