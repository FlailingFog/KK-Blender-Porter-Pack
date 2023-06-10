import bpy, os, traceback, json, time, sys
from pathlib import Path
from .. import common as c
from .cleanarmature import get_bone_list
from .darkcolors import create_darktex

 

class import_everything(bpy.types.Operator):
    bl_idname = "kkbp.importeverything"
    bl_label = "Finish separating objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            last_step = time.time()
            directory = context.scene.kkbp.import_dir
            
            c.kklog('\nApplying material templates and textures...')

            scene = context.scene.kkbp
            use_fake_user = scene.use_material_fake_user
            single_outline_mode = scene.use_single_outline
            modify_armature = scene.armature_dropdown in ['A', 'B']

            #these methods will return true if an error was encountered to make sure the error popup shows
            template_error = get_templates_and_apply(directory, use_fake_user)
            if template_error:
                return {'FINISHED'}
            
            #redraw the UI after each operation to let the user know the plugin is actually doing something
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            texture_error = get_and_load_textures(directory)
            if texture_error:
                return {'FINISHED'}
            
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
            add_outlines(single_outline_mode)
            if modify_armature and bpy.data.objects['Armature'].pose.bones["Spine"].custom_shape == None:
                #c.kklog(str(time.time() - last_step))
                c.kklog('Adding bone widgets...')
                apply_bone_widgets()
            hide_widgets()
            
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
            #clean data
            clean_orphan_data()

            if context.scene.kkbp.categorize_dropdown in ['A', 'B', 'C']:
                

            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            return {'FINISHED'}

        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_everything)

    # test call
    print((bpy.ops.kkbp.importeverything('INVOKE_DEFAULT')))
