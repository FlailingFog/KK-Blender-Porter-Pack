'''
SELECT BONES SCRIPT
- Selects bones that aren't needed. This is useful for reducing the bone count with the "Merge Weights" option in CATS

Usage:
- Make sure all the hair / accessory bones you want to keep are visible in pose mode
- Run the script
- Use the "Merge Weights to Parent" option in CATS (under Model Options)
'''

import bpy, traceback
from ..importing.finalizepmx import kklog
from ..importing.bonedrivers import rename_bones_for_clarity

def main(prep_type):

    armature = bpy.data.objects['Armature']

    kklog('\nPrepping for export...')
    #Combine all objects
    kklog('\nCombining all objects...')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active=bpy.data.objects['Body']
    body = bpy.context.view_layer.objects.active
    bpy.ops.object.join()
    
    kklog('\nRemoving object outline modifier...')
    body.modifiers['Outline Modifier'].show_render = False
    body.modifiers['Outline Modifier'].show_viewport = False

    #remove the second Template Eye slot if there are two of the same name in a row
    kklog('\nRemoving duplicate Eye materials...')
    eye_index = 0
    for mat_slot_index in range(len(body.material_slots)):
        if body.material_slots[mat_slot_index].name == 'Template Eye (hitomi)':
            index = mat_slot_index
    if body.material_slots[index].name == body.material_slots[index-1].name:
        body.active_material_index = index
        bpy.ops.object.material_slot_remove()

    #Select the armature and make it active
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects['Armature'].hide_set(False)
    bpy.data.objects['Armature'].select_set(True)
    bpy.context.view_layer.objects.active=bpy.data.objects['Armature']
    bpy.ops.object.mode_set(mode='POSE')

    #If simplifying the bones...
    if prep_type in ['A', 'B', 'C']:
        #show all bones on the armature
        allLayers = [True, True, True, True, True, True, True, True,
                    True, True, True, True, True, True, True, True,
                    True, True, True, True, True, True, True, True,
                    True, True, True, True, True, True, True, True]
        bpy.data.objects['Armature'].data.layers = allLayers
        bpy.ops.pose.select_all(action='DESELECT')

        #Select bones on layer 11
        armature = bpy.data.objects['Armature']
        armature.data.bones['Left Eye'].layers[16] = True
        armature.data.bones['Left Eye'].layers[10] = False
        armature.data.bones['Right Eye'].layers[16] = True
        armature.data.bones['Right Eye'].layers[10] = False

        #Select bones on layer 11
        for bone in armature.data.bones:
            if bone.layers[10]==True:
                bone.select = True
        
        kklog('Using CATS to simplify bones...')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.cats_manual.merge_weights()

    #If exporting for VRM...
    if prep_type == 'A':
        
        '''
        #remove materials and shapekeys
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active=body
        for x in body.material_slots:
            body.active_material_index = 0
            bpy.ops.object.material_slot_remove()
        
        bpy.ops.object.shape_key_remove(all=True)
        '''

        bpy.context.view_layer.objects.active=armature
        bpy.ops.object.mode_set(mode='EDIT')

        #Rearrange bones to match CATS output 
        armature.data.edit_bones['Pelvis'].parent = None
        armature.data.edit_bones['Spine'].parent = armature.data.edit_bones['Pelvis']
        armature.data.edit_bones['Hips'].name = 'dont need lol'
        armature.data.edit_bones['Pelvis'].name = 'Hips'
        armature.data.edit_bones['Left leg'].parent = armature.data.edit_bones['Hips']
        armature.data.edit_bones['Right leg'].parent = armature.data.edit_bones['Hips']
        armature.data.edit_bones['Left ankle'].parent = armature.data.edit_bones['Left knee']
        armature.data.edit_bones['Right ankle'].parent = armature.data.edit_bones['Right knee']
        armature.data.edit_bones['Left shoulder'].parent = armature.data.edit_bones['Upper Chest']
        armature.data.edit_bones['Right shoulder'].parent = armature.data.edit_bones['Upper Chest']

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        #Select bones on layer 3/5/12/13
        armature = bpy.data.objects['Armature']
        merge_these = ['cf_j_waist02', 'cf_s_waist01', 'cf_s_hand_L', 'cf_s_hand_R']
        for bone in armature.data.bones:
            if bone.layers[11]==True or bone.layers[12] == True or bone.layers[2] == True or bone.layers[4] == True:
                bone.select = True
            if bone.name in merge_these:
                bone.select = True
        
        kklog('Using CATS to simplify more bones for VRM...')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.cats_manual.merge_weights()

    #If exporting for MMD...
    if prep_type == 'B':
        #Create the empty
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
        empty = bpy.data.objects['Empty']
        bpy.ops.object.select_all(action='DESELECT')
        armature.parent = empty
        bpy.context.view_layer.objects.active = armature

        #rename bones to stock
        if armature.data.bones.get('Center'):
            bpy.ops.kkb.switcharmature('INVOKE_DEFAULT')
        
        #then rename bones to japanese
        pmx_rename_dict = {
        '全ての親':'cf_n_height',
        'センター':'cf_j_hips',
        '上半身':'cf_j_spine01',
        '上半身２':'cf_j_spine02',
        '上半身３':'cf_j_spine03',
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

        for bone in pmx_rename_dict:
            armature.data.bones[pmx_rename_dict[bone]].name = bone
        
        #Rearrange bones to match a random pmx model I found 
        bpy.ops.object.mode_set(mode='EDIT')
        armature.data.edit_bones['左肩'].parent = armature.data.edit_bones['上半身３']
        armature.data.edit_bones['右肩'].parent = armature.data.edit_bones['上半身３']
        armature.data.edit_bones['左足'].parent = armature.data.edit_bones['下半身']
        armature.data.edit_bones['右足'].parent = armature.data.edit_bones['下半身']

        #refresh the vertex groups? Bones will act as if they're detached if this isn't done
        body.vertex_groups.active=0

        kklog('Using CATS to simplify more bones for MMD...')

        #use mmd_tools to convert
        bpy.ops.mmd_tools.convert_to_mmd_model()

    bpy.ops.object.mode_set(mode='OBJECT')

class select_bones(bpy.types.Operator):
    bl_idname = "kkb.selectbones"
    bl_label = "Prep for target application"
    bl_description = "Check the dropdown for more info"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene.placeholder
        prep_type = scene.prep_dropdown

        try:
            main(prep_type)
            return {'FINISHED'}
        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
    

if __name__ == "__main__":
    bpy.utils.register_class(select_bones)

    # test call
    print((bpy.ops.kkb.selectbones('INVOKE_DEFAULT')))
