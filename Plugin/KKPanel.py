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
        name="Incr-Decr", min=1, max = 6, default=1, description="Set this to 2 or 3 if the baked texture is blurry")
    driver_bool : BoolProperty(
    name="Enable or Disable", description="Enable to use in-process \nhip bone joint correction drivers", default = False)
    delete_shapekey_bool : BoolProperty(
    name="Enable or Disable", description="Enable to save the partial shapekeys \nthat are used to generate the KK shapekeys.\nThese are useless on their own", default = False)
    fix_eyewhites_bool : BoolProperty(
    name="Enable or Disable", description="Disable this if Blender crashes during the shapekeys script.\nIf this is disabled, mesh operations on the Eyewhites material\nwill be skipped so there may be gaps between \nthe eyes and the eyewhites", default = True)
    textureoutline_bool : BoolProperty(
    name="Enable or Disable", description="Enable to use one generic outline material \nas opposed to using several unique ones. \nChecking this may cause outline transparency issues", default = False)
    texturecheck_bool : BoolProperty(
    name="Enable or Disable", description="Disable this if you're 100% sure you're selecting the textures folder correctly", default = True)
    templates_bool : BoolProperty(
    name="Enable or Disable", description="Keep enabled to prevent the material templates from being deleted\nif Blender is restarted between steps 6 and 7. \nHandy for crashes during Step 7", default = True)
    dropdown_box : EnumProperty(
        items=(
            ("A", "Principled BSDF", "Default shading"),
            ("B", "Emission", "Flat shading"),
            ("C", "KK Shader", "Anime cel shading"),
            ("D", "Custom", "Custom shading")
        ), name="Shader type", default="A", description="Shader type")
    shadows_dropdown : EnumProperty(
        items=(
            ("A", "None", "No shadows"),
            ("B", "Opaque", ""),
            ("C", "Alpha Clip", ""),
            ("D", "Alpha Hashed", "")
        ), name="Shadow Mode", default="A", description="Shadow Mode")
    blend_dropdown : EnumProperty(
        items=(
            ("A", "Opaque", ""),
            ("B", "Alpha Clip", ""),
            ("C", "Alpha Hashed", ""),
            ("D", "Alpha Blend", ""),
        ), name="Blend Mode", default="B", description="Blend Mode")

class KK_Panel(bpy.types.Panel):
    bl_idname = "KK_PT_Panel"
    bl_label = "KK Panel"
    bl_category = "KK Scripts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self,context):
        layout = self.layout
        
        splitfac = 0.7
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="1) Run right after importing:")
        split.operator('kkb.beforecats', text = '1')
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="2) Fix shapekeys:")
        split.operator('kkb.shapekeys', text = '2')
        row = col.row(align=True)
        split = row.split(align=True, factor=0.3)
        split.label(text="")
        split.prop(context.scene.placeholder, "delete_shapekey_bool", toggle=True, text = "Save partial shapekeys")
        split.prop(context.scene.placeholder, "fix_eyewhites_bool", toggle=True, text = "Fix eyewhites")
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="3) Separate the body:")
        split.operator('kkb.separatebody', text = '3')
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="4) Clean the armature:")
        split.operator('kkb.cleanarmature', text = '4')
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="5) Add bone drivers:")
        split.operator('kkb.bonedrivers', text = '5')
        row = col.row(align=True)
        split = row.split(align=True, factor=0.5)
        split.label(text="")
        split.prop(context.scene.placeholder, "driver_bool", toggle=True, text = "Enable hip drivers")
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="6) Import material templates:")
        split.operator('kkb.importtemplates', text = '6')
        row = col.row(align=True)
        split = row.split(align=True, factor=0.5)
        split.label(text="")
        split.prop(context.scene.placeholder, "templates_bool", toggle=True, text = "Set fake user")
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="7) Import textures:")
        split.operator('kkb.importtextures', text = '7')
        row = col.row(align=True)
        split = row.split(align=True, factor=0.3)
        split.label(text="")
        split.prop(context.scene.placeholder, "textureoutline_bool", toggle=True, text = "Use generic outline")
        split.prop(context.scene.placeholder, "texturecheck_bool", toggle=True, text = "Check folder")
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="8) Bake material templates:")
        split.operator('kkb.bakematerials', text = '8')
        row = col.row(align=True)
        split = row.split(align=True, factor=0.5)
        split.label(text="")
        split.prop(context.scene.placeholder, "inc_dec_int", text = 'Multiplier:')
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="9) Apply material templates:")
        split.operator('kkb.applymaterials', text = '9')
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="10) Select unused bones:")
        split.operator('kkb.selectbones', text = '10')
        
        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        split = row.split(align=True, factor=splitfac)
        split.label(text="11) Import studio object")
        split.operator('kkb.importstudio', text = '11')
        row = col.row(align=True)
        split = row.split(align=True, factor=0.1)
        split.label(text="")
        split.prop(context.scene.placeholder, "dropdown_box")
        split.prop(context.scene.placeholder, "shadows_dropdown")
        split.prop(context.scene.placeholder, "blend_dropdown")
        
def register():
    bpy.utils.register_class(KK_Panel)

def unregister():
    bpy.utils.unregister_class(KK_Panel)

if __name__ == "__main__":
    register()
