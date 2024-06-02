'''
This file performs the following operations
·	Downloads the blender 3.6 zip file
·	Unzips it to the dependencies folder
'''

import bpy, os, requests, zipfile, io

from ..interface.dictionary_en import t
from .. import common as c

class install_dependency(bpy.types.Operator):
    bl_idname = "kkbp.installdependency"
    bl_label = "Install import dependency"
    bl_description = 'Download Blender 3.6 from the official site'#t('install_dependency_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        '''download the blender zip file from https://download.blender.org/release/Blender3.6/blender-3.6.9-windows-x64.zip, and unzip it to the dependencies directory'''
        c.initialize_timer()
        #clear the dependencies folder
        c.toggle_console()
        c.kklog('Clearing the dependencies folder...')
        for f in os.listdir(os.path.join(os.path.dirname(__file__), 'dependencies')):
            try:
                os.remove(os.path.join(os.path.dirname(__file__), 'dependencies', f))
            except:
                pass
        
        #get the blender zip and unzip it to the dependencies folder
        c.kklog('Downloading blender zip file from https://download.blender.org/release/Blender3.6/blender-3.6.9-windows-x64.zip. This could take five to twenty minutes depending on your network speed...')
        zip_url = "https://download.blender.org/release/Blender3.6/blender-3.6.9-windows-x64.zip"
        r = requests.get(zip_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        c.kklog('Extracting blender zip file...')
        z.extractall(os.path.join(os.path.dirname(__file__), 'dependencies'))

        c.kklog('Updating KKBP blender path...')
        bpy.context.scene.kkbp.blender_path = os.path.join(os.path.dirname(__file__), 'dependencies', 'blender-3.6.9-windows-x64', 'blender.exe')
        c.toggle_console()
        c.print_timer('Blender 3.6 installation')
        
        return {'FINISHED'}
        