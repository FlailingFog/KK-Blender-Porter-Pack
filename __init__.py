#The init file for the plugin

bl_info = {
    "name" : "KK Blender Pack",
    "author" : "a blendlet",
    "location" : "View 3D > Tool Shelf > KK Scripts",
    "description" : "Scripts for automating the cleanup process of a Koikatsu export",
    "version": (4, 3, 1), #great now I have to remember to update this number each time
    "blender" : (2, 93, 0),
    "location" : "View3D",
    "category" : "3D View",
    "tracker_url" : "https://github.com/FlailingFog/KK-Blender-Shader-Pack/"
}

import bpy
from bpy.utils import register_class, unregister_class

from bpy.types import Panel, PropertyGroup, Scene, WindowManager
from bpy.props import PointerProperty

from .importing.finalizepmx import finalize_pmx
from .importing.shapekeys import shape_keys
from .importing.separatebody import separate_body
from .importing.importtemplates import import_templates
from .importing.importtextures import import_textures
from .importing.cleanarmature import clean_armature
from .importing.bonedrivers import bone_drivers
from .exporting.bakematerials import bake_materials
from .exporting.applymaterials import apply_materials
from .exporting.selectbones import select_bones
from .extras.importstudio import import_studio
from .extras.linkshapekeys import link_shapekeys

from . KKPanel import PlaceholderProperties
from . KKPanel import KK_Panel

classes = (
    finalize_pmx,
    shape_keys, 
    separate_body, 
    import_templates, 
    import_textures, 
    clean_armature, 
    bone_drivers, 
    bake_materials, 
    apply_materials, 
    select_bones, 
    import_studio, 
    link_shapekeys, 
    PlaceholderProperties, 
    KK_Panel)

def register():
    
    for cls in classes:
        register_class(cls)

    Scene.placeholder = PointerProperty(type=PlaceholderProperties)

def unregister():

    for cls in reversed(classes):
        unregister_class(cls)

    del Scene.placeholder

if __name__ == "__main__":
    register()
