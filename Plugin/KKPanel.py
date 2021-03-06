import bpy

class KK_Panel(bpy.types.Panel):
    bl_idname = "KK_Panel"
    bl_label = "KK Panel"
    bl_category = "KK Scripts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self,context):
        layout = self.layout
        
        row = layout.row()
        row.operator('kkb.beforecats', text = '1 Run before clicking the Fix Model in CATS')
        row = layout.row()
        row.operator('kkb.shapekeys', text = '2 Fix shapekeys')
        row = layout.row()
        row.operator('kkb.separatebody', text = '3 Separate the body') 
        row = layout.row()
        row.operator('kkb.cleanarmature', text = '4 Clean armature')
        row = layout.row()
        row.operator('kkb.bonedrivers', text = '5 Add bone drivers')    
        row = layout.row()
        row.operator('kkb.importtemplates', text = '6 Import material templates')
        row = layout.row()
        row.operator('kkb.importtextures', text = '7 Import textures')
        row = layout.row()
        row.operator('kkb.bakematerials', text = '8 Bake material templates')
        row = layout.row()
        row.operator('kkb.applymaterials', text = '9 Apply material templates')
