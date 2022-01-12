#100% stolen from https://github.com/Grim-es/material-combiner-addon/

import os
from subprocess import call

import bpy, sys

class InstallPIL(bpy.types.Operator):
    bl_idname = 'kkb.getpillow'
    bl_label = 'Install PIL'
    bl_description = 'Click to install Pillow. This could take a while and might require you to start Blender as admin'

    def execute(self, context):
        try:
            import pip
            try:
                from PIL import Image, ImageChops
                from colour import read_LUT
            except ImportError:
                call([sys.executable, '-m', 'pip', 'install', 'Pillow', '--user', '--upgrade', '--ignore-installed'], shell=True)
                call([sys.executable, '-m', 'pip', 'install', 'colour-science', '--user', '--upgrade', '--ignore-installed', '--target='], shell=True)
        except ImportError:
            call([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'get_pip.py'),
                  '--user'], shell=True)
            call([sys.executable, '-m', 'pip', 'install', 'Pillow', '--user', '--upgrade'], shell=True)
            call([sys.executable, '-m', 'pip', 'install', 'colour-science', '--user', '--upgrade'], shell=True)
        self.report({'INFO'}, 'Installation complete')
        return {'FINISHED'}