#words words words

bl_info = {
    "name" : "KKBlenderPack",
    "author" : "a blendlet",
    "description" : "Scripts for automating the cleanup process for a Koikatsu export. See https://github.com/FlailingFog/KK-Blender-Shader-Pack/ for info",
    "blender" : (2, 91, 2),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy

from . beforeCATS import before_CATS
from . shapekeys import shape_keys
from . separateBody import separate_Body
from . importTemplates import import_Templates
from . importTextures import import_Textures
from . cleanArmature import clean_Armature
from . bonedrivers import bone_drivers
from . bakeMaterials import bake_Materials


from . KKPanel    import KK_Panel

classes = (before_CATS, shape_keys, separate_Body, import_Templates, import_Textures, clean_Armature, bone_drivers, bake_Materials, KK_Panel)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
