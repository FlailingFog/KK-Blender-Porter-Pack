'''
AFTER CATS (CLEAN ARMATURE) SCRIPT
- Hides all bones that aren't in the bonelist
- Connects the finger bones that CATS sometimes misses for koikatsu imports
Usage:
- Make sure the Fix Model button has already been used in CATS
- Run the script
'''

import bpy

class clean_Armature(bpy.types.Operator):
    bl_idname = "kkb.cleanarmature"
    bl_label = "Clean armature"
    bl_description = "Makes the armature less of an eyesore"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        #Set this to True to make the joint correction bones visible
        debugMode = False

        ########################
        import bpy

        #main bone list
        boneList = ['Cf_Pv_Knee_L', 'MiddleFinger1_L', 'LittleFinger3_R', 'Sk_03_02', 'Cf_D_Sk_04_00', 'Sk_03_04', 'Left ankle', 'Left wrist', 'AH1_R', 'Eyesx', 'Right knee', 'LittleFinger1_L', 'Right elbow', 'Sk_07_04', 'Cf_Pv_Foot_R', 'LittleFinger3_L', 'Sk_06_00', 'Cf_D_Sk_00_00', 'Sk_01_03', 'Sk_04_00', 'Sk_05_02', 'ToeTipIK_R', 'IndexFinger2_R', 'Sk_00_01', 'MiddleFinger2_L', 'Cf_D_Sk_06_00', 'Sk_04_01', 'IndexFinger1_L', 'Sk_02_04', 'Left arm', 'Sk_06_03', 'IndexFinger3_R', 'MiddleFinger2_R', 'Sk_05_00', 'MiddleFinger1_R', 'Sk_03_00', 'IndexFinger1_R', 'Sk_01_01', 'Right ankle', 'Thumb2_R', 'Cf_Pv_Elbo_L', 'Sk_02_02', 'Left leg', 'Cf_D_Siri_L', 'Spine', 'Sk_04_04', 'Sk_05_03', 'Kokan', 'Right leg', 'RingFinger3_L', 'MiddleFinger3_L', 'Sk_07_02', 'Neck', 'Thumb1_L', 'MiddleFinger3_R', 'Cf_D_Sk_02_00', 'RingFinger1_R', 'Thumb0_L', 'IndexFinger2_L', 'Thumb1_R', 'Sk_03_01', 'Cf_D_Sk_01_00', 'Sk_02_00', 'Cf_D_Siri_R', 'Sk_06_01', 'Sk_02_01', 'Sk_01_00', 'RingFinger2_R', 'Sk_07_01', 'Thumb0_R', 'Left elbow', 'IndexFinger3_L', 'Left shoulder', 'Cf_D_Sk_03_00', 'Sk_00_02', 'Cf_Pv_Hand_R', 'Right wrist', 'RingFinger3_R', 'Sk_01_02', 'Sk_07_03', 'Thumb2_L', 'Sk_04_03', 'Sk_00_04', 'Sk_06_02', 'Cf_Pv_Knee_R', 'Cf_Pv_Hand_L', 'Head', 'Sk_03_03', 'Left knee', 'Sk_04_02', 'Sk_00_03', 'Sk_01_04', 'Hips', 'Cf_Pv_Foot_L', 'LittleFinger1_R', 'LittleFinger2_L', 'RingFinger1_L', 'Cf_Pv_Elbo_R', 'Sk_06_04', 'Sk_05_01', 'Sk_00_00', 'Sk_07_00', 'LittleFinger2_R', 'ToeTipIK_L', 'Right shoulder', 'Right arm', 'Chest', 'Sk_02_03', 'Sk_05_04', 'Cf_D_Sk_05_00', 'Cf_D_Bust00', 'RingFinger2_L', 'AH1_L', 'Cf_D_Sk_07_00', 'Right toe', 'Left toe']

        #joint correction bone list
        #cf_j_ bones are merged into cf_s_ bones. cf_s_ bones have their prefix removed by CATS
        jointCorrectionList = ['Elboback_L_Twist', 'Elboback_R_Twist', 'Forearm01_L_Twist', 'Forearm01_R_Twist', 'KneeB_R_Twist', 'Shoulder_L_Twist', 'Shoulder_R_Twist', 'Shoulder02_L_Twist', 'Shoulder02_R_Twist', 'KneeB_L_Twist', 'Wrist_L_Twist', 'Wrist_R_Twist', 'Cf_D_Wrist_L_Twist', 'Cf_D_Wrist_R_Twist', 'Cf_D_Hand_L_Twist', 'Cf_D_Hand_R_Twist', 'Elbo_L_Twist', 'Elbo_R_Twist', 'Arm01_R_Twist', 'Arm01_L_Twist', 'Cf_D_Arm01_L_Twist', 'Cf_D_Arm01_R_Twist', 'Leg_L_Twist', 'Leg_R_Twist', 'Cf_D_Siri_L_Twist', 'Cf_D_Siri_R_Twist', 'Cf_D_Siri01_L_Twist', 'Cf_D_Siri01_R_Twist', 'Waist02_Twist', 'Waist02_Twist_001']

        if debugMode:
            for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
                for bone in armature.data.bones:
                    bone.hide=True
                    if bone.name in boneList or bone.name in jointCorrectionList: 
                        bone.hide = False
        else:
            for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
                for bone in armature.data.bones:
                    bone.hide=True
                    if bone.name in boneList:
                        bone.hide = False

        #Select the armature and make it active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Armature'].select_set(True)
        bpy.context.view_layer.objects.active=bpy.data.objects['Armature']

        # Make sure finger bones on the armature are visually connected (ignores A_N_ finger bones)
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.data.objects['Armature'].data.edit_bones['IndexFinger1_L'].tail = bpy.data.objects['Armature'].data.edit_bones['IndexFinger2_L'].head
        bpy.data.objects['Armature'].data.edit_bones['MiddleFinger1_L'].tail = bpy.data.objects['Armature'].data.edit_bones['MiddleFinger2_L'].head
        bpy.data.objects['Armature'].data.edit_bones['RingFinger1_L'].tail = bpy.data.objects['Armature'].data.edit_bones['RingFinger2_L'].head

        bpy.data.objects['Armature'].data.edit_bones['IndexFinger1_R'].tail = bpy.data.objects['Armature'].data.edit_bones['IndexFinger2_R'].head
        bpy.data.objects['Armature'].data.edit_bones['MiddleFinger1_R'].tail = bpy.data.objects['Armature'].data.edit_bones['MiddleFinger2_R'].head
        bpy.data.objects['Armature'].data.edit_bones['RingFinger1_R'].tail = bpy.data.objects['Armature'].data.edit_bones['RingFinger2_R'].head

        bpy.ops.object.mode_set(mode='OBJECT')
                    
        return {'FINISHED'}


