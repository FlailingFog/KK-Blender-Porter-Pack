'''
FINALIZE PMX
- Standardizes the armature to match the Koikatsu armature
- Sets rolls for all bones
- Optionally modifies the armature for IK usage
- Runs several other scripts when finished

some code stolen from MediaMoots here https://github.com/FlailingFog/KK-Blender-Shader-Pack/issues/29
'''

import bpy, math, time, traceback
from mathutils import Vector
from .importbuttons import kklog

def rename_and_merge_outfits():
    bpy.ops.object.mode_set(mode='OBJECT')
    
    #get objects
    armature = bpy.data.objects['Model_arm']
    body = bpy.data.objects['Model_mesh']
    empty = bpy.data.objects['Model']
    
    #rename
    armature.parent = None
    armature.name = 'Armature'
    body.name = 'Body'
    
    #Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    bpy.data.objects.remove(empty)
    
    idx = 1
    for obj in bpy.data.objects:
        if "Model_arm" in obj.name and obj.type == 'ARMATURE':
            #get objects
            empty = bpy.data.objects['Model.' + str(idx).zfill(3)]
            outfit_arm = bpy.data.objects['Model_arm.' + str(idx).zfill(3)]
            outfit = bpy.data.objects[empty.name  + '_mesh']
            
            bpy.data.objects.remove(empty)
            bpy.data.objects.remove(outfit_arm)
            #rename
            outfit.name = 'Outfit ' + str(idx).zfill(2)
            outfit.parent = armature
            outfit.modifiers[0].object = armature
            
            idx += 1
        
    #Select the Body object
    body.select_set(True)
    #and make it active
    bpy.context.view_layer.objects.active = armature   

# makes the pmx armature and bone names match the koikatsu armature structure and bone names
def standardize_armature(modify_arm):
    rename_and_merge_outfits()
    
    armature = bpy.data.objects['Armature']
    
    #scale all bone sizes down by a factor of 12
    try:
        bpy.ops.object.mode_set(mode='EDIT')
    except:
        armature.hide = False
        bpy.ops.object.mode_set(mode='EDIT')
    for bone in armature.data.edit_bones:
        bone.tail.z = bone.head.z + (bone.tail.z - bone.head.z)/12
    
    if modify_arm != 'D':
        #reparent foot to leg03
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
    
    #recreate the eyex bone so I can use it for later
    new_bone = armature.data.edit_bones.new('Eyesx')
    new_bone.head = armature.data.edit_bones['cf_hit_head'].tail
    new_bone.head.y = new_bone.head.y + 0.05
    new_bone.tail = armature.data.edit_bones['cf_J_Mayu_R'].tail
    new_bone.tail.x = new_bone.head.x
    new_bone.tail.y = new_bone.head.y
    new_bone.parent = armature.data.edit_bones['cf_j_head']

    bpy.ops.armature.select_all(action='DESELECT')

    #delete bones not under the cf_n_height bone
    def select_children(parent):
        try:
            parent.select = True
            parent.select_head = True
            parent.select_tail = True
            for child in parent.children:
                select_children(child)
            
        except:
            #The script hit the last bone in the chain
            return

    if modify_arm == 'D':
        select_children(armature.data.edit_bones['BodyTop'])
    else:
        select_children(armature.data.edit_bones['cf_n_height'])

        #make sure these bones aren't deleted
        for preserve_bone in ['cf_j_root', 'p_cf_body_bone', 'cf_n_height']:
            armature.data.edit_bones[preserve_bone].select = True
            armature.data.edit_bones[preserve_bone].select_head = True
            armature.data.edit_bones[preserve_bone].select_tail = True

    bpy.ops.armature.select_all(action='INVERT')
    bpy.ops.armature.delete()

