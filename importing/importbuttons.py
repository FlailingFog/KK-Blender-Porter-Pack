'''
This file performs the following operations
·	Delete default scene
·	Set view transform to Standard
·	Create KK log in the scripting tab
·	Save the import folder path and character name for later
·	Import all pmx files from folder path, then tag them for later
.   Invokes the other import operations based on what options were chosen on the panel
'''

import bpy, os, datetime

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
        bpy.data.scenes[0].display_settings.display_device = 'sRGB'
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.data.scenes[0].view_settings.look = 'None'

        #save filepath for later
        bpy.context.scene.kkbp.import_dir = str(self.filepath)[:-9]

        #delete the cached files if the option is enabled
        if bpy.context.scene.kkbp.delete_cache and c.get_import_path():
            c.kklog('Clearing the cache folder...')
            for cache_folder in ['atlas_files', 'baked_files', 'dark_files', 'saturated_files']:
                try:
                    for f in os.listdir(os.path.join(c.get_import_path(), cache_folder)):
                        try:
                            os.remove(os.path.join(c.get_import_path(), cache_folder, f))
                        except:
                            pass
                except:
                    #that cache folder did not exist
                    pass

        #check if there is at least one "Outfit ##" folder inside of this directory
        #   if there isn't, then the user incorrectly chose the .pmx file inside of the outfit directory
        #   correct to the .pmx file inside of the root directory
        subdirs = [i[1] for i in os.walk(c.get_import_path())][0]
        outfit_subdirs = [i for i in subdirs if 'Outfit ' in i]
        if not outfit_subdirs:
            bpy.context.scene.kkbp.import_dir = os.path.dirname(os.path.dirname(c.get_import_path()))
            c.kklog('User chose wrong pmx file. Defaulting to pmx file located at ' + str(c.get_import_path()), 'warn')
                
        #get the character name and use it for some things later on
        bpy.context.scene.kkbp.character_name = c.get_import_path().replace(os.path.dirname(os.path.dirname(c.get_import_path())), '').split('_', maxsplit = 1)[1][:-1]

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
        c.kklog('KKBP import finished in {} minutes'.format(round(((datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6) - bpy.context.scene.kkbp.total_timer) / 60, 2)))
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def import_pmx_models(self):
        c.kklog('Importing pmx files with mmdtools...')
        
        for subdir, dirs, files in os.walk(c.get_import_path()):
            for file in [f for f in files if f == 'model.pmx']:
                pmx_path = os.path.join(subdir, file)
                outfit = 'Outfit' in subdir

                #import the pmx file with mmd_tools
                if bpy.app.version[0] == 3:
                    bpy.ops.mmd_tools.import_model('EXEC_DEFAULT',
                        files=[{'name': pmx_path}],
                        directory=pmx_path,
                        scale=1,
                        clean_model = False,
                        types={'MESH', 'ARMATURE', 'MORPHS'} if not outfit else {'MESH'},
                        log_level='WARNING')
                else:
                    bpy.ops.mmd_tools.import_model('EXEC_DEFAULT',
                        filepath=pmx_path,
                        scale=1,
                        clean_model = False,
                        types={'MESH', 'ARMATURE', 'MORPHS'} if not outfit else {'MESH', 'ARMATURE'})

                #tag the newly import object after pmx import. The active object is the empty, so apply it to the armature and the mesh
                bpy.context.view_layer.objects.active['name'] = c.get_name()
                bpy.context.view_layer.objects.active.children[0]['name'] = c.get_name()
                bpy.context.view_layer.objects.active.children[0].children[0]['name'] = c.get_name()
                #keep track of the outfit ID if this is an outfit
                if outfit:
                    bpy.context.view_layer.objects.active.children[0].children[0]['id'] = str(subdir[-2:])
                    bpy.context.view_layer.objects.active.children[0].children[0]['outfit'] = True
                    bpy.context.view_layer.objects.active.children[0].children[0].name = 'Outfit ' + str(subdir[-2:]) + ' ' + c.get_name()
                else:
                    bpy.context.view_layer.objects.active.children[0].children[0].name = 'Body ' + c.get_name()
                    bpy.context.view_layer.objects.active.children[0].children[0]['body'] = True
                    bpy.context.view_layer.objects.active.children[0].name = 'Armature ' + c.get_name()
                    bpy.context.view_layer.objects.active.children[0]['armature'] = True
                #get rid of the text files the mmd tools addon generates
                if bpy.data.texts.get('Model'):
                    bpy.data.texts.remove(bpy.data.texts['Model'])
                    bpy.data.texts.remove(bpy.data.texts['Model_e'])
        #rename the collection to the character name
        bpy.data.collections['Collection'].name = c.get_name()
        c.initialize_timer()
        c.print_timer('Import PMX')

