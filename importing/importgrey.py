#Imports the fbx file from GME and performs a few fixes

import bpy, os
from mathutils import Vector
from pathlib import Path

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

def import_the_fbx(directory):

    #delete the cube, light and camera
    if len(bpy.data.objects) == 3:
        for obj in bpy.data.objects:
            bpy.data.objects.remove(obj)
    
    #import the fbx file
    bpy.ops.import_scene.fbx(filepath=str(directory), use_prepost_rot=False, global_scale=96)
    
    #rename all the shapekeys to be compatible with the other script
    #rename face shapekeys based on category
    keyset = bpy.data.objects['cf_O_face'].data.shape_keys.name
    index = 0
    while index < len(bpy.data.shape_keys[keyset].key_blocks):
        key = bpy.data.shape_keys[keyset].key_blocks[index]
        
        #reset the key value
        key.value = 0
        
        #rename the key
        if index < 29:
            key.name = key.name.replace("f00", "eye_face.f00")
        else:
            key.name = key.name.replace("f00", "kuti_face.f00")
        key.name = key.name.replace('.001','')
        
        index+=1
    
    #rename nose shapekeys based on category
    keyset = bpy.data.objects['cf_O_noseline'].data.shape_keys.name
    index = 0
    while index < len(bpy.data.shape_keys[keyset].key_blocks):
        key = bpy.data.shape_keys[keyset].key_blocks[index]
        
        #reset the key value
        key.value = 0
        
        #rename the key
        if index < 26:
            key.name = key.name.replace("nl00", "eye_nose.nl00")
        else:
            key.name = key.name.replace("nl00", "kuti_nose.nl00")
        key.name = key.name.replace('.001','')
        
        index+=1
    
    #rename the rest of the shapekeys
    def rename_keys(object):
        keyset = bpy.data.objects[object].data.shape_keys.name
        for key in bpy.data.shape_keys[keyset].key_blocks:
            key.value = 0
            key.name = key.name.replace("sL00",  "eye_siroL.sL00")
            key.name = key.name.replace("sR00",  "eye_siroR.sR00")
            key.name = key.name.replace('elu00', "eye_line_u.elu00")
            key.name = key.name.replace('ell00', "eye_line_l.ell00")
            key.name = key.name.replace('ha00',  "kuti_ha.ha00")
            key.name = key.name.replace('y00',   "kuti_yaeba.y00")
            key.name = key.name.replace('t00',   "kuti_sita.t00")
            key.name = key.name.replace('mayu00',"mayuge.mayu00")
    
    objects = [
    'cf_Ohitomi_L',
    'cf_Ohitomi_R',
    'cf_O_eyeline',
    'cf_O_eyeline_low',
    #eyenaM?
    'cf_O_tooth',
    #fangs?
    'o_tang',
    'cf_O_mayuge']
    
    for object in objects:
        rename_keys(object)
    
    #reset rotations, scale and locations in pose mode for all bones
    armature = bpy.data.objects['Armature']
    armature.show_in_front = True
    
    for bone in armature.pose.bones:
        bone.rotation_quaternion = (1,0,0,0)
        bone.scale = (1,1,1)
        bone.location = (0,0,0)
        
        #Hide all root bones
        if 'root' in bone.name:
            armature.data.bones[bone.name].hide = True
    
    #Hide the height bone
    armature.data.bones['cf_n_height'].hide = True

    #tag the armature with a bone to let the plugin distinguish between pmx/fbx origin
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    new_bone = armature.data.edit_bones.new('Greybone')
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    new_bone.head = Vector((0,0,0))
    new_bone.tail = Vector((0,0.1,0))
    
    #create the missing armature bones
    missing_bones = [
    'cf_pv_root',
    'cf_pv_elbo_L', 'cf_pv_elbo_R',
    'cf_pv_foot_L', 'cf_pv_foot_R',
    'cf_pv_hand_L', 'cf_pv_hand_R',
    'cf_pv_heel_L', 'cf_pv_heel_R',
    'cf_pv_knee_L', 'cf_pv_knee_R',
    'N_EyesLookTargetP', 'cf_hit_head'
    ]
    
    height_adder = Vector((0,0.1,0))
    for bone in missing_bones:
        empty_location = bpy.data.objects[bone].location
        new_bone = armature.data.edit_bones.new(bone)
        new_bone.head = empty_location
        new_bone.tail = empty_location + height_adder
        
    #then fix the cf hit_head location
    new_bone.head = armature.data.edit_bones['cf_s_head'].head + empty_location
    new_bone.tail = armature.data.edit_bones['cf_s_head'].head + height_adder +  empty_location
    
    #then fix the wrist location
    for side in ['R','L']:
        armature.data.edit_bones['cf_pv_hand_'+side].head.z = armature.data.edit_bones['cf_j_forearm01_'+side].head.z
        armature.data.edit_bones['cf_pv_hand_'+side].tail.z = armature.data.edit_bones['cf_j_forearm01_'+side].tail.z
        armature.data.edit_bones['cf_s_hand_'+side].head.z = armature.data.edit_bones['cf_j_forearm01_'+side].head.z
        armature.data.edit_bones['cf_s_hand_'+side].tail.z = armature.data.edit_bones['cf_j_forearm01_'+side].tail.z
        armature.data.edit_bones['cf_d_hand_'+side].head.z = armature.data.edit_bones['cf_j_forearm01_'+side].head.z
        armature.data.edit_bones['cf_d_hand_'+side].tail.z = armature.data.edit_bones['cf_j_forearm01_'+side].tail.z
        armature.data.edit_bones['cf_j_hand_'+side].head.z = armature.data.edit_bones['cf_j_forearm01_'+side].head.z
        armature.data.edit_bones['cf_j_hand_'+side].tail.z = armature.data.edit_bones['cf_j_forearm01_'+side].tail.z
    
    #then recreate the eyex bone so I can use it for later
    new_bone = armature.data.edit_bones.new('Eyesx')
    new_bone.head = armature.data.edit_bones['cf_hit_head'].tail
    new_bone.head.y = new_bone.head.y + 0.05
    new_bone.tail = armature.data.edit_bones['cf_J_Mayu_R'].tail
    new_bone.tail.x = new_bone.head.x
    new_bone.tail.y = new_bone.head.y
    
    #then reparent the pv bones to the root bone
    armature.data.edit_bones['cf_pv_root'].parent = armature.data.edit_bones['cf_j_root']
    armature.data.edit_bones['cf_pv_root'].head = armature.data.edit_bones['cf_j_root'].head
    armature.data.edit_bones['cf_pv_root'].tail = armature.data.edit_bones['cf_j_root'].tail
    pv_bones = [
    'Greybone',
    'cf_pv_elbo_L', 'cf_pv_elbo_R',
    'cf_pv_foot_L', 'cf_pv_foot_R',
    'cf_pv_hand_L', 'cf_pv_hand_R',
    'cf_pv_heel_L', 'cf_pv_heel_R',
    'cf_pv_knee_L', 'cf_pv_knee_R']
    for bone in pv_bones:
        armature.data.edit_bones[bone].parent = armature.data.edit_bones['cf_pv_root']
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    #rename the first UV map to be consistent with the PMX file
    #The fbx file seems to contains the extra UV maps for blush, hair shine and nipple locations
    #but I'm not going to use these in the KK shader until pmx imports are dropped entirely
    #remove for now because it'll probably cause issues with material baking and atlas generation
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if obj.data.uv_layers[0]:
                obj.data.uv_layers[0].name = 'UVMap'
            
            try:
                obj.data.uv_layers.remove(obj.data.uv_layers['uv2'])
                obj.data.uv_layers.remove(obj.data.uv_layers['uv3'])
                obj.data.uv_layers.remove(obj.data.uv_layers['uv4'])
            except:
                pass
    
    #manually scale armature down
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='SELECT')
    armature.data.edit_bones['cf_n_height'].select=False
    armature.data.edit_bones['cf_n_height'].select_head=False
    armature.data.edit_bones['cf_n_height'].select_tail=False
    
    scale_multiplier = armature.data.edit_bones['cf_n_height'].tail.y / armature.data.edit_bones['cf_hit_head'].head.y
    bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    
    for bone in bpy.context.selected_bones:
        bone.head *= (scale_multiplier * .9675)
        bone.tail *= (scale_multiplier * .9675)
    
    #Set the view transform 
    bpy.context.scene.view_settings.view_transform = 'Standard'

class import_grey(bpy.types.Operator):
    bl_idname = "kkb.importgrey"
    bl_label = "Import Grey's .fbx"
    bl_description = "Select the .fbx file from Grey's Mesh Exporter"
    bl_options = {'REGISTER', 'UNDO'}

    filepath : StringProperty(maxlen=1024, default='', options={'HIDDEN'})
    filter_glob : StringProperty(default='*.fbx', options={'HIDDEN'})
    
    def execute(self, context): 
        
        import_the_fbx(self.filepath)

        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_grey)
    
    # test call
    print((bpy.ops.kkb.importgrey('INVOKE_DEFAULT')))
