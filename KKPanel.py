from typing import Text
import bpy
from bpy.types import Panel, PropertyGroup, Scene, WindowManager
from bpy.props import (
    IntProperty,
    EnumProperty,
    BoolProperty,
    StringProperty
)

#load plugin language
from bpy.app.translations import locale
if locale == 'ja_JP':
    from .interface.dictionary_jp import t
else:
    from .interface.dictionary_en import t

class PlaceholderProperties(PropertyGroup):
    # A property used by the plugin to keep track of the user's pmx directory during the import process.
    # This string is automatically cleared after the Import Colors script is run.
    import_dir: StringProperty(
        default='')

    bake_mult: IntProperty(
        min=1, max = 6,
        default=1,
        description=t('bake_mult_tt'))

    #A property used to let the plugin know if the model has been prepped for export or not
    is_prepped : BoolProperty(
    default = False)

    sfw_mode : BoolProperty(
    description=t('sfw_mode_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.sfw_mode)

    fix_seams : BoolProperty(
    description=t('seams_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.fix_seams)
    
    texture_outline_bool : BoolProperty(
    description= t('outline_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.texture_outline_bool)
    
    templates_bool : BoolProperty(
    description=t('keep_templates_tt'),
    default = bpy.context.preferences.addons[__package__].preferences.templates_bool)

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
            ("C", t('cat_drop_C'), t('cat_drop_C_tt') ),
            ("D", t('cat_drop_D'), t('cat_drop_D_tt')),
        ), name="", default=bpy.context.preferences.addons[__package__].preferences.categorize_dropdown, description=t('cat_drop'))
    
    colors_dropdown : EnumProperty(
        items=(
            ("A", t('dark_A'), t('dark_A_tt')),
            ("B", t('dark_B'), t('dark_B_tt')),
            ("C", t('dark_C'), t('dark_C_tt')),
            ("D", t('dark_D'), t('dark_D_tt')),
            ("E", t('dark_E'), t('dark_E_tt')),
            ("F", t('dark_F'), t('dark_F_tt'))
        ), name="", default=bpy.context.preferences.addons[__package__].preferences.colors_dropdown, description=t('dark'))
    
    prep_dropdown : EnumProperty(
        items=(
            ("A", t('prep_drop_A'), t('prep_drop_A_tt')),
            #("C", "MikuMikuDance - PMX compatible", " "),
            ("D", t('prep_drop_D'), t('prep_drop_D_tt')),
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
        ), name="", default=bpy.context.preferences.addons[__package__].preferences.shapekeys_dropdown, description="")
    
    shader_dropdown : EnumProperty(
        items=(
            ("A", t('shader_A'), ''),
            ("B", t('shader_B'), ''),
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
        description="""Enable this if you want the plugin to saturate the item's textures using the in-game LUT""",
        default = False)

    rokoko_bool : BoolProperty(
        name="Enable or Disable",
        description="""Enable this if you don't want KKBP to process the fbx animation, and instead want to use the rokoko plugin to transfer the fbx animation to your character.
        Stock / unmodified armatures only!""",
        default = False)

    image_dropdown : EnumProperty(
        items=(
            ("A", t('dark_C'), "Use Day LUT to saturate image"),
            ("B", t('dark_A'), "Use Night LUT to saturate image"),
            ("C", t('dark_B'), "Use Sunset LUT to saturate image")
        ), name="", default="A", description="LUT Choice")
    

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
        
        row = col.row(align=True)
        row.operator('kkb.quickimport', text = t('import_model'), icon='MODIFIER')
        row.enabled = not scene.import_dir == 'cleared' and not scene.is_prepped
        
        row = col.row(align=True)
        row.label(text="")
        
        row = col.row(align = True)
        box = row.box()
        col = box.column(align=True)
        
        if scene.categorize_dropdown in ['B']:
            row = col.row(align=True)
            row.operator('kkb.matimport', text = t('finish_cat'), icon='BRUSHES_ALL')
            row.enabled = not scene.import_dir == 'cleared' and not scene.is_prepped
        
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "armature_dropdown")
        split.prop(context.scene.kkbp, "categorize_dropdown")
        row.enabled = not scene.import_dir == 'cleared' and not scene.is_prepped
        
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "colors_dropdown")
        split.operator('kkb.importcolors', text = t('recalc_dark'), icon='IMAGE')
        row.enabled = True

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "shapekeys_dropdown")
        split.prop(context.scene.kkbp, "shader_dropdown")
        
        row.enabled = not scene.import_dir == 'cleared' and not scene.is_prepped
        
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "fix_seams", toggle=True, text = t('seams'))
        split.prop(context.scene.kkbp, "templates_bool", toggle=True, text = t('keep_templates'))
        row.enabled = not scene.import_dir == 'cleared' and not scene.is_prepped

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.prop(context.scene.kkbp, "texture_outline_bool", toggle=True, text = t('outline'))
        split.prop(context.scene.kkbp, "sfw_mode", toggle=True, text = t('sfw_mode'))
        row.enabled = not scene.import_dir == 'cleared' and not scene.is_prepped
    
class EXPORTING_PT_panel(bpy.types.Panel):
    bl_parent_id = "IMPORTING_PT_panel"
    bl_label = 'Exporting'
    bl_options = {'HIDE_HEADER'}
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self,context):
        layout = self.layout
        splitfac = 0.5
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator('kkb.selectbones', text = t('prep'), icon = 'GROUP')
        row.enabled = not context.scene.kkbp.is_prepped
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.prop(context.scene.kkbp, "simp_dropdown")
        split.prop(context.scene.kkbp, "prep_dropdown")
        row.enabled = not context.scene.kkbp.is_prepped

        col = box.column(align=True)
        row = col.row(align=True)
        row.operator('kkb.bakematerials', text = t('bake'), icon='VIEW_CAMERA')
        row = col.row(align=True)
        split = row.split(align=True, factor=0.33)
        split.prop(context.scene.kkbp, "bake_light_bool", toggle=True, text = t('bake_light'))
        split.prop(context.scene.kkbp, "bake_dark_bool", toggle=True, text = t('bake_dark'))
        split.prop(context.scene.kkbp, "bake_norm_bool", toggle=True, text = t('bake_norm'))
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.prop(context.scene.kkbp, 'old_bake_bool', toggle=True, text = t('old_bake'))
        split.prop(context.scene.kkbp, "bake_mult", text = t('bake_mult'))

        col = box.column(align=True)
        row = col.row(align=True)
        row.operator('kkb.applymaterials', text = t('apply_temp'), icon = 'FILE_REFRESH')
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.label(text=t('atlas'))
        split.prop(context.scene.kkbp, "atlas_dropdown")
    
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator('kkb.exportfbx', text = t('export_fbx'), icon = 'FILEBROWSER')

