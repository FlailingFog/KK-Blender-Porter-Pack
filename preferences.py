#The preferences for the plugin 

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty

from .interface.dictionary_en import t

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
    
    use_single_outline : BoolProperty(
    description= t('outline_tt'),
    default = False)
    
    use_material_fake_user : BoolProperty(
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
        ), name="", default="A", description=t('cat_drop'))

    colors_dropdown : BoolProperty(
    description=t('dark_F_tt'),
    default = True)

    bake_light_bool : BoolProperty(
    description=t('bake_light_tt'),
    default = True)

    bake_dark_bool : BoolProperty(
    description=t('bake_dark_tt'),
    default = True)

    bake_norm_bool : BoolProperty(
    description=t('bake_norm_tt'),
    default = False)

    use_atlas : BoolProperty(
    description=t('use_atlas'),
    default = False)

    delete_cache : BoolProperty(
    description=t('delete_cache'),
    default = False)

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
            ("D", t('shader_D'), ''),
            ("C", t('shader_C'), t('shader_C_tt')),
        ), name="", default="A", description="Shader")
    
    max_thread_num: IntProperty(
        min=1, max = 128,
        default=8,
        description='''This is how many cpu cores you want to use to saturate the images. 
If you have a better CPU, you can set it higher.
Default is 8''')

    max_image_num: IntProperty(
        min=1, max = 20,
        default=2,
        description='''this is related to memory usage.
Actually it's not perfect because the size of each image varies.
If loading two 4096 * 4096, the peak memory usage could reach 8000MB.
If the user doesn't have this much available memory, the program will crash.
In that case, the user should lower the value.
Default is 2''')

    batch_rows: IntProperty(
        min=256, max = 4096,
        default=512,
        description='''this is related to cpu and memory usage.
This is the number of rows of pixels to process in one batch (images are saturated in batches).
Simply separate images in rows, ignoring that the num of column usually increase as num of rows increasing
For a 1024 * 1024, a batch is 512 * 1024.But for 2048 * 2048, a batch is 512 * 2048.
Default is 512''')

    def draw(self, context):
        layout = self.layout
        splitfac = 0.5

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text='Change the default options for the KKBP Importer below:')
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(self, "categorize_dropdown")
        split.prop(self, "armature_dropdown")
        
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(self, "shapekeys_dropdown")
        split.prop(self, "shader_dropdown")

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(self, "colors_dropdown", toggle=True, text = t('dark_F'))
        split.prop(self, "delete_cache", toggle=True, text = t('delete_cache'))

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(self, "fix_seams", toggle=True, text = t('seams'))
        split.prop(self, "use_material_fake_user", toggle=True, text = t('keep_templates'))

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(self, "use_single_outline", toggle=True, text = t('outline'))
        split.prop(self, "sfw_mode", toggle=True, text = t('sfw_mode'))
        
        col = layout.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=0.33)
        split.prop(self, "bake_light_bool", toggle=True, text = t('bake_light'))
        split.prop(self, "bake_dark_bool", toggle=True, text = t('bake_dark'))
        split.prop(self, "bake_norm_bool", toggle=True, text = t('bake_norm'))
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.prop(self, 'old_bake_bool', toggle=True, text = t('old_bake'))
        row = col.row(align = True)
        split = row.split(align=True, factor=splitfac)
        split.prop(self, "use_atlas", toggle=True, text = t('use_atlas'))
        
        col = layout.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.prop(self, "simp_dropdown")
        split.prop(self, "prep_dropdown")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text='Change these options based on your computer specs to speed up the import process:')
        row = col.row(align=True)
        split = row.split(align=True, factor=0.33)
        split.prop(self, "max_thread_num", text = 'Maxthreads')
        split.prop(self, "max_image_num", text = 'Max parallel images')
        split.prop(self, "batch_rows", text = 'Max rows in one batch')

