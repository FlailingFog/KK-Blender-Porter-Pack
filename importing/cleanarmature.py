### redo toe bone connections
#       when did i put this note here

'''
AFTER CATS (CLEAN ARMATURE) SCRIPT
- Hides all bones that aren't in the bonelists
- Connects the finger bones that CATS sometimes misses for koikatsu imports
- Corrects the toe bones on the better penetration armature
Usage:
- Run the script
'''

import bpy, time, traceback
from .finalizepmx import survey_vertexes
from .importbuttons import kklog

#function that returns a type of bone list
def get_bone_list(kind):
    if kind == 'core_list':
        #main bone list
        return [
        'cf_n_height', 'cf_j_hips', 'cf_j_waist01', 'cf_j_waist02',
        'cf_j_spine01', 'cf_j_spine02', 'cf_j_spine03',
        'cf_j_neck', 'cf_j_head',
        'cf_d_bust00', 'cf_j_bust01_L', 'cf_j_bust01_R', 'Eyesx',

        'cf_j_shoulder_L', 'cf_j_shoulder_R', 'cf_j_arm00_L', 'cf_j_arm00_R',
        'cf_j_forearm01_L', 'cf_j_forearm01_R', 'cf_j_hand_R', 'cf_j_hand_L',

        'cf_j_thumb01_L','cf_j_thumb02_L', 'cf_j_thumb03_L',
        'cf_j_ring01_L', 'cf_j_ring02_L', 'cf_j_ring03_L', 
        'cf_j_middle01_L','cf_j_middle02_L', 'cf_j_middle03_L', 
        'cf_j_little01_L','cf_j_little02_L', 'cf_j_little03_L', 
        'cf_j_index01_L','cf_j_index02_L', 'cf_j_index03_L', 

        'cf_j_thumb01_R','cf_j_thumb02_R',  'cf_j_thumb03_R',
        'cf_j_ring01_R','cf_j_ring02_R', 'cf_j_ring03_R', 
        'cf_j_middle01_R','cf_j_middle02_R', 'cf_j_middle03_R', 
        'cf_j_little01_R','cf_j_little02_R', 'cf_j_little03_R', 
        'cf_j_index01_R', 'cf_j_index02_R', 'cf_j_index03_R',

        'cf_j_thigh00_L', 'cf_j_thigh00_R', 'cf_j_leg01_L', 'cf_j_leg01_R',
        'cf_j_foot_L', 'cf_j_foot_R', 'cf_j_toes_L', 'cf_j_toes_R',

        'cf_j_siri_L', 'cf_j_siri_R',

        'cf_pv_knee_L', 'cf_pv_knee_R',
        'cf_pv_elbo_L', 'cf_pv_elbo_R',
        'cf_pv_hand_L', 'cf_pv_hand_R',
        'cf_pv_foot_L', 'cf_pv_foot_R'
        ]
        
    elif kind == 'non_ik':
        #IK bone list
        return [
        'cf_j_forearm01_L', 'cf_j_forearm01_R',
        'cf_j_arm00_L', 'cf_j_arm00_R',
        'cf_j_thigh00_L', 'cf_j_thigh00_R',
        'cf_j_leg01_L', 'cf_j_leg01_R',
        'cf_j_leg03_L', 'cf_j_leg03_R',
        'cf_j_foot_L', 'cf_j_foot_R',
        'cf_j_hand_L', 'cf_j_hand_R',
        'cf_j_bust03_L', 'cf_j_bnip02root_L', 'cf_j_bnip02_L',
        'cf_j_bust03_R', 'cf_j_bnip02root_R', 'cf_j_bnip02_R']
        
    elif kind == 'eye_list':
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
        'cf_J_Mayu_L', 'cf_J_MayuMid_s_L', 'cf_J_MayuTip_s_L']

    elif kind == 'mouth_list':
        return [
        'cf_J_Mouth_R', 'cf_J_Mouth_L',
        'cf_J_Mouthup', 'cf_J_MouthLow', 'cf_J_MouthMove', 'cf_J_MouthCavity',
        
        'cf_J_EarUp_L', 'cf_J_EarBase_ry_L', 'cf_J_EarLow_L',
        'cf_J_CheekUp2_L', 'cf_J_Eye_rz_L', 'cf_J_Eye_rz_L', 
        'cf_J_CheekUp_s_L', 'cf_J_CheekLow_s_L', 

        'cf_J_EarUp_R', 'cf_J_EarBase_ry_R', 'cf_J_EarLow_R',
        'cf_J_CheekUp2_R', 'cf_J_Eye_rz_R', 'cf_J_Eye_rz_R', 
        'cf_J_CheekUp_s_R', 'cf_J_CheekLow_s_R',

        'cf_J_ChinLow', 'cf_J_Chin_s', 'cf_J_ChinTip_Base', 
        'cf_J_NoseBase', 'cf_J_NoseBridge_rx', 'cf_J_Nose_tip']
        
    elif kind == 'toe_list':
        #bones that appear on the Better Penetration armature
        return [
        'cf_j_toes0_L', 'cf_j_toes1_L', 'cf_j_toes10_L',
        'cf_j_toes2_L', 'cf_j_toes20_L',
        'cf_j_toes3_L', 'cf_j_toes30_L', 'cf_j_toes4_L',
        
        'cf_j_toes0_R', 'cf_j_toes1_R', 'cf_j_toes10_R',
        'cf_j_toes2_R', 'cf_j_toes20_R',
        'cf_j_toes3_R', 'cf_j_toes30_R', 'cf_j_toes4_R']
        
    elif kind == 'bp_list':
        #more bones that appear on the Better Penetration armature
        return [
        'cf_j_kokan', 'cf_j_ana', 'cf_J_Vagina_root', 'cf_J_Vagina_B', 'cf_J_Vagina_F',
        'cf_J_Vagina_L.001', 'cf_J_Vagina_L.002', 'cf_J_Vagina_L.003', 'cf_J_Vagina_L.004', 'cf_J_Vagina_L.005', 
        'cf_J_Vagina_R.001', 'cf_J_Vagina_R.002', 'cf_J_Vagina_R.003', 'cf_J_Vagina_R.004', 'cf_J_Vagina_R.005']

    elif kind == 'skirt_list':
        return [
        'cf_j_sk_00_00', 'cf_j_sk_00_01', 'cf_j_sk_00_02', 'cf_j_sk_00_03', 'cf_j_sk_00_04',
        'cf_j_sk_01_00', 'cf_j_sk_01_01', 'cf_j_sk_01_02', 'cf_j_sk_01_03', 'cf_j_sk_01_04',
        'cf_j_sk_02_00', 'cf_j_sk_02_01', 'cf_j_sk_02_02', 'cf_j_sk_02_03', 'cf_j_sk_02_04',
        'cf_j_sk_03_00', 'cf_j_sk_03_01', 'cf_j_sk_03_02', 'cf_j_sk_03_03', 'cf_j_sk_03_04',
        'cf_j_sk_04_00', 'cf_j_sk_04_01', 'cf_j_sk_04_02', 'cf_j_sk_04_03', 'cf_j_sk_04_04',
        'cf_j_sk_05_00', 'cf_j_sk_05_01', 'cf_j_sk_05_02', 'cf_j_sk_05_03', 'cf_j_sk_05_04',
        'cf_j_sk_06_00', 'cf_j_sk_06_01', 'cf_j_sk_06_02', 'cf_j_sk_06_03', 'cf_j_sk_06_04',
        'cf_j_sk_07_00', 'cf_j_sk_07_01', 'cf_j_sk_07_02', 'cf_j_sk_07_03', 'cf_j_sk_07_04']
    
    elif kind == 'tongue_list':
        return [
            'cf_j_tang_01', 'cf_j_tang_02', 'cf_j_tang_03', 'cf_j_tang_04', 'cf_j_tang_05', 
            'cf_j_tang_L_03', 'cf_j_tang_L_04', 'cf_j_tang_L_05', 
            'cf_j_tang_R_03', 'cf_j_tang_R_04', 'cf_j_tang_R_05', 
            ]

