#The init file for the plugin
bl_info = {
    "name" : "KKBP (Koikatsu Blender Porter)",
    "author" : "a blendlet and some blenderchads",
    "location" : "View 3D > Tool Shelf > KKBP and Image Editor > Tool Shelf > KKBP",
    "description" : "Scripts to automate cleanup of a Koikatsu export",
    "version": (8, 1, 1),
    "blender" : (3, 6, 0),
    "category" : "3D View",
    "tracker_url" : "https://github.com/FlailingFog/KK-Blender-Porter-Pack/",
    "doc_url": "https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md",
}

from .exporting.material_combiner.extend_types import register_smc_types, unregister_smc_types
from bpy.utils import register_class, unregister_class
from bpy.types import Scene
from bpy.props import PointerProperty

def reg_unreg(register_bool):
    from .preferences import KKBPPreferences
    if register_bool:
        register_class(KKBPPreferences)
    else:
        unregister_class(KKBPPreferences)

    from .importing.importbuttons import kkbp_import
    from .importing.modifymesh import modify_mesh
    from .importing.modifyarmature import modify_armature
    from .importing.modifymaterial import modify_material
    from .importing.postoperations import post_operations

    from .exporting.bakematerials import bake_materials
    from .exporting.exportprep import export_prep
    from .exporting.material_combiner.combiner import Combiner
    from .exporting.material_combiner.combine_list import RefreshObData, CombineSwitch
    from .exporting.material_combiner.extend_types import CombineList
    from .exporting.material_combiner.get_pillow import InstallPIL

    from .extras.importstudio import import_studio
    from .extras.createmapassetlibrary import map_asset_lib
    from .extras.createanimationlibrary import anim_asset_lib
    from .extras.linkshapekeys import link_shapekeys
    from .extras.updatebones import update_bones
    from .extras.imageconvert import image_convert
    from .extras.imageconvert import image_dark_convert
    from .extras.rigifywrapper import rigify_convert
    from .extras.rigifyscripts.rigify_before import rigify_before
    from .extras.rigifyscripts.rigify_after import rigify_after
    from .extras.catsscripts.armature_manual import MergeWeights
    from .extras.importanimation import anim_import
    from .extras.matcombsetup import mat_comb_setup
    from .extras.matcombswitch import mat_comb_switch
    from .extras.resetmaterials import reset_materials
    from .extras.linkhair import link_hair

    from . KKPanel import PlaceholderProperties
    from . KKPanel import (
        IMPORTINGHEADER_PT_panel,
        IMPORTING_PT_panel,
        EXPORTING_PT_panel,
        EXTRAS_PT_panel,
        HAIR_PT_panel,
    )

    classes = (
        bake_materials, 
        export_prep,
        image_convert, 
        image_dark_convert,

        import_studio,
        map_asset_lib,
        anim_asset_lib,
        link_shapekeys,
        update_bones,
        rigify_convert,
        rigify_before,
        rigify_after,
        MergeWeights,
        anim_import,
        Combiner,
        RefreshObData,
        CombineSwitch,
        CombineList,
        mat_comb_setup,
        mat_comb_switch,
        InstallPIL,
        reset_materials,
        link_hair,

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
        HAIR_PT_panel,
        )

    for cls in classes:
        register_class(cls) if register_bool else unregister_class(cls)
    
    if register_bool:
        Scene.kkbp = PointerProperty(type=PlaceholderProperties)
    else:
        del Scene.kkbp

def register():
    reg_unreg(True)
    register_smc_types()

def unregister():
    reg_unreg(False)
    unregister_smc_types()

if __name__ == "__main__":
    register()
