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
    name="Enable or Disable", description="Check to use in-process \nhip bone joint correction drivers", default = False)
    shapekey_bool : BoolProperty(
    name="Enable or Disable", description="Check to save the partial shapekeys \nthat are used to generate the KK shapekeys.\nThese are useless on their own", default = False)
    textureoutline_bool : BoolProperty(
    name="Enable or Disable", description="Check to use one generic outline material \nas opposed to using several unique ones. \nChecking this may cause outline transparency issues", default = False)
    texturecheck_bool : BoolProperty(
    name="Enable or Disable", description="Disable this if you're 100% sure you're selecting the textures folder correctly", default = True)
   
        
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
        split = row.split(align=True, factor=0.5)
        split.label(text="")
        split.prop(context.scene.placeholder, "shapekey_bool", toggle=True, text = "Save partial shapekeys")
        
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
        split.label(text="5) Import material templates:")
        split.operator('kkb.importtemplates', text = '6')
        
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
        split.operator('kkb.importtextures', text = '8')
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

def register():
    bpy.utils.register_class(KK_Panel)

def unregister():
    bpy.utils.unregister_class(KK_Panel)

if __name__ == "__main__":
    register()
