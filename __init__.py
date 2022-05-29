#The init file for the plugin
bl_info = {
    "name" : "KK Blender Porter Pack",
    "author" : "a blendlet and some blenderchads",
    "location" : "View 3D > Tool Shelf > KKBP and Image Editor > Tool Shelf > KKBP",
    "description" : "Scripts to automate cleanup of a Koikatsu export",
    "version": (6, 0, 0),
    "blender" : (3, 1, 0),
    "category" : "3D View",
    "tracker_url" : "https://github.com/FlailingFog/KK-Blender-Porter-Pack/"
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
from .importing.importbuttons import quick_import, mat_import
from .importing.separatebody import separate_body
from .importing.shapekeys import shape_keys

from .exporting.bakematerials import bake_materials
from .exporting.applymaterials import apply_materials
from .exporting.exportprep import export_prep

from .extras.importstudio import import_studio
from .extras.linkshapekeys import link_shapekeys
from .extras.importanimation import import_animation
from .extras.switcharmature import switch_armature
from .extras.separatemeshes import separate_meshes
from .extras.separatemeshes import export_separate_meshes
from .extras.toggleik import toggle_ik
from .extras.imageconvert import image_convert
from .extras.rigifywrapper import rigify_convert
from .pillow.getpillow import InstallPIL


from . KKPanel import PlaceholderProperties
from . KKPanel import (
    IMPORTINGHEADER_PT_panel,
    IMPORTING_PT_panel,
    EXPORTING_PT_panel,
    EXTRAS_PT_panel,
    EDITOR_PT_panel
)

classes = (
    apply_materials,
    bake_materials, 
    export_prep,
    image_convert, 

    import_animation, 
    import_studio, 
    link_shapekeys,
    switch_armature,
    separate_meshes,
    export_separate_meshes,
    toggle_ik,
    rigify_convert,
    InstallPIL,

    bone_drivers, 
    clean_armature, 
    finalize_grey, 
    finalize_pmx, 
    import_everything, 
    import_colors, 
    import_grey,
    quick_import,
    mat_import,
    separate_body, 
    shape_keys,

    PlaceholderProperties, 
    IMPORTINGHEADER_PT_panel,
    IMPORTING_PT_panel,
    EXPORTING_PT_panel,
    EXTRAS_PT_panel,
    EDITOR_PT_panel)

def register():
    
    for cls in classes:
        register_class(cls)

    Scene.kkbp = PointerProperty(type=PlaceholderProperties)

def unregister():

    for cls in reversed(classes):
        unregister_class(cls)

    del Scene.kkbp

if __name__ == "__main__":
    register()
