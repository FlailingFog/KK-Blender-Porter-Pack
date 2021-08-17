#Imports the fbx file from GME and performs a few fixes

import bpy
import os
from mathutils import Vector
from pathlib import Path

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

class import_grey(bpy.types.Operator):
    bl_idname = "kkb.importgrey"
    bl_label = "Import Grey's .fbx"
    bl_description = "Select the .fbx file from Grey's Mesh Exporter"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', options={'HIDDEN'})
    filter_glob : StringProperty(default='.fbx', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context): 
        def runIt():
            
            fbx = Path('C:\\Users\\C\\Desktop\\GME process\\20210815_Hachikuji_Mayoi\\Hachikuji_Mayoi.fbx')
            bpy.ops.import_scene.fbx(filepath=str(fbx), use_prepost_rot=False, global_scale=500)
            
            armature = bpy.data.objects['Armature']
            armature.show_in_front = True
            
            #reset rotations, scale and locations in pose mode for all bones
            #Hide all root bones
            for bone in armature.pose.bones:
                bone.rotation_quaternion = (1,0,0,0)
                bone.scale = (1,1,1)
                bone.location = (0,0,0)
                
                if 'root' in bone.name:
                    armature.data.bones[bone.name].hide = True
            
            #Hide the height bone
            armature.data.bones['cf_n_height'].hide = True
            
            #add "twist" to certain bones so they aren't deleted by CATS
            joint_bones = ['cf_s_elboback_R', 'cf_s_elboback_L', 'cf_s_forearm01_R', 'cf_s_forearm01_L', '肩.L', '肩.R', 'cf_s_shoulder02_L', 'cf_s_shoulder02_R', 'cf_s_kneeB_R', 'cf_s_kneeB_L', 'cf_s_wrist_R', 'cf_s_wrist_L', 'cf_d_wrist_R', 'cf_d_wrist_L', 'cf_d_hand_L', 'cf_d_hand_R', 'cf_s_elbo_L', 'cf_s_elbo_R', 'cf_d_arm01_L', 'cf_d_arm01_R', 'cf_s_arm01_R', 'cf_s_arm01_L', 'cf_s_leg_R', 'cf_s_leg_L', 'cf_d_siri_L', 'cf_d_siri_R', 'cf_j_siri_L', 'cf_j_siri_R', 'cf_d_siri01_R', 'cf_d_siri01_L', 'cf_s_waist02', 'cf_j_waist02', '下半身', 'cf_s_waist01']
            for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
                for bone in armature.data.bones:
                    if bone.name in joint_bones:
                        bone.name = bone.name + '_twist'
                    
                    #and rename these bones so CATS can detect them
                    bone.name.replace('cf_j_arm00_', 'Arm_')
                    bone.name.replace('cf_j_forearm01_', 'Elbow_')
                    bone.name.replace('cf_j_hand_', 'Hand_')
            
            #create the missing armature bones
            missing_bones = [
            'cf_pv_elbo_L',
            'cf_pv_elbo_R',
            'cf_pv_foot_L',
            'cf_pv_foot_R',
            'cf_pv_hand_L',
            'cf_pv_hand_R',
            'cf_pv_heel_L',
            'cf_pv_heel_R',
            'cf_pv_knee_L',
            'cf_pv_knee_R',
            'cf_hit_head'
            ]
            
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='EDIT')
            height_adder = Vector((0,0.1,0))
            
            for bone in missing_bones:
                empty_location = bpy.data.objects[bone]
                new_bone = armature.data.edit_bones.new(bone)
                new_bone.head = empty_location.location
                new_bone.tail = empty_location.location + height_adder
            
            #then fix the hit_head location
            new_bone.head = armature.data.edit_bones['cf_s_head'].head + empty_location.location 
            new_bone.tail = armature.data.edit_bones['cf_s_head'].head + height_adder +  empty_location.location
            
            bpy.ops.object.mode_set(mode='OBJECT')
            
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
                    key.name = key.name.replace("nl00", "eye_nose.f00")
                else:
                    key.name = key.name.replace("nl00", "kuti_nose.f00")
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
            
            #scale armature down
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
            
            #fix the fingers too
            
        #I need a better way to do this
        runIt()
        
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_grey)
    
    # test call
    print((bpy.ops.kkb.importgrey('INVOKE_DEFAULT')))