class EXTRAS_PT_panel(bpy.types.Panel):
    bl_label = 'KKBP Extras'
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self,context):
        layout = self.layout
        splitfac = 0.6
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="Import studio object")
        split.operator('kkb.importstudio', text = '', icon = 'MATCUBE')
        row = col.row(align=True)
        split = row.split(align=True)
        split.label(text="Shader")
        split.label(text="Shadow type")
        split.label(text="Blend mode")
        split.label(text="")
        row = col.row(align=True)
        split = row.split(align=True)
        split.prop(context.scene.kkbp, "dropdown_box")
        split.prop(context.scene.kkbp, "shadows_dropdown")
        split.prop(context.scene.kkbp, "blend_dropdown")
        split.prop(context.scene.kkbp, "studio_lut_bool", toggle=True, text = "Convert texture?")

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="Update bone visibility")
        split.operator('kkb.updatebones', text = '', icon = 'HIDE_OFF')

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text=t('rigify_convert'))
        split.operator('kkb.rigifyconvert', text = '', icon='SOLO_OFF')

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="Import ripped FBX animation")
        split.operator('kkb.importanimation', text = '', icon = 'ARMATURE_DATA')
        #row = col.row(align=True)
        #split = row.split(align=True, factor=splitfac)
        #split.label(text="")
        #split.prop(context.scene.kkbp, "rokoko_bool", toggle=True, text = "Use Rokoko plugin")
        
        #col = box.column(align=True)
        #row = col.row(align=True)
        #split = row.split(align=True, factor=splitfac)
        #split.label(text="Swap armature type")
        #split.operator('kkb.switcharmature', text = '', icon = 'ARROW_LEFTRIGHT')

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="Toggle hand IKs")
        split.operator('kkb.toggleik', text = '', icon = 'BONE_DATA')
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        
        split.label(text="Export Seperate Meshes")
        split.operator('kkb.exportseparatemeshes', text = '', icon = 'EXPORT')
        
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text=t('sep_eye'))
        split.operator('kkb.linkshapekeys', text = '', icon='SPHERECURVE')

        #put all icons available in blender at the end of the panel

