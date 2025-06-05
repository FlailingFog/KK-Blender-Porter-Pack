#simplfies bone count using the merge weights function in CATS

import bpy, traceback, time
from .. import common as c
from ..interface.dictionary_en import t

def main(prep_type, simp_type, ue_apply_scale, ue_triangulate_mesh):
    try:
        #always try to use the atlased model first
        body = bpy.data.objects['Body ' + c.get_name() + '.001']
        bpy.context.view_layer.objects.active=body
        body_name = body.name
        armature_name = 'Armature.001'
        if not bpy.data.objects[armature_name].data.bones.get('Pelvis'):
            #the atlased body has already been modified. Skip.
            c.kklog('Model with atlas has already been prepped. Skipping export prep functions...', type='warn')
            return False
    except:
        #fallback to the non-atlased model if the atlased model collection is not visible
        body = bpy.data.objects['Body ' + c.get_name()]
        bpy.context.view_layer.objects.active=body
        body_name = body.name
        armature_name = 'Armature'

    armature = bpy.data.objects[armature_name]

    c.kklog('\nPrepping for export...')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')

    #Assume hidden items are unused and move them to their own collection
    c.kklog('Moving unused objects to their own collection...')
    no_move_objects = ['Hitboxes ' + c.get_name(), body_name, armature_name]
    for object in bpy.context.scene.objects:
        try:
            move_this_one = object.name not in no_move_objects and 'Widget' not in object.name and object.hide_get()
            if move_this_one:
                object.hide_set(False)
                object.select_set(True)
                bpy.context.view_layer.objects.active=object
        except:
            c.kklog("During export prep, couldn't move object '{}' for some reason...".format(object), type='error')
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
    body = bpy.data.objects[body_name]
    bpy.context.view_layer.objects.active=body
    body.select_set(True)

    #Select the armature and make it active
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[armature_name].hide_set(False)
    bpy.data.objects[armature_name].select_set(True)
    bpy.context.view_layer.objects.active=bpy.data.objects[armature_name]
    bpy.ops.object.mode_set(mode='POSE')

    # If exporting for Unreal...
    if prep_type == 'E':
        armature = bpy.data.objects['Armature']
        bpy.context.view_layer.objects.active = armature
        bpy.ops.armature.collection_show_all()

        bpy.ops.object.mode_set(mode='EDIT')

        #Clear IK, it won't work in unreal
        for bone in armature.pose.bones:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)

        #Rename some bones to make it match Mannequin skeleton
        #Not necessary, but allows Unreal automatically recognize and match bone names when retargeting
        ue_rename_dict = {
            'Hips': 'pelvis',
            'Spine': 'spine_01',
            'Chest': 'spine_02',
            'Upper Chest': 'spine_03',
            'Neck': 'neck',
            'Head': 'head',
            'Left shoulder': 'clavicle_l',
            'Right shoulder': 'clavicle_r',
            'Left arm': 'upperarm_l',
            'Right arm': 'upperarm_r',
            'Left elbow': 'lowerarm_l',
            'Right elbow': 'lowerarm_r',
            'Left wrist': 'hand_l',
            'Right wrist': 'hand_r',

            'Left leg': 'thigh_l',
            'Right leg': 'thigh_r',
            'Left knee': 'calf_l',
            'Right knee': 'calf_r',
            'cf_j_leg03_L': 'foot_l',
            'cf_j_leg03_R': 'foot_r',
            'Left toe': 'ball_l',
            'Right toe': 'ball_r',
        }
        for bone in ue_rename_dict:
            if armature.data.bones.get(bone):
                armature.data.bones[bone].name = ue_rename_dict[bone]

        # Switch to Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')

        # Create a new bone named "root"
        root_bone = armature.data.edit_bones.new('root')
        # Set root bone at world origin
        root_bone.head = (0, 0, 0)
        root_bone.tail = (0, 0, 1) # Tail position can be arbitrary for a root, typically Z-up

        # Ensure it has no parent
        root_bone.parent = None

        # Find the bone now named "pelvis"
        pelvis_bone = armature.data.edit_bones.get('pelvis')

        if pelvis_bone:
            # Parent the "pelvis" bone to the new "root" bone
            pelvis_bone.parent = root_bone
            # Ensure the "pelvis" bone's head is at the same location as the new "root" bone's head
            pelvis_bone.head = root_bone.head
        else:
            c.kklog("Could not find 'pelvis' bone to parent to 'root'.", type='warn')

        # The script should already be in EDIT mode here due to the line above,
        # but to be safe and adhere to instructions if the above line is removed/changed:
        if bpy.context.object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        #Make all the bones on the legs face the same direction, otherwise IK won't work in Unreal
        armature.data.edit_bones["calf_l"].tail.z = armature.data.edit_bones["calf_l"].head.z + 0.1
        armature.data.edit_bones["calf_l"].head.y += 0.01
        armature.data.edit_bones["calf_r"].tail.z = armature.data.edit_bones["calf_r"].head.z + 0.1
        armature.data.edit_bones["calf_r"].head.y += 0.01

        armature.data.edit_bones["ball_l"].tail.z = armature.data.edit_bones["ball_l"].head.z
        armature.data.edit_bones["ball_l"].tail.y = armature.data.edit_bones["ball_l"].head.y - 0.05
        armature.data.edit_bones["ball_r"].tail.z = armature.data.edit_bones["ball_r"].head.z
        armature.data.edit_bones["ball_r"].tail.y = armature.data.edit_bones["ball_r"].head.y - 0.05

        bpy.ops.object.mode_set(mode='POSE')

        if ue_apply_scale:
            c.kklog('Applying 100x scale for Unreal Engine...')

            # Ensure Object Mode for scaling
            if bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            bpy.ops.object.select_all(action='DESELECT')

            # Select armature and its mesh children
            armature.select_set(True)
            for child in armature.children:
                if child.type == 'MESH':
                    child.select_set(True)

            bpy.context.view_layer.objects.active = armature

            # Apply scale
            bpy.ops.transform.resize(value=(100, 100, 100))
            # Apply transformations (scale) to selected objects
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            c.kklog('Unreal Engine scaling complete.')
            # Switch back to Pose Mode as it was before this block,
            # in case subsequent operations within this prep_type=='E' expect it.
            # However, there are no further operations in this specific 'E' block after this.
            bpy.ops.object.mode_set(mode='POSE')

        if ue_triangulate_mesh:
            c.kklog('Triangulating meshes for Unreal Engine...')
            # Assumes armature is active and in POSE mode from the end of the scaling block or bone setup.

            # Switch to OBJECT mode for modifier operations
            if bpy.context.object.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            meshes_to_triangulate = []
            for child_obj in armature.children:
                if child_obj.type == 'MESH':
                    meshes_to_triangulate.append(child_obj)

            if meshes_to_triangulate:
                original_active = bpy.context.view_layer.objects.active
                bpy.ops.object.select_all(action='DESELECT')
                for mesh_obj in meshes_to_triangulate:
                    mesh_obj.select_set(True)
                    bpy.context.view_layer.objects.active = mesh_obj

                    c.kklog(f"Triangulating {mesh_obj.name}...")
                    # Ensure it's in object mode, an individual object might be in edit/pose if previously selected.
                    if bpy.context.object.mode != 'OBJECT':
                        bpy.ops.object.mode_set(mode='OBJECT')

                    bpy.ops.object.modifier_add(type='TRIANGULATE')
                    try:
                        # By default, new modifier is named "Triangulate". If localized, this might differ.
                        # It's safer to get the modifier by its type if possible, or use its default name.
                        # For this script, "Triangulate" is likely fine.
                        bpy.ops.object.modifier_apply(modifier="Triangulate")
                    except RuntimeError as e:
                        c.kklog(f"Could not apply Triangulate modifier to {mesh_obj.name}. Error: {e}", type='warn')

                # Restore original active object if it was among those processed or set armature active
                if original_active in meshes_to_triangulate or original_active == armature : # Check if original active was a mesh or the armature
                     bpy.context.view_layer.objects.active = original_active
                else: # Fallback to armature
                    bpy.context.view_layer.objects.active = armature

            c.kklog('Mesh triangulation complete.')

            # Restore armature to active and set POSE mode, consistent with previous block's end state
            bpy.ops.object.select_all(action='DESELECT')
            armature.select_set(True)
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.mode_set(mode='POSE')

    #If simplifying the bones...
    if simp_type in ['A', 'B']:
        #show all bones on the armature
        bpy.ops.armature.collection_show_all()
        bpy.ops.pose.select_all(action='DESELECT')

        #Move pupil bones to layer 1
        armature = bpy.data.objects[armature_name]
        if armature.data.bones.get('Left Eye'):
            armature.data.bones['Left Eye'].collections.clear()
            armature.data.collections['0'].assign(armature.data.bones.get('Left Eye'))
            armature.data.bones['Right Eye'].collections.clear()
            armature.data.collections['0'].assign(armature.data.bones.get('Right Eye'))
        
        #Select bones on layer 11
        for bone in armature.data.bones:
            if bone.collections.get('10'):
                bone.select = True
        
        #if very simple selected, also get 3-5,12,17-19
        if simp_type in ['A']:
            for bone in armature.data.bones:
                select_bool = (bone.collections.get('2')  or 
                               bone.collections.get('3')  or 
                               bone.collections.get('4')  or 
                               bone.collections.get('11') or 
                               bone.collections.get('12') or 
                               bone.collections.get('16') or 
                               bone.collections.get('17') or 
                               bone.collections.get('18')
                               )
                if select_bool:
                    bone.select = True
        
        c.kklog('Using the merge weights function in CATS to simplify bones...')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.kkbp.cats_merge_weights()

    #If exporting for VRM or VRC...
    if prep_type in ['A', 'D']:
        c.kklog('Editing armature for VRM...')
        bpy.context.view_layer.objects.active=armature
        bpy.ops.object.mode_set(mode='EDIT')

        #Rearrange bones to match CATS output 
        if armature.data.edit_bones.get('Pelvis'):
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
        armature = bpy.data.objects[armature_name]
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

    #only disable the prep button if the non-atlas model has been modified.
    #This is because the model with atlas can be regenerated with the bake materials button
    return armature_name == 'Armature'

class export_prep(bpy.types.Operator):
    bl_idname = "kkbp.exportprep"
    bl_label = "Prep for target application"
    bl_description = t('export_prep_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene.kkbp
        prep_type = scene.prep_dropdown
        simp_type = scene.simp_dropdown
        ue_apply_scale = scene.ue_apply_scale
        ue_triangulate_mesh = scene.ue_triangulate_mesh # Retrieve ue_triangulate_mesh
        last_step = time.time()
        try:
            c.toggle_console()
            if main(prep_type, simp_type, ue_apply_scale, ue_triangulate_mesh): # Pass ue_triangulate_mesh to main
                scene.plugin_state = 'prepped'
            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            c.toggle_console()
            return {'FINISHED'}
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
    
