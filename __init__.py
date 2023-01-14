#The init file for the plugin
bl_info = {
    "name" : "KK Blender Porter",
    "author" : "a blendlet and some blenderchads",
    "location" : "View 3D > Tool Shelf > KKBP and Image Editor > Tool Shelf > KKBP",
    "description" : "Scripts to automate cleanup of a Koikatsu export",
    "version": (6, 3, 1),
    "blender" : (3, 4, 0),
    "category" : "3D View",
    "tracker_url" : "https://github.com/FlailingFog/KK-Blender-Porter-Pack/"
}

import bpy
from bpy.utils import register_class, unregister_class

from bpy.types import Scene
from bpy.props import PointerProperty

def wrap(register_bool):
    from .preferences import KKBPPreferences
    if register_bool:
        register_class(KKBPPreferences)
    else:
        unregister_class(KKBPPreferences)

    from .importing.bonedrivers import bone_drivers
    from .importing.cleanarmature import clean_armature
    #from .importing.importgrey import import_grey
    #from .importing.finalizegrey import finalize_grey
    from .importing.finalizepmx import finalize_pmx
    from .importing.importeverything import import_everything
    from .importing.importcolors import import_colors
    from .importing.importbuttons import quick_import, mat_import
    from .importing.separatebody import separate_body
    from .importing.shapekeys import shape_keys

    from .exporting.bakematerials import bake_materials
    from .exporting.applymaterials import apply_materials
    from .exporting.exportprep import export_prep
    from .exporting.exportfbx import export_fbx

    from .extras.importstudio import import_studio
    from .extras.animationlibrary.createmapassetlibrary import map_asset_lib
    from .extras.animationlibrary.createanimationlibrary import anim_asset_lib
    from .extras.linkshapekeys import link_shapekeys
    from .extras.importanimation import import_animation
    from .extras.switcharmature import switch_armature
    from .extras.separatemeshes import separate_meshes
    from .extras.separatemeshes import export_separate_meshes
    from .extras.toggleik import toggle_ik
    from .extras.updatebones import update_bones
    from .extras.imageconvert import image_convert
    from .extras.imageconvert import image_dark_convert
    from .extras.rigifywrapper import rigify_convert
    from .extras.rigifyscripts.rigify_before import rigify_before
    from .extras.rigifyscripts.rigify_after import rigify_after
    from .extras.catsscripts.armature_manual import MergeWeights

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
        export_fbx,
        image_convert, 
        image_dark_convert,

        import_animation, 
        import_studio,
        map_asset_lib,
        anim_asset_lib,
        link_shapekeys,
        switch_armature,
        separate_meshes,
        export_separate_meshes,
        toggle_ik,
        update_bones,
        rigify_convert,
        rigify_before,
        rigify_after,
        MergeWeights,

        bone_drivers, 
        clean_armature, 
        #finalize_grey, 
        finalize_pmx, 
        import_everything, 
        import_colors, 
        #import_grey,
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

    for cls in classes:
        register_class(cls) if register_bool else unregister_class(cls)
    
    if register_bool:
        Scene.kkbp = PointerProperty(type=PlaceholderProperties)
    else:
        del Scene.kkbp

def register():
    wrap(True)

def unregister():
    wrap(False)

if __name__ == "__main__":
    register()