def reset_and_reroll_bones():
    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.data.objects['Armature']
    height_adder = Vector((0,0,0.1))
    
    #all finger bones need to be rotated a specific direction
    def rotate_thumb(bone, direction='L'):
        bpy.ops.armature.select_all(action='DESELECT')
        armature.data.edit_bones[bone].select = True
        armature.data.edit_bones[bone].select_head = True
        armature.data.edit_bones[bone].select_tail = True
        parent = armature.data.edit_bones[bone].parent
        armature.data.edit_bones[bone].parent = None

        #right thumbs face towards hand center
        #left thumbs face away from hand center
        angle = -math.pi/2
        
        s = math.sin(angle)
        c = math.cos(angle)

        # translate point back to origin:
        armature.data.edit_bones[bone].tail.x -= armature.data.edit_bones[bone].head.x
        armature.data.edit_bones[bone].tail.y -= armature.data.edit_bones[bone].head.y

        # rotate point
        xnew = armature.data.edit_bones[bone].tail.x * c - armature.data.edit_bones[bone].tail.y * s
        ynew = armature.data.edit_bones[bone].tail.x * s + armature.data.edit_bones[bone].tail.y * c

        # translate point back:
        armature.data.edit_bones[bone].tail.x = xnew + armature.data.edit_bones[bone].head.x
        armature.data.edit_bones[bone].tail.y = ynew + armature.data.edit_bones[bone].head.y
        armature.data.edit_bones[bone].roll = 0
        #armature.data.edit_bones[bone].tail.z = armature.data.edit_bones[bone].head.z
        armature.data.edit_bones[bone].parent = parent
        
    rotate_thumb('cf_j_thumb03_L')
    rotate_thumb('cf_j_thumb02_L')
    rotate_thumb('cf_j_thumb01_L')
    rotate_thumb('cf_j_thumb03_R', 'R')
    rotate_thumb('cf_j_thumb02_R', 'R')
    rotate_thumb('cf_j_thumb01_R', 'R')
    
    height_adder = Vector((0,0,0.05))
    def flip_finger(bone):
        parent = armature.data.edit_bones[bone].parent
        armature.data.edit_bones[bone].parent = None
        armature.data.edit_bones[bone].tail = armature.data.edit_bones[bone].head - height_adder
        armature.data.edit_bones[bone].parent = parent
    
    finger_list = (
    'cf_j_index03_R', 'cf_j_index02_R', 'cf_j_index01_R',
    'cf_j_middle03_R', 'cf_j_middle02_R', 'cf_j_middle01_R',
    'cf_j_ring03_R', 'cf_j_ring02_R', 'cf_j_ring01_R',
    'cf_j_little03_R', 'cf_j_little02_R', 'cf_j_little01_R'
    )
    
    for finger in finger_list:
        flip_finger(finger)
    
        height_adder = Vector((0,0,0.05))
    def resize_finger(bone):
        parent = armature.data.edit_bones[bone].parent
        armature.data.edit_bones[bone].parent = None
        armature.data.edit_bones[bone].tail = armature.data.edit_bones[bone].head + height_adder
        armature.data.edit_bones[bone].parent = parent
    
    finger_list = (
    'cf_j_index03_L', 'cf_j_index02_L', 'cf_j_index01_L',
    'cf_j_middle03_L', 'cf_j_middle02_L', 'cf_j_middle01_L',
    'cf_j_ring03_L', 'cf_j_ring02_L', 'cf_j_ring01_L',
    'cf_j_little03_L', 'cf_j_little02_L', 'cf_j_little01_L'
    )
    
    for finger in finger_list:
        resize_finger(finger)
    
    #reset the orientation of certain bones
    height_adder = Vector((0,0,0.1))
    def reorient(bone):
        #print(bone)
        armature.data.edit_bones[bone].tail = bpy.data.objects['Armature'].data.edit_bones[bone].head + height_adder
        #print(bone)
        #print(height_adder)  

    reorient_list = [
        'cf_j_thigh00_R', 'cf_j_thigh00_L',
        'cf_j_leg01_R', 'cf_j_leg01_L',
        'cf_j_leg03_R', 'cf_j_leg03_L',
        'cf_j_foot_R', 'cf_j_foot_L',
        'cf_d_arm01_R', 'cf_d_arm01_L',
        'cf_d_shoulder02_R', 'cf_d_shoulder02_L',]

    for bone in reorient_list:
        reorient(bone)
    
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
    
    bpy.ops.object.mode_set(mode='OBJECT')
  
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

    bpy.ops.object.mode_set(mode='OBJECT')

