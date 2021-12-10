from typing import Text
import bpy
from bpy.types import Panel, PropertyGroup, Scene, WindowManager
from bpy.props import (
    IntProperty,
    EnumProperty,
    BoolProperty,
    StringProperty,
    PointerProperty,
)

class PlaceholderProperties(PropertyGroup):
    inc_dec_int: IntProperty(
        name="Incr-Decr",
        min=1, max = 6,
        default=1,
        description="Set this to 2 or 3 if the baked texture is blurry")
    
    armature_edit_bool : BoolProperty(
    name="Enable or Disable",
    description="""Disable this to keep the stock Koikatsu armature structure.
    Disabling this will...
    --Leave you with a stock armature (no bone renames or rotated bones)
    --Skip IK creation
    --Skip Eye Controller creation
    You can swap between the original structure and modified structure
    at any time by using the button in the Extras panel""",
    default = True)
    
    delete_shapekey_bool : BoolProperty(
    name="Enable or Disable",
    description="""Enable to save the partial shapekeys that are used to generate the KK shapekeys.
    These are useless on their own""",
    default = False)

    fix_ackus : BoolProperty(
    name="Enable or Disable",
    description="""[SLOW] Sometimes when an accessory bone is duplicated
    (like when two accessories of the same type are used in different slots),
    the accessory bone weights will merge into each other.
    Keep enabled to let KKBP automatically fix these merged vertex groups""",
    default = True)

    fix_eyewhites_bool : BoolProperty(
    name="Enable or Disable",
    description="""Disable this if Blender crashes during the shapekeys script.
    If this is disabled, mesh operations on the Eyewhites material
    will be skipped so there may be gaps between
    the eyes and the eyewhites""",
    default = True)
    
    textureoutline_bool : BoolProperty(
    name="Enable or Disable",
    description="""Enable to use one generic outline material
    as opposed to using several unique ones.
    Checking this may cause outline transparency issues""",
    default = False)
    
    texturecheck_bool : BoolProperty(
    name="Enable or Disable",
    description="Disable this if you're 100% sure you're selecting the Textures folder correctly",
    default = False)
    
    templates_bool : BoolProperty(
    name="Enable or Disable",
    description="""Keep enabled to prevent the material templates from being deleted.
    Useful if you plan to import additional accessories or Studio objects 
    into Blender after your character is finished""",
    default = True)
    
    colors_dropdown : EnumProperty(
        items=(
            ("A", "Dark colors: LUT Night", "Makes everything blue"),
            ("B", "Dark colors: LUT Sunset", "Makes everything red"),
            ("C", "Dark colors: LUT Day", "Keeps dark colors the same as the light ones"),
            ("D", "Dark colors: Saturation based", "Makes everything saturated"),
            ("E", "Dark colors: Value reduction", "Makes everything darker")
        ), name="", default="A", description="Dark colors")
    
    prep_dropdown : EnumProperty(
        items=(
            ("A", "Very simplified", "Combines all objects, removes the outline, removes duplicate Eye material slot, simplifies bones on armature layer 3 / 5 / 11 / 12 / 13, reparents hip bone"),
            ("B", "Simplified", "Combines all objects, Removes the outline, removes duplicate Eye material slot, simplifies bones on armature layer 11"),
            ("C", "Stock", "Combines all objects, Removes the outline, removes duplicate Eye material slot"),
        ), name="", default="A", description="Prep type")
    
    atlas_dropdown : EnumProperty(
        items=(
            ("A", "Light atlas", ""),
            ("B", "Dark atlas", ""),
            ("C", "Normal atlas", ""),
        ), name="", default="A", description="Atlas type")
    
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
            ("A", "LUT Day", "Use Day LUT to saturate image"),
            ("B", "LUT Night", "Use Night LUT to saturate image"),
            ("C", "LUT Sunset", "Use Sunset LUT to saturate image")
        ), name="", default="A", description="LUT Choice")
    

class IMPORTING_PT_panel(bpy.types.Panel):
    bl_label = 'Importing and Exporting'
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    def draw(self,context):
        layout = self.layout

class IMPORTING1_PT_panel(bpy.types.Panel):
    bl_parent_id = "IMPORTING_PT_panel"
    bl_label = "Importing and Exporting"
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'HIDE_HEADER'}
    
    def draw(self,context):
        layout = self.layout
        splitfac = 0.6
        col = layout.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=1)#factor=0.5)
        
        box1 = split.box()
        box1.label(text="")
        split1 = box1.split(align=True, factor=splitfac)
        split1.label(text="1a) Finalize PMX file")
        split1.operator('kkb.finalizepmx', text = '', icon='MODIFIER')
        
        '''
        box2 = split.box()
        split2 = box2.split(align=True, factor=splitfac)
        split2.label(text="1a) Import FBX file")
        split2.operator('kkb.importgrey', text = '', icon = 'FILEBROWSER')

        split2 = box2.split(align=True, factor=splitfac)
        split2.label(text="2b) Finalize FBX file")
        split2.operator('kkb.finalizegrey', text = '', icon = 'MODIFIER')
        '''


