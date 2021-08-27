'''
AFTER CATS (CLEAN ARMATURE) SCRIPT
- Hides all bones that aren't in the bonelists
- Connects the finger bones that CATS sometimes misses for koikatsu imports
- Corrects the toe bones on the better penetration armature
Usage:
- Run the script
'''

import bpy

#function that returns a type of bone list
def get_bone_list(kind):
    if kind == 'core_list':
        #main bone list
        return [
        'Center',
        'Head', 'Neck', 'Upper Chest', 'Chest', 'Eyesx',
        'cf_d_bust00', 'cf_d_bust02_L', 'cf_d_bust02_R',
        
        'Left shoulder', 'Left arm', 'Left elbow', 'Left wrist', 
        'IndexFinger1_L', 'IndexFinger2_L', 'IndexFinger3_L',
        'MiddleFinger1_L', 'MiddleFinger2_L', 'MiddleFinger3_L',
        'RingFinger1_L', 'RingFinger2_L', 'RingFinger3_L',
        'LittleFinger1_L', 'LittleFinger2_L', 'LittleFinger3_L',
        'Thumb0_L', 'Thumb1_L', 'Thumb2_L',
        
        'Right shoulder', 'Right arm', 'Right elbow', 'Right wrist', 
        'IndexFinger1_R', 'IndexFinger2_R', 'IndexFinger3_R',
        'MiddleFinger1_R', 'MiddleFinger2_R', 'MiddleFinger3_R',
        'RingFinger1_R', 'RingFinger2_R', 'RingFinger3_R',
        'LittleFinger1_R', 'LittleFinger2_R', 'LittleFinger3_R',
        'Thumb0_R', 'Thumb1_R', 'Thumb2_R',
        
        'Spine', 'Hips', 'Pelvis', 'cf_d_siri_L', 'cf_d_siri_R',
        'Right leg', 'Right knee', 'Right ankle', 'Right toe',
        'Left leg', 'Left knee', 'Left ankle', 'Left toe',
        
        'cf_pv_knee_L', 'cf_pv_knee_R',
        'cf_pv_elbo_L', 'cf_pv_elbo_R',
        'cf_pv_hand_L', 'cf_pv_hand_R',
        'cf_pv_foot_L', 'cf_pv_foot_R']
        
    elif kind == 'non_ik':
        #IK bone list
        return [
        'Left elbow', 'Right elbow',
        'Left arm', 'Right arm',
        'Left leg', 'Right leg',
        'Left knee', 'Right knee',
        'Left ankle', 'Right ankle',
        'Left wrist', 'Right wrist']
        
    elif kind == 'face_list':
        return [
        'cf_J_Eye01_s_L', 'cf_J_Eye01_s_R',
        'cf_J_Eye02_s_L', 'cf_J_Eye02_s_R',
        'cf_J_Eye03_s_L', 'cf_J_Eye03_s_R',
        'cf_J_Eye04_s_L', 'cf_J_Eye04_s_R',
        'cf_J_Eye05_s_L', 'cf_J_Eye05_s_R',
        'cf_J_Eye06_s_L', 'cf_J_Eye06_s_R',
        'cf_J_Eye07_s_L', 'cf_J_Eye07_s_R',
        'cf_J_Eye08_s_L', 'cf_J_Eye08_s_R',
        'cf_J_Mayu_R', 'cf_J_MayuMid_s_R', 'cf_J_MayuTip_s_R',
        'cf_J_Mayu_L', 'cf_J_MayuMid_s_L', 'cf_J_MayuTip_s_L',
        'cf_J_Mouth_R', 'cf_J_Mouth_L',
        'cf_J_Mouthup', 'cf_J_MouthLow', 'cf_J_MouthMove', 'cf_J_MouthCavity']
        
    elif kind == 'toe_list':
        #bones that appear on the Better Penetration armature
        return [
        'Toes0_L', 'Toes1_L', 'Toes10_L',
        'Toes2_L', 'Toes20_L',
        'Toes3_L', 'Toes30_L', 'Toes4_L',
        
        'Toes0_R', 'Toes1_R', 'Toes10_R',
        'Toes2_R', 'Toes20_R',
        'Toes3_R', 'Toes30_R', 'Toes4_R']
        
    elif kind == 'bp_list':
        return [
        'cf_j_Kokan', 'cf_j_Ana', 'Vagina_Root', 'Vagina_B', 'Vagina_F',
        'Vagina_L_001', 'Vagina_L_002', 'Vagina_L_003', 'Vagina_L_004', 'Vagina_L_005', 
        'Vagina_R_001', 'Vagina_R_002', 'Vagina_R_003', 'Vagina_R_004', 'Vagina_R_005']
    
    elif kind == 'upper_joint_list':
        #joint correction bone lists
        #cf_j_ bones are merged into cf_s_ bones. cf_s_ bones have their prefix removed by CATS
        return [
        'cf_s_elboback_L', 'cf_s_elboback_R',
        'cf_s_forearm01_L', 'cf_s_forearm01_R',
        'cf_d_shoulder02_L', 'cf_d_shoulder02_R',
        #'cf_s_shoulder02_L', 'cf_s_shoulder02_R',
        'cf_s_wrist_L', 'cf_s_wrist_R',
        'cf_d_wrist_L', 'cf_d_wrist_R',
        'cf_d_hand_L', 'cf_d_hand_R',
        'cf_s_elbo_L', 'cf_s_elbo_R',
        'cf_s_arm01_L', 'cf_s_arm01_R',
        'cf_d_arm01_L', 'cf_d_arm01_R']
    
    elif kind == 'lower_joint_list':
        return [
        'cf_s_kneeB_L', 'cf_s_kneeB_R',
        'cf_d_thigh01_L', 'cf_d_thigh01_R',
        'cf_d_siri_L', 'cf_d_siri_R', 'cf_d_siri01_L', 'cf_d_siri01_R',
        'cf_s_waist02', 'cf_s_waist01']

    elif kind == 'skirt_list':
        return [
        'cf_d_sk_00_00', 'cf_j_sk_00_00', 'cf_j_sk_00_01', 'cf_j_sk_00_02', 'cf_j_sk_00_03', 'cf_j_sk_00_04',
        'cf_d_sk_01_00', 'cf_j_sk_01_00', 'cf_j_sk_01_01', 'cf_j_sk_01_02', 'cf_j_sk_01_03', 'cf_j_sk_01_04',
        'cf_d_sk_02_00', 'cf_j_sk_02_00', 'cf_j_sk_02_01', 'cf_j_sk_02_02', 'cf_j_sk_02_03', 'cf_j_sk_02_04',
        'cf_d_sk_03_00', 'cf_j_sk_03_00', 'cf_j_sk_03_01', 'cf_j_sk_03_02', 'cf_j_sk_03_03', 'cf_j_sk_03_04',
        'cf_d_sk_04_00', 'cf_j_sk_04_00', 'cf_j_sk_04_01', 'cf_j_sk_04_02', 'cf_j_sk_04_03', 'cf_j_sk_04_04',
        'cf_d_sk_05_00', 'cf_j_sk_05_00', 'cf_j_sk_05_01', 'cf_j_sk_05_02', 'cf_j_sk_05_03', 'cf_j_sk_05_04',
        'cf_d_sk_06_00', 'cf_j_sk_06_00', 'cf_j_sk_06_01', 'cf_j_sk_06_02', 'cf_j_sk_06_03', 'cf_j_sk_06_04',
        'cf_d_sk_07_00', 'cf_j_sk_07_00', 'cf_j_sk_07_01', 'cf_j_sk_07_02', 'cf_j_sk_07_03', 'cf_j_sk_07_04']

