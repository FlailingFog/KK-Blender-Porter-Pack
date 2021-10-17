#The init file for the plugin
bl_info = {
    "name" : "KK Blender Porter Pack",
    "author" : "a blendlet",
    "location" : "View 3D > Tool Shelf > KK Scripts",
    "description" : "Scripts for automating the cleanup process of a Koikatsu export",
    "version": (5, 0, 0),
    "blender" : (2, 93, 0),
    "location" : "View3D",
    "category" : "3D View",
    "tracker_url" : "https://github.com/FlailingFog/KK-Blender-Shader-Pack/"
}

import bpy
from bpy.utils import register_class, unregister_class

from bpy.types import Scene
from bpy.props import PointerProperty

from .importing.bonedrivers import bone_drivers
from .importing.cleanarmature import clean_armature
from .importing.finalizegrey import finalize_grey
from .importing.finalizepmx import finalize_pmx
from .importing.importeverything import import_everything
from .importing.importcolors import import_colors
from .importing.importgrey import import_grey
from .importing.separatebody import separate_body
from .importing.shapekeys import shape_keys

from .exporting.bakematerials import bake_materials
from .exporting.applymaterials import apply_materials
from .exporting.selectbones import select_bones

from .extras.importstudio import import_studio
from .extras.linkshapekeys import link_shapekeys
from .extras.importanimation import import_animation
from .extras.switcharmature import switch_armature
from .extras.toggleik import toggle_ik
from .pillow.getpillow import InstallPIL

from . KKPanel import PlaceholderProperties
from . KKPanel import IMPORTING_PT_panel, IMPORTING1_PT_panel,IMPORTOPTIONS_PT_Panel, IMPORTING2_PT_panel, APPLYOPTIONS_PT_Panel, EXPORTING_PT_panel, EXTRAS_PT_panel

classes = (
    apply_materials,
    bake_materials, 
    select_bones, 

    import_animation, 
    import_studio, 
    link_shapekeys,
    switch_armature,
    toggle_ik,
    InstallPIL,

    bone_drivers, 
    clean_armature, 
    finalize_grey, 
    finalize_pmx, 
    import_everything, 
    import_colors, 
    import_grey, 
    separate_body, 
    shape_keys,

    PlaceholderProperties, 
    IMPORTING_PT_panel,
    IMPORTING1_PT_panel,
    IMPORTOPTIONS_PT_Panel,
    IMPORTING2_PT_panel,
    APPLYOPTIONS_PT_Panel,
    EXPORTING_PT_panel,
    EXTRAS_PT_panel)

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
