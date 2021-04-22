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
    my_bool : BoolProperty(
    name="Enable or Disable", description="Enables debug mode if checked", default = False)
        
class KK_Panel(bpy.types.Panel):
    bl_idname = "KK_Panel"
    bl_label = "KK Panel"
    bl_category = "KK Scripts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self,context):
        layout = self.layout
        
        row = layout.row()
        row.operator('kkb.beforecats', text = '1 Run right after importing')
        row = layout.row()
        row.operator('kkb.shapekeys', text = '2 Fix shapekeys')
        row.prop(context.scene.placeholder, "my_bool", text = "Enable debug mode")
        row = layout.row()
        row.operator('kkb.separatebody', text = '3 Separate the body') 
        row = layout.row()
        row.operator('kkb.cleanarmature', text = '4 Clean armature')
        #row.prop(context.scene.placeholder, "my_bool", text = "Enable debug mode")
        row = layout.row()
        row.operator('kkb.bonedrivers', text = '5 Add bone drivers')
        row.prop(context.scene.placeholder, "my_bool", text = "Enable debug mode")
        row = layout.row()
        row.operator('kkb.importtemplates', text = '6 Import material templates')
        row = layout.row()
        row.operator('kkb.importtextures', text = '7 Import textures')
        row = layout.row()
        row.operator('kkb.bakematerials', text = '8 Bake material templates')
        row.prop(context.scene.placeholder, "inc_dec_int", text = 'Multiplier:')
        row = layout.row()
        row.operator('kkb.applymaterials', text = '9 Apply material templates')
        row = layout.row()
        row.operator('kkb.selectbones', text = '10 Select unused bones')
