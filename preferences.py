#The preferences for the plugin 

import bpy
from bpy.props import BoolProperty, EnumProperty

from .interface.dictionary_en import t

class KKBPPreferences(bpy.types.AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    sfw_mode : BoolProperty(
    description=t('sfw_mode_tt'),
    default = False)

    fix_seams : BoolProperty(
    description=t('seams_tt'),
    default = True)
    
    texture_outline_bool : BoolProperty(
    description= t('outline_tt'),
    default = False)
    
    templates_bool : BoolProperty(
    description=t('keep_templates_tt'),
    default = True)

    old_bake_bool : BoolProperty(
    description=t('old_bake_tt'),
    default = False)

    armature_dropdown : EnumProperty(
        items=(
            ("A", t('arm_drop_A'), t('arm_drop_A_tt')),
            ("B", t('arm_drop_B'), t('arm_drop_B_tt')),
            ("C", t('arm_drop_C'), t('arm_drop_C_tt')),
            ("D", t('arm_drop_D'), t('arm_drop_D_tt')),
        ), name="", default="A", description=t('arm_drop'))

    categorize_dropdown : EnumProperty(
        items=(
            ("A", t('cat_drop_A'), t('cat_drop_A_tt')),
            ("B", t('cat_drop_B'), t('cat_drop_B_tt')),
            ("C", t('cat_drop_C'), t('cat_drop_C_tt') ),
            ("D", t('cat_drop_D'), t('cat_drop_D_tt')),
        ), name="", default="A", description=t('cat_drop'))
    
    colors_dropdown : EnumProperty(
        items=(
            ("A", t('dark_A'), t('dark_A_tt')),
            ("B", t('dark_B'), t('dark_B_tt')),
            ("C", t('dark_C'), t('dark_C_tt')),
            ("D", t('dark_D'), t('dark_D_tt')),
            ("E", t('dark_E'), t('dark_E_tt')),
            ("F", t('dark_F'), t('dark_F_tt'))
        ), name="", default="F", description=t('dark'))
    
    prep_dropdown : EnumProperty(
        items=(
            ("A", t('prep_drop_A'), t('prep_drop_A_tt')),
            #("C", "MikuMikuDance - PMX compatible", " "),
            ("D", t('prep_drop_D'), t('prep_drop_D_tt')),
            ("B", t('prep_drop_B'), t('prep_drop_B_tt')),
        ), name="", default="A", description=t('prep_drop'))

    simp_dropdown : EnumProperty(
        items=(
            ("A", t('simp_drop_A'), t('simp_drop_A_tt')),
            ("B", t('simp_drop_B'), t('simp_drop_B_tt')),
            ("C", t('simp_drop_C'), t('simp_drop_C_tt')),
        ), name="", default="A", description=t('simp_drop'))
    
    bake_light_bool : BoolProperty(
    description=t('bake_light_tt'),
    default = True)

    bake_dark_bool : BoolProperty(
    description=t('bake_dark_tt'),
    default = True)

    bake_norm_bool : BoolProperty(
    description=t('bake_norm_tt'),
    default = False)

    shapekeys_dropdown : EnumProperty(
        items=(
            ("A", t('shape_A'), t('shape_A_tt')),
            ("B", t('shape_B'), t('shape_B_tt')),
            ("C", t('shape_C'), t('shape_C_tt')),
        ), name="", default="A", description="")
    
    shader_dropdown : EnumProperty(
        items=(
            ("A", t('shader_A'), ''),
            ("B", t('shader_B'), ''),
            ("C", t('shader_C'), t('shader_C_tt')),
        ), name="", default="A", description="Shader")
    
    def draw(self, context):
        layout = self.layout
        splitfac = 0.5
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.prop(self, "armature_dropdown")
        split.prop(self, "categorize_dropdown")

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(self, "colors_dropdown")

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(self, "shapekeys_dropdown")
        split.prop(self, "shader_dropdown")
        
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(self, "fix_seams", toggle=True, text = t('seams'))
        split.prop(self, "templates_bool", toggle=True, text = t('keep_templates'))

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(self, "texture_outline_bool", toggle=True, text = t('outline'))
        split.prop(self, "sfw_mode", toggle=True, text = t('sfw_mode'))

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.prop(self, 'old_bake_bool', toggle=True, text = t('old_bake'))
