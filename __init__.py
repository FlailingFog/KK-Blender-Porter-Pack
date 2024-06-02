#The init file for the plugin
bl_info = {
    "name" : "KK Blender Porter",
    "author" : "a blendlet and some blenderchads",
    "location" : "View 3D > Tool Shelf > KKBP and Image Editor > Tool Shelf > KKBP",
    "description" : "Scripts to automate cleanup of a Koikatsu export",
    "version": (7, 0, 0),
    "blender" : (4, 2, 0),
    "category" : "3D View",
    "tracker_url" : "https://github.com/FlailingFog/KK-Blender-Porter-Pack/"
}

from bpy.utils import register_class, unregister_class
from bpy.types import Scene
from bpy.props import PointerProperty

def reg_unreg(register_bool):
    from .preferences import KKBPPreferences
    if register_bool:
        register_class(KKBPPreferences)
    else:
        unregister_class(KKBPPreferences)

    from .importing.installdependency import install_dependency
    from .importing.importbuttons import kkbp_import
    from .importing.modifymesh import modify_mesh
    from .importing.modifyarmature import modify_armature
    from .importing.modifymaterial import modify_material
    from .importing.postoperations import post_operations

    from .exporting.bakematerials import bake_materials
    from .exporting.applymaterials import apply_materials
    from .exporting.exportprep import export_prep
    from .exporting.exportfbx import export_fbx

    from .extras.importstudio import import_studio
    from .extras.animationlibrary.createmapassetlibrary import map_asset_lib
    from .extras.animationlibrary.createanimationlibrary import anim_asset_lib
    from .extras.linkshapekeys import link_shapekeys
    from .extras.importanimation import import_animation
    from .extras.separatemeshes import separate_meshes
    from .extras.separatemeshes import export_separate_meshes
    from .extras.toggleik import toggle_ik
    from .extras.updatebones import update_bones
    from .extras.imageconvert import image_convert
    from .extras.imageconvert import image_dark_convert
    from .extras.finalizematerials import finalize_materials
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
        separate_meshes,
        export_separate_meshes,
        toggle_ik,
        update_bones,
        finalize_materials,
        rigify_convert,
        rigify_before,
        rigify_after,
        MergeWeights,

        install_dependency,
        kkbp_import,
        modify_mesh,
        modify_armature,
        modify_material,
        post_operations,

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
    reg_unreg(True)

def unregister():
    reg_unreg(False)

if __name__ == "__main__":
    register()
