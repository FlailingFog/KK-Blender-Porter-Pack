#wrapper for blender's File > Export > FBX dialog

import bpy, traceback, time
from ..importing.importbuttons import kklog
from bpy.props import StringProperty

#load plugin language
from bpy.app.translations import locale
if locale == 'ja_JP':
    from ..interface.dictionary_jp import t
elif locale == 'zh_CN':
    from ..interface.dictionary_zh import t
else:
    from ..interface.dictionary_en import t

class export_fbx(bpy.types.Operator):
    bl_idname = "kkb.exportfbx"
    bl_label = "Export model"
    bl_description = t('export_fbx_tt')
    bl_options = {'REGISTER', 'UNDO'}

    filepath : StringProperty(maxlen=1024, default='', options={'HIDDEN'})
    filter_glob : StringProperty(default='*.fbx', options={'HIDDEN'})

    def execute(self, context):
        last_step = time.time()
        kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
        try:
            kklog('Exporting model to fbx format...')
            bpy.ops.export_scene.fbx('EXEC_DEFAULT',
                filepath=self.filepath if self.filepath[-4:] == '.fbx' else self.filepath+'.fbx',
                object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
                use_mesh_modifiers=False,
                add_leaf_bones=False,
                bake_anim=False,
                apply_scale_options='FBX_SCALE_ALL',
                path_mode='COPY',
                embed_textures=True,
                mesh_smooth_type='OFF')
            return {'FINISHED'}
        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

if __name__ == "__main__":
    bpy.utils.register_class(export_fbx)

    # test call
    print((bpy.ops.kkb.selectbones('INVOKE_DEFAULT')))
