import bpy, time, traceback
import os
from bpy.props import StringProperty

from ..interface.dictionary_en import t

def toggle_console():
    #show the console so you can see some kind of progression
    try:
        bpy.ops.wm.console_toggle()
    except:
        return #only available on windows so it might error out for other platforms

def kklog(log_text, type = 'standard'):
    if not bpy.data.texts.get('KKBP Log'):
        bpy.data.texts.new(name='KKBP Log')
        if bpy.data.screens.get('Scripting'):
            for area in bpy.data.screens['Scripting'].areas:
                if area.type == 'TEXT_EDITOR':
                    area.spaces[0].text = bpy.data.texts['KKBP Log']

    if type == 'error':
        log_text = '\nError:          ' + str(log_text)
    elif type == 'warn':
        log_text = 'Warning:        ' + str(log_text)
    bpy.data.texts['KKBP Log'].write(str(log_text) + '\n')

    print(str(log_text))

def import_pmx_models(directory):

    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if (file == 'model.pmx'):
                pmx_path = os.path.join(subdir, file)
                outfit = 'Outfit' in subdir
                
                #import the pmx file with mmd_tools
                bpy.ops.mmd_tools.import_model('EXEC_DEFAULT',
                    files=[{'name': pmx_path}],
                    directory=pmx_path,
                    scale=1,
                    clean_model = False,
                    types={'MESH', 'ARMATURE', 'MORPHS'} if not outfit else {'MESH'} ,
                    log_level='WARNING')
                
                if outfit:
                    #keep track of outfit ID after pmx import. The active object is the empty after import, so that's where its going
                    bpy.context.view_layer.objects.active['KKBP outfit ID'] = str(subdir[-2:])
    
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
        kklog('Importing pmx files with mmdtools...')

        #save filepath for later
        context.scene.kkbp.import_dir = str(self.filepath)[:-9]

        #run commands based on selection
        if context.scene.kkbp.categorize_dropdown == 'A': #Automatic separation
            commands = [
                toggle_console(),
                import_pmx_models(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT'),
                bpy.ops.kkb.importeverything('INVOKE_DEFAULT'),
                bpy.ops.kkb.importcolors('EXEC_DEFAULT'),
                toggle_console(),
            ]
        elif context.scene.kkbp.categorize_dropdown == 'B': #Manual separation
            commands = [
                import_pmx_models(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT'),
            ]
        elif context.scene.kkbp.categorize_dropdown == 'C': #Separate every piece
            commands = [
                toggle_console(),
                import_pmx_models(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatemeshes('EXEC_DEFAULT'),
                bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT'),
                bpy.ops.kkb.importeverything('INVOKE_DEFAULT'),
                bpy.ops.kkb.importcolors('EXEC_DEFAULT'),
                toggle_console(),
            ]
        else: #SMR pipeline
            commands = [
                import_pmx_models(context.scene.kkbp.import_dir),
                bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT'),
                bpy.ops.kkb.shapekeys('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatebody('INVOKE_DEFAULT'),
                bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT'),
                bpy.ops.kkb.separatemeshes('INVOKE_DEFAULT'),
            ]

        #run commands based on selection, and show progress bar
        #wm = bpy.context.window_manager
        #wm.progress_begin(0, len(commands))
        for i, command in enumerate(commands):
            command
            #wm.progress_update(i)
        #wm.progress_end()

        if context.scene.kkbp.armature_dropdown == 'B' and context.scene.kkbp.categorize_dropdown in ['A', 'B', 'C']:
            bpy.ops.kkb.rigifyconvert('INVOKE_DEFAULT')
        
        if context.scene.kkbp.categorize_dropdown in ['A', 'B', 'C']:
            #set the viewport shading
            my_areas = bpy.context.workspace.screens[0].areas
            my_shading = 'MATERIAL'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'

            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading 

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

