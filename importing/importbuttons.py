'''
This file performs the following operations
·	Delete default scene
·	Set view transform to Standard
·	Create KK log in the scripting tab
·	Save the import folder path
·	Import all pmx files from folder path
·	If the pmx file is an outfit, save the ID to the empty object of that pmx file
.   Invokes the other import operations based on what options were chosen on the panel
'''

import bpy, os, time

from ..interface.dictionary_en import t
from .. import common as c

class kkbp_import(bpy.types.Operator):
    bl_idname = "kkbp.kkbpimport"
    bl_label = "Import .pmx file"
    bl_description = t('kkbp_import_tt')
    bl_options = {'REGISTER', 'UNDO'}

    filepath : bpy.props.StringProperty(maxlen=1024, default='', options={'HIDDEN'})
    filter_glob : bpy.props.StringProperty(default='*.pmx', options={'HIDDEN'})
    
    def execute(self, context):
        #do this thing because cats does it
        if hasattr(bpy.context.scene, 'layers'):
            bpy.context.scene.layers[0] = True

        #delete the default scene if present
        if len(bpy.data.objects) == 3:
            for obj in ['Camera', 'Light', 'Cube']:
                if bpy.data.objects.get(obj):
                    bpy.data.objects.remove(bpy.data.objects[obj])

        #Set the view transform 
        bpy.context.scene.view_settings.view_transform = 'Standard'

        #save filepath for later
        bpy.context.scene.kkbp.import_dir = str(self.filepath)[:-9]

        #check if there is at least one "Outfit ##" folder inside of this directory
        #   if there isn't, then the user incorrectly chose the .pmx file inside of the outfit directory
        #   correct to the .pmx file inside of the root directory
        subdirs = [i[1] for i in os.walk(bpy.context.scene.kkbp.import_dir)][0]
        outfit_subdirs = [i for i in subdirs if 'Outfit ' in i]
        if not outfit_subdirs:
            bpy.context.scene.kkbp.import_dir = os.path.dirname(os.path.dirname(bpy.context.scene.kkbp.import_dir))
            c.kklog('User chose wrong pmx file. Defaulting to pmx file located at ' + str(bpy.context.scene.kkbp.import_dir), 'warn')

        #force pmx armature selection if exportCurrentPose in the Exporter Config json is true
        force_current_pose = c.get_json_file('KK_KKBPExporterConfig.json')['exportCurrentPose']
        if force_current_pose:
            bpy.context.scene.kkbp.armature_dropdown = 'C'

        #run functions based on selection
        if bpy.context.scene.kkbp.categorize_dropdown == 'A': #Automatic separation
            functions = [
                lambda:bpy.ops.kkbp.modifymesh('INVOKE_DEFAULT'),
                lambda:bpy.ops.kkbp.modifyarmature('INVOKE_DEFAULT'),
                lambda:bpy.ops.kkbp.modifymaterial('INVOKE_DEFAULT'),
                lambda:bpy.ops.kkbp.postoperations('INVOKE_DEFAULT'),
            ]
        elif bpy.context.scene.kkbp.categorize_dropdown == 'C': #Separate every piece
            functions = [
                lambda:bpy.ops.kkbp.modifymesh('INVOKE_DEFAULT'),
                lambda:bpy.ops.kkbp.modifyarmature('INVOKE_DEFAULT'),
                lambda:bpy.ops.kkbp.separatemeshes('EXEC_DEFAULT'),
                lambda:bpy.ops.kkbp.modifymaterial('INVOKE_DEFAULT'),
                lambda:bpy.ops.kkbp.postoperations('INVOKE_DEFAULT'),
            ]
        else: #SMR pipeline
            functions = [
                lambda:bpy.ops.kkbp.modifymesh('INVOKE_DEFAULT'),
                lambda:bpy.ops.kkbp.modifyarmature('INVOKE_DEFAULT'),
                lambda:bpy.ops.kkbp.separatemeshes('INVOKE_DEFAULT'),
            ]

        #run functions based on selection
        c.toggle_console()
        self.import_pmx_models()
        for index, function in enumerate(functions):
            print('Import function {} running'.format(index))
            function()
        c.toggle_console()
        bpy.context.scene.kkbp.plugin_state = 'imported'
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def import_pmx_models(self):
        c.kklog('Importing pmx files with mmdtools...')
        
        for subdir, dirs, files in os.walk(bpy.context.scene.kkbp.import_dir):
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
                        #keep track of outfit ID after pmx import. The active object is the outfit empty after import, so that's where its going
                        bpy.context.view_layer.objects.active['KKBP outfit ID'] = str(subdir[-2:])
        
                    #get rid of the text files mmd tools generates
                    if bpy.data.texts.get('Model'):
                            bpy.data.texts.remove(bpy.data.texts['Model'])
                            bpy.data.texts.remove(bpy.data.texts['Model_e'])
        c.initialize_timer()
        c.print_timer('Import PMX')