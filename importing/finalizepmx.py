#Finalize the pmx file
#some code stolen from MediaMoots here https://github.com/FlailingFog/KK-Blender-Shader-Pack/issues/29

import bpy
from mathutils import Vector
import math

# makes the pmx armature and bone names match the koikatsu armature structure and bone names
def standardize_armature():
    bpy.ops.object.mode_set(mode='OBJECT')
    armature = bpy.data.objects['Model_arm']
    body = bpy.data.objects['Model_mesh']
    empty = bpy.data.objects['Model']
    armature.parent = None
    armature.name = 'Armature'
    body.name = 'Body'

    #Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    #Select the Body object
    body.select_set(True)
    #and make it active
    bpy.context.view_layer.objects.active = armature

    bpy.data.objects.remove(empty)

    #un-pmxify the bone names
    pmx_rename_dict = {
    '全ての親':'PMX_Allbones',
    'センター':'PMX_Centaa',
    #'p_cf_body_00':'p_cf_body_00Extra',
    #'p_cf_body_bone':'p_cf_body_00',
    '上半身':'cf_j_spine01',
    '上半身2':'cf_j_spine02',
    '首':'cf_j_neck',
    '頭':'cf_j_head',
    '両目x':'Eyesx',
    '目x.L':'cf_J_hitomi_tx_L',
    '目x.R':'cf_J_hitomi_tx_R',
    '腕.L':'cf_j_arm00_L',
    '腕.R':'cf_j_arm00_R',
    'ひじ.L':'cf_j_forearm01_L',
    'ひじ.R':'cf_j_forearm01_R',
    '肩.L':'cf_d_shoulder02_L',
    '肩.R':'cf_d_shoulder02_R',
    '手首.L':'cf_j_hand_L',
    '手首.R':'cf_j_hand_R',
    '親指０.L':'cf_j_thumb01_L',
    '親指１.L':'cf_j_thumb02_L',
    '親指２.L':'cf_j_thumb03_L',
    '薬指１.L':'cf_j_ring01_L',
    '薬指２.L':'cf_j_ring02_L',
    '薬指３.L':'cf_j_ring03_L',
    '中指１.L':'cf_j_middle01_L',
    '中指２.L':'cf_j_middle02_L',
    '中指３.L':'cf_j_middle03_L',
    '小指１.L':'cf_j_little01_L',
    '小指２.L':'cf_j_little02_L',
    '小指３.L':'cf_j_little03_L',
    '人指１.L':'cf_j_index01_L',
    '人指２.L':'cf_j_index02_L',
    '人指３.L':'cf_j_index03_L',
    '親指０.R':'cf_j_thumb01_R',
    '親指１.R':'cf_j_thumb02_R',
    '親指２.R':'cf_j_thumb03_R',
    '薬指１.R':'cf_j_ring01_R',
    '薬指２.R':'cf_j_ring02_R',
    '薬指３.R':'cf_j_ring03_R',
    '中指１.R':'cf_j_middle01_R',
    '中指２.R':'cf_j_middle02_R',
    '中指３.R':'cf_j_middle03_R',
    '小指１.R':'cf_j_little01_R',
    '小指２.R':'cf_j_little02_R',
    '小指３.R':'cf_j_little03_R',
    '人指１.R':'cf_j_index01_R',
    '人指２.R':'cf_j_index02_R',
    '人指３.R':'cf_j_index03_R',
    '下半身':'cf_j_waist01',
    '足.L':'cf_j_thigh00_L',
    '足.R':'cf_j_thigh00_R',
    'ひざ.L':'cf_j_leg01_L',
    'ひざ.R':'cf_j_leg01_R',
    '足首.L':'cf_j_foot_L',
    '足首.R':'cf_j_foot_R',
    }
    for bone in pmx_rename_dict:
        if armature.data.bones[bone]:
            armature.data.bones[bone].name = pmx_rename_dict[bone]
    
    #reparent foot to leg03
    bpy.ops.object.mode_set(mode='EDIT')
    armature.data.edit_bones['cf_j_foot_R'].parent = armature.data.edit_bones['cf_j_leg03_R']
    armature.data.edit_bones['cf_j_foot_L'].parent = armature.data.edit_bones['cf_j_leg03_L']

    #unparent body bone to match KK
    armature.data.edit_bones['p_cf_body_bone'].parent = None

    #remove all constraints from all bones
    bpy.ops.object.mode_set(mode='POSE')
    for bone in armature.pose.bones:
        for constraint in bone.constraints:
            bone.constraints.remove(constraint)
    
    #remove all drivers from all armature bones
    #animation_data is nonetype if no drivers have been created yet
    if armature.animation_data:
        drivers_data = armature.animation_data.drivers
        for driver in drivers_data:  
            armature.driver_remove(driver.data_path, -1)

    #unlock the armature and all bones
    armature.lock_location = [False, False, False]
    armature.lock_rotation = [False, False, False]
    armature.lock_scale = [False, False, False]
    
    for bone in armature.pose.bones:
        bone.lock_location = [False, False, False]

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')

    #delete bones not under the cf_n_height bone
    def select_children(parent):
        try:
            #don't select cf_hit, k_f_ so they get deleted
            if 'cf_hit_' not in parent.name and 'k_f_' not in parent.name:
                parent.select = True
                parent.select_head = True
                parent.select_tail = True

            for child in parent.children:
                select_children(child)
        except:
            #The script hit the last bone in the chain
            return
    select_children(armature.data.edit_bones['cf_n_height'])

    #make sure these bones aren't deleted
    for preserve_bone in ['cf_j_root', 'p_cf_body_bone']:
        armature.data.edit_bones[preserve_bone].select = True
        armature.data.edit_bones[preserve_bone].select_head = True
        armature.data.edit_bones[preserve_bone].select_tail = True

    bpy.ops.armature.select_all(action='INVERT')
    bpy.ops.armature.delete()

