'''
LINK EYEBROW SHAPEKEYS TO BODY SCRIPT
Usage:
- Seperate the eyebrow mesh into its own object
- Select the eyebrows object, then shift click the body object and run the script to control the eyebrow shapekeys from the body object

Script 90% stolen from https://blender.stackexchange.com/questions/86757/python-how-to-connect-shapekeys-via-drivers
'''

import bpy

class link_Shapekeys(bpy.types.Operator):
    bl_idname = "kkb.linkshapekeys"
    bl_label = "Link shapekeys"
    bl_description = "Links the selected objects' shapekeys to the active object's shapekeys"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

      selected_obj = bpy.context.selected_objects
      selected_obj.remove(bpy.context.active_object)

      active_obj = bpy.context.active_object
      shapekey_list_string = str(active_obj.data.shape_keys.key_blocks.keys()).lower()

      for obj in selected_obj:
          for key in obj.data.shape_keys.key_blocks:
              if key.name.lower() in shapekey_list_string:
                  if not key.name == obj.data.shape_keys.key_blocks[0]:
                      skey_driver = key.driver_add('value')
                      skey_driver.driver.type = 'AVERAGE'
                      #skey_driver.driver.show_debug_info = True
                      if skey_driver.driver.variables:
                          for v in skey_driver.driver.variables:
                              skey_driver.driver.variables.remove(v)
                      newVar = skey_driver.driver.variables.new()
                      newVar.name = "value"
                      newVar.type = 'SINGLE_PROP'
                      newVar.targets[0].id_type = 'KEY'
                      newVar.targets[0].id = active_obj.data.shape_keys
                      newVar.targets[0].data_path = 'key_blocks["' + key.name+ '"].value' 
                      skey_driver = key.driver_add('mute')
                      skey_driver.driver.type = 'AVERAGE'
                      #skey_driver.driver.show_debug_info = True
                      if skey_driver.driver.variables:
                          for v in skey_driver.driver.variables:
                              skey_driver.driver.variables.remove(v)
                      newVar = skey_driver.driver.variables.new()
                      newVar.name = "hide"
                      newVar.type = 'SINGLE_PROP'
                      newVar.targets[0].id_type = 'KEY'
                      newVar.targets[0].id = active_obj.data.shape_keys
                      newVar.targets[0].data_path = 'key_blocks["' + key.name+ '"].mute'
    return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(link_Shapekeys)

    # test call
    print((bpy.ops.kkb.linkshapekeys('INVOKE_DEFAULT')))