#100% repurposed from https://github.com/FlailingFog/KK-Blender-Shader-Pack/issues/29
### Function to check for empty vertex groups
#returns a dictionary in the form {vertex_group1: weight1, vertex_group2: weight2, etc}
def survey(obj):
    maxWeight = {}
    #prefill vertex group list with zeroes
    for i in obj.vertex_groups:
        maxWeight[i.name] = 0
    #preserve the indexes
    keylist = list(maxWeight)
    #then fill in the real value using the indexes
    for v in obj.data.vertices:
        for g in v.groups:
            gn = g.group
            w = obj.vertex_groups[g.group].weight(v.index)
            if (maxWeight.get(keylist[gn]) is None or w>maxWeight[keylist[gn]]):
                maxWeight[keylist[gn]] = w
    return maxWeight

'''
Duplicated accesory vertex groups are merged. This function makes sure they're separate.

Basic strategy:
* Get bones under each ca_slot accessory bone
* Get the locations of the bones
* Get the average vertex group locations separated by material
* Match the bone and vertex group locations per material
* Extract the vertices from the merged vertex group and assign them to the matched vertex group for each material + vertex group / bone combo
'''
def fix_accessories():
    armature = bpy.data.objects['Armature']
    body = bpy.data.objects['Body']

    duplicated_groups = {} #{child_bone1:[caslot01_child_bone1, caslot02_child_bone1]}, {child_bone2: [caslot05_child_bone2]}, etc...

    #if there are any duplicated bones under any ca_slot bones, rename it and put it in the duplicated groups dictionary
    #renaming the bone will also automatically rename the associated vertex group
    def rename_all_child_bones(parent):
        try:
            for child_bone in parent.children:
                if '.0' in child_bone.name:
                    base_child_name = child_bone.name[:-4]
                    child_bone.name = ca_bone.name[-6:] + '_' + base_child_name
                    if duplicated_groups.get(base_child_name):
                        duplicated_groups[base_child_name].append(child_bone.name)
                    else:
                        duplicated_groups[base_child_name] = []
                        duplicated_groups[base_child_name].append(child_bone.name)
                rename_all_child_bones(child_bone)
        except:
            #the script hit the last bone in the chain
            return

    for ca_bone in armature.data.bones:
        if 'ca_slot' in ca_bone.name:
            rename_all_child_bones(ca_bone)

    #print(duplicated_groups)

    bpy.ops.object.mode_set(mode='OBJECT')
    armature.select_set(False)
    body.select_set(True)
    bpy.context.view_layer.objects.active=body
    for v in body.data.vertices:
        v.select = False
    #bpy.ops.object.mode_set(mode='EDIT')

    #collect all vertices used by all materials
    materialPolys = { ms.material.name : [] for ms in body.material_slots }
    for i, p in enumerate( body.data.polygons ):
        materialPolys[ body.material_slots[ p.material_index ].name ].append( body.data.polygons[i] )
    
    materialVertices = {ms.material.name : [] for ms in body.material_slots}
    for mat in materialPolys:
        for polygon in materialPolys[mat]:
            for vert in polygon.vertices:
                materialVertices[ mat ].append( vert )

    #Collect all vertices used by all vertex groups
    vertices_in_all_groups = {}
    vertexWeightMap = survey(body)

    for group in duplicated_groups:
        if vertexWeightMap.get(group):
            group_index = body.vertex_groups.find(group)
            vertices_in_all_groups[group] = [ v.index for v in body.data.vertices if group_index in [ vg.group for vg in v.groups ] ]
    #print(vertices_in_all_groups.keys())

    #Go through each base vertex group and separate the duplicates
    for base_group in vertices_in_all_groups:
        #refresh UI after each base group to let the user know it's doing something
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        #print("The base group is: {}".format(base_group))
        base_group_index = body.vertex_groups.find(base_group)
        #check which materials are being used by the vertexes in this group
        base_group_materials = set()
        for mat in materialVertices:
            #print("Getting material verticies for {}".format(mat))
            for matvert in materialVertices[mat]:
                if matvert in vertices_in_all_groups[base_group]:
                    base_group_materials.add(mat)
        #use each material vertex and the base group vertices to find the weighted average location for the vertexes of each material
        locations_dictionary = {}
        #print("Finding each material location for {} using these materials: {}".format(base_group, base_group_materials))
        for mat in base_group_materials:
            #get the total of all weights shared by the vertex group and the material
            total_weight = None
            for vertex in materialVertices[mat]:
                if vertex in vertices_in_all_groups[base_group]:
                    #find the correct vertex group
                    group_for_weights = 0
                    for index, grp in enumerate(body.data.vertices[vertex].groups):
                        #print("The real group index is {} and the numbering the vertex sees is {}".format(grp.group, index))
                        if grp.group == base_group_index:
                            group_for_weights = index
                    #add the weight
                    vertex_weight = body.data.vertices[vertex].groups[group_for_weights].weight
                    total_weight = (total_weight + vertex_weight) if total_weight else vertex_weight
            average_location = None
            for vertex in materialVertices[mat]:
                if vertex in vertices_in_all_groups[base_group]:
                    #find the correct vertex group
                    group_for_weights = 0
                    for index, grp in enumerate(body.data.vertices[vertex].groups):
                        if grp.group == base_group_index:
                            group_for_weights = index
                    vertex_weight = body.data.vertices[vertex].groups[group_for_weights].weight
                    average_location = (body.data.vertices[vertex].co * vertex_weight + average_location) if average_location else body.data.vertices[vertex].co * vertex_weight
            locations_dictionary[mat] = average_location / total_weight
            bpy.context.scene.cursor.location = locations_dictionary[mat]
            #print("Found the location for {} at {}".format(mat, locations_dictionary[mat]) )

        #locations dictionary holds locations per material for this base_group vertex group (mat:base_group)
        #duplicated_groups holds the duplicated group names for the base_group in an array (base_group: [slot01_base_group, slot02_base_group])
        #the armature has bones for base_group, slot01_base_group, slot02_base_group, etc

        #Get locations of each duplicate bone head and match them to the average location of each duplicated vertex group
        dupe_groups = duplicated_groups[base_group]
        kklog("Correcting merged bones {}".format(dupe_groups))
        bone_locations_dictionary = {}
        for duplicate_group in dupe_groups:
            bone_locations_dictionary[duplicate_group] = (armature.pose.bones[duplicate_group].head)# + armature.pose.bones[duplicate_group].tail) / 2

        final_data = {}
        error_dist = 0.1 #If the bone match isn't detected properly there's no point in moving it

        for material in locations_dictionary:
            #best bone match for this material in distance, material
            best_match_for_material = [100, None]
            for duplicate_bone in bone_locations_dictionary:
                distance = (locations_dictionary[material] - bone_locations_dictionary[duplicate_bone]).length
                if (distance < best_match_for_material[0]):
                    best_match_for_material = [distance, duplicate_bone]
            matched_bone = best_match_for_material[1]
            #The bone and the material are now matched
            #move the vertex group data from the base bone to the duplicated bone, but only if it belongs to the matched material
            if best_match_for_material[0] < error_dist:
                final_data[material] = matched_bone
                kklog("Matched bone {} to material {} with a distance of {}".format(matched_bone, material, round(best_match_for_material[0],4)))
            else:
                kklog("Bone {} was too far from material {} and not automatically separated from the vertex group {}".format(matched_bone, material, base_group), 'warn')

        for material in final_data:
            duplicate_bone = final_data[material]
            #kklog("Correcting material vertices {} using the bone {}".format(material, duplicate_bone))
            #add all base_group vertices to the new group
            new_group_index = body.vertex_groups.find(duplicate_bone)
            #print("The vertices for {} will be taken out of the vertex group {} placed into the new vertex group {}".format(duplicate_bone, base_group_index, new_group_index))
            #check if each base_group vertex is in the matched material group. If it is, set the weight and remove it from the base_group
            for vertex in vertices_in_all_groups[base_group]:
                body.vertex_groups[new_group_index].add([vertex], 0.0, 'ADD')
                for index, grp in enumerate(body.data.vertices[vertex].groups):
                    if grp.group == new_group_index:
                        new_vg_index = index
                    elif grp.group == base_group_index:
                        old_vg_index = index
                if vertex in materialVertices[material]:
                    body.data.vertices[vertex].groups[new_vg_index].weight = body.data.vertices[vertex].groups[old_vg_index].weight
                    #body.data.vertices[vertex].groups[old_vg_index].weight = 0
                    #body.vertex_groups[old_vg_index].remove([vertex])
                    #print("Moved vertex {} from {} (real {}) to {} (real {}) with weight {}".format(vertex,old_vg_index,base_group_index,new_vg_index,new_group_index, body.data.vertices[vertex].groups[new_vg_index].weight))
                #Else remove it from the new group
                else:
                    body.vertex_groups[new_vg_index].remove([vertex])
                    #print("vertex {} was not moved from group {}".format(vertex,old_vg_index))
            
        #Now that the vertex weights are copied over, remove them from the original group
        #kklog("Cleaning vertexes {}".format(dupe_groups))
        for material in final_data:
            duplicate_bone = final_data[material]
            new_group_index = body.vertex_groups.find(duplicate_bone)
            for vertex in vertices_in_all_groups[base_group]:
                body.vertex_groups[new_group_index].add([vertex], 0.0, 'ADD')
                for index, grp in enumerate(body.data.vertices[vertex].groups):
                    if grp.group == new_group_index:
                        new_vg_index = index
                    elif grp.group == base_group_index:
                        old_vg_index = index
                if vertex in materialVertices[material]:
                    body.data.vertices[vertex].groups[old_vg_index].weight = 0
                    body.vertex_groups[old_vg_index].remove([vertex])

