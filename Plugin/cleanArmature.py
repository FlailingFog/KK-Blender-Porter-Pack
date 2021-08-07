'''
AFTER CATS (CLEAN ARMATURE) SCRIPT
- Hides all bones that aren't in the bonelist
- Connects the finger bones that CATS sometimes misses for koikatsu imports
- Corrects the toe bones on the better penetration armature
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

        ########################
        import bpy
        
        #Select the armature and make it active
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        armature = bpy.data.objects['Armature']
        armature.hide = False
        armature.select_set(True)
        bpy.context.view_layer.objects.active=armature
        bpy.ops.object.mode_set(mode='POSE')
        
        #main bone list
        coreList = ['Cf_Pv_Knee_L', 'MiddleFinger1_L', 'LittleFinger3_R', 'Left ankle', 'Left wrist', 'AH1_R', 'Eyesx', 'Right knee', 'LittleFinger1_L', 'Right elbow', 'Cf_Pv_Foot_R', 'LittleFinger3_L', 'ToeTipIK_R', 'IndexFinger2_R', 'MiddleFinger2_L', 'IndexFinger1_L', 'Left arm', 'IndexFinger3_R', 'MiddleFinger2_R', 'MiddleFinger1_R', 'IndexFinger1_R', 'Right ankle', 'Thumb2_R', 'Cf_Pv_Elbo_L', 'Left leg', 'Cf_D_Siri_L', 'Spine', 'Sk_04_04', 'Sk_05_03', 'Right leg', 'RingFinger3_L', 'MiddleFinger3_L', 'Sk_07_02', 'Neck', 'Thumb1_L', 'MiddleFinger3_R', 'RingFinger1_R', 'Thumb0_L', 'IndexFinger2_L', 'Thumb1_R', 'RingFinger2_R', 'Thumb0_R', 'Left elbow', 'IndexFinger3_L', 'Left shoulder', 'Cf_Pv_Hand_R', 'Right wrist', 'RingFinger3_R', 'Thumb2_L', 'Cf_Pv_Knee_R', 'Cf_Pv_Hand_L', 'Head', 'Left knee', 'Hips', 'Cf_Pv_Foot_L', 'LittleFinger1_R', 'LittleFinger2_L', 'RingFinger1_L', 'Cf_Pv_Elbo_R', 'LittleFinger2_R', 'ToeTipIK_L', 'Right shoulder', 'Right arm', 'Chest', 'Cf_D_Bust00', 'RingFinger2_L', 'AH1_L', 'Right toe', 'Left toe', 'LowerBody_Twist', 'Upper Chest']
        
        #IK bone list
        nonIK = ['Left elbow', 'Right elbow', 'Left arm', 'Right arm', 'Left leg', 'Right leg', 'Left knee', 'Right knee', 'Right ankle', 'Left ankle']

        skirtList = ['Cf_D_Sk_00_00', 'Sk_00_00', 'Sk_00_01', 'Sk_00_02', 'Sk_00_03', 'Sk_00_04', 'Cf_D_Sk_01_00', 'Sk_01_00', 'Sk_01_01', 'Sk_01_02', 'Sk_01_03', 'Sk_01_04', 'Cf_D_Sk_02_00', 'Sk_02_00', 'Sk_02_01', 'Sk_02_02', 'Sk_02_03', 'Sk_02_04', 'Cf_D_Sk_03_00', 'Sk_03_00', 'Sk_03_01', 'Sk_03_02', 'Sk_03_03', 'Sk_03_04', 'Cf_D_Sk_04_00', 'Sk_04_00', 'Sk_04_01', 'Sk_04_02', 'Sk_04_03', 'Sk_04_04', 'Cf_D_Sk_05_00', 'Sk_05_00', 'Sk_05_01', 'Sk_05_02', 'Sk_05_03', 'Sk_05_04', 'Cf_D_Sk_06_00', 'Sk_06_00', 'Sk_06_01', 'Sk_06_02', 'Sk_06_03', 'Sk_06_04', 'Cf_D_Sk_07_00', 'Sk_07_00', 'Sk_07_01', 'Sk_07_02', 'Sk_07_03', 'Sk_07_04']
        
        faceList = ['Eye01_S_L', 'Eye01_S_R', 'Eye02_S_L', 'Eye02_S_R', 'Eye03_S_L', 'Eye03_S_R', 'Eye04_S_L', 'Eye04_S_R', 'Eye05_S_L', 'Eye05_S_R', 'Eye06_S_L', 'Eye06_S_R', 'Eye07_S_L', 'Eye07_S_R', 'Eye08_S_L', 'Eye08_S_R', 'Mayu_R', 'MayuMid_S_R', 'MayuTip_S_R', 'Mayu_L', 'MayuMid_S_L', 'MayuTip_S_L', 'Mouth_R', 'Mouth_L', 'Mouthup', 'MouthLow', 'MouthMove', 'MouthCavity']
        
        toeList = ['Toes0_L', 'Toes1_L', 'Toes10_L', 'Toes2_L', 'Toes20_L', 'Toes3_L', 'Toes30_L', 'Toes4_L', 'Toes0_R', 'Toes1_R', 'Toes10_R', 'Toes2_R', 'Toes20_R', 'Toes3_R', 'Toes30_R', 'Toes4_R']
        
        BPList = ['Kokan', 'Ana', 'Vagina_Root', 'Vagina_B', 'Vagina_F', 'Vagina_L_001', 'Vagina_L_002', 'Vagina_L_003', 'Vagina_L_004', 'Vagina_L_005',  'Vagina_R_001', 'Vagina_R_002', 'Vagina_R_003', 'Vagina_R_004', 'Vagina_R_005']
        
        #joint correction bone lists
        #cf_j_ bones are merged into cf_s_ bones. cf_s_ bones have their prefix removed by CATS
        upperJointList = ['Elboback_L_Twist', 'Elboback_R_Twist', 'Forearm01_L_Twist', 'Forearm01_R_Twist', 'Shoulder_L_Twist', 'Shoulder_R_Twist', 'Shoulder02_L_Twist', 'Shoulder02_R_Twist', 'Wrist_L_Twist', 'Wrist_R_Twist', 'Cf_D_Wrist_L_Twist', 'Cf_D_Wrist_R_Twist', 'Cf_D_Hand_L_Twist', 'Cf_D_Hand_R_Twist', 'Elbo_L_Twist', 'Elbo_R_Twist', 'Arm01_R_Twist', 'Arm01_L_Twist', 'Cf_D_Arm01_L_Twist', 'Cf_D_Arm01_R_Twist']
        lowerJointList = ['KneeB_R_Twist', 'KneeB_L_Twist', 'Leg_L_Twist', 'Leg_R_Twist', 'Cf_D_Siri_L_Twist', 'Cf_D_Siri_R_Twist', 'Cf_D_Siri01_L_Twist', 'Cf_D_Siri01_R_Twist', 'Waist02_Twist', 'Waist02_Twist_001', 'cf_s_waist01_Twist']

        allLayers = (True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, True, True, True, False, False, False, False, False, False, False, False, False, False, False, False, False)
        layer2 =    (False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
        layer3 =    (False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
        layer17 =   (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
        layer18 =   (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
        layer19 =   (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False)

        for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
            for bone in armature.data.bones:
                bone.hide=True
                if bone.name in coreList:
                    #Make core list bones visible on layer 1
                    bone.hide = False
                if bone.name in skirtList or bone.name in faceList or bone.name in toeList:
                    #Make secondary bones visible on layer 2
                    bone.hide = False
                    bpy.ops.pose.select_all(action='DESELECT')
                    bone.select = True
                    bpy.ops.pose.bone_layers(layers=layer2)
                if bone.name in BPList:
                    #Make kokan / better penetration bones visible on layer 3
                    bone.hide = False
                    bpy.ops.pose.select_all(action='DESELECT')
                    bone.select = True
                    bpy.ops.pose.bone_layers(layers=layer3)
                    #Also, rename the bones so you can mirror them over the x axis in pose mode
                    if 'Vagina_L_' in bone.name or 'Vagina_R_' in bone.name:
                        bone.name = 'Vagina' + bone.name[8:] + '_' + bone.name[7]
                if bone.name in nonIK:
                    #Move bones that don't need to be visible for IK to layer 17
                    bone.hide = False
                    bpy.ops.pose.select_all(action='DESELECT')
                    bone.select = True
                    bpy.ops.pose.bone_layers(layers=layer17)                   
                if bone.name in upperJointList:
                    bone.hide = False
                    #select and move to layer 18
                    bpy.ops.pose.select_all(action='DESELECT')
                    bone.select = True
                    bpy.ops.pose.bone_layers(layers=layer18)
                if bone.name in lowerJointList:
                    bone.hide = False
                    #select and move to layer 19
                    bpy.ops.pose.select_all(action='DESELECT')
                    bone.select = True
                    bpy.ops.pose.bone_layers(layers=layer19)
        
        bpy.ops.pose.select_all(action='DESELECT')
        
        #Make all bone layers visible for now
        bpy.ops.armature.armature_layers(layers=allLayers)
        bpy.context.object.data.display_type = 'STICK'
        
        # Make sure finger bones on the armature are visually connected (ignores A_N_ finger bones)
        bpy.ops.object.mode_set(mode='EDIT')

        armature.data.edit_bones['IndexFinger1_L'].tail = bpy.data.objects['Armature'].data.edit_bones['IndexFinger2_L'].head
        armature.data.edit_bones['MiddleFinger1_L'].tail = bpy.data.objects['Armature'].data.edit_bones['MiddleFinger2_L'].head
        armature.data.edit_bones['RingFinger1_L'].tail = bpy.data.objects['Armature'].data.edit_bones['RingFinger2_L'].head

        armature.data.edit_bones['IndexFinger1_R'].tail = bpy.data.objects['Armature'].data.edit_bones['IndexFinger2_R'].head
        armature.data.edit_bones['MiddleFinger1_R'].tail = bpy.data.objects['Armature'].data.edit_bones['MiddleFinger2_R'].head
        armature.data.edit_bones['RingFinger1_R'].tail = bpy.data.objects['Armature'].data.edit_bones['RingFinger2_R'].head

        # Make sure all toe bones are visually correct if using the better penetration armature 
        try:
            armature.data.edit_bones['Toes4_L'].tail.y = bpy.data.objects['Armature'].data.edit_bones['Toes30_L'].head.y
            armature.data.edit_bones['Toes4_L'].tail.z = bpy.data.objects['Armature'].data.edit_bones['Toes30_L'].head.z*.8
            armature.data.edit_bones['Toes0_L'].tail.y = bpy.data.objects['Armature'].data.edit_bones['Toes10_L'].head.y
            armature.data.edit_bones['Toes0_L'].tail.z = bpy.data.objects['Armature'].data.edit_bones['Toes30_L'].head.z*.9
            
            armature.data.edit_bones['Toes30_L'].tail.z = armature.data.edit_bones['Toes30_L'].head.z*0.8
            armature.data.edit_bones['Toes30_L'].tail.y = armature.data.edit_bones['Toes30_L'].head.y*1.2
            armature.data.edit_bones['Toes20_L'].tail.z = armature.data.edit_bones['Toes20_L'].head.z*0.8
            armature.data.edit_bones['Toes20_L'].tail.y = armature.data.edit_bones['Toes20_L'].head.y*1.2
            armature.data.edit_bones['Toes10_L'].tail.z = armature.data.edit_bones['Toes10_L'].head.z*0.8
            armature.data.edit_bones['Toes10_L'].tail.y = armature.data.edit_bones['Toes10_L'].head.y*1.2
            
            armature.data.edit_bones['Toes4_R'].tail.y = bpy.data.objects['Armature'].data.edit_bones['Toes30_R'].head.y
            armature.data.edit_bones['Toes4_R'].tail.z = bpy.data.objects['Armature'].data.edit_bones['Toes30_R'].head.z*.8
            armature.data.edit_bones['Toes0_R'].tail.y = bpy.data.objects['Armature'].data.edit_bones['Toes10_R'].head.y
            armature.data.edit_bones['Toes0_R'].tail.z = bpy.data.objects['Armature'].data.edit_bones['Toes30_R'].head.z*.9
            
            armature.data.edit_bones['Toes30_R'].tail.z = armature.data.edit_bones['Toes30_R'].head.z*0.8
            armature.data.edit_bones['Toes30_R'].tail.y = armature.data.edit_bones['Toes30_R'].head.y*1.2
            armature.data.edit_bones['Toes20_R'].tail.z = armature.data.edit_bones['Toes20_R'].head.z*0.8
            armature.data.edit_bones['Toes20_R'].tail.y = armature.data.edit_bones['Toes20_R'].head.y*1.2
            armature.data.edit_bones['Toes10_R'].tail.z = armature.data.edit_bones['Toes10_R'].head.z*0.8
            armature.data.edit_bones['Toes10_R'].tail.y = armature.data.edit_bones['Toes10_R'].head.y*1.2
        except:
            #this character isn't using the BP/toe control armature
            pass
        
        #Make sure top skirt root bones are visually correct (flip them)
        def flip(switchbone):
            chain = switchbone[5:10]
            armature.data.edit_bones[switchbone].tail = (armature.data.edit_bones[switchbone].head + armature.data.edit_bones[chain+'_00'].tail)/2
        for skirtroot in skirtList:
            if '_D_' in skirtroot:
                flip(skirtroot)
        
        bpy.ops.object.mode_set(mode='OBJECT')
                    
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(clean_Armature)

    # test call
    print((bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT')))