def hide_extra_bones():
    #Select the armature and make it active
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature = bpy.data.objects['Armature']
    armature.hide = False
    armature.select_set(True)
    bpy.context.view_layer.objects.active=armature
    bpy.ops.object.mode_set(mode='POSE')
    
    core_list = get_bone_list('core_list')
    non_ik = get_bone_list('non_ik')
    face_list = get_bone_list('face_list')
    toe_list = get_bone_list('toe_list')
    bp_list = get_bone_list('bp_list')
    upper_joint_list = get_bone_list('upper_joint_list')
    lower_joint_list = get_bone_list('lower_joint_list')
    skirt_list = get_bone_list('skirt_list')

    allLayers = (
    True, True, True, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    True, True, True, False, False, False, False, False,
    False, False, False, False, False, False, False, False)
    layer2 = (
    False, True, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False)
    layer3 = (
    False, False, True, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False)
    layer17 = (
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    True, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False)
    layer18 = (
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    False, True, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False)
    layer19 = (
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    False, False, True, False, False, False, False, False,
    False, False, False, False, False, False, False, False)

    armature = bpy.data.objects['Armature']
    for bone in armature.data.bones:
        bone.hide=True
        if bone.name in core_list:
            #Make core list bones visible on layer 1
            bone.hide = False
        if bone.name in skirt_list or bone.name in face_list or bone.name in toe_list:
            #Make secondary bones visible on layer 2
            bone.hide = False
            bpy.ops.pose.select_all(action='DESELECT')
            bone.select = True
            bpy.ops.pose.bone_layers(layers=layer2)
        if bone.name in bp_list:
            #Make kokan / better penetration bones visible on layer 3
            bone.hide = False
            bpy.ops.pose.select_all(action='DESELECT')
            bone.select = True
            bpy.ops.pose.bone_layers(layers=layer3)
            #Also, rename the bones so you can mirror them over the x axis in pose mode
            if 'Vagina_L_' in bone.name or 'Vagina_R_' in bone.name:
                bone.name = 'Vagina' + bone.name[8:] + '_' + bone.name[7]
        if bone.name in non_ik:
            #Move bones that don't need to be visible for IK to layer 17
            bone.hide = False
            bpy.ops.pose.select_all(action='DESELECT')
            bone.select = True
            bpy.ops.pose.bone_layers(layers=layer17)                   
        if bone.name in upper_joint_list:
            bone.hide = False
            #select and move to layer 18
            bpy.ops.pose.select_all(action='DESELECT')
            bone.select = True
            bpy.ops.pose.bone_layers(layers=layer18)
        if bone.name in lower_joint_list:
            bone.hide = False
            #select and move to layer 19
            bpy.ops.pose.select_all(action='DESELECT')
            bone.select = True
            bpy.ops.pose.bone_layers(layers=layer19)
    
    bpy.ops.pose.select_all(action='DESELECT')
    
    #Make all bone layers visible for now
    bpy.ops.armature.armature_layers(layers=allLayers)
    bpy.context.object.data.display_type = 'STICK'
    bpy.ops.object.mode_set(mode='OBJECT')
    
