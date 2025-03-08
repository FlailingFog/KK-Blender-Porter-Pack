'''
LINK EYEBROW SHAPEKEYS TO BODY SCRIPT
Usage:
- Seperate the eyebrow mesh into its own object
- Select the eyebrows object, then shift click the body object and run the script to control the eyebrow shapekeys from the body object

Script 90% stolen from https://blender.stackexchange.com/questions/86757/python-how-to-connect-shapekeys-via-drivers
'''
import bpy
from ..interface.dictionary_en import t
from .. import common as c

def link_keys(shapekey_holder_object, objects_to_link):

    shapekey_list_string = str(shapekey_holder_object.data.shape_keys.key_blocks.keys()).lower()
    for obj in objects_to_link:
        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.material_slot_remove_unused()
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
                    newVar.targets[0].id = shapekey_holder_object.data.shape_keys
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
                    newVar.targets[0].id = shapekey_holder_object.data.shape_keys
                    newVar.targets[0].data_path = 'key_blocks["' + key.name+ '"].mute'


class link_shapekeys(bpy.types.Operator):
    bl_idname = "kkbp.linkshapekeys"
    bl_label = "Link shapekeys"
    bl_description = t('sep_eye_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #separate the eyes from the body object
        body = c.get_body()
        c.switch(body, 'EDIT')

        def separateMaterial(matList):
            for mat in matList:
                try:
                    def moveUp():
                        return bpy.ops.object.material_slot_move(direction='UP')
                    while moveUp() != {"CANCELLED"}:
                        pass
                    bpy.context.object.active_material_index = body.data.materials.find(mat)
                    bpy.ops.object.material_slot_select()
                except:
                    print('material wasn\'t found: ' + mat)
            bpy.ops.mesh.separate(type='SELECTED')

        eye_list = ['KK EyeR (hitomi) ' + c.get_name(),
                    'KK EyeL (hitomi) ' + c.get_name(),
                    'KK Eyewhites (sirome) ' + c.get_name(),
                    'KK Eyeline up ' + c.get_name(), 
                    'KK Eyeline down ' + c.get_name()]
        separateMaterial(eye_list)

        eyes = bpy.data.objects[body.name + '.001']
        eyes.name = 'Eyes'
        if eyes.modifiers.get('Outline Modifier'):
            eyes.modifiers['Outline Modifier'].show_viewport = False
            eyes.modifiers['Outline Modifier'].show_render = False
        
        #do the same for the eyebrows
        separateMaterial(['KK Eyebrows (mayuge) ' + c.get_name()])
        eyebrows = bpy.data.objects[body.name + '.001']
        eyebrows.name = 'Eyebrows'
        if eyebrows.modifiers.get('Outline Modifier'):
            eyebrows.modifiers['Outline Modifier'].show_viewport = False
            eyebrows.modifiers['Outline Modifier'].show_render = False

        bpy.ops.object.mode_set(mode = 'OBJECT')
        link_keys(body, [eyes, eyebrows])
        
        return {'FINISHED'}