def rename_mmd_bones():
    #renames japanese name field for importing vmds via mmd tools
    #these names are separate from Blender's bone names

    pmx_rename_dict = {
    '全ての親':'p_cf_body_bone',
    'センター':'cf_j_hips',
    '上半身':'cf_j_spine01',
    '上半身2':'cf_j_spine02',
    '首':'cf_j_neck',
    '頭':'cf_j_head',
    '両目':'Eyesx',
    '左目':'cf_J_hitomi_tx_L',
    '右目':'cf_J_hitomi_tx_R',
    '左腕':'cf_j_arm00_L',
    '右腕':'cf_j_arm00_R',
    '左ひじ':'cf_j_forearm01_L',
    '右ひじ':'cf_j_forearm01_R',
    '左肩':'cf_j_shoulder_L',
    '右肩':'cf_j_shoulder_R',
    '左手首':'cf_j_hand_L',
    '右手首':'cf_j_hand_R',
    '左親指０':'cf_j_thumb01_L',
    '左親指１':'cf_j_thumb02_L',
    '左親指２':'cf_j_thumb03_L',
    '左薬指１':'cf_j_ring01_L',
    '左薬指２':'cf_j_ring02_L',
    '左薬指３':'cf_j_ring03_L',
    '左中指１':'cf_j_middle01_L',
    '左中指２':'cf_j_middle02_L',
    '左中指３':'cf_j_middle03_L',
    '左小指１':'cf_j_little01_L',
    '左小指２':'cf_j_little02_L',
    '左小指３':'cf_j_little03_L',
    '左人指１':'cf_j_index01_L',
    '左人指２':'cf_j_index02_L',
    '左人指３':'cf_j_index03_L',
    '右親指０':'cf_j_thumb01_R',
    '右親指１':'cf_j_thumb02_R',
    '右親指２':'cf_j_thumb03_R',
    '右薬指１':'cf_j_ring01_R',
    '右薬指２':'cf_j_ring02_R',
    '右薬指３':'cf_j_ring03_R',
    '右中指１':'cf_j_middle01_R',
    '右中指２':'cf_j_middle02_R',
    '右中指３':'cf_j_middle03_R',
    '右小指１':'cf_j_little01_R',
    '右小指２':'cf_j_little02_R',
    '右小指３':'cf_j_little03_R',
    '右人指１':'cf_j_index01_R',
    '右人指２':'cf_j_index02_R',
    '右人指３':'cf_j_index03_R',
    '下半身':'cf_j_waist01',
    '左足':'cf_j_thigh00_L',
    '右足':'cf_j_thigh00_R',
    '左ひざ':'cf_j_leg01_L',
    '右ひざ':'cf_j_leg01_R',
    '左足首':'cf_j_leg03_L',
    '右足首':'cf_j_leg03_R',
    }

    armature = bpy.data.objects['Armature']
    for bone in pmx_rename_dict:
        if armature.pose.bones.get(pmx_rename_dict[bone]):
            armature.pose.bones[pmx_rename_dict[bone]].mmd_bone.name_j = bone

