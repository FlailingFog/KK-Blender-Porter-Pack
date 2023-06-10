import bpy, json, time, traceback
from .. import common as c
from ..extras.linkshapekeys import link_keys



class separate_body(bpy.types.Operator):
    bl_idname = "kkbp.separatebody"
    bl_label = "The separate body script"
    bl_description = "Separates the Body, shadowcast and bonelyfans into separate objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            last_step = time.time()
            c.kklog('\nSeparating body, clothes, hair, hitboxes and shadowcast, then removing duplicate materials...')
            
            clean_body()
            #make tear and gageye shapekeys if shapekey modifications are enabled
            if context.scene.kkbp.shapekeys_dropdown != 'C':
                make_tear_and_gag_shapekeys()
            add_freestyle_faces()
            remove_duplicate_slots()
            separate_everything(context)
            if context.scene.kkbp.fix_seams:
                fix_body_seams()
            cleanup()

            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            return{'FINISHED'}

        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
