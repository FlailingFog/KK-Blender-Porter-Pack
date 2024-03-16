#simplfies bone count using the merge weights function in CATS

import bpy, traceback, time
from .. import common as c
from ..interface.dictionary_en import t

def main(prep_type, simp_type, separate_hair):

    armature = bpy.data.objects['Armature']

    c.kklog('\nPrepping for export...')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    #Assume hidden items are unused and move them to their own collection
    c.kklog('Moving unused objects to their own collection...')
    no_move_objects = ['Bonelyfans', 'Shadowcast', 'Hitboxes', 'Body', 'Armature']
    for object in bpy.context.scene.objects:
        #print(object.name)
        move_this_one = object.name not in no_move_objects and 'Widget' not in object.name and object.hide
        if move_this_one:
            object.hide = False
            object.select_set(True)
            bpy.context.view_layer.objects.active=object
    if bpy.context.selected_objects:
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name='Unused clothing items')
    #hide the new collection
    try:
        bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children['Unused clothing items']
        bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
    except:
        try:
            #maybe the collection is in the default Collection collection
            bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children['Collection'].children['Unused clothing items']
            bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
        except:
            #maybe the collection is already hidden, or doesn't exist
            pass
    
    c.kklog('Removing object outline modifier...')
    for ob in bpy.data.objects:
        if ob.modifiers.get('Outline Modifier'):
            ob.modifiers['Outline Modifier'].show_render = False
            ob.modifiers['Outline Modifier'].show_viewport = False
        #remove the outline materials because they won't be baked
        if ob in [obj for obj in bpy.context.view_layer.objects if obj.type == 'MESH']:
            ob.select_set(True)
            bpy.context.view_layer.objects.active=ob
            bpy.ops.object.material_slot_remove_unused()
    bpy.ops.object.select_all(action='DESELECT')
    body = bpy.data.objects['Body']
    bpy.context.view_layer.objects.active=body
    body.select_set(True)

    c.kklog('disabling uv warp modifiers on the eyes...')
    for ob in bpy.data.objects:
        if ob.modifiers.get('Left Eye UV warp'):
            ob.modifiers['Left Eye UV warp'].show_render = False
            ob.modifiers['Left Eye UV warp'].show_viewport = False
            ob.modifiers['Right Eye UV warp'].show_render = False
            ob.modifiers['Right Eye UV warp'].show_viewport = False

    #remove the second Template Eyewhite slot if there are two of the same name in a row
    index = 0
    for mat_slot_index in range(len(body.material_slots)):
        if body.material_slots[mat_slot_index].name == 'KK Eyewhites (sirome)':
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
    if simp_type in ['A', 'B']:
        show_bones()

        #Move pupil bones to layer 1
        armature = bpy.data.objects['Armature']
        if armature.data.bones.get('Left Eye'):
            armature.data.bones['Left Eye'].layers[0] = True
            armature.data.bones['Left Eye'].layers[10] = False
            armature.data.bones['Right Eye'].layers[0] = True
            armature.data.bones['Right Eye'].layers[10] = False

        #Select bones on layer 11
        for bone in armature.data.bones:
            if bone.layers[10]==True:
                bone.select = True
        
        #if very simple selected, also get 3-5,12,17-19
        if simp_type in ['A']:
            for bone in armature.data.bones:
                select_bool = bone.layers[2] or bone.layers[3] or bone.layers[4] or bone.layers[11] or bone.layers[12] or bone.layers[16] or bone.layers[17] or bone.layers[18]
                if select_bool:
                    bone.select = True
        
        c.kklog('Using the merge weights function in CATS to simplify bones...')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.kkbp.cats_merge_weights()

    #if separate the hair...
    if separate_hair:
        show_bones()
        
        #Select bones on layer 10
        for bone in armature.data.bones:
            if bone.layers[9]==True:
                bone.select = True

        #Separate the hair bones to a new armature
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.separate()
        new_armature = bpy.data.objects['Armature.001']
        new_armature.name="Hair"

        #Move hair meshes to the new armature
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects['Hair Outfit 00'].select_set(True)
        bpy.context.view_layer.objects.active=new_armature
        bpy.ops.object.parent_set(type='ARMATURE')

    #If exporting for VRM or VRC...
    if prep_type in ['A', 'D']:
        c.kklog('Editing armature for VRM...')
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
        armature.data.edit_bones.remove(armature.data.edit_bones['dont need lol'])

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')

        #Merge specific bones for unity rig autodetect
        armature = bpy.data.objects['Armature']
        merge_these = ['cf_j_waist02', 'cf_s_waist01', 'cf_s_hand_L', 'cf_s_hand_R']
        #Delete the upper chest for VR chat models, since it apparently causes errors with eye tracking
        if prep_type == 'D':
            merge_these.append('Upper Chest')
        for bone in armature.data.bones:
            if bone.name in merge_these:
                bone.select = True

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.kkbp.cats_merge_weights()

    #If exporting for MMD...
    if prep_type == 'C':
        #Create the empty
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(0, 0, 0))
        empty = bpy.data.objects['Empty']
        bpy.ops.object.select_all(action='DESELECT')
        armature.parent = empty
        bpy.context.view_layer.objects.active = armature

        #rename bones to stock
        if armature.data.bones.get('Center'):
            bpy.ops.kkbp.switcharmature('INVOKE_DEFAULT')
        
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
        body.vertex_groups.active=body.vertex_groups['BodyTop']

        #combine all objects into one

        #create leg IKs?
        
        c.kklog('Using CATS to simplify more bones for MMD...')

        #use mmd_tools to convert
        bpy.ops.mmd_tools.convert_to_mmd_model()

    bpy.ops.object.mode_set(mode='OBJECT')

def show_bones():
    #show all bones on the armature
    bpy.ops.object.mode_set(mode='POSE')
    allLayers = [True, True, True, True, True, True, True, True,
                True, True, True, True, True, True, True, True,
                True, True, True, True, True, True, True, True,
                True, True, True, True, True, True, True, True]
    bpy.data.objects['Armature'].data.layers = allLayers
    bpy.ops.pose.select_all(action='DESELECT')

class export_prep(bpy.types.Operator):
    bl_idname = "kkbp.exportprep"
    bl_label = "Prep for target application"
    bl_description = t('export_prep_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene.kkbp
        prep_type = scene.prep_dropdown
        simp_type = scene.simp_dropdown
        separate_hair = scene.separate_hair_bool
        last_step = time.time()
        try:
            c.toggle_console()
            main(prep_type, simp_type, separate_hair)
            scene.plugin_state = 'prepped'
            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            c.toggle_console()
            return {'FINISHED'}
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
    

if __name__ == "__main__":
    bpy.utils.register_class(export_prep)

    # test call
    print((bpy.ops.kkbp.exportprep('INVOKE_DEFAULT')))