'''        icons = ['NONE', 'QUESTION', 'ERROR', 'CANCEL', 'TRIA_RIGHT', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_UP', 'ARROW_LEFTRIGHT', 'PLUS', 'DISCLOSURE_TRI_RIGHT', 'DISCLOSURE_TRI_DOWN', 'RADIOBUT_OFF', 'RADIOBUT_ON', 'MENU_PANEL', 'BLENDER', 'GRIP', 'DOT', 'COLLAPSEMENU', 'X', 'DUPLICATE', 'TRASH', 'COLLECTION_NEW', 'OPTIONS', 'NODE', 'NODE_SEL', 'WINDOW', 'WORKSPACE', 'RIGHTARROW_THIN', 'BORDERMOVE', 'VIEWZOOM', 'ADD', 'REMOVE', 'PANEL_CLOSE', 'COPY_ID', 'EYEDROPPER', 'CHECKMARK', 'AUTO', 'CHECKBOX_DEHLT', 'CHECKBOX_HLT', 'UNLOCKED', 'LOCKED', 'UNPINNED', 'PINNED', 'SCREEN_BACK', 'RIGHTARROW', 'DOWNARROW_HLT', 'FCURVE_SNAPSHOT', 'OBJECT_HIDDEN', 'TOPBAR', 'STATUSBAR', 'PLUGIN', 'HELP', 'GHOST_ENABLED', 'COLOR', 'UNLINKED', 'LINKED', 'HAND', 'ZOOM_ALL', 'ZOOM_SELECTED', 'ZOOM_PREVIOUS', 'ZOOM_IN', 'ZOOM_OUT', 'DRIVER_DISTANCE', 'DRIVER_ROTATIONAL_DIFFERENCE', 'DRIVER_TRANSFORM', 'FREEZE', 'STYLUS_PRESSURE', 'GHOST_DISABLED', 'FILE_NEW', 'FILE_TICK', 'QUIT', 'URL', 'RECOVER_LAST', 'THREE_DOTS', 'FULLSCREEN_ENTER', 'FULLSCREEN_EXIT', 'BRUSHES_ALL', 'LIGHT', 'MATERIAL', 'TEXTURE', 'ANIM', 'WORLD', 'SCENE', 'OUTPUT', 'SCRIPT', 'PARTICLES', 'PHYSICS', 'SPEAKER', 'TOOL_SETTINGS', 'SHADERFX', 'MODIFIER', 'BLANK1', 'FAKE_USER_OFF', 'FAKE_USER_ON', 'VIEW3D', 'GRAPH', 'OUTLINER', 'PROPERTIES', 'FILEBROWSER', 'IMAGE', 'INFO', 'SEQUENCE', 'TEXT', 'SPREADSHEET', 'SOUND', 'ACTION', 'NLA', 'PREFERENCES', 'TIME', 'NODETREE', 'CONSOLE', 'TRACKER', 'ASSET_MANAGER', 'NODE_COMPOSITING', 'NODE_TEXTURE', 'NODE_MATERIAL', 'UV', 'OBJECT_DATAMODE', 'EDITMODE_HLT', 'UV_DATA', 'VPAINT_HLT', 'TPAINT_HLT', 'WPAINT_HLT', 'SCULPTMODE_HLT', 'POSE_HLT', 'PARTICLEMODE', 'TRACKING', 'TRACKING_BACKWARDS', 'TRACKING_FORWARDS', 'TRACKING_BACKWARDS_SINGLE', 'TRACKING_FORWARDS_SINGLE', 'TRACKING_CLEAR_BACKWARDS', 'TRACKING_CLEAR_FORWARDS', 'TRACKING_REFINE_BACKWARDS', 'TRACKING_REFINE_FORWARDS', 'SCENE_DATA', 'RENDERLAYERS', 'WORLD_DATA', 'OBJECT_DATA', 'MESH_DATA', 'CURVE_DATA', 'META_DATA', 'LATTICE_DATA', 'LIGHT_DATA', 'MATERIAL_DATA', 'TEXTURE_DATA', 'ANIM_DATA', 'CAMERA_DATA', 'PARTICLE_DATA', 'LIBRARY_DATA_DIRECT', 'GROUP', 'ARMATURE_DATA', 'COMMUNITY', 'BONE_DATA', 'CONSTRAINT', 'SHAPEKEY_DATA', 'CONSTRAINT_BONE', 'CAMERA_STEREO', 'PACKAGE', 'UGLYPACKAGE', 'EXPERIMENTAL', 'BRUSH_DATA', 'IMAGE_DATA', 'FILE', 'FCURVE', 'FONT_DATA', 'RENDER_RESULT', 'SURFACE_DATA', 'EMPTY_DATA', 'PRESET', 'RENDER_ANIMATION', 'RENDER_STILL', 'LIBRARY_DATA_BROKEN', 'BOIDS', 'STRANDS', 'LIBRARY_DATA_INDIRECT', 'GREASEPENCIL', 'LINE_DATA', 'LIBRARY_DATA_OVERRIDE', 'GROUP_BONE', 'GROUP_VERTEX', 'GROUP_VCOL', 'GROUP_UVS', 'FACE_MAPS', 'RNA', 'RNA_ADD', 'MOUSE_LMB', 'MOUSE_MMB', 'MOUSE_RMB', 'MOUSE_MOVE', 'MOUSE_LMB_DRAG', 'MOUSE_MMB_DRAG', 'MOUSE_RMB_DRAG', 'MEMORY', 'PRESET_NEW', 'DECORATE', 'DECORATE_KEYFRAME', 'DECORATE_ANIMATE', 'DECORATE_DRIVER', 'DECORATE_LINKED', 'DECORATE_LIBRARY_OVERRIDE', 'DECORATE_UNLOCKED', 'DECORATE_LOCKED', 'DECORATE_OVERRIDE', 'FUND', 'TRACKER_DATA', 'HEART', 'ORPHAN_DATA', 'USER', 'SYSTEM', 'SETTINGS', 'OUTLINER_OB_EMPTY', 'OUTLINER_OB_MESH', 'OUTLINER_OB_CURVE', 'OUTLINER_OB_LATTICE', 'OUTLINER_OB_META', 'OUTLINER_OB_LIGHT', 'OUTLINER_OB_CAMERA', 'OUTLINER_OB_ARMATURE', 'OUTLINER_OB_FONT', 'OUTLINER_OB_SURFACE', 'OUTLINER_OB_SPEAKER', 'OUTLINER_OB_FORCE_FIELD', 'OUTLINER_OB_GROUP_INSTANCE', 'OUTLINER_OB_GREASEPENCIL', 'OUTLINER_OB_LIGHTPROBE', 'OUTLINER_OB_IMAGE', 'OUTLINER_COLLECTION', 'RESTRICT_COLOR_OFF', 'RESTRICT_COLOR_ON', 'HIDE_ON', 'HIDE_OFF', 'RESTRICT_SELECT_ON', 'RESTRICT_SELECT_OFF', 'RESTRICT_RENDER_ON', 'RESTRICT_RENDER_OFF', 'RESTRICT_INSTANCED_OFF', 'OUTLINER_DATA_EMPTY', 'OUTLINER_DATA_MESH', 'OUTLINER_DATA_CURVE', 'OUTLINER_DATA_LATTICE', 'OUTLINER_DATA_META', 'OUTLINER_DATA_LIGHT', 'OUTLINER_DATA_CAMERA', 'OUTLINER_DATA_ARMATURE', 'OUTLINER_DATA_FONT', 'OUTLINER_DATA_SURFACE', 'OUTLINER_DATA_SPEAKER', 'OUTLINER_DATA_LIGHTPROBE', 'OUTLINER_DATA_GP_LAYER', 'OUTLINER_DATA_GREASEPENCIL', 'GP_SELECT_POINTS', 'GP_SELECT_STROKES', 'GP_MULTIFRAME_EDITING', 'GP_ONLY_SELECTED', 'GP_SELECT_BETWEEN_STROKES', 'MODIFIER_OFF', 'MODIFIER_ON', 'ONIONSKIN_OFF', 'ONIONSKIN_ON', 'RESTRICT_VIEW_ON', 'RESTRICT_VIEW_OFF', 'RESTRICT_INSTANCED_ON', 'MESH_PLANE', 'MESH_CUBE', 'MESH_CIRCLE', 'MESH_UVSPHERE', 'MESH_ICOSPHERE', 'MESH_GRID', 'MESH_MONKEY', 'MESH_CYLINDER', 'MESH_TORUS', 'MESH_CONE', 'MESH_CAPSULE', 'EMPTY_SINGLE_ARROW', 'LIGHT_POINT', 'LIGHT_SUN', 'LIGHT_SPOT', 'LIGHT_HEMI', 'LIGHT_AREA', 'CUBE', 'SPHERE', 'CONE', 'META_PLANE', 'META_CUBE', 'META_BALL', 'META_ELLIPSOID', 'META_CAPSULE', 'SURFACE_NCURVE', 'SURFACE_NCIRCLE', 'SURFACE_NSURFACE', 'SURFACE_NCYLINDER', 'SURFACE_NSPHERE', 'SURFACE_NTORUS', 'EMPTY_AXIS', 'STROKE', 'EMPTY_ARROWS', 'CURVE_BEZCURVE', 'CURVE_BEZCIRCLE', 'CURVE_NCURVE', 'CURVE_NCIRCLE', 'CURVE_PATH', 'LIGHTPROBE_CUBEMAP', 'LIGHTPROBE_PLANAR', 'LIGHTPROBE_GRID', 'COLOR_RED', 'COLOR_GREEN', 'COLOR_BLUE', 'TRIA_RIGHT_BAR', 'TRIA_DOWN_BAR', 'TRIA_LEFT_BAR', 'TRIA_UP_BAR', 'FORCE_FORCE', 'FORCE_WIND', 'FORCE_VORTEX', 'FORCE_MAGNETIC', 'FORCE_HARMONIC', 'FORCE_CHARGE', 'FORCE_LENNARDJONES', 'FORCE_TEXTURE', 'FORCE_CURVE', 'FORCE_BOID', 'FORCE_TURBULENCE', 'FORCE_DRAG', 'FORCE_FLUIDFLOW', 'RIGID_BODY', 'RIGID_BODY_CONSTRAINT', 'IMAGE_PLANE', 'IMAGE_BACKGROUND', 'IMAGE_REFERENCE', 'NODE_INSERT_ON', 'NODE_INSERT_OFF', 'NODE_TOP', 'NODE_SIDE', 'NODE_CORNER', 'ANCHOR_TOP', 'ANCHOR_BOTTOM', 'ANCHOR_LEFT', 'ANCHOR_RIGHT', 'ANCHOR_CENTER', 'SELECT_SET', 'SELECT_EXTEND', 'SELECT_SUBTRACT', 'SELECT_INTERSECT', 'SELECT_DIFFERENCE', 'ALIGN_LEFT', 'ALIGN_CENTER', 'ALIGN_RIGHT', 'ALIGN_JUSTIFY', 'ALIGN_FLUSH', 'ALIGN_TOP', 'ALIGN_MIDDLE', 'ALIGN_BOTTOM', 'BOLD', 'ITALIC', 'UNDERLINE', 'SMALL_CAPS', 'CON_ACTION', 'HOLDOUT_OFF', 'HOLDOUT_ON', 'INDIRECT_ONLY_OFF', 'INDIRECT_ONLY_ON', 'CON_CAMERASOLVER', 'CON_FOLLOWTRACK', 'CON_OBJECTSOLVER', 'CON_LOCLIKE', 'CON_ROTLIKE', 'CON_SIZELIKE', 'CON_TRANSLIKE', 'CON_DISTLIMIT', 'CON_LOCLIMIT', 'CON_ROTLIMIT', 'CON_SIZELIMIT', 'CON_SAMEVOL', 'CON_TRANSFORM', 'CON_TRANSFORM_CACHE', 'CON_CLAMPTO', 'CON_KINEMATIC', 'CON_LOCKTRACK', 'CON_SPLINEIK', 'CON_STRETCHTO', 'CON_TRACKTO', 'CON_ARMATURE', 'CON_CHILDOF', 'CON_FLOOR', 'CON_FOLLOWPATH', 'CON_PIVOT', 'CON_SHRINKWRAP', 'MODIFIER_DATA', 'MOD_WAVE', 'MOD_BUILD', 'MOD_DECIM', 'MOD_MIRROR', 'MOD_SOFT', 'MOD_SUBSURF', 'HOOK', 'MOD_PHYSICS', 'MOD_PARTICLES', 'MOD_BOOLEAN', 'MOD_EDGESPLIT', 'MOD_ARRAY', 'MOD_UVPROJECT', 'MOD_DISPLACE', 'MOD_CURVE', 'MOD_LATTICE', 'MOD_TINT', 'MOD_ARMATURE', 'MOD_SHRINKWRAP', 'MOD_CAST', 'MOD_MESHDEFORM', 'MOD_BEVEL', 'MOD_SMOOTH', 'MOD_SIMPLEDEFORM', 'MOD_MASK', 'MOD_CLOTH', 'MOD_EXPLODE', 'MOD_FLUIDSIM', 'MOD_MULTIRES', 'MOD_FLUID', 'MOD_SOLIDIFY', 'MOD_SCREW', 'MOD_VERTEX_WEIGHT', 'MOD_DYNAMICPAINT', 'MOD_REMESH', 'MOD_OCEAN', 'MOD_WARP', 'MOD_SKIN', 'MOD_TRIANGULATE', 'MOD_WIREFRAME', 'MOD_DATA_TRANSFER', 'MOD_NORMALEDIT', 'MOD_PARTICLE_INSTANCE', 'MOD_HUE_SATURATION', 'MOD_NOISE', 'MOD_OFFSET', 'MOD_SIMPLIFY', 'MOD_THICKNESS', 'MOD_INSTANCE', 'MOD_TIME', 'MOD_OPACITY', 'REC', 'PLAY', 'FF', 'REW', 'PAUSE', 'PREV_KEYFRAME', 'NEXT_KEYFRAME', 'PLAY_SOUND', 'PLAY_REVERSE', 'PREVIEW_RANGE', 'ACTION_TWEAK', 'PMARKER_ACT', 'PMARKER_SEL', 'PMARKER', 'MARKER_HLT', 'MARKER', 'KEYFRAME_HLT', 'KEYFRAME', 'KEYINGSET', 'KEY_DEHLT', 'KEY_HLT', 'MUTE_IPO_OFF', 'MUTE_IPO_ON', 'DRIVER', 'SOLO_OFF', 'SOLO_ON', 'FRAME_PREV', 'FRAME_NEXT', 'NLA_PUSHDOWN', 'IPO_CONSTANT', 'IPO_LINEAR', 'IPO_BEZIER', 'IPO_SINE', 'IPO_QUAD', 'IPO_CUBIC', 'IPO_QUART', 'IPO_QUINT', 'IPO_EXPO', 'IPO_CIRC', 'IPO_BOUNCE', 'IPO_ELASTIC', 'IPO_BACK', 'IPO_EASE_IN', 'IPO_EASE_OUT', 'IPO_EASE_IN_OUT', 'NORMALIZE_FCURVES', 'VERTEXSEL', 'EDGESEL', 'FACESEL', 'CURSOR', 'PIVOT_BOUNDBOX', 'PIVOT_CURSOR', 'PIVOT_INDIVIDUAL', 'PIVOT_MEDIAN', 'PIVOT_ACTIVE', 'CENTER_ONLY', 'ROOTCURVE', 'SMOOTHCURVE', 'SPHERECURVE', 'INVERSESQUARECURVE', 'SHARPCURVE', 'LINCURVE', 'NOCURVE', 'RNDCURVE', 'PROP_OFF', 'PROP_ON', 'PROP_CON', 'PROP_PROJECTED', 'PARTICLE_POINT', 'PARTICLE_TIP', 'PARTICLE_PATH', 'SNAP_FACE_CENTER', 'SNAP_PERPENDICULAR', 'SNAP_MIDPOINT', 'SNAP_OFF', 'SNAP_ON', 'SNAP_NORMAL', 'SNAP_GRID', 'SNAP_VERTEX', 'SNAP_EDGE', 'SNAP_FACE', 'SNAP_VOLUME', 'SNAP_INCREMENT', 'STICKY_UVS_LOC', 'STICKY_UVS_DISABLE', 'STICKY_UVS_VERT', 'CLIPUV_DEHLT', 'CLIPUV_HLT', 'SNAP_PEEL_OBJECT', 'GRID', 'OBJECT_ORIGIN', 'ORIENTATION_GLOBAL', 'ORIENTATION_GIMBAL', 'ORIENTATION_LOCAL', 'ORIENTATION_NORMAL', 'ORIENTATION_VIEW', 'COPYDOWN', 'PASTEDOWN', 'PASTEFLIPUP', 'PASTEFLIPDOWN', 'VIS_SEL_11', 'VIS_SEL_10', 'VIS_SEL_01', 'VIS_SEL_00', 'AUTOMERGE_OFF', 'AUTOMERGE_ON', 'UV_VERTEXSEL', 'UV_EDGESEL', 'UV_FACESEL', 'UV_ISLANDSEL', 'UV_SYNC_SELECT', 'TRANSFORM_ORIGINS', 'GIZMO', 'ORIENTATION_CURSOR', 'NORMALS_VERTEX', 'NORMALS_FACE', 'NORMALS_VERTEX_FACE', 'SHADING_BBOX', 'SHADING_WIRE', 'SHADING_SOLID', 'SHADING_RENDERED', 'SHADING_TEXTURE', 'OVERLAY', 'XRAY', 'LOCKVIEW_OFF', 'LOCKVIEW_ON', 'AXIS_SIDE', 'AXIS_FRONT', 'AXIS_TOP', 'LAYER_USED', 'LAYER_ACTIVE', 'OUTLINER_OB_HAIR', 'OUTLINER_DATA_HAIR', 'HAIR_DATA', 'OUTLINER_OB_POINTCLOUD', 'OUTLINER_DATA_POINTCLOUD', 'POINTCLOUD_DATA', 'OUTLINER_OB_VOLUME', 'OUTLINER_DATA_VOLUME', 'VOLUME_DATA', 'HOME', 'DOCUMENTS', 'TEMP', 'SORTALPHA', 'SORTBYEXT', 'SORTTIME', 'SORTSIZE', 'SHORTDISPLAY', 'LONGDISPLAY', 'IMGDISPLAY', 'BOOKMARKS', 'FONTPREVIEW', 'FILTER', 'NEWFOLDER', 'FOLDER_REDIRECT', 'FILE_PARENT', 'FILE_REFRESH', 'FILE_FOLDER', 'FILE_BLANK', 'FILE_BLEND', 'FILE_IMAGE', 'FILE_MOVIE', 'FILE_SCRIPT', 'FILE_SOUND', 'FILE_FONT', 'FILE_TEXT', 'SORT_DESC', 'SORT_ASC', 'LINK_BLEND', 'APPEND_BLEND', 'IMPORT', 'EXPORT', 'LOOP_BACK', 'LOOP_FORWARDS', 'BACK', 'FORWARD', 'FILE_ARCHIVE', 'FILE_CACHE', 'FILE_VOLUME', 'FILE_3D', 'FILE_HIDDEN', 'FILE_BACKUP', 'DISK_DRIVE', 'MATPLANE', 'MATSPHERE', 'MATCUBE', 'MONKEY', 'HAIR', 'ALIASED', 'ANTIALIASED', 'MAT_SPHERE_SKY', 'MATSHADERBALL', 'MATCLOTH', 'MATFLUID', 'WORDWRAP_OFF', 'WORDWRAP_ON', 'SYNTAX_OFF', 'SYNTAX_ON', 'LINENUMBERS_OFF', 'LINENUMBERS_ON', 'SCRIPTPLUGINS', 'DISC', 'DESKTOP', 'EXTERNAL_DRIVE', 'NETWORK_DRIVE', 'SEQ_SEQUENCER', 'SEQ_PREVIEW', 'SEQ_LUMA_WAVEFORM', 'SEQ_CHROMA_SCOPE', 'SEQ_HISTOGRAM', 'SEQ_SPLITVIEW', 'SEQ_STRIP_META', 'SEQ_STRIP_DUPLICATE', 'IMAGE_RGB', 'IMAGE_RGB_ALPHA', 'IMAGE_ALPHA', 'IMAGE_ZDEPTH', 'HANDLE_AUTOCLAMPED', 'HANDLE_AUTO', 'HANDLE_ALIGNED', 'HANDLE_VECTOR', 'HANDLE_FREE', 'VIEW_PERSPECTIVE', 'VIEW_ORTHO', 'VIEW_CAMERA', 'VIEW_PAN', 'VIEW_ZOOM', 'BRUSH_BLOB', 'BRUSH_BLUR', 'BRUSH_CLAY', 'BRUSH_CLAY_STRIPS', 'BRUSH_CLONE', 'BRUSH_CREASE', 'BRUSH_FILL', 'BRUSH_FLATTEN', 'BRUSH_GRAB', 'BRUSH_INFLATE', 'BRUSH_LAYER', 'BRUSH_MASK', 'BRUSH_MIX', 'BRUSH_NUDGE', 'BRUSH_PINCH', 'BRUSH_SCRAPE', 'BRUSH_SCULPT_DRAW', 'BRUSH_SMEAR', 'BRUSH_SMOOTH', 'BRUSH_SNAKE_HOOK', 'BRUSH_SOFTEN', 'BRUSH_TEXDRAW', 'BRUSH_TEXFILL', 'BRUSH_TEXMASK', 'BRUSH_THUMB', 'BRUSH_ROTATE', 'GPBRUSH_SMOOTH', 'GPBRUSH_THICKNESS', 'GPBRUSH_STRENGTH', 'GPBRUSH_GRAB', 'GPBRUSH_PUSH', 'GPBRUSH_TWIST', 'GPBRUSH_PINCH', 'GPBRUSH_RANDOMIZE', 'GPBRUSH_CLONE', 'GPBRUSH_WEIGHT', 'GPBRUSH_PENCIL', 'GPBRUSH_PEN', 'GPBRUSH_INK', 'GPBRUSH_INKNOISE', 'GPBRUSH_BLOCK', 'GPBRUSH_MARKER', 'GPBRUSH_FILL', 'GPBRUSH_AIRBRUSH', 'GPBRUSH_CHISEL', 'GPBRUSH_ERASE_SOFT', 'GPBRUSH_ERASE_HARD', 'GPBRUSH_ERASE_STROKE', 'SMALL_TRI_RIGHT_VEC', 'KEYTYPE_KEYFRAME_VEC', 'KEYTYPE_BREAKDOWN_VEC', 'KEYTYPE_EXTREME_VEC', 'KEYTYPE_JITTER_VEC', 'KEYTYPE_MOVING_HOLD_VEC', 'HANDLETYPE_FREE_VEC', 'HANDLETYPE_ALIGNED_VEC', 'HANDLETYPE_VECTOR_VEC', 'HANDLETYPE_AUTO_VEC', 'HANDLETYPE_AUTO_CLAMP_VEC', 'COLORSET_01_VEC', 'COLORSET_02_VEC', 'COLORSET_03_VEC', 'COLORSET_04_VEC', 'COLORSET_05_VEC', 'COLORSET_06_VEC', 'COLORSET_07_VEC', 'COLORSET_08_VEC', 'COLORSET_09_VEC', 'COLORSET_10_VEC', 'COLORSET_11_VEC', 'COLORSET_12_VEC', 'COLORSET_13_VEC', 'COLORSET_14_VEC', 'COLORSET_15_VEC', 'COLORSET_16_VEC', 'COLORSET_17_VEC', 'COLORSET_18_VEC', 'COLORSET_19_VEC', 'COLORSET_20_VEC', 'COLLECTION_COLOR_01', 'COLLECTION_COLOR_02', 'COLLECTION_COLOR_03', 'COLLECTION_COLOR_04', 'COLLECTION_COLOR_05', 'COLLECTION_COLOR_06', 'COLLECTION_COLOR_07', 'COLLECTION_COLOR_08', 'EVENT_A', 'EVENT_B', 'EVENT_C', 'EVENT_D', 'EVENT_E', 'EVENT_F', 'EVENT_G', 'EVENT_H', 'EVENT_I', 'EVENT_J', 'EVENT_K', 'EVENT_L', 'EVENT_M', 'EVENT_N', 'EVENT_O', 'EVENT_P', 'EVENT_Q', 'EVENT_R', 'EVENT_S', 'EVENT_T', 'EVENT_U', 'EVENT_V', 'EVENT_W', 'EVENT_X', 'EVENT_Y', 'EVENT_Z', 'EVENT_SHIFT', 'EVENT_CTRL', 'EVENT_ALT', 'EVENT_OS', 'EVENT_F1', 'EVENT_F2', 'EVENT_F3', 'EVENT_F4', 'EVENT_F5', 'EVENT_F6', 'EVENT_F7', 'EVENT_F8', 'EVENT_F9', 'EVENT_F10', 'EVENT_F11', 'EVENT_F12', 'EVENT_ESC', 'EVENT_TAB', 'EVENT_PAGEUP', 'EVENT_PAGEDOWN', 'EVENT_RETURN', 'EVENT_SPACEKEY']
        for icon in icons:
            row = col.row(align=True)
            split = row.split(align=True, factor=.5)
            split.label(text=icon)
            split.operator('kkb.linkshapekeys', icon = icon)
'''


