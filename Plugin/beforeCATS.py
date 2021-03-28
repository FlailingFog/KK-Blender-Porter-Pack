'''
BEFORE CATS SCRIPT
- Adds "_twist" to the end of the bones listed below so CATS doesn't delete them.
- These bones are later used in the Drivers script
Usage:
- Import pmx file using CATS
- Run the script to rename the bones listed below
'''

import bpy

class before_CATS(bpy.types.Operator):
    bl_idname = "kkb.beforecats"
    bl_label = "The before CATS script"
    bl_description = "Preserves bones for later use"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        jointBones = ['cf_s_elboback_R', 'cf_s_elboback_L', 'cf_s_forearm01_R', 'cf_s_forearm01_L', '肩.L', '肩.R', 'cf_s_shoulder02_L', 'cf_s_shoulder02_R', 'cf_s_kneeB_R', 'cf_s_kneeB_L', 'cf_s_wrist_R', 'cf_s_wrist_L', 'cf_d_wrist_R', 'cf_d_wrist_L', 'cf_d_hand_L', 'cf_d_hand_R', 'cf_s_elbo_L', 'cf_s_elbo_R', 'cf_d_arm01_L', 'cf_d_arm01_R', 'cf_s_arm01_R', 'cf_s_arm01_L', 'cf_s_leg_R', 'cf_s_leg_L', 'cf_d_siri_L', 'cf_d_siri_R', 'cf_j_siri_L', 'cf_j_siri_R', 'cf_d_siri01_R', 'cf_d_siri01_L', 'cf_s_waist02', 'cf_j_waist02']

        for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
            for bone in armature.data.bones:
                if bone.name in jointBones:
                    bone.name = bone.name + '_twist'
                    
        return {'FINISHED'}