def set_armature_layer(bone_name, show_layer, hidden = False):
    bpy.data.armatures[0].bones[bone_name].layers = (
        True, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, 
        False, False, False, False, False, False, False, False, 
        False, False, False, False, False, False, False, False
    )
    bpy.data.armatures[0].bones[bone_name].layers[show_layer] = True
    bpy.data.armatures[0].bones[bone_name].layers[0] = False
    bpy.data.armatures[0].bones[bone_name].hide = hidden

def reorganize_armature_layers():
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
    toe_list = get_bone_list('toe_list')
    bp_list = get_bone_list('bp_list')
    eye_list = get_bone_list('eye_list')
    mouth_list = get_bone_list('mouth_list')
    skirt_list = get_bone_list('skirt_list')
    tongue_list = get_bone_list('tongue_list')
    
    armature = bpy.data.objects['Armature']
    bpy.ops.pose.select_all(action='DESELECT')

    #throw all bones to armature layer 11
    for bone in bpy.data.armatures[0].bones:
        set_armature_layer(bone.name, 10)

    #reshow cf_hit_ bones on layer 12
    for bone in [bones for bones in bpy.data.armatures[0].bones if 'cf_hit_' in bones.name]:
        set_armature_layer(bone.name, show_layer = 11)

    #reshow k_f_ bones on layer 13
    for bone in [bones for bones in bpy.data.armatures[0].bones if 'k_f_' in bones.name]:
        set_armature_layer(bone.name, show_layer = 12)

    #reshow core bones on layer 1
    for bone in core_list:
        set_armature_layer(bone, show_layer = 0)

    #reshow non_ik bones on layer 2
    for bone in non_ik:
        set_armature_layer(bone, show_layer = 1)

    #Put the charamaker bones on layer 3
    for bone in [bones for bones in bpy.data.armatures[0].bones if 'cf_s_' in bones.name]:
        set_armature_layer(bone.name, show_layer = 2)

    #Put the deform bones on layer 4
    for bone in [bones for bones in bpy.data.armatures[0].bones if 'cf_d_' in bones.name]:
        set_armature_layer(bone.name, show_layer = 3)

    try:
        #Put the better penetration bones on layer 5
        for bone in bp_list:
            set_armature_layer(bone, show_layer = 4)

            #rename the bones so you can mirror them over the x axis in pose mode
            if 'Vagina_L_' in bone or 'Vagina_R_' in bone:
                bpy.data.armatures[0].bones[bone].name = 'Vagina' + bone[8:] + '_' + bone[7]

        #Put the toe bones on layer 5
        for bone in toe_list:
            set_armature_layer(bone, show_layer = 4)
    except:
        #this armature isn't a BP armature
        pass

    #Put the upper eye bones on layer 17
    for bone in eye_list:
        set_armature_layer(bone, show_layer = 16)
    
    #Put the lower mouth bones on layer 18
    for bone in mouth_list:
        set_armature_layer(bone, show_layer = 17)

    #Put the tongue rig bones on layer 19
    for bone in tongue_list:
        set_armature_layer(bone, show_layer = 18)

    #Put the skirt bones on layer 9
    for bone in skirt_list:
        set_armature_layer(bone, show_layer = 8)

    #put accessory bones on layer 10 during reshow_accessory_bones() later on

    bpy.ops.pose.select_all(action='DESELECT')
    
    #Make all bone layers visible for now
    all_layers = [
    True, True, True, True, True, False, False, False, #body
    True, True, True, False, False, False, False, False, #clothes
    True, True, False, False, False, False, False, False, #face
    False, False, False, False, False, False, False, False]
    bpy.ops.armature.armature_layers(layers=all_layers)
    bpy.context.object.data.display_type = 'STICK'
    bpy.ops.object.mode_set(mode='OBJECT')
    
