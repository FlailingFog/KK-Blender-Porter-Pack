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
    name="Enable or Disable", description="Check to use experimental \nhip joint correction drivers", default = False)
    shapekey_bool : BoolProperty(
    name="Enable or Disable", description="Check to save the partial shapekeys \nthat are used to generate the KK shapekeys.\nThese are useless on their own", default = False)
    textureoutline_bool : BoolProperty(
    name="Enable or Disable", description="Check to use one generic outline material \nas opposed to using several unique ones. \nChecking this may cause outline transparency issues", default = False)
    texturecheck_bool : BoolProperty(
    name="Enable or Disable", description="Uncheck this if you're having issues loading the textures folder", default = True)
   
        
class KK_Panel(bpy.types.Panel):
    bl_idname = "KK_Panel"
    bl_label = "KK Panel"
    bl_category = "KK Scripts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self,context):
        layout = self.layout
        
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator('kkb.beforecats', text = '1 Run right after importing')
        
        row = col.row(align=True)
        split = row.split(align=True, percentage=0.7)
        split.operator('kkb.shapekeys', text = '2 Fix shapekeys')
        split.prop(context.scene.placeholder, "shapekey_bool", text = "Save partial shapekeys")
        
        row = col.row(align=True)
        row.operator('kkb.separatebody', text = '3 Separate the body') 
        
        row = col.row(align=True)
        row.operator('kkb.cleanarmature', text = '4 Clean armature')
        
        row = col.row(align=True)
        split = row.split(align=True, percentage=0.7)
        split.operator('kkb.bonedrivers', text = '5 Add bone drivers')
        split.prop(context.scene.placeholder, "driver_bool", text = "Enable beta hip drivers")
        
        row = col.row(align=True)
        row.operator('kkb.importtemplates', text = '6 Import material templates')
        
        row = col.row(align=True)
        split = row.split(align=True, percentage=0.5)
        split.operator('kkb.importtextures', text = '7 Import textures')
        split = split.split(align=True, percentage=0.5)
        split.prop(context.scene.placeholder, "textureoutline_bool", text = "Use generic outline")
        split.prop(context.scene.placeholder, "texturecheck_bool", text = "Check folder before execution")
        
        row = col.row(align=True)
        split = row.split(align=True, percentage=0.7)
        split.operator('kkb.bakematerials', text = '8 Bake material templates')
        split.prop(context.scene.placeholder, "inc_dec_int", text = 'Multiplier:')
        
        row = col.row(align=True)
        row.operator('kkb.applymaterials', text = '9 Apply material templates')
        
        row = col.row(align=True)
        row.operator('kkb.selectbones', text = '10 Select unused bones')
