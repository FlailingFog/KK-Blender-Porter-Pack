import os
import subprocess
import sys
from typing import Set
from . import globs
from ... import common as c
from ...interface.dictionary_en import t
import bpy

class InstallPIL(bpy.types.Operator):
    bl_idname = 'kkbp.get_pillow'
    bl_label = 'Install Pillow'
    bl_description = t('pillow_tt')

    def execute(self, context: bpy.types.Context) -> Set[str]:
        try:
            from PIL import Image, ImageChops
        except ImportError:
            self._install_pillow()

        globs.pil_exist = 'restart'

        self.report({'INFO'}, 'Installation complete')
        return {'FINISHED'}

    @staticmethod
    def _install_pillow() -> None:
        from pip import _internal
        _internal.main(['install', 'pip', 'setuptools', 'wheel', '-U', '--user'])
        _internal.main(['install', 'Pillow', '--user'])
