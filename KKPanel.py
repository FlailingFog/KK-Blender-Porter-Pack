import bpy, os, textwrap
from bpy.types import PropertyGroup
from bpy.props import (
    IntProperty,
    FloatProperty,
    EnumProperty,
    BoolProperty,
    StringProperty
)

from .interface.dictionary_en import t
from .exporting.material_combiner import globs

class PlaceholderProperties(PropertyGroup):
    #this will let the plugin know where to look for texture / json data
    import_dir: StringProperty(default='')

    #this will let the plugin know where the user is in the import / export process
    plugin_state:StringProperty(default='')

    #This will let the plugin track what objects belong to what character
    character_name: StringProperty(default='')

    #this lets the plugin time various actions
    total_timer : FloatProperty(default=0)
    timer : FloatProperty(default=0)
    
    bake_mult: IntProperty(
        min=1, max = 6,
        default=1,
        description=t('bake_mult_tt'))

    sfw_mode : BoolProperty(
    description=t('sfw_mode_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.sfw_mode)

    fix_seams : BoolProperty(
    description=t('seams_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.fix_seams)
    
    use_single_outline : BoolProperty(
    description= t('outline_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.use_single_outline)
    
    use_material_fake_user : BoolProperty(
    description=t('keep_templates_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.use_material_fake_user)

    old_bake_bool : BoolProperty(
    description=t('old_bake_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.old_bake_bool)

    armature_dropdown : EnumProperty(
        items=(
            ("A", t('arm_drop_A'), t('arm_drop_A_tt')),
            ("B", t('arm_drop_B'), t('arm_drop_B_tt')),
            ("C", t('arm_drop_C'), t('arm_drop_C_tt')),
            ("D", t('arm_drop_D'), t('arm_drop_D_tt')),
        ), name="", default=bpy.context.preferences.addons[__package__].preferences.armature_dropdown, description=t('arm_drop'))

    categorize_dropdown : EnumProperty(
        items=(
            ("A", t('cat_drop_A'), t('cat_drop_A_tt')),
            ("B", t('cat_drop_B'), t('cat_drop_B_tt')),
        ), name="", default=bpy.context.preferences.addons[__package__].preferences.categorize_dropdown, description=t('cat_drop'))
    
    colors_dropdown : BoolProperty(
        description = t('dark'),
        default=bpy.context.preferences.addons[__package__].preferences.colors_dropdown)
    
    prep_dropdown : EnumProperty(
        items=(
            ("A", t('prep_drop_A'), t('prep_drop_A_tt')),
            #("C", "MikuMikuDance - PMX compatible", " "),
            ("D", t('prep_drop_D'), t('prep_drop_D_tt')),
            ("E", t('prep_drop_E'), t('prep_drop_E_tt')),
            ("B", t('prep_drop_B'), t('prep_drop_B_tt')),
        ), name="", default=bpy.context.preferences.addons[__package__].preferences.prep_dropdown, description=t('prep_drop'))

    simp_dropdown : EnumProperty(
        items=(
            ("A", t('simp_drop_A'), t('simp_drop_A_tt')),
            ("B", t('simp_drop_B'), t('simp_drop_B_tt')),
            ("C", t('simp_drop_C'), t('simp_drop_C_tt')),
        ), name="", default=bpy.context.preferences.addons[__package__].preferences.simp_dropdown, description=t('simp_drop'))
    
    bake_light_bool : BoolProperty(
    description=t('bake_light_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.bake_light_bool)

    bake_dark_bool : BoolProperty(
    description=t('bake_dark_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.bake_dark_bool)

    bake_norm_bool : BoolProperty(
    description=t('bake_norm_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.bake_norm_bool)

    delete_cache : BoolProperty(
    description=t('delete_cache_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.delete_cache)

    use_atlas : BoolProperty(
    description=t('use_atlas_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.use_atlas)

    animation_library_scale : BoolProperty(
    description=t('animation_library_scale_tt'),
    default = True)

    shapekeys_dropdown : EnumProperty(
        items=(
            ("A", t('shape_A'), t('shape_A_tt')),
            ("B", t('shape_B'), t('shape_B_tt')),
            ("C", t('shape_C'), t('shape_C_tt')),
        ), name="", default=bpy.context.preferences.addons[__package__].preferences.shapekeys_dropdown, description="")
    
    shader_dropdown : EnumProperty(
        items=(
            ("A", t('shader_A'), ''),
            ("B", t('shader_B'), ''),
            ("D", t('shader_D'), ''),
            ("C", t('shader_C'), t('shader_C_tt')),
        ), name="", default=bpy.context.preferences.addons[__package__].preferences.shader_dropdown, description="Shader")
    
    atlas_dropdown : EnumProperty(
        items=(
            ("A", t('bake_light'), ""),
            ("B", t('bake_dark'), ""),
            ("C", t('bake_norm'), ""),
        ), name="", default="A", description='')
    
    dropdown_box : EnumProperty(
        items=(
            ("A", "Principled BSDF", "Default shading"),
            ("B", "Emission", "Flat shading"),
            ("C", "KK Shader", "Anime cel shading"),
            ("D", "Custom", "Custom shading")
        ), name="", default="A", description="Shader type")

    shadows_dropdown : EnumProperty(
        items=(
            ("A", "None", "No shadows"),
            ("B", "Opaque", ""),
            ("C", "Alpha Clip", ""),
            ("D", "Alpha Hashed", "")
        ), name="", default="A", description="Shadow Mode")

    blend_dropdown : EnumProperty(
        items=(
            ("A", "Opaque", ""),
            ("B", "Alpha Clip", ""),
            ("C", "Alpha Hashed", ""),
            ("D", "Alpha Blend", ""),
        ), name="", default="B", description="Blend Mode")

    studio_lut_bool : BoolProperty(
        name="Enable or Disable",
        description=t('convert_texture_tt'),
        default = True)

    rokoko_bool : BoolProperty(
        name="Enable or Disable",
        description="""Enable this if you don't want KKBP to process the fbx animation, and instead want to use the rokoko plugin to transfer the fbx animation to your character.
        Stock / unmodified armatures only!""",
        default = False)
    
    animation_import_type : BoolProperty(
        name="Enable or Disable",
        description=t('animation_type_tt'),
        default = False)

    image_dropdown : EnumProperty(
        items=(
            ("A", t('dark_C'), "Use Day LUT to saturate image"),
            ("B", t('dark_A'), "Use Night LUT to saturate image"),
            ("C", t('dark_B'), "Use Sunset LUT to saturate image")
        ), name="", default="A", description="LUT Choice")

#The main panel
class IMPORTINGHEADER_PT_panel(bpy.types.Panel):
    bl_label = t('import_export')
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    def draw(self,context):
        layout = self.layout

class IMPORTING_PT_panel(bpy.types.Panel):
    bl_parent_id = "IMPORTINGHEADER_PT_panel"
    bl_label = t('import_export')
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'HIDE_HEADER'}

    def draw(self,context):
        scene = context.scene.kkbp
        layout = self.layout
        splitfac = 0.5
        box = layout.box()
        col = box.column(align=True)
        
        # row = col.row(align=True)
        # row.operator('kkbp.debug', text = 'Debug', icon='FILE_FOLDER')

        row = col.row(align=True)
        row.operator('kkbp.kkbpimport', text = t('import_model'), icon='FILE_FOLDER')
        row.enabled = scene.plugin_state not in ['imported', 'prepped']
                    
        row = col.row(align = True)
        box = row.box()
        col = box.column(align=True)
        
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "categorize_dropdown")
        split.prop(context.scene.kkbp, "armature_dropdown")
        split.enabled = scene.plugin_state not in ['imported', 'prepped']
        
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "shapekeys_dropdown")
        split.prop(context.scene.kkbp, "shader_dropdown")
        row.enabled = scene.plugin_state not in ['imported', 'prepped']

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "colors_dropdown", toggle=True, text = t('dark_F') if scene.colors_dropdown else t('dark_C'))
        split.prop(context.scene.kkbp, "delete_cache", toggle=True, text = t('delete_cache'))
        row.enabled = scene.plugin_state not in ['imported', 'prepped']

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "fix_seams", toggle=True, text = t('seams'))
        split.prop(context.scene.kkbp, "use_material_fake_user", toggle=True, text = t('keep_templates'))
        row.enabled = scene.plugin_state not in ['imported', 'prepped']

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "use_single_outline", toggle=True, text = t('outline'))
        split.prop(context.scene.kkbp, "sfw_mode", toggle=True, text = t('sfw_mode'))
        row.enabled = scene.plugin_state not in ['imported', 'prepped']
        
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator('kkbp.bakematerials', text = t('bake'), icon='OUTPUT')
        row.enabled = scene.plugin_state in ['imported', 'prepped']
        row = col.row(align=True)
        split = row.split(align=True, factor=0.33)
        split.prop(context.scene.kkbp, "bake_light_bool", toggle=True, text = t('bake_light'))
        split.prop(context.scene.kkbp, "bake_dark_bool", toggle=True, text = t('bake_dark'))
        split.prop(context.scene.kkbp, "bake_norm_bool", toggle=True, text = t('bake_norm'))
        row.enabled = scene.plugin_state in ['imported', 'prepped']
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.prop(context.scene.kkbp, 'old_bake_bool', toggle=True, text = t('old_bake'))
        split.prop(context.scene.kkbp, "bake_mult", text = t('bake_mult'))
        row.enabled = scene.plugin_state in ['imported', 'prepped']
        row = col.row(align = True)
        split = row.split(align=True, factor=splitfac)
        if globs.pil_exist == 'no':
            split.operator('kkbp.get_pillow', text = t('pillow'), icon='FILE_REFRESH')
            split.operator('kkbp.resetmaterials', text = t('reset_mats'), icon='RECOVER_LAST')
        elif globs.pil_exist == 'restart':
            col = col.box().column()
            col.label(text='Installation complete')
            col.label(text='Please restart Blender')
        else:
            split.prop(context.scene.kkbp, "use_atlas", toggle=True, text = t('use_atlas') if scene.use_atlas else t('dont_use_atlas'))
            split.operator('kkbp.resetmaterials', text = t('reset_mats'), icon='RECOVER_LAST')

        row.enabled = scene.plugin_state in ['imported', 'prepped']

class EXPORTING_PT_panel(bpy.types.Panel):
    bl_parent_id = "IMPORTING_PT_panel"
    bl_label = 'Exporting'
    bl_options = {'HIDE_HEADER'}
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self,context):
        scene = context.scene.kkbp
        layout = self.layout
        splitfac = 0.5
        
        box = layout.box()

        col = box.column(align=True)
        row = col.row(align=True)
        row.operator('kkbp.exportprep', text = t('prep'), icon = 'MODIFIER')
        row.enabled = scene.plugin_state in ['imported'] and bpy.context.scene.kkbp.armature_dropdown in ['A', 'C', 'D']
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.prop(context.scene.kkbp, "simp_dropdown")
        split.prop(context.scene.kkbp, "prep_dropdown")
        row.enabled = scene.plugin_state in ['imported'] and bpy.context.scene.kkbp.armature_dropdown in ['A', 'C', 'D']

class EXTRAS_PT_panel(bpy.types.Panel):
    bl_label = t('extras')
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        scene = context.scene.kkbp
        splitfac = 0.6
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text=t('studio_object'))
        split.operator('kkbp.importstudio', text = '', icon = 'PACKAGE')
        row = col.row(align=True)
        split = row.split(align=True)
        split.label(text="Shader")
        split.label(text="Shadow Mode")
        split.label(text="Blend Mode")
        split.label(text="")
        row = col.row(align=True)
        split = row.split(align=True)
        split.prop(context.scene.kkbp, "dropdown_box")
        split.prop(context.scene.kkbp, "shadows_dropdown")
        split.prop(context.scene.kkbp, "blend_dropdown")
        split.prop(context.scene.kkbp, "studio_lut_bool", toggle=True, text = t('convert_texture'))

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text = t('single_animation'))
        split.operator('kkbp.importanimation', text = '', icon = 'ARMATURE_DATA')
        row.enabled = scene.plugin_state in ['imported'] and bpy.context.scene.kkbp.armature_dropdown == 'B'
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="")
        split.prop(context.scene.kkbp, "animation_import_type", toggle=True, text = t('animation_mix') if scene.animation_import_type else t('animation_koi'))
        row.enabled = scene.plugin_state in ['imported'] and bpy.context.scene.kkbp.armature_dropdown == 'B'

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text=t('animation_library'))
        split.operator('kkbp.createanimassetlib', text = '', icon = 'ARMATURE_DATA')
        row.enabled = scene.plugin_state in ['imported'] and bpy.context.scene.kkbp.armature_dropdown == 'B'
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="")
        split.prop(context.scene.kkbp, "animation_library_scale", toggle=True, text = t('animation_library_scale'))
        row.enabled = scene.plugin_state in ['imported'] and bpy.context.scene.kkbp.armature_dropdown == 'B'

        # col = box.column(align=True)
        # row = col.row(align=True)
        # split = row.split(align=True, factor=splitfac)
        # split.label(text=t('map_library'))
        # split.operator('kkbp.createmapassetlib', text = '', icon = 'WORLD')

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text=t('sep_eye'))
        split.operator('kkbp.linkshapekeys', text = '', icon='HIDE_OFF')

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text=t('bone_visibility'))
        split.operator('kkbp.updatebones', text = '', icon = 'GROUP_BONE')

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text=t('rigify_convert'))
        split.operator('kkbp.rigifyconvert', text = '', icon='MOD_ARMATURE')

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text=t('matcomb'))
        split.operator('kkbp.matcombsetup', text = '', icon='NODETREE')
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text=t('mat_comb_switch'))
        split.operator('kkbp.matcombswitch', text = '', icon='FILE_REFRESH')
        
        #check https://ui.blender.org/icons/ for all icon names

#Add a button to the materials tab that lets you update all hair material settings at once
class HAIR_PT_panel(bpy.types.Panel):
    #bl_parent_id = "EEVEE_MATERIAL_PT_surface"
    bl_label = "kkbp_hair"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT'}

    def draw(self, context):
        layout = self.layout
        mat = context.material
        if mat:
            if mat.get('hair'):
                layout.operator('kkbp.linkhair', text = t('link_hair'), icon='NODETREE')

def register():
    bpy.utils.register_class(PlaceholderProperties)
    bpy.utils.register_class(IMPORTINGHEADER_PT_panel)
    bpy.utils.register_class(IMPORTING_PT_panel)
    bpy.utils.register_class(EXPORTING_PT_panel)
    bpy.utils.register_class(EXTRAS_PT_panel)
    bpy.utils.register_class(HAIR_PT_panel)

def unregister():
    bpy.utils.unregister_class(HAIR_PT_panel)
    bpy.utils.unregister_class(EXTRAS_PT_panel)
    bpy.utils.unregister_class(EXPORTING_PT_panel)
    bpy.utils.unregister_class(IMPORTING_PT_panel)
    bpy.utils.unregister_class(IMPORTINGHEADER_PT_panel)
    bpy.utils.unregister_class(PlaceholderProperties)

if __name__ == "__main__":
    #unregister()
    register()