def connect_finger_skirt_bones():
    # Make sure finger bones on the armature are visually connected (ignores A_N_ finger bones)
    skirt_list = get_bone_list('skirt_list')
    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.data.objects['Armature']
    
    armature.data.edit_bones['IndexFinger1_L'].tail = armature.data.edit_bones['IndexFinger2_L'].head
    armature.data.edit_bones['MiddleFinger1_L'].tail = armature.data.edit_bones['MiddleFinger2_L'].head
    armature.data.edit_bones['RingFinger1_L'].tail = armature.data.edit_bones['RingFinger2_L'].head

    armature.data.edit_bones['IndexFinger1_R'].tail = armature.data.edit_bones['IndexFinger2_R'].head
    armature.data.edit_bones['MiddleFinger1_R'].tail = armature.data.edit_bones['MiddleFinger2_R'].head
    armature.data.edit_bones['RingFinger1_R'].tail = armature.data.edit_bones['RingFinger2_R'].head

    # Make sure all toe bones are visually correct if using the better penetration armature 
    try:
        armature.data.edit_bones['Toes4_L'].tail.y = armature.data.edit_bones['Toes30_L'].head.y
        armature.data.edit_bones['Toes4_L'].tail.z = armature.data.edit_bones['Toes30_L'].head.z*.8
        armature.data.edit_bones['Toes0_L'].tail.y = armature.data.edit_bones['Toes10_L'].head.y
        armature.data.edit_bones['Toes0_L'].tail.z = armature.data.edit_bones['Toes30_L'].head.z*.9
        
        armature.data.edit_bones['Toes30_L'].tail.z = armature.data.edit_bones['Toes30_L'].head.z*0.8
        armature.data.edit_bones['Toes30_L'].tail.y = armature.data.edit_bones['Toes30_L'].head.y*1.2
        armature.data.edit_bones['Toes20_L'].tail.z = armature.data.edit_bones['Toes20_L'].head.z*0.8
        armature.data.edit_bones['Toes20_L'].tail.y = armature.data.edit_bones['Toes20_L'].head.y*1.2
        armature.data.edit_bones['Toes10_L'].tail.z = armature.data.edit_bones['Toes10_L'].head.z*0.8
        armature.data.edit_bones['Toes10_L'].tail.y = armature.data.edit_bones['Toes10_L'].head.y*1.2
        
        armature.data.edit_bones['Toes4_R'].tail.y = armature.data.edit_bones['Toes30_R'].head.y
        armature.data.edit_bones['Toes4_R'].tail.z = armature.data.edit_bones['Toes30_R'].head.z*.8
        armature.data.edit_bones['Toes0_R'].tail.y = armature.data.edit_bones['Toes10_R'].head.y
        armature.data.edit_bones['Toes0_R'].tail.z = armature.data.edit_bones['Toes30_R'].head.z*.9
        
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
        armature.data.edit_bones[switchbone].tail = (armature.data.edit_bones[switchbone].head + armature.data.edit_bones['cf_j_'+chain+'_00'].tail)/2
    for skirtroot in skirt_list:
        if '_d_' in skirtroot:
            flip(skirtroot)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
class clean_armature(bpy.types.Operator):
    bl_idname = "kkb.cleanarmature"
    bl_label = "Clean armature"
    bl_description = "Makes the armature less of an eyesore"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        hide_extra_bones()
        #connect_finger_skirt_bones()
        
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(clean_armature)

    # test call
    print((bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT')))
