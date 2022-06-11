import bpy, time, traceback, statistics, bmesh, math, sys, mathutils
from pathlib import Path
from bpy.props import StringProperty

from math import radians

from mathutils import Matrix, Vector, Euler
from typing import NamedTuple
from pathlib import Path

#load plugin language
from bpy.app.translations import locale
if locale == 'ja_JP':
    from ..interface.dictionary_jp import t
else:
    from ..interface.dictionary_en import t

def kklog(log_text, type = 'standard'):
    if not bpy.data.texts.get('KKBP Log'):
        bpy.data.texts.new(name='KKBP Log')
        if bpy.data.screens.get('Scripting'):
            for area in bpy.data.screens['Scripting'].areas:
                if area.type == 'TEXT_EDITOR':
                    area.spaces[0].text = bpy.data.texts['KKBP Log']

    if type == 'error':
        log_text = '\nError:          ' + log_text
    elif type == 'warn':
        log_text = 'Warning:        ' + log_text
    bpy.data.texts['KKBP Log'].write(log_text + '\n')

    print(log_text)

def import_pmx_model(directory):
    #import the pmx file with mmd_tools
    bpy.ops.mmd_tools.import_model('EXEC_DEFAULT',
        files=[{'name': directory}],
        directory=directory,
        scale=1,
        types={'MESH', 'ARMATURE', 'MORPHS'},
        log_level='WARNING')
    
    #get rid of the text files mmd tools generates
    if bpy.data.texts.get('Model'):
            bpy.data.texts.remove(bpy.data.texts['Model'])
            bpy.data.texts.remove(bpy.data.texts['Model_e'])

class quick_import(bpy.types.Operator):
    bl_idname = "kkb.quickimport"
    bl_label = "Import .pmx file"
    bl_description = t('quick_import_tt')
    bl_options = {'REGISTER', 'UNDO'}

    filepath : StringProperty(maxlen=1024, default='', options={'HIDDEN'})
    filter_glob : StringProperty(default='*.pmx', options={'HIDDEN'})
    
    def execute(self, context):
        #do this thing because cats does it
        if hasattr(context.scene, 'layers'):
            context.scene.layers[0] = True

        #delete the default scene if present
        if len(bpy.data.objects) == 3:
            for obj in ['Camera', 'Light', 'Cube']:
                if bpy.data.objects.get(obj):
                    bpy.data.objects.remove(bpy.data.objects[obj])

        #Set the view transform 
        bpy.context.scene.view_settings.view_transform = 'Standard'

        #create KKLog
        kklog('====    KKBP Log    ====')

        #save filepath for later
        context.scene.kkbp.import_dir = str(self.filepath)

        #run commands based on selection
        if context.scene.kkbp.categorize_dropdown == 'A':
            commands = [
                import_pmx_model(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT'),
                bpy.ops.kkb.importeverything('INVOKE_DEFAULT'),
                bpy.ops.kkb.importcolors('EXEC_DEFAULT'),
            ]
        elif context.scene.kkbp.categorize_dropdown == 'B':
            commands = [
                import_pmx_model(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT'),
            ]
        elif context.scene.kkbp.categorize_dropdown == 'D':
            commands = [
                import_pmx_model(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatemeshes('INVOKE_DEFAULT'),
            ]
        else:
            commands = [
                import_pmx_model(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT'),
                bpy.ops.kkb.importeverything('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatemeshes('EXEC_DEFAULT'),
                bpy.ops.kkb.importcolors('EXEC_DEFAULT'),
            ]

        #run commands based on selection
        for command in commands:
            command

        if context.scene.kkbp.armature_dropdown == 'B' and context.scene.kkbp.categorize_dropdown in ['A', 'B', 'C']:
            bpy.ops.kkb.rigifyconvert('INVOKE_DEFAULT')
        
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class mat_import(bpy.types.Operator):
    bl_idname = "kkb.matimport"
    bl_label = "Load textures and colors"
    bl_description = t('mat_import_tt')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        # run bone drivers after
        if bpy.context.scene.kkbp.categorize_dropdown == 'D':
            bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT')
        
        bpy.ops.kkb.importeverything('INVOKE_DEFAULT')
        bpy.ops.kkb.importcolors('EXEC_DEFAULT')

        if context.scene.kkbp.armature_dropdown == 'B' and context.scene.kkbp.categorize_dropdown in ['A', 'B', 'C']:
            bpy.ops.kkb.rigifyconvert('INVOKE_DEFAULT')

        return {'FINISHED'}