class EDITOR_PT_panel(bpy.types.Panel):
    bl_label = 'Convert Image'
    bl_category = "KKBP"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    def draw(self,context):
        layout = self.layout
        splitfac = 0.6

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align = True)
        row.operator('kkb.imageconvert', text = t('convert_image'), icon = 'IMAGE')

        row = col.row(align=True)
        row.prop(context.scene.kkbp, "image_dropdown")

def register():
    bpy.utils.register_class(PlaceholderProperties)
    bpy.utils.register_class(IMPORTINGHEADER_PT_panel)
    bpy.utils.register_class(IMPORTING_PT_panel)
    bpy.utils.register_class(EXPORTING_PT_panel)
    bpy.utils.register_class(EXTRAS_PT_panel)
    bpy.utils.register_class(EDITOR_PT_panel)

def unregister():
    bpy.utils.unregister_class(EDITOR_PT_panel)
    bpy.utils.unregister_class(EXTRAS_PT_panel)
    bpy.utils.unregister_class(EXPORTING_PT_panel)
    bpy.utils.unregister_class(IMPORTING_PT_panel)
    bpy.utils.unregister_class(IMPORTINGHEADER_PT_panel)
    bpy.utils.unregister_class(PlaceholderProperties)

if __name__ == "__main__":
    #unregister()
    register()