def survey_vertexes(obj):
    has_vertexes = {}
    for i in obj.vertex_groups:
        has_vertexes[i.name] = False
    #preserve the indexes
    keylist = list(has_vertexes)
    #then fill in the real value using the indexes
    for v in obj.data.vertices:
        for g in v.groups:
            gn = g.group
            w = obj.vertex_groups[g.group].weight(v.index)
            if (has_vertexes.get(keylist[gn]) is None or w>has_vertexes[keylist[gn]]):
                has_vertexes[keylist[gn]] = True
    return has_vertexes
    
def remove_empty_vertex_groups():
    #check body for groups with no vertexes. Delete if the group is not a bone on the armature
    body = bpy.data.objects['Body']
    armature = bpy.data.objects['Armature']
    vertexWeightMap = survey_vertexes(body)
    bones_in_armature = [bone.name for bone in armature.data.bones]
    for group in vertexWeightMap:
        if group not in bones_in_armature and vertexWeightMap[group] == False and 'cf_J_Vagina' not in group:
            body.vertex_groups.remove(body.vertex_groups[group])

class finalize_pmx(bpy.types.Operator):
    bl_idname = "kkb.finalizepmx"
    bl_label = "Finalize .pmx file"
    bl_description = "Finalize CATS .pmx file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            last_step = time.time()

            scene = context.scene.kkbp
            modify_armature = scene.armature_dropdown

            kklog('\nFinalizing PMX file...')
            standardize_armature(modify_armature)
            reset_and_reroll_bones()
            if modify_armature in ['A', 'B']:
                kklog('Modifying armature...', type='timed')
                modify_pmx_armature()
            #if fix_accs:
                #kklog('Fixing accessories...')
                #fix_accessories()
            rename_mmd_bones()
            remove_empty_vertex_groups()

            kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            
            return {'FINISHED'}
        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(finalize_pmx)
    
    # test call
    print((bpy.ops.kkb.finalizepmx('INVOKE_DEFAULT')))