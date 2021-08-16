#Imports the fbx file from GME and performs a few fixes

import bpy
import os
from pathlib import Path

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

class import_grey(bpy.types.Operator):
    bl_idname = "kkb.importgrey"
    bl_label = "Import Grey's exported .fbx"
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
                    armature.data.bone[bone.name].hide = True
            
            #Hide the height bone
            armature.data.bones['cf_n_height'].hide = True
            
            #add "twist" to certain bones so they aren't deleted by CATS
            jointBones = ['cf_s_elboback_R', 'cf_s_elboback_L', 'cf_s_forearm01_R', 'cf_s_forearm01_L', '肩.L', '肩.R', 'cf_s_shoulder02_L', 'cf_s_shoulder02_R', 'cf_s_kneeB_R', 'cf_s_kneeB_L', 'cf_s_wrist_R', 'cf_s_wrist_L', 'cf_d_wrist_R', 'cf_d_wrist_L', 'cf_d_hand_L', 'cf_d_hand_R', 'cf_s_elbo_L', 'cf_s_elbo_R', 'cf_d_arm01_L', 'cf_d_arm01_R', 'cf_s_arm01_R', 'cf_s_arm01_L', 'cf_s_leg_R', 'cf_s_leg_L', 'cf_d_siri_L', 'cf_d_siri_R', 'cf_j_siri_L', 'cf_j_siri_R', 'cf_d_siri01_R', 'cf_d_siri01_L', 'cf_s_waist02', 'cf_j_waist02', '下半身', 'cf_s_waist01']
            for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
                for bone in armature.data.bones:
                    if bone.name in jointBones:
                        bone.name = bone.name + '_twist'
                    
                    #and rename these bones so CATS can detect them
                    bone.name.replace('cf_j_arm00_', 'Arm_')
                    bone.name.replace('cf_j_forearm01_', 'Elbow_')
                    bone.name.replace('cf_j_hand_', 'Hand_')
            
            #recreate the missing armature bones using the empty locations
            
            #rename all the shapekeys to be compatible with the other script
            
            #scale armature down and fix accessories manually
            
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