#make sure certain bones are visually connected
def visually_connect_bones():
    
    skirt_list = get_bone_list('skirt_list')
    bpy.ops.object.mode_set(mode='EDIT')
    armature = bpy.data.objects['Armature']

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
    
    '''#Make sure top skirt root bones are visually correct (flip them)
    def flip(switchbone):
        chain = switchbone[5:10]
        armature.data.edit_bones[switchbone].tail = (armature.data.edit_bones[switchbone].head + armature.data.edit_bones['cf_j_'+chain+'_00'].tail)/2
    for skirtroot in skirt_list:
        if '_d_' in skirtroot:
            flip(skirtroot)
    '''
    bpy.ops.object.mode_set(mode='OBJECT')

def move_accessory_bones(context):
    armature = bpy.data.objects['Armature']
    #go through each outfit and move ALL accessory bones to layer 10
    dont_move_these = [
            'cf_pv', 'Eyesx',
            'cf_J_hitomi_tx_', 'cf_J_FaceRoot', 'cf_J_FaceUp_t',
            'n_cam', 'EyesLookTar', 'N_move', 'a_n_', 'cf_hit',
            'cf_j_bnip02', 'cf_j_kokan', 'cf_j_ana']

    for outfit_or_hair in [obj for obj in bpy.data.objects if 'Outfit ' in obj.name]:
        # Find empty vertex groups
        vertexWeightMap = survey_vertexes(outfit_or_hair)
        #add outfit id to all accessory bones in an array that represents if the bone is used in each outfit slot ([True, False, True] means the bone is used in outfits 0 and 2)
        number_of_outfits = len([outfit for outfit in bpy.data.objects if 'Outfit ' in outfit.name and 'Hair' not in outfit.name and 'alt ' not in outfit.name and 'Indoor' not in outfit.name])
        for bone in [bone for bone in armature.data.bones if bone.layers[10]]:
            no_move_bone = False
            for this_prefix in dont_move_these:
                if this_prefix in bone.name:
                    no_move_bone = True
            if not no_move_bone and vertexWeightMap.get(bone.name):
                try:
                    outfit_id_array = bone['KKBP outfit ID'].to_list()
                    outfit_id_array.append(outfit_or_hair['KKBP outfit ID'])
                    bone['KKBP outfit ID'] = outfit_id_array
                except:
                    bone['KKBP outfit ID'] = [outfit_or_hair['KKBP outfit ID']]

    #move accessory bones to armature layer 10
    for bone in [bone for bone in armature.data.bones if bone.get('KKBP outfit ID')]:
        set_armature_layer(bone.name, show_layer = 9)

    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='DESELECT')

class clean_armature(bpy.types.Operator):
    bl_idname = "kkb.cleanarmature"
    bl_label = "Clean armature"
    bl_description = "Makes the armature less of an eyesore"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            last_step = time.time()

            kklog('\nCategorizing bones into armature layers...', 'timed')

            reorganize_armature_layers()
            if context.scene.kkbp.categorize_dropdown in ['A', 'B']:
                visually_connect_bones()
            move_accessory_bones(context)
            
            kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')

            return {'FINISHED'}
        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
if __name__ == "__main__":
    bpy.utils.register_class(clean_armature)

    # test call
    print((bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT')))