def reset_and_reroll_bones():
    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.data.objects['Armature']
    height_adder = Vector((0,0,0.1))
    
    #the finger bones need to be rotated a specific direction
    #this is probably the worst way this can be done
    def rotate_thumb(bone, direction='L'):
        bpy.ops.armature.select_all(action='DESELECT')
        armature.data.edit_bones[bone].select = True
        armature.data.edit_bones[bone].select_head = True
        armature.data.edit_bones[bone].select_tail = True
        #save location this way because it updates for some reason after the ops call
        head_location = armature.data.edit_bones[bone].head + Vector((0,0,1))
        if direction == 'R':
            bpy.ops.transform.rotate(value=-1.5708, orient_axis='X', orient_type='NORMAL', orient_matrix=((0.895944, 0.444168, -0), (0, 0, 1), (0.444168, -0.895944, 0)), orient_matrix_type='NORMAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        else:
            bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='NORMAL', orient_matrix=((0.733637, -0.679542, 0), (0, 0, 1), (-0.679542, -0.733637, 0)), orient_matrix_type='NORMAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        armature.data.edit_bones[bone].head = head_location - Vector((0,0,1))
        armature.data.edit_bones[bone].roll = 0
        armature.data.edit_bones[bone].tail.z = head_location.z - 1
        
    rotate_thumb('cf_j_thumb01_L')
    rotate_thumb('cf_j_thumb02_L')
    rotate_thumb('cf_j_thumb03_L')
    rotate_thumb('cf_j_thumb01_R', 'R')
    rotate_thumb('cf_j_thumb02_R', 'R')
    rotate_thumb('cf_j_thumb03_R', 'R')
    
    height_adder = Vector((0,0,0.1))
    def flip_finger(bone):
        armature.data.edit_bones[bone].tail = armature.data.edit_bones[bone].head - height_adder
    
    finger_list = (
    'cf_j_index01_R', 'cf_j_index02_R', 'cf_j_index03_R',
    'cf_j_middle01_R', 'cf_j_middle02_R', 'cf_j_middle03_R',
    'cf_j_ring01_R', 'cf_j_ring02_R', 'cf_j_ring03_R',
    'cf_j_little01_R', 'cf_j_little02_R', 'cf_j_little03_R',
    )
    
    for finger in finger_list:
        flip_finger(finger)
    
    #reset the orientation for the leg/foot bones
    height_adder = Vector((0,0,0.1))
    def reorient(bone):
        print(bone)
        armature.data.edit_bones[bone].tail = bpy.data.objects['Armature'].data.edit_bones[bone].head + height_adder
        print(bone)
        print(height_adder)  

    reorient('cf_j_thigh00_R')
    reorient('cf_j_thigh00_L')
    reorient('cf_j_leg01_R')
    reorient('cf_j_leg01_L')
    reorient('cf_j_foot_R')
    reorient('cf_j_foot_L')
    
    #Use roll data from a reference armature dump to set the roll for each bone
    reroll_data = {
    'BodyTop':0.0,
    'p_cf_body_bone':0.0,
    'cf_j_root':0.0,
    'cf_n_height':0.0,
    'cf_j_hips':0.0,
    'cf_j_spine01':0.0,
    'cf_j_spine02':0.0,
    'cf_j_spine03':0.0,
    'cf_d_backsk_00':0.0,
    'cf_j_backsk_C_01':-1.810556946517264e-23,
    'cf_j_backsk_C_02':-1.1667208633608472e-15,
    'cf_j_backsk_L_01':-0.001851903973147273,
    'cf_j_backsk_L_02':-0.0034122250508517027,
    'cf_j_backsk_R_01':0.0018519698642194271,
    'cf_j_backsk_R_02':0.003412271151319146,
    'cf_d_bust00':0.0,
    'cf_s_bust00_L':0.0,
    'cf_d_bust01_L':0.4159948229789734,
    'cf_j_bust01_L':0.4159948229789734,
    'cf_d_bust02_L':0.4159948229789734,
    'cf_j_bust02_L':0.4151105582714081,
    'cf_d_bust03_L':0.4151104986667633,
    'cf_j_bust03_L':0.4151104986667633,
    'cf_d_bnip01_L':0.4151104986667633,
    'cf_j_bnip02root_L':0.4151104986667633,
    'cf_s_bnip02_L':0.4151104986667633,
    'cf_j_bnip02_L':0.4154767096042633,
    'cf_s_bnip025_L':0.4154742360115051,
    'cf_s_bnip01_L':0.41547420620918274,
    'cf_s_bnip015_L':0.41547420620918274,
    'cf_s_bust03_L':0.4153861403465271,
    'cf_s_bust02_L':0.38631150126457214,
    'cf_s_bust01_L':0.4159947633743286,
    'cf_s_bust00_R':0.0,
    'cf_d_bust01_R':-0.4159948527812958,
    'cf_j_bust01_R':-0.4159948229789734,
    'cf_d_bust02_R':-0.41599488258361816,
    'cf_j_bust02_R':-0.41511064767837524,
    'cf_d_bust03_R':-0.41511061787605286,
    'cf_j_bust03_R':-0.41511064767837524,
    'cf_d_bnip01_R':-0.41511061787605286,
    'cf_j_bnip02root_R':-0.41511061787605286,
    'cf_s_bnip02_R':-0.41511061787605286,
    'cf_j_bnip02_R':-0.41547682881355286,
    'cf_s_bnip025_R':-0.4154742360115051,
    'cf_s_bnip01_R':-0.4154742956161499,
    'cf_s_bnip015_R':-0.4154742956161499,
    'cf_s_bust03_R':-0.41538622975349426,
    'cf_s_bust02_R':-0.38631150126457214,
    'cf_s_bust01_R':-0.4159948229789734,
    'cf_d_shoulder_L':0.0,
    'cf_j_shoulder_L':0.0,
    'cf_d_shoulder02_L':4.2021918488899246e-05,
    'cf_s_shoulder02_L':4.202192212687805e-05,
    'cf_j_arm00_L':0.0,
    'cf_d_arm01_L':-0.0012054670369252563,
    'cf_s_arm01_L':0.009222406893968582,
    'cf_d_arm02_L':-0.0012054670369252563,
    'cf_s_arm02_L':0.004008470103144646,
    'cf_d_arm03_L':-0.0012054670369252563,
    'cf_s_arm03_L':-0.0012097591534256935,
    'cf_j_forearm01_L':0.0,
    'cf_d_forearm02_L':0.0,
    'cf_s_forearm02_L':0.0,
    'cf_d_wrist_L':0.0,
    'cf_s_wrist_L':0.0,
    'cf_d_hand_L':0.0,
    'cf_j_hand_L':-6.776263578034403e-21,
    'cf_s_hand_L':-6.776263578034403e-21,
    'cf_j_index01_L':math.radians(-11),
    'cf_j_index02_L':math.radians(-5),
    'cf_j_index03_L':math.radians(0),
    'cf_j_little01_L':math.radians(30),
    'cf_j_little02_L':math.radians(11),
    'cf_j_little03_L':math.radians(30),
    'cf_j_middle01_L':math.radians(3),
    'cf_j_middle02_L':math.radians(3),
    'cf_j_middle03_L':math.radians(3),
    'cf_j_ring01_L':math.radians(15),
    'cf_j_ring02_L':math.radians(7),
    'cf_j_ring03_L':math.radians(15),
    'cf_j_thumb01_L':math.pi,
    'cf_j_thumb02_L':math.pi,
    'cf_j_thumb03_L':math.pi,
    'cf_s_elbo_L':0.0,
    'cf_s_forearm01_L':0.0,
    'cf_s_elboback_L':0.0,
    'cf_d_shoulder_R':0.0,
    'cf_j_shoulder_R':0.0,
    'cf_d_shoulder02_R':-4.355472628958523e-05,
    'cf_s_shoulder02_R':-4.355472628958523e-05,
    'cf_j_arm00_R':0.0,
    'cf_d_arm01_R':0.0009736516512930393,
    'cf_s_arm01_R':0.0009736517095007002,
    'cf_d_arm02_R':0.0009736516512930393,
    'cf_s_arm02_R':-0.004238337744027376,
    'cf_d_arm03_R':0.0009736516512930393,
    'cf_s_arm03_R':0.0009736517095007002,
    'cf_j_forearm01_R':0.0,
    'cf_d_forearm02_R':2.6637668270268477e-05,
    'cf_s_forearm02_R':2.6637668270268477e-05,
    'cf_d_wrist_R':1.9139706637361087e-05,
    'cf_s_wrist_R':1.9139704818371683e-05,
    'cf_d_hand_R':1.9139704818371683e-05,
    'o_brac':0.0,
    'cf_j_hand_R':-6.776470373187541e-21,
    'cf_s_hand_R':-6.776470373187541e-21,
    'cf_j_index01_R':math.radians(-11),
    'cf_j_index02_R':math.radians(-5),
    'cf_j_index03_R':math.radians(0),
    'cf_j_little01_R':math.radians(30),
    'cf_j_little02_R':math.radians(11),
    'cf_j_little03_R':math.radians(30),
    'cf_j_middle01_R':math.radians(3),
    'cf_j_middle02_R':math.radians(3),
    'cf_j_middle03_R':math.radians(3),
    'cf_j_ring01_R':math.radians(15),
    'cf_j_ring02_R':math.radians(7),
    'cf_j_ring03_R':math.radians(15),
    'cf_j_thumb01_R':math.radians(0),
    'cf_j_thumb02_R':math.radians(0),
    'cf_j_thumb03_R':math.radians(0),
    'cf_s_elbo_R':0.0,
    'cf_s_forearm01_R':0.0,
    'cf_s_elboback_R':4.203895392974451e-44,
    'cf_d_spinesk_00':0.0,
    'cf_j_spinesk_00':5.2774636787104646e-23,
    'cf_j_spinesk_01':-0.01019450556486845,
    'cf_j_spinesk_02':0.0032659571152180433,
    'cf_j_spinesk_03':-0.001969193108379841,
    'cf_j_spinesk_04':-0.001969192875549197,
    'cf_j_spinesk_05':-0.00196919240988791,
    'cf_j_neck':0.0,
    'cf_j_head':0.0,
    'cf_s_head':0.0,
    'p_cf_head_bone':0.0,
    'cf_J_N_FaceRoot':2.1210576051089447e-07,
    'cf_J_FaceRoot':2.1210573208918504e-07,
    'cf_J_FaceBase':2.1210573208918504e-07,
    'cf_J_FaceLow_tz':2.1210573208918504e-07,
    'cf_J_FaceLow_sx':2.1210573208918504e-07,
    'cf_J_CheekUpBase':2.1210573208918504e-07,
    'cf_J_CheekUp_s_L':2.1210573208918504e-07,
    'cf_J_CheekUp_s_R':2.1210573208918504e-07,
    'cf_J_Chin_Base':2.1210574630003975e-07,
    'cf_J_CheekLow_s_L':2.1210573208918504e-07,
    'cf_J_CheekLow_s_R':2.1210573208918504e-07,
    'cf_J_Chin_s':2.1210573208918504e-07,
    'cf_J_ChinTip_Base':2.1210574630003975e-07,
    'cf_J_ChinLow':2.1210573208918504e-07,
    'cf_J_MouthBase_ty':2.1210573208918504e-07,
    'cf_J_MouthBase_rx':2.1210573208918504e-07,
    'cf_J_MouthCavity':2.1210571787833032e-07,
    'cf_J_MouthMove':2.1210571787833032e-07,
    'cf_J_Mouth_L':2.1210573208918504e-07,
    'cf_J_Mouth_R':2.1210573208918504e-07,
    'cf_J_MouthLow':2.1210573208918504e-07,
    'cf_J_Mouthup':2.1210573208918504e-07,
    'cf_J_FaceUp_ty':2.1210573208918504e-07,
    'a_n_headside':2.1210574630003975e-07,
    'cf_J_EarBase_ry_L':-0.1504509449005127,
    'cf_J_EarLow_L':-0.1504509449005127,
    'cf_J_EarUp_L':-0.1504509449005127,
    'cf_J_EarBase_ry_R':0.15762563049793243,
    'cf_J_EarLow_R':0.15762564539909363,
    'cf_J_EarUp_R':0.15762564539909363,
    'cf_J_FaceUp_tz':2.1210574630003975e-07,
    'cf_J_Eye_tz':2.1210574630003975e-07,
    'cf_J_Eye_txdam_L':2.1210574630003975e-07,
    'cf_J_Eye_tx_L':2.1210573208918504e-07,
    'cf_J_Eye_rz_L':0.20466913282871246,
    'cf_J_CheekUp2_L':0.004773593973368406,
    'cf_J_Eye01_s_L':0.20466917753219604,
    'cf_J_Eye02_s_L':0.20466917753219604,
    'cf_J_Eye03_s_L':0.20466917753219604,
    'cf_J_Eye04_s_L':0.20466917753219604,
    'cf_J_Eye05_s_L':0.20466917753219604,
    'cf_J_Eye06_s_L':0.20466917753219604,
    'cf_J_Eye07_s_L':0.20466917753219604,
    'cf_J_Eye08_s_L':0.20466917753219604,
    'cf_J_hitomi_tx_L':0.18981075286865234,
    'cf_J_Eye_txdam_R':2.1210574630003975e-07,
    'cf_J_Eye_tx_R':2.1210576051089447e-07,
    'cf_J_Eye_rz_R':-0.2046687752008438,
    'cf_J_CheekUp2_R':-0.0047732163220644,
    'cf_J_Eye01_s_R':-0.2046687752008438,
    'cf_J_Eye02_s_R':-0.2046687752008438,
    'cf_J_Eye03_s_R':-0.2046687752008438,
    'cf_J_Eye04_s_R':-0.2046687752008438,
    'cf_J_Eye05_s_R':-0.2046687752008438,
    'cf_J_Eye06_s_R':-0.2046687752008438,
    'cf_J_Eye07_s_R':-0.2046687752008438,
    'cf_J_Eye08_s_R':-0.2046687752008438,
    'cf_J_hitomi_tx_R':-0.2046687752008438,
    'cf_J_Mayu_ty':2.1210574630003975e-07,
    'cf_J_Mayumoto_L':0.3458269536495209,
    'cf_J_Mayu_L':0.34616410732269287,
    'cf_J_MayuMid_s_L':0.34626930952072144,
    'cf_J_MayuTip_s_L':0.3462893068790436,
    'cf_J_Mayumoto_R':-0.34582653641700745,
    'cf_J_Mayu_R':-0.34616369009017944,
    'cf_J_MayuMid_s_R':-0.3462689220905304,
    'cf_J_MayuTip_s_R':-0.34628885984420776,
    'cf_J_NoseBase':2.1210573208918504e-07,
    'cf_J_NoseBase_rx':2.1210573208918504e-07,
    'cf_J_Nose_rx':2.1210573208918504e-07,
    'cf_J_Nose_tip':2.1210571787833032e-07,
    'cf_J_NoseBridge_ty':2.1210573208918504e-07,
    'cf_J_NoseBridge_rx':2.1210573208918504e-07,
    'cf_s_neck':0.0,
    'cf_s_spine03':0.0,
    'a_n_back':-3.1415927410125732,
    'cf_s_spine02':0.0,
    'cf_s_spine01':0.0,
    'cf_j_waist01':0.0,
    'cf_d_sk_top':0.0,
    'cf_d_sk_00_00':-3.1415927410125732,
    'cf_j_sk_00_00':-3.1415927410125732,
    'cf_j_sk_00_01':-3.1415927410125732,
    'cf_j_sk_00_02':3.1415293216705322,
    'cf_j_sk_00_03':3.1415293216705322,
    'cf_j_sk_00_04':3.1415293216705322,
    'cf_j_sk_00_05':3.1415293216705322,
    'cf_d_sk_01_00':2.3621666431427,
    'cf_j_sk_01_00':2.3621666431427,
    'cf_j_sk_01_01':2.364142656326294,
    'cf_j_sk_01_02':2.3684122562408447,
    'cf_j_sk_01_03':2.3684122562408447,
    'cf_j_sk_01_04':2.3684122562408447,
    'cf_j_sk_01_05':2.3684122562408447,
    'cf_d_sk_02_00':1.5806118249893188,
    'cf_j_sk_02_00':1.5808137655258179,
    'cf_j_sk_02_01':1.5806832313537598,
    'cf_j_sk_02_02':1.5820348262786865,
    'cf_j_sk_02_03':1.5820348262786865,
    'cf_j_sk_02_04':1.5820348262786865,
    'cf_j_sk_02_05':1.5820348262786865,
    'cf_d_sk_03_00':0.7112568616867065,
    'cf_j_sk_03_00':0.7112571597099304,
    'cf_j_sk_03_01':0.7112568020820618,
    'cf_j_sk_03_02':0.709623396396637,
    'cf_j_sk_03_03':0.7096233367919922,
    'cf_j_sk_03_04':0.7096233367919922,
    'cf_j_sk_03_05':0.7096234560012817,
    'cf_d_sk_04_00':3.4498308600352867e-17,
    'cf_j_sk_04_00':0.00037256989162415266,
    'cf_j_sk_04_01':0.00012998198508284986,
    'cf_j_sk_04_02':0.0001299990399274975,
    'cf_j_sk_04_03':0.0001299990399274975,
    'cf_j_sk_04_04':0.0001299990399274975,
    'cf_j_sk_04_05':0.0001299990399274975,
    'cf_d_sk_05_00':-0.7112577557563782,
    'cf_j_sk_05_00':-0.7112579345703125,
    'cf_j_sk_05_01':-0.7112577557563782,
    'cf_j_sk_05_02':-0.7096185088157654,
    'cf_j_sk_05_03':-0.7096185088157654,
    'cf_j_sk_05_04':-0.7096185088157654,
    'cf_j_sk_05_05':-0.7096185088157654,
    'cf_d_sk_06_00':-1.5806118249893188,
    'cf_j_sk_06_00':-1.5808138847351074,
    'cf_j_sk_06_01':-1.5806833505630493,
    'cf_j_sk_06_02':-1.5820401906967163,
    'cf_j_sk_06_03':-1.5820401906967163,
    'cf_j_sk_06_04':-1.5820401906967163,
    'cf_j_sk_06_05':-1.5820401906967163,
    'cf_d_sk_07_00':-2.3621666431427,
    'cf_j_sk_07_00':-2.3621666431427,
    'cf_j_sk_07_01':-2.3649401664733887,
    'cf_j_sk_07_02':-2.3683762550354004,
    'cf_j_sk_07_03':-2.3683762550354004,
    'cf_j_sk_07_04':-2.3683762550354004,
    'cf_j_sk_07_05':-2.3683762550354004,
    'cf_j_waist02':0.0,
    'cf_d_siri_L':4.435180380824022e-05,
    'cf_d_siri01_L':4.484502278501168e-05,
    'cf_j_siri_L':4.435180744621903e-05,
    'cf_s_siri_L':4.607543087331578e-05,
    'cf_d_ana':4.053832753925235e-07,
    'cf_j_ana':4.053832753925235e-07,
    'cf_s_ana':4.0538333223594236e-07,
    'cf_d_kokan':0.0,
    'cf_j_kokan':7.531064056820469e-07,
    'cf_d_siri_R':-5.766015220842746e-08,
    'cf_d_siri01_R':-5.766015220842746e-08,
    'cf_j_siri_R':-5.766015220842746e-08,
    'cf_s_siri_R':-5.766015576114114e-08,
    'cf_j_thigh00_L':0.0,
    'cf_d_thigh01_L':0.0,
    'cf_s_thigh01_L':0.0,
    'cf_d_thigh02_L':0.0,
    'cf_s_thigh02_L':0.0,
    'cf_d_thigh03_L':0.0,
    'cf_s_thigh03_L':0.0,
    'cf_j_leg01_L':0.0,
    'cf_d_kneeF_L':0.0,
    'cf_d_leg02_L':-8.435114585980674e-12,
    'cf_s_leg02_L':0.0019489085534587502,
    'cf_d_leg03_L':2.6021072699222714e-05,
    'cf_s_leg03_L':2.6021054509328678e-05,
    'cf_j_leg03_L':-1.7005811689396744e-11,
    'cf_j_foot_L':-1.6870217028897017e-11,
    'cf_j_toes_L':-1.6870217028897017e-11,
    'cf_s_leg01_L':1.5783663344534925e-25,
    'cf_s_kneeB_L':1.5783659646749431e-25,
    'cf_j_thigh00_R':0.0,
    'cf_d_thigh01_R':-2.9915531455925155e-27,
    'cf_s_thigh01_R':-2.3654518046693106e-22,
    'cf_d_thigh02_R':0.0,
    'cf_s_thigh02_R':0.0,
    'cf_d_thigh03_R':0.0,
    'cf_s_thigh03_R':0.0,
    'cf_j_leg01_R':0.0,
    'cf_d_kneeF_R':0.0,
    'cf_d_leg02_R':-3.092561655648751e-07,
    'cf_s_leg02_R':-3.092561655648751e-07,
    'cf_d_leg03_R':-4.125216790384911e-08,
    'cf_s_leg03_R':-4.125216790384911e-08,
    'cf_j_leg03_R':-6.69778160045098e-07,
    'cf_j_foot_R':-6.185123311297502e-07,
    'cf_j_toes_R':-6.185122742863314e-07,
    'cf_s_leg01_R':-8.901179133911008e-16,
    'cf_s_kneeB_R':-8.901180192702192e-16,
    'cf_s_waist02':0.0,
    'cf_s_leg_L':-0.004678195342421532,
    'cf_s_leg_R':0.004779986571520567,
    'cf_s_waist01':0.0,
    }
    for bone in reroll_data:
        if armature.data.edit_bones.get(bone):
            armature.data.edit_bones[bone].roll = reroll_data[bone]
    
    bpy.ops.object.mode_set(mode='EDIT')
  
#slightly modify the armature to support IKs
def modify_pmx_armature():
    armature = bpy.data.objects['Armature']
    body = bpy.data.objects['Body']
    
    armature.select_set(True)
    bpy.context.view_layer.objects.active=armature
    bpy.ops.object.mode_set(mode='EDIT')
    armature.data.edit_bones['cf_n_height'].parent = None
    armature.data.edit_bones['cf_j_root'].parent = armature.data.edit_bones['cf_pv_root']
    armature.data.edit_bones['p_cf_body_bone'].parent = armature.data.edit_bones['cf_pv_root']
    
    #relocate the tail of some bones to make IKs easier
    #this is different from the one in finalizefbx.py
    def relocate_tail(bone1, bone2, direction):
        if direction == 'leg':
            armature.data.edit_bones[bone1].tail.z = armature.data.edit_bones[bone2].head.z
            #move the bone forward a bit or the ik bones might not bend correctly
            armature.data.edit_bones[bone1].head.y += -.004
            armature.data.edit_bones[bone1].roll = 0
        elif direction == 'arm':
            armature.data.edit_bones[bone1].tail.x = armature.data.edit_bones[bone2].head.x
            armature.data.edit_bones[bone1].tail.z = armature.data.edit_bones[bone2].head.z
            armature.data.edit_bones[bone1].roll = -math.pi/2
        elif direction == 'hand':
            armature.data.edit_bones[bone1].tail = armature.data.edit_bones[bone2].tail
            armature.data.edit_bones[bone1].tail.z += .01
            armature.data.edit_bones[bone1].head = armature.data.edit_bones[bone2].head
        else:
            armature.data.edit_bones[bone1].tail.y = armature.data.edit_bones[bone2].head.y
            armature.data.edit_bones[bone1].tail.z = armature.data.edit_bones[bone2].head.z
            armature.data.edit_bones[bone1].roll = 0
    
    relocate_tail('cf_j_leg01_R', 'cf_j_foot_R', 'leg')
    relocate_tail('cf_j_foot_R', 'cf_j_toes_R', 'foot')
    relocate_tail('cf_j_forearm01_R', 'cf_j_hand_R', 'arm')
    relocate_tail('cf_pv_hand_R', 'cf_j_hand_R', 'hand')

    relocate_tail('cf_j_leg01_L', 'cf_j_foot_L', 'leg')
    relocate_tail('cf_j_foot_L', 'cf_j_toes_L', 'foot')
    relocate_tail('cf_j_forearm01_L', 'cf_j_hand_L', 'arm')
    relocate_tail('cf_pv_hand_L', 'cf_j_hand_L', 'hand')
    
    #remove whatever these stupid shadow bones are
    armature.data.edit_bones.remove(armature.data.edit_bones['_dummy_目x.L'])
    armature.data.edit_bones.remove(armature.data.edit_bones['_dummy_目x.R'])
    armature.data.edit_bones.remove(armature.data.edit_bones['_shadow_目x.L'])
    armature.data.edit_bones.remove(armature.data.edit_bones['_shadow_目x.R'])

    bpy.ops.object.mode_set(mode='OBJECT')
    
class finalize_pmx(bpy.types.Operator):
    bl_idname = "kkb.finalizepmx"
    bl_label = "Finalize .pmx file"
    bl_description = "Finalize CATS .pmx file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context): 

        scene = context.scene.placeholder
        modify_armature = scene.armature_edit_bool

        #get rid of the text files mmd tools generates
        if bpy.data.texts['Model']:
                bpy.data.texts.remove(bpy.data.texts['Model'])
                bpy.data.texts.remove(bpy.data.texts['Model_e'])
        
        standardize_armature()
        reset_and_reroll_bones()
        if modify_armature:
            modify_pmx_armature()
        
        #Set the view transform 
        bpy.context.scene.view_settings.view_transform = 'Standard'
        
        #redraw the UI after each operation to let the user know the plugin is actually doing something
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.kkb.shapekeys('INVOKE_DEFAULT')

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.kkb.separatebody('INVOKE_DEFAULT')

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT')

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT')
        
        return {'FINISHED'}
    
if __name__ == "__main__":
    bpy.utils.register_class(finalize_pmx)
    
    # test call
    print((bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT')))