class kkbp_debug(bpy.types.Operator):
    bl_idname = "kkbp.debug"
    bl_label = "Import .pmx file"
    bl_description = 'wow how convenient'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        filepath = r"C:\Koi\Koikatsu\Export_PMX\20250104133404_singleoutfit\model.pmx"
        # filepath = r"C:\Koi\Koikatsu\Export_PMX\20250111150404_alloutfitsvariations\model.pmx"
        bpy.context.scene.kkbp.import_dir = str(filepath)[:-9]
        
        #do this thing because cats does it
        if hasattr(bpy.context.scene, 'layers'):
            bpy.context.scene.layers[0] = True

        #delete the default scene if present
        if len(bpy.data.objects) == 3:
            for obj in ['Camera', 'Light', 'Cube']:
                if bpy.data.objects.get(obj):
                    bpy.data.objects.remove(bpy.data.objects[obj])

        #Set the view transform 
        bpy.data.scenes[0].display_settings.display_device = 'sRGB'
        bpy.context.scene.view_settings.view_transform = 'Standard'
        bpy.data.scenes[0].view_settings.look = 'None'

        #delete the cached files if the option is enabled
        if bpy.context.scene.kkbp.delete_cache and c.get_import_path():
            c.kklog('Clearing the cache folder...')
            for cache_folder in ['atlas_files', 'baked_files', 'dark_files', 'saturated_files']:
                try:
                    for f in os.listdir(os.path.join(c.get_import_path(), cache_folder)):
                        try:
                            os.remove(os.path.join(c.get_import_path(), cache_folder, f))
                        except:
                            pass
                except:
                    #that cache folder did not exist
                    pass

        #check if there is at least one "Outfit ##" folder inside of this directory
        #   if there isn't, then the user incorrectly chose the .pmx file inside of the outfit directory
        #   correct to the .pmx file inside of the root directory
        subdirs = [i[1] for i in os.walk(c.get_import_path())][0]
        outfit_subdirs = [i for i in subdirs if 'Outfit ' in i]
        if not outfit_subdirs:
            bpy.context.scene.kkbp.import_dir = os.path.dirname(os.path.dirname(c.get_import_path()))
            c.kklog('User chose wrong pmx file. Defaulting to pmx file located at ' + str(c.get_import_path()), 'warn')
                
        #get the character name and use it for some things later on
        bpy.context.scene.kkbp.character_name = c.get_import_path().replace(os.path.dirname(os.path.dirname(c.get_import_path())), '').split('_', maxsplit = 1)[1][:-1]

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
        c.kklog('KKBP import finished in {} minutes'.format(round(((datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6) - bpy.context.scene.kkbp.total_timer) / 60, 2)))
        return {'FINISHED'}
    
    def import_pmx_models(self):
        c.kklog('Importing pmx files with mmdtools...')
        
        for subdir, dirs, files in os.walk(c.get_import_path()):
            for file in [f for f in files if f == 'model.pmx']:
                pmx_path = os.path.join(subdir, file)
                outfit = 'Outfit' in subdir

                #import the pmx file with mmd_tools
                if bpy.app.version[0] == 3:
                    bpy.ops.mmd_tools.import_model('EXEC_DEFAULT',
                        files=[{'name': pmx_path}],
                        directory=pmx_path,
                        scale=1,
                        clean_model = False,
                        types={'MESH', 'ARMATURE', 'MORPHS'} if not outfit else {'MESH'},
                        log_level='WARNING')
                else:
                    bpy.ops.mmd_tools.import_model('EXEC_DEFAULT',
                        filepath=pmx_path,
                        scale=1,
                        clean_model = False,
                        types={'MESH', 'ARMATURE', 'MORPHS'} if not outfit else {'MESH', 'ARMATURE'})

                #tag the newly import object after pmx import. The active object is the empty, so apply it to the armature and the mesh
                bpy.context.view_layer.objects.active['name'] = c.get_name()
                bpy.context.view_layer.objects.active.children[0]['name'] = c.get_name()
                bpy.context.view_layer.objects.active.children[0].children[0]['name'] = c.get_name()
                #keep track of the outfit ID if this is an outfit
                if outfit:
                    bpy.context.view_layer.objects.active.children[0].children[0]['id'] = str(subdir[-2:])
                    bpy.context.view_layer.objects.active.children[0].children[0]['outfit'] = True
                    bpy.context.view_layer.objects.active.children[0].children[0].name = 'Outfit ' + str(subdir[-2:]) + ' ' + c.get_name()
                else:
                    bpy.context.view_layer.objects.active.children[0].children[0].name = 'Body ' + c.get_name()
                    bpy.context.view_layer.objects.active.children[0].children[0]['body'] = True
                    bpy.context.view_layer.objects.active.children[0].name = 'Armature ' + c.get_name()
                    bpy.context.view_layer.objects.active.children[0]['armature'] = True
                #get rid of the text files the mmd tools addon generates
                if bpy.data.texts.get('Model'):
                    bpy.data.texts.remove(bpy.data.texts['Model'])
                    bpy.data.texts.remove(bpy.data.texts['Model_e'])
        #rename the collection to the character name
        bpy.data.collections['Collection'].name = c.get_name()
        c.initialize_timer()
        c.print_timer('Import PMX')