class IMPORTOPTIONS_PT_Panel(bpy.types.Panel):
    bl_parent_id = "IMPORTING_PT_panel"
    bl_label = "Import options (Finalization)"
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        
        col = layout.column(align=True)
        
        row = col.row(align=True)
        split = row.split(align = True, factor=.5)
        split.prop(context.scene.placeholder, "fix_eyewhites_bool", toggle=True, text = "Fix eyewhites (PMX only)")
        split.prop(context.scene.placeholder, "delete_shapekey_bool", toggle=True, text = "Save partial shapekeys")
        
        row = col.row(align=True)
        split = row.split(align = True, factor=.5)
        split.prop(context.scene.placeholder, "armature_edit_bool", toggle=True, text = "Use modified armature")
        #split.prop(context.scene.placeholder, "fix_ackus", toggle=True, text = "Fix accessories")
        

class IMPORTING2_PT_panel(bpy.types.Panel):
    bl_parent_id = "IMPORTING_PT_panel"
    bl_options = {'HIDE_HEADER'}
    bl_label = "Import options2"
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self,context):
        layout = self.layout
        splitfac = 0.6
        
        box = layout.box()
        split2 = box.split(align=True, factor=splitfac)
        split2.label(text="2a) Import KK Shader and Textures")
        split2.operator('kkb.importeverything', text = '', icon = 'BRUSHES_ALL')
        
        col = box.column(align=True)
        row = col.row(align = True)
        split2 = row.split(align=True, factor=splitfac)
        split2.label(text="2b) Convert and Apply colors to Shaders")
        split2.operator('kkb.importcolors', text = '', icon = 'IMAGE')

        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.label(text="")
        split.prop(context.scene.placeholder, "colors_dropdown")

        
class APPLYOPTIONS_PT_Panel(bpy.types.Panel):
    bl_parent_id = "IMPORTING_PT_panel"
    bl_label = "Import options (KK Shader and Textures)"
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        splitfac = 0.3
        
        col = layout.column(align = True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split = row.split(align=True, factor=0.5)
        split.prop(context.scene.placeholder, "textureoutline_bool", toggle=True, text = "Use generic outline")
        split.prop(context.scene.placeholder, "templates_bool", toggle=True, text = "Set fake user")
    
class EXPORTING_PT_panel(bpy.types.Panel):
    bl_parent_id = "IMPORTING_PT_panel"
    bl_label = 'Exporting'
    bl_options = {'HIDE_HEADER'}
    bl_category = "KKBP"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self,context):
        layout = self.layout
        splitfac = 0.6
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="3) Prep things for export")
        split.operator('kkb.selectbones', text = '', icon = 'GROUP')
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="")
        split.prop(context.scene.placeholder, "prep_dropdown")

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="4) Bake material templates")
        split.operator('kkb.bakematerials', text = '', icon='VIEW_CAMERA')
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="")
        split.prop(context.scene.placeholder, "inc_dec_int", text = 'Bake multiplier:')
        
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="5) Apply baked templates")
        split.operator('kkb.applymaterials', text = '', icon = 'FILE_REFRESH')
        row = col.row(align=True)
        split = row.split(align = True, factor=splitfac)
        split.label(text="")
        split.prop(context.scene.placeholder, "atlas_dropdown")

class EXTRAS_PT_panel(bpy.types.Panel):
    bl_label = 'Extras'
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
        split.label(text="Shader:")
        split.label(text="Shadows:")
        split.label(text="Blend mode:")
        split.label(text="")
        row = col.row(align=True)
        split = row.split(align=True)
        split.prop(context.scene.placeholder, "dropdown_box")
        split.prop(context.scene.placeholder, "shadows_dropdown")
        split.prop(context.scene.placeholder, "blend_dropdown")
        split.prop(context.scene.placeholder, "studio_lut_bool", toggle=True, text = "Convert texture?")
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="Separate and Link Eyebrow and Eye shapekeys")
        split.operator('kkb.linkshapekeys', text = '', icon='SPHERECURVE')
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="Import ripped FBX animation")
        split.operator('kkb.importanimation', text = '', icon = 'ARMATURE_DATA')
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="")
        split.prop(context.scene.placeholder, "rokoko_bool", toggle=True, text = "Use Rokoko plugin")
        
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="Swap armature type")
        split.operator('kkb.switcharmature', text = '', icon = 'ARROW_LEFTRIGHT')

        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="Toggle hand IKs")
        split.operator('kkb.toggleik', text = '', icon = 'BONE_DATA')
        
