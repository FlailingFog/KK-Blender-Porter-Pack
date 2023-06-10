import bpy, os, traceback
import bgl
import gpu
import json
from .. import common as c
from .darkcolors import clothes_dark_color, hair_dark_color, skin_dark_color
import numpy as np
from pathlib import Path
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
#from gpu_extras.batch import batch_for_shader
from bpy.props import StringProperty, BoolProperty

from ..interface.dictionary_en import t









      


class import_colors(bpy.types.Operator):
    bl_idname = "kkbp.importcolors"
    bl_label = "Open Export folder"
    bl_description = t('import_colors_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None

    def execute(self, context):
        c.kklog('\nConverting Colors...')
        print(context.scene.kkbp.import_dir)
        try:
            if self.directory == '':
                directory = context.scene.kkbp.import_dir
            else:
                directory = self.directory

            error = checks(directory)

            if not error:
                load_luts(lut_light, lut_dark)
                convert_main_textures(lut_light)
                load_json_colors(directory, lut_light, lut_dark, lut_selection)

            
            bpy.data.objects['Armature'].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects['Armature']

            return {'FINISHED'}
        
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

if __name__ == "__main__":
    bpy.utils.register_class(import_colors)
    print((bpy.ops.kkbp.importcolors('INVOKE_DEFAULT')))