'''
        #put all icons available in blender at the end of the panel

        icons = ['NONE', 'QUESTION', 'ERROR', 'CANCEL', 'TRIA_RIGHT', 'TRIA_DOWN', 'TRIA_LEFT', 'TRIA_UP', 'ARROW_LEFTRIGHT', 'PLUS', 'DISCLOSURE_TRI_RIGHT', 'DISCLOSURE_TRI_DOWN', 'RADIOBUT_OFF', 'RADIOBUT_ON', 'MENU_PANEL', 'BLENDER', 'GRIP', 'DOT', 'COLLAPSEMENU', 'X', 'DUPLICATE', 'TRASH', 'COLLECTION_NEW', 'OPTIONS', 'NODE', 'NODE_SEL', 'WINDOW', 'WORKSPACE', 'RIGHTARROW_THIN', 'BORDERMOVE', 'VIEWZOOM', 'ADD', 'REMOVE', 'PANEL_CLOSE', 'COPY_ID', 'EYEDROPPER', 'CHECKMARK', 'AUTO', 'CHECKBOX_DEHLT', 'CHECKBOX_HLT', 'UNLOCKED', 'LOCKED', 'UNPINNED', 'PINNED', 'SCREEN_BACK', 'RIGHTARROW', 'DOWNARROW_HLT', 'FCURVE_SNAPSHOT', 'OBJECT_HIDDEN', 'TOPBAR', 'STATUSBAR', 'PLUGIN', 'HELP', 'GHOST_ENABLED', 'COLOR', 'UNLINKED', 'LINKED', 'HAND', 'ZOOM_ALL', 'ZOOM_SELECTED', 'ZOOM_PREVIOUS', 'ZOOM_IN', 'ZOOM_OUT', 'DRIVER_DISTANCE', 'DRIVER_ROTATIONAL_DIFFERENCE', 'DRIVER_TRANSFORM', 'FREEZE', 'STYLUS_PRESSURE', 'GHOST_DISABLED', 'FILE_NEW', 'FILE_TICK', 'QUIT', 'URL', 'RECOVER_LAST', 'THREE_DOTS', 'FULLSCREEN_ENTER', 'FULLSCREEN_EXIT', 'BRUSHES_ALL', 'LIGHT', 'MATERIAL', 'TEXTURE', 'ANIM', 'WORLD', 'SCENE', 'OUTPUT', 'SCRIPT', 'PARTICLES', 'PHYSICS', 'SPEAKER', 'TOOL_SETTINGS', 'SHADERFX', 'MODIFIER', 'BLANK1', 'FAKE_USER_OFF', 'FAKE_USER_ON', 'VIEW3D', 'GRAPH', 'OUTLINER', 'PROPERTIES', 'FILEBROWSER', 'IMAGE', 'INFO', 'SEQUENCE', 'TEXT', 'SPREADSHEET', 'SOUND', 'ACTION', 'NLA', 'PREFERENCES', 'TIME', 'NODETREE', 'CONSOLE', 'TRACKER', 'ASSET_MANAGER', 'NODE_COMPOSITING', 'NODE_TEXTURE', 'NODE_MATERIAL', 'UV', 'OBJECT_DATAMODE', 'EDITMODE_HLT', 'UV_DATA', 'VPAINT_HLT', 'TPAINT_HLT', 'WPAINT_HLT', 'SCULPTMODE_HLT', 'POSE_HLT', 'PARTICLEMODE', 'TRACKING', 'TRACKING_BACKWARDS', 'TRACKING_FORWARDS', 'TRACKING_BACKWARDS_SINGLE', 'TRACKING_FORWARDS_SINGLE', 'TRACKING_CLEAR_BACKWARDS', 'TRACKING_CLEAR_FORWARDS', 'TRACKING_REFINE_BACKWARDS', 'TRACKING_REFINE_FORWARDS', 'SCENE_DATA', 'RENDERLAYERS', 'WORLD_DATA', 'OBJECT_DATA', 'MESH_DATA', 'CURVE_DATA', 'META_DATA', 'LATTICE_DATA', 'LIGHT_DATA', 'MATERIAL_DATA', 'TEXTURE_DATA', 'ANIM_DATA', 'CAMERA_DATA', 'PARTICLE_DATA', 'LIBRARY_DATA_DIRECT', 'GROUP', 'ARMATURE_DATA', 'COMMUNITY', 'BONE_DATA', 'CONSTRAINT', 'SHAPEKEY_DATA', 'CONSTRAINT_BONE', 'CAMERA_STEREO', 'PACKAGE', 'UGLYPACKAGE', 'EXPERIMENTAL', 'BRUSH_DATA', 'IMAGE_DATA', 'FILE', 'FCURVE', 'FONT_DATA', 'RENDER_RESULT', 'SURFACE_DATA', 'EMPTY_DATA', 'PRESET', 'RENDER_ANIMATION', 'RENDER_STILL', 'LIBRARY_DATA_BROKEN', 'BOIDS', 'STRANDS', 'LIBRARY_DATA_INDIRECT', 'GREASEPENCIL', 'LINE_DATA', 'LIBRARY_DATA_OVERRIDE', 'GROUP_BONE', 'GROUP_VERTEX', 'GROUP_VCOL', 'GROUP_UVS', 'FACE_MAPS', 'RNA', 'RNA_ADD', 'MOUSE_LMB', 'MOUSE_MMB', 'MOUSE_RMB', 'MOUSE_MOVE', 'MOUSE_LMB_DRAG', 'MOUSE_MMB_DRAG', 'MOUSE_RMB_DRAG', 'MEMORY', 'PRESET_NEW', 'DECORATE', 'DECORATE_KEYFRAME', 'DECORATE_ANIMATE', 'DECORATE_DRIVER', 'DECORATE_LINKED', 'DECORATE_LIBRARY_OVERRIDE', 'DECORATE_UNLOCKED', 'DECORATE_LOCKED', 'DECORATE_OVERRIDE', 'FUND', 'TRACKER_DATA', 'HEART', 'ORPHAN_DATA', 'USER', 'SYSTEM', 'SETTINGS', 'OUTLINER_OB_EMPTY', 'OUTLINER_OB_MESH', 'OUTLINER_OB_CURVE', 'OUTLINER_OB_LATTICE', 'OUTLINER_OB_META', 'OUTLINER_OB_LIGHT', 'OUTLINER_OB_CAMERA', 'OUTLINER_OB_ARMATURE', 'OUTLINER_OB_FONT', 'OUTLINER_OB_SURFACE', 'OUTLINER_OB_SPEAKER', 'OUTLINER_OB_FORCE_FIELD', 'OUTLINER_OB_GROUP_INSTANCE', 'OUTLINER_OB_GREASEPENCIL', 'OUTLINER_OB_LIGHTPROBE', 'OUTLINER_OB_IMAGE', 'OUTLINER_COLLECTION', 'RESTRICT_COLOR_OFF', 'RESTRICT_COLOR_ON', 'HIDE_ON', 'HIDE_OFF', 'RESTRICT_SELECT_ON', 'RESTRICT_SELECT_OFF', 'RESTRICT_RENDER_ON', 'RESTRICT_RENDER_OFF', 'RESTRICT_INSTANCED_OFF', 'OUTLINER_DATA_EMPTY', 'OUTLINER_DATA_MESH', 'OUTLINER_DATA_CURVE', 'OUTLINER_DATA_LATTICE', 'OUTLINER_DATA_META', 'OUTLINER_DATA_LIGHT', 'OUTLINER_DATA_CAMERA', 'OUTLINER_DATA_ARMATURE', 'OUTLINER_DATA_FONT', 'OUTLINER_DATA_SURFACE', 'OUTLINER_DATA_SPEAKER', 'OUTLINER_DATA_LIGHTPROBE', 'OUTLINER_DATA_GP_LAYER', 'OUTLINER_DATA_GREASEPENCIL', 'GP_SELECT_POINTS', 'GP_SELECT_STROKES', 'GP_MULTIFRAME_EDITING', 'GP_ONLY_SELECTED', 'GP_SELECT_BETWEEN_STROKES', 'MODIFIER_OFF', 'MODIFIER_ON', 'ONIONSKIN_OFF', 'ONIONSKIN_ON', 'RESTRICT_VIEW_ON', 'RESTRICT_VIEW_OFF', 'RESTRICT_INSTANCED_ON', 'MESH_PLANE', 'MESH_CUBE', 'MESH_CIRCLE', 'MESH_UVSPHERE', 'MESH_ICOSPHERE', 'MESH_GRID', 'MESH_MONKEY', 'MESH_CYLINDER', 'MESH_TORUS', 'MESH_CONE', 'MESH_CAPSULE', 'EMPTY_SINGLE_ARROW', 'LIGHT_POINT', 'LIGHT_SUN', 'LIGHT_SPOT', 'LIGHT_HEMI', 'LIGHT_AREA', 'CUBE', 'SPHERE', 'CONE', 'META_PLANE', 'META_CUBE', 'META_BALL', 'META_ELLIPSOID', 'META_CAPSULE', 'SURFACE_NCURVE', 'SURFACE_NCIRCLE', 'SURFACE_NSURFACE', 'SURFACE_NCYLINDER', 'SURFACE_NSPHERE', 'SURFACE_NTORUS', 'EMPTY_AXIS', 'STROKE', 'EMPTY_ARROWS', 'CURVE_BEZCURVE', 'CURVE_BEZCIRCLE', 'CURVE_NCURVE', 'CURVE_NCIRCLE', 'CURVE_PATH', 'LIGHTPROBE_CUBEMAP', 'LIGHTPROBE_PLANAR', 'LIGHTPROBE_GRID', 'COLOR_RED', 'COLOR_GREEN', 'COLOR_BLUE', 'TRIA_RIGHT_BAR', 'TRIA_DOWN_BAR', 'TRIA_LEFT_BAR', 'TRIA_UP_BAR', 'FORCE_FORCE', 'FORCE_WIND', 'FORCE_VORTEX', 'FORCE_MAGNETIC', 'FORCE_HARMONIC', 'FORCE_CHARGE', 'FORCE_LENNARDJONES', 'FORCE_TEXTURE', 'FORCE_CURVE', 'FORCE_BOID', 'FORCE_TURBULENCE', 'FORCE_DRAG', 'FORCE_FLUIDFLOW', 'RIGID_BODY', 'RIGID_BODY_CONSTRAINT', 'IMAGE_PLANE', 'IMAGE_BACKGROUND', 'IMAGE_REFERENCE', 'NODE_INSERT_ON', 'NODE_INSERT_OFF', 'NODE_TOP', 'NODE_SIDE', 'NODE_CORNER', 'ANCHOR_TOP', 'ANCHOR_BOTTOM', 'ANCHOR_LEFT', 'ANCHOR_RIGHT', 'ANCHOR_CENTER', 'SELECT_SET', 'SELECT_EXTEND', 'SELECT_SUBTRACT', 'SELECT_INTERSECT', 'SELECT_DIFFERENCE', 'ALIGN_LEFT', 'ALIGN_CENTER', 'ALIGN_RIGHT', 'ALIGN_JUSTIFY', 'ALIGN_FLUSH', 'ALIGN_TOP', 'ALIGN_MIDDLE', 'ALIGN_BOTTOM', 'BOLD', 'ITALIC', 'UNDERLINE', 'SMALL_CAPS', 'CON_ACTION', 'HOLDOUT_OFF', 'HOLDOUT_ON', 'INDIRECT_ONLY_OFF', 'INDIRECT_ONLY_ON', 'CON_CAMERASOLVER', 'CON_FOLLOWTRACK', 'CON_OBJECTSOLVER', 'CON_LOCLIKE', 'CON_ROTLIKE', 'CON_SIZELIKE', 'CON_TRANSLIKE', 'CON_DISTLIMIT', 'CON_LOCLIMIT', 'CON_ROTLIMIT', 'CON_SIZELIMIT', 'CON_SAMEVOL', 'CON_TRANSFORM', 'CON_TRANSFORM_CACHE', 'CON_CLAMPTO', 'CON_KINEMATIC', 'CON_LOCKTRACK', 'CON_SPLINEIK', 'CON_STRETCHTO', 'CON_TRACKTO', 'CON_ARMATURE', 'CON_CHILDOF', 'CON_FLOOR', 'CON_FOLLOWPATH', 'CON_PIVOT', 'CON_SHRINKWRAP', 'MODIFIER_DATA', 'MOD_WAVE', 'MOD_BUILD', 'MOD_DECIM', 'MOD_MIRROR', 'MOD_SOFT', 'MOD_SUBSURF', 'HOOK', 'MOD_PHYSICS', 'MOD_PARTICLES', 'MOD_BOOLEAN', 'MOD_EDGESPLIT', 'MOD_ARRAY', 'MOD_UVPROJECT', 'MOD_DISPLACE', 'MOD_CURVE', 'MOD_LATTICE', 'MOD_TINT', 'MOD_ARMATURE', 'MOD_SHRINKWRAP', 'MOD_CAST', 'MOD_MESHDEFORM', 'MOD_BEVEL', 'MOD_SMOOTH', 'MOD_SIMPLEDEFORM', 'MOD_MASK', 'MOD_CLOTH', 'MOD_EXPLODE', 'MOD_FLUIDSIM', 'MOD_MULTIRES', 'MOD_FLUID', 'MOD_SOLIDIFY', 'MOD_SCREW', 'MOD_VERTEX_WEIGHT', 'MOD_DYNAMICPAINT', 'MOD_REMESH', 'MOD_OCEAN', 'MOD_WARP', 'MOD_SKIN', 'MOD_TRIANGULATE', 'MOD_WIREFRAME', 'MOD_DATA_TRANSFER', 'MOD_NORMALEDIT', 'MOD_PARTICLE_INSTANCE', 'MOD_HUE_SATURATION', 'MOD_NOISE', 'MOD_OFFSET', 'MOD_SIMPLIFY', 'MOD_THICKNESS', 'MOD_INSTANCE', 'MOD_TIME', 'MOD_OPACITY', 'REC', 'PLAY', 'FF', 'REW', 'PAUSE', 'PREV_KEYFRAME', 'NEXT_KEYFRAME', 'PLAY_SOUND', 'PLAY_REVERSE', 'PREVIEW_RANGE', 'ACTION_TWEAK', 'PMARKER_ACT', 'PMARKER_SEL', 'PMARKER', 'MARKER_HLT', 'MARKER', 'KEYFRAME_HLT', 'KEYFRAME', 'KEYINGSET', 'KEY_DEHLT', 'KEY_HLT', 'MUTE_IPO_OFF', 'MUTE_IPO_ON', 'DRIVER', 'SOLO_OFF', 'SOLO_ON', 'FRAME_PREV', 'FRAME_NEXT', 'NLA_PUSHDOWN', 'IPO_CONSTANT', 'IPO_LINEAR', 'IPO_BEZIER', 'IPO_SINE', 'IPO_QUAD', 'IPO_CUBIC', 'IPO_QUART', 'IPO_QUINT', 'IPO_EXPO', 'IPO_CIRC', 'IPO_BOUNCE', 'IPO_ELASTIC', 'IPO_BACK', 'IPO_EASE_IN', 'IPO_EASE_OUT', 'IPO_EASE_IN_OUT', 'NORMALIZE_FCURVES', 'VERTEXSEL', 'EDGESEL', 'FACESEL', 'CURSOR', 'PIVOT_BOUNDBOX', 'PIVOT_CURSOR', 'PIVOT_INDIVIDUAL', 'PIVOT_MEDIAN', 'PIVOT_ACTIVE', 'CENTER_ONLY', 'ROOTCURVE', 'SMOOTHCURVE', 'SPHERECURVE', 'INVERSESQUARECURVE', 'SHARPCURVE', 'LINCURVE', 'NOCURVE', 'RNDCURVE', 'PROP_OFF', 'PROP_ON', 'PROP_CON', 'PROP_PROJECTED', 'PARTICLE_POINT', 'PARTICLE_TIP', 'PARTICLE_PATH', 'SNAP_FACE_CENTER', 'SNAP_PERPENDICULAR', 'SNAP_MIDPOINT', 'SNAP_OFF', 'SNAP_ON', 'SNAP_NORMAL', 'SNAP_GRID', 'SNAP_VERTEX', 'SNAP_EDGE', 'SNAP_FACE', 'SNAP_VOLUME', 'SNAP_INCREMENT', 'STICKY_UVS_LOC', 'STICKY_UVS_DISABLE', 'STICKY_UVS_VERT', 'CLIPUV_DEHLT', 'CLIPUV_HLT', 'SNAP_PEEL_OBJECT', 'GRID', 'OBJECT_ORIGIN', 'ORIENTATION_GLOBAL', 'ORIENTATION_GIMBAL', 'ORIENTATION_LOCAL', 'ORIENTATION_NORMAL', 'ORIENTATION_VIEW', 'COPYDOWN', 'PASTEDOWN', 'PASTEFLIPUP', 'PASTEFLIPDOWN', 'VIS_SEL_11', 'VIS_SEL_10', 'VIS_SEL_01', 'VIS_SEL_00', 'AUTOMERGE_OFF', 'AUTOMERGE_ON', 'UV_VERTEXSEL', 'UV_EDGESEL', 'UV_FACESEL', 'UV_ISLANDSEL', 'UV_SYNC_SELECT', 'TRANSFORM_ORIGINS', 'GIZMO', 'ORIENTATION_CURSOR', 'NORMALS_VERTEX', 'NORMALS_FACE', 'NORMALS_VERTEX_FACE', 'SHADING_BBOX', 'SHADING_WIRE', 'SHADING_SOLID', 'SHADING_RENDERED', 'SHADING_TEXTURE', 'OVERLAY', 'XRAY', 'LOCKVIEW_OFF', 'LOCKVIEW_ON', 'AXIS_SIDE', 'AXIS_FRONT', 'AXIS_TOP', 'LAYER_USED', 'LAYER_ACTIVE', 'OUTLINER_OB_HAIR', 'OUTLINER_DATA_HAIR', 'HAIR_DATA', 'OUTLINER_OB_POINTCLOUD', 'OUTLINER_DATA_POINTCLOUD', 'POINTCLOUD_DATA', 'OUTLINER_OB_VOLUME', 'OUTLINER_DATA_VOLUME', 'VOLUME_DATA', 'HOME', 'DOCUMENTS', 'TEMP', 'SORTALPHA', 'SORTBYEXT', 'SORTTIME', 'SORTSIZE', 'SHORTDISPLAY', 'LONGDISPLAY', 'IMGDISPLAY', 'BOOKMARKS', 'FONTPREVIEW', 'FILTER', 'NEWFOLDER', 'FOLDER_REDIRECT', 'FILE_PARENT', 'FILE_REFRESH', 'FILE_FOLDER', 'FILE_BLANK', 'FILE_BLEND', 'FILE_IMAGE', 'FILE_MOVIE', 'FILE_SCRIPT', 'FILE_SOUND', 'FILE_FONT', 'FILE_TEXT', 'SORT_DESC', 'SORT_ASC', 'LINK_BLEND', 'APPEND_BLEND', 'IMPORT', 'EXPORT', 'LOOP_BACK', 'LOOP_FORWARDS', 'BACK', 'FORWARD', 'FILE_ARCHIVE', 'FILE_CACHE', 'FILE_VOLUME', 'FILE_3D', 'FILE_HIDDEN', 'FILE_BACKUP', 'DISK_DRIVE', 'MATPLANE', 'MATSPHERE', 'MATCUBE', 'MONKEY', 'HAIR', 'ALIASED', 'ANTIALIASED', 'MAT_SPHERE_SKY', 'MATSHADERBALL', 'MATCLOTH', 'MATFLUID', 'WORDWRAP_OFF', 'WORDWRAP_ON', 'SYNTAX_OFF', 'SYNTAX_ON', 'LINENUMBERS_OFF', 'LINENUMBERS_ON', 'SCRIPTPLUGINS', 'DISC', 'DESKTOP', 'EXTERNAL_DRIVE', 'NETWORK_DRIVE', 'SEQ_SEQUENCER', 'SEQ_PREVIEW', 'SEQ_LUMA_WAVEFORM', 'SEQ_CHROMA_SCOPE', 'SEQ_HISTOGRAM', 'SEQ_SPLITVIEW', 'SEQ_STRIP_META', 'SEQ_STRIP_DUPLICATE', 'IMAGE_RGB', 'IMAGE_RGB_ALPHA', 'IMAGE_ALPHA', 'IMAGE_ZDEPTH', 'HANDLE_AUTOCLAMPED', 'HANDLE_AUTO', 'HANDLE_ALIGNED', 'HANDLE_VECTOR', 'HANDLE_FREE', 'VIEW_PERSPECTIVE', 'VIEW_ORTHO', 'VIEW_CAMERA', 'VIEW_PAN', 'VIEW_ZOOM', 'BRUSH_BLOB', 'BRUSH_BLUR', 'BRUSH_CLAY', 'BRUSH_CLAY_STRIPS', 'BRUSH_CLONE', 'BRUSH_CREASE', 'BRUSH_FILL', 'BRUSH_FLATTEN', 'BRUSH_GRAB', 'BRUSH_INFLATE', 'BRUSH_LAYER', 'BRUSH_MASK', 'BRUSH_MIX', 'BRUSH_NUDGE', 'BRUSH_PINCH', 'BRUSH_SCRAPE', 'BRUSH_SCULPT_DRAW', 'BRUSH_SMEAR', 'BRUSH_SMOOTH', 'BRUSH_SNAKE_HOOK', 'BRUSH_SOFTEN', 'BRUSH_TEXDRAW', 'BRUSH_TEXFILL', 'BRUSH_TEXMASK', 'BRUSH_THUMB', 'BRUSH_ROTATE', 'GPBRUSH_SMOOTH', 'GPBRUSH_THICKNESS', 'GPBRUSH_STRENGTH', 'GPBRUSH_GRAB', 'GPBRUSH_PUSH', 'GPBRUSH_TWIST', 'GPBRUSH_PINCH', 'GPBRUSH_RANDOMIZE', 'GPBRUSH_CLONE', 'GPBRUSH_WEIGHT', 'GPBRUSH_PENCIL', 'GPBRUSH_PEN', 'GPBRUSH_INK', 'GPBRUSH_INKNOISE', 'GPBRUSH_BLOCK', 'GPBRUSH_MARKER', 'GPBRUSH_FILL', 'GPBRUSH_AIRBRUSH', 'GPBRUSH_CHISEL', 'GPBRUSH_ERASE_SOFT', 'GPBRUSH_ERASE_HARD', 'GPBRUSH_ERASE_STROKE', 'SMALL_TRI_RIGHT_VEC', 'KEYTYPE_KEYFRAME_VEC', 'KEYTYPE_BREAKDOWN_VEC', 'KEYTYPE_EXTREME_VEC', 'KEYTYPE_JITTER_VEC', 'KEYTYPE_MOVING_HOLD_VEC', 'HANDLETYPE_FREE_VEC', 'HANDLETYPE_ALIGNED_VEC', 'HANDLETYPE_VECTOR_VEC', 'HANDLETYPE_AUTO_VEC', 'HANDLETYPE_AUTO_CLAMP_VEC', 'COLORSET_01_VEC', 'COLORSET_02_VEC', 'COLORSET_03_VEC', 'COLORSET_04_VEC', 'COLORSET_05_VEC', 'COLORSET_06_VEC', 'COLORSET_07_VEC', 'COLORSET_08_VEC', 'COLORSET_09_VEC', 'COLORSET_10_VEC', 'COLORSET_11_VEC', 'COLORSET_12_VEC', 'COLORSET_13_VEC', 'COLORSET_14_VEC', 'COLORSET_15_VEC', 'COLORSET_16_VEC', 'COLORSET_17_VEC', 'COLORSET_18_VEC', 'COLORSET_19_VEC', 'COLORSET_20_VEC', 'COLLECTION_COLOR_01', 'COLLECTION_COLOR_02', 'COLLECTION_COLOR_03', 'COLLECTION_COLOR_04', 'COLLECTION_COLOR_05', 'COLLECTION_COLOR_06', 'COLLECTION_COLOR_07', 'COLLECTION_COLOR_08', 'EVENT_A', 'EVENT_B', 'EVENT_C', 'EVENT_D', 'EVENT_E', 'EVENT_F', 'EVENT_G', 'EVENT_H', 'EVENT_I', 'EVENT_J', 'EVENT_K', 'EVENT_L', 'EVENT_M', 'EVENT_N', 'EVENT_O', 'EVENT_P', 'EVENT_Q', 'EVENT_R', 'EVENT_S', 'EVENT_T', 'EVENT_U', 'EVENT_V', 'EVENT_W', 'EVENT_X', 'EVENT_Y', 'EVENT_Z', 'EVENT_SHIFT', 'EVENT_CTRL', 'EVENT_ALT', 'EVENT_OS', 'EVENT_F1', 'EVENT_F2', 'EVENT_F3', 'EVENT_F4', 'EVENT_F5', 'EVENT_F6', 'EVENT_F7', 'EVENT_F8', 'EVENT_F9', 'EVENT_F10', 'EVENT_F11', 'EVENT_F12', 'EVENT_ESC', 'EVENT_TAB', 'EVENT_PAGEUP', 'EVENT_PAGEDOWN', 'EVENT_RETURN', 'EVENT_SPACEKEY']
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
        row.operator('kkb.imageconvert', text = 'Convert image with KKBP', icon = 'IMAGE')

        row = col.row(align=True)
        row.prop(context.scene.placeholder, "image_dropdown")

def register():
    bpy.utils.register_class(PlaceholderProperties)
    bpy.utils.register_class(IMPORTING_PT_panel)
    bpy.utils.register_class(IMPORTING1_PT_panel)
    bpy.utils.register_class(IMPORTOPTIONS_PT_Panel)
    bpy.utils.register_class(IMPORTING2_PT_panel)
    bpy.utils.register_class(APPLYOPTIONS_PT_Panel)
    bpy.utils.register_class(EXPORTING_PT_panel)
    bpy.utils.register_class(EXTRAS_PT_panel)
    bpy.utils.register_class(EDITOR_PT_panel)

def unregister():
    bpy.utils.unregister_class(EDITOR_PT_panel)
    bpy.utils.unregister_class(EXTRAS_PT_panel)
    bpy.utils.unregister_class(EXPORTING_PT_panel)
    bpy.utils.unregister_class(APPLYOPTIONS_PT_Panel)
    bpy.utils.unregister_class(IMPORTING2_PT_panel)
    bpy.utils.unregister_class(IMPORTOPTIONS_PT_Panel)
    bpy.utils.unregister_class(IMPORTING1_PT_panel)
    bpy.utils.unregister_class(IMPORTING_PT_panel)
    bpy.utils.unregister_class(PlaceholderProperties)

if __name__ == "__main__":
    #unregister()
    register()
