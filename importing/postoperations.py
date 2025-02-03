
# This file performs the following operations

# 	Hide all clothes except the first outfit (alts are always hidden)

#   (Cycles) Applies Cycles conversion script
#   (Eevee Mod) Applies Eevee Mod conversion script
#   (Rigify) Applies Rigify conversion script
#   (SFW) Runs SFW cleanup script

# 	Clean orphaned data as long as users = 0 and fake user = False

# Parts of cycles replacement was taken from https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/234


import bpy, traceback
from .. import common as c

class post_operations(bpy.types.Operator):
    bl_idname = "kkbp.postoperations"
    bl_label = bl_idname
    bl_description = bl_idname
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            self.hide_unused_objects()

            self.apply_cycles()
            self.apply_eeveemod()
            self.apply_rigify()
            self.apply_sfw()
            
            c.clean_orphaned_data()
            c.set_viewport_shading('SOLID')

            return {'FINISHED'}
        except Exception as error:
            c.handle_error(self, error)
            return {"CANCELLED"}

    # %% Main functions    
    def hide_unused_objects(self):
        """
        Hides unused objects in the Blender scene based on certain conditions.

        This method performs the following operations:
        1. Ensures the armature is not hidden.
        2. If the 'categorize_dropdown' property in the scene is not set to 'A', it exits early.
        3. Hides all outfits except the one with the lowest ID.
        4. Moves eyegags and tears into their own collection.
        5. Always hides the rigged tongue if present.
        6. Always hides the Bone Widgets collection.
        """
        c.get_armature().hide_set(False)
        #don't hide any outfits if not automatically categorizing
        if not bpy.context.scene.kkbp.categorize_dropdown in ['A']:
            return
        #hide all outfits except the first one
        clothes_and_hair = c.get_outfits()
        clothes_and_hair.extend(c.get_hairs())
        outfit_ids = (int(c['id']) for c in c.get_outfits() if c.get('id'))
        outfit_ids = list(set(outfit_ids))
        for id in outfit_ids:
            clothes_in_this_id = [c for c in clothes_and_hair if c.get('id') == str(id).zfill(2)]
            c.move_and_hide_collection(clothes_in_this_id, 'Outfit ' + str(id).zfill(2) + ' ' + c.get_name(), hide = (id != min(outfit_ids)))

        #put any clothes variations into their own collection
        outfit_ids = (int(c['id']) for c in c.get_alts() if c.get('id'))
        outfit_ids = list(set(outfit_ids))
        for index, id in enumerate(outfit_ids):
            clothes_in_this_id = [c for c in c.get_alts() if c.get('id') == str(id).zfill(2)]
            c.switch(clothes_in_this_id[0], 'OBJECT')
            #find the character index
            character_collection_index = len(bpy.context.view_layer.layer_collection.children)-1
            #find the index of the outfit collection
            for i, child in enumerate(bpy.context.view_layer.layer_collection.children[character_collection_index].children):
                if child.name == 'Outfit ' + str(id).zfill(2) + ' ' + c.get_name():
                    break
            for ob in clothes_in_this_id:
                ob.select_set(True)
                bpy.context.view_layer.objects.active=ob
            new_collection_name = 'Alts ' + str(id).zfill(2) + ' ' + c.get_name()
            #extremely confusing move to under the clothes collection. Index is the outfit index + outfit collection index (starts at 1) + Scene collection (1) +  + character collection index (usually 0) + 1
            bpy.ops.object.move_to_collection(collection_index = (index+i) + 1 + (character_collection_index + 1), is_new = True, new_collection_name = new_collection_name)
            #then hide the alts
            child.children[0].exclude = True

        #put the eyegags and tears into their own collection
        face_objects = []
        if c.get_gags():
            face_objects.append(c.get_gags())
        if c.get_tears():
            face_objects.append(c.get_tears())
        if face_objects:
            c.move_and_hide_collection(face_objects, 'Tears and gag eyes ' + c.get_name(), hide = False)

        #always hide the rigged tongue if present
        if c.get_tongue():
            c.move_and_hide_collection([c.get_tongue()], 'Rigged tongue ' + c.get_name(), hide = True)
        
        #always hide the hitboxes collection
        if bpy.data.collections.get('Hitboxes ' + c.get_name()):
            c.switch(c.get_armature(), 'OBJECT')
            for child in bpy.context.view_layer.layer_collection.children[0].children:
                if ('Hitboxes ' + c.get_name()) in child.name:
                    child.exclude = True

        #always hide the bone widgets collection
        if bpy.data.collections.get('Bone Widgets'):
            c.switch(c.get_armature(), 'OBJECT')
            for child in bpy.context.view_layer.layer_collection.children[0].children:
                if child.name == 'Bone Widgets':
                    child.exclude = True

    def apply_cycles(self):
        if not bpy.context.scene.kkbp.shader_dropdown in ['B', 'D']:
            return
        c.kklog('Applying Cycles adjustments...')
        c.import_from_library_file('NodeTree', ['.Cycles', '.Cycles no shadows', '.Cycles Classic'], bpy.context.scene.kkbp.use_material_fake_user)
        c.import_from_library_file('Image', ['Template: Black'], bpy.context.scene.kkbp.use_material_fake_user)

        #remove outline modifier
        for o in bpy.context.view_layer.objects:
            for m in o.modifiers:
                if(m.name == "Outline Modifier"):
                    m.show_viewport = False
                    m.show_render = False
                    
        ####fix the eyelash mesh overlap
        # deselect everything and make body active object
        body = c.get_body()
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active=body
        bpy.ops.object.mode_set(mode = 'EDIT')
        # define some stuff
        ops = bpy.ops
        obj = ops.object
        mesh = ops.mesh
        context = bpy.context
        object = context.object
        # edit mode and deselect everything
        obj.mode_set(mode='EDIT')
        mesh.select_all(action='DESELECT')
        # delete eyeline down verts and kage faces
        object.active_material_index = 6
        obj.material_slot_select()
        mesh.delete(type='VERT')
        object.active_material_index = 5
        obj.material_slot_select()
        mesh.delete(type='ONLY_FACE')
        mesh.select_all(action='DESELECT')

        ignore_list = [
            'KK Eyebrows (mayuge) ' + c.get_name(),
            'KK EyeL (hitomi) ' + c.get_name(),
            'KK EyeR (hitomi) ' + c.get_name(),
            'KK Eyeline up ' + c.get_name(),
            'KK Eyewhites (sirome) ' + c.get_name()]
        everything = [c.get_body()]
        everything.extend(c.get_hairs())
        everything.extend(c.get_alts())
        everything.extend(c.get_outfits())

        #add cycles node group
        for object in everything:
            for node_tree in [mat_slot.material.node_tree for mat_slot in object.material_slots if mat_slot.material.get('bake') and mat_slot.material.name not in ignore_list]:
                nodes = node_tree.nodes
                links = node_tree.links
                if nodes.get('combine'):
                    nodes['combine'].node_tree = bpy.data.node_groups['.Cycles' if bpy.context.scene.kkbp.shader_dropdown == 'B' else '.Cycles Classic']
                    #setup the node links again because they break when you replace the node group
                    def relink(outnode, outport, innode, inport):
                        try:
                            links.new(nodes[outnode].outputs[outport], nodes[innode].inputs[inport])
                        except:
                            c.kklog(f'Could not link these nodes on tree: {node_tree.name} | {outnode}:{outport} to {innode}:{inport}')
                    relink('combine',   0,                      'out',     0)
                    relink('light',     0,                      'combine', 'Light colors')
                    relink('dark',      0,                      'combine', 'Dark colors')
                    relink('textures', 'Main texture (alpha)',  'combine', 'Main texture (alpha)')
                    relink('textures', 'Alpha mask',            'combine', 'Alpha mask')
                    relink('textures', 'Alpha mask (alpha)',    'combine', 'Alpha mask (alpha)')
                    relink('textures', 'Alpha mask (custom)',   'combine', 'Alpha mask (custom)')

                    #Cycles makes missing images PINK (?!) instead of black for some reason and this screws with the shaders
                    #If an image is missing, fill it in with Template: Black
                    if nodes.get('textures'):
                        for image_node in [n for n in nodes['textures'].node_tree.nodes if n.type == 'TEX_IMAGE']:
                            if not image_node.image:
                                image_node.image = bpy.data.images['Template: Black']

                    #disable detail shine color too
                    if nodes.get('light'):
                        if nodes['light'].inputs.get('Detail intensity (shine)'):
                            nodes['light'].inputs['Detail intensity (shine)'].default_value = 0

                    if nodes.get('dark'):
                        if nodes['dark'].inputs.get('Detail intensity (shine)'):
                            nodes['dark'].inputs['Detail intensity (shine)'].default_value = 0
        
        #remove linemask and blush on face material
        if c.get_body():
            face_material = [m.material for m in c.get_body().material_slots if 'KK Face' in m.material.name]
            if face_material:
                face_material[0].node_tree.nodes['light'].inputs['Linemask intensity'].default_value = 0
                face_material[0].node_tree.nodes['dark'].inputs['Linemask intensity'].default_value = 0
                face_material[0].node_tree.nodes['light'].inputs['Blush intensity'].default_value = 0
                face_material[0].node_tree.nodes['dark'].inputs['Blush intensity'].default_value = 0

        #set eyeline up and eyebrows as shadowless
        shadowless_mats =      [m.material for m in c.get_body().material_slots if 'KK Eyeline up'          in m.material.name]
        shadowless_mats.extend([m.material for m in c.get_body().material_slots if 'KK Eyebrows (mayuge)'   in m.material.name])
        for mat in shadowless_mats:
            mat.node_tree.nodes['combine'].node_tree = bpy.data.node_groups['.Cycles no shadows']
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            def relink(outnode, outport, innode, inport):
                try:
                    links.new(nodes[outnode].outputs[outport], nodes[innode].inputs[inport])
                except:
                    c.kklog(f'Could not link these nodes on tree: {node_tree.name} | {outnode}:{outport} to {innode}:{inport}')
            relink('combine',   0,                      'out',     0)
            relink('light',     0,                      'combine', 'Light colors')
            relink('dark',      0,                      'combine', 'Dark colors')
            relink('textures', 'Main texture (alpha)',  'combine', 'Main texture (alpha)')
            relink('textures', 'Alpha mask',            'combine', 'Alpha mask')
            relink('textures', 'Alpha mask (alpha)',    'combine', 'Alpha mask (alpha)')
            relink('textures', 'Alpha mask (custom)',   'combine', 'Alpha mask (custom)')
        
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.preview_samples = 10
        mesh.select_all(action='DESELECT')
        obj.mode_set(mode='OBJECT')

    def apply_eeveemod(self):
        if not bpy.context.scene.kkbp.shader_dropdown == 'C':
            return
        c.import_from_library_file('NodeTree', ['.Eevee Mod', '.Eevee Mod (face)'], bpy.context.scene.kkbp.use_material_fake_user)

        c.kklog('Applying Eevee Shader adjustments...')
        #Import eevee mod node group and replace the combine colors group with the eevee mod group
        ignore_list = [
            'KK Eyebrows (mayuge) ' + c.get_name(),
            'KK EyeL (hitomi) ' + c.get_name(),
            'KK EyeR (hitomi) ' + c.get_name(),
            'KK Eyeline up ' + c.get_name(),
            'KK Eyewhites (sirome) ' + c.get_name()]
        everything = [c.get_body()]
        everything.extend(c.get_hairs())
        everything.extend(c.get_alts())
        everything.extend(c.get_outfits())
        
        for object in everything:
            for node_tree in [mat_slot.material.node_tree for mat_slot in object.material_slots if mat_slot.material.get('bake') and mat_slot.material.name not in ignore_list]:
                nodes = node_tree.nodes
                links = node_tree.links
                if nodes.get('combine'):
                    nodes['combine'].node_tree = bpy.data.node_groups['.Eevee Mod']
                    #setup the node links again because they break when you replace the node group
                    def relink(outnode, outport, innode, inport):
                        try:
                            links.new(nodes[outnode].outputs[outport], nodes[innode].inputs[inport])
                        except:
                            c.kklog(f'Could not link these nodes on tree: {node_tree.name} | {outnode}:{outport} to {innode}:{inport}')
                    relink('combine',   0,                      'out',     0)
                    relink('light',     0,                      'combine', 'Light colors')
                    relink('dark',      0,                      'combine', 'Dark colors')
                    relink('textures', 'Main texture (alpha)',  'combine', 'Main texture (alpha)')
                    relink('textures', 'Alpha mask',            'combine', 'Alpha mask')
                    relink('textures', 'Alpha mask (alpha)',    'combine', 'Alpha mask (alpha)')
                    relink('textures', 'Alpha mask (custom)',   'combine', 'Alpha mask (custom)')

        if bpy.app.version[0] == 3:
            #turn on ambient occlusion and bloom in render settings
            bpy.context.scene.eevee.use_gtao = True

            #turn on bloom in render settings
            bpy.context.scene.eevee.use_bloom = True

            #face has special normal setup. make a copy and add the normals inside of the copy
            #this group prevents Amb Occ issues around nose, and mouth interior
            face_nodes = bpy.data.node_groups['.Eevee Mod (face)']
            face_nodes.use_fake_user = True

        #select entire face and body, then reset vectors to prevent Amb Occ seam around the neck 
        body = c.get_body()
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active=body
        bpy.ops.object.mode_set(mode = 'EDIT')
        body.active_material_index = 1
        bpy.ops.object.material_slot_select()
        bpy.ops.mesh.normals_tools(mode='RESET')
        bpy.ops.object.mode_set(mode = 'OBJECT')
    
    @classmethod
    def apply_rigify(cls):
        self = cls
        #correct some bone layering errors. I don't feel like tracking these down, so do it here before the rigify script
        layer0_bones = [
            'MasterFootIK.L',
            'MasterFootIK.R',
            'Eyesx',
            'cf_pv_root_upper',
            'cf_pv_elbo_R',
            'cf_pv_elbo_L',
            'cf_pv_knee_L',
            'cf_pv_knee_R',
            'cf_pv_hand_L',
            'cf_pv_hand_R',
        ]
        layer1_bones = [
            'Left toe',
            'Right toe',
            'cf_pv_foot_L',
            'FootPin.L',
            'ToePin.L',
            'cf_pv_foot_R',
            'FootPin.R',
            'ToePin.R',
        ]
        armature = c.get_armature()
        def set_armature_layer(bone_name, show_layer, hidden = False):
            '''Assigns a bone to a bone collection.'''
            bone = armature.data.bones.get(bone_name)
            if bone:
                if bpy.app.version[0] == 3:
                    armature.data.bones[bone_name].layers = (
                        True, False, False, False, False, False, False, False,
                        False, False, False, False, False, False, False, False, 
                        False, False, False, False, False, False, False, False, 
                        False, False, False, False, False, False, False, False
                    )
                    #have to show the bone on both layer 1 and chosen layer before setting it to just chosen layer
                    armature.data.bones[bone_name].layers[show_layer] = True 
                    armature.data.bones[bone_name].layers[0] = False
                    armature.data.bones[bone_name].hide = hidden
                else:
                    show_layer = str(show_layer)
                    bone.collections.clear()
                    if armature.data.bones.get(bone_name):
                        if armature.data.collections.get(show_layer):
                            armature.data.collections[show_layer].assign(armature.data.bones.get(bone_name))
                        else:
                            armature.data.collections.new(show_layer)
                            armature.data.collections[show_layer].assign(armature.data.bones.get(bone_name))
                        armature.data.bones[bone_name].hide = hidden
        
        c.switch(armature, 'OBJECT')
        for bone in layer0_bones:
            set_armature_layer(bone, 0)
        for bone in layer1_bones:
            set_armature_layer(bone, 1)
        
        if not bpy.context.scene.kkbp.armature_dropdown == 'B':
            return
        c.kklog('Running Rigify conversion scripts...')
        c.switch(armature, 'object')
        try:
            bpy.ops.kkbp.rigbefore('INVOKE_DEFAULT')
            #remove the left ankle and right ankle's super copy prop
            if bpy.app.version[0] != 3:
                armature.pose.bones['Left ankle'].rigify_type = ""
                armature.pose.bones['Right ankle'].rigify_type = ""
        except:
            if 'Calling operator "bpy.ops.pose.rigify_layer_init" error, could not be found' in traceback.format_exc():
                c.kklog("There was an issue preparing the rigify metarig. \nMake sure the Rigify addon is installed and enabled. Skipping operation...", 'error')
            c.kklog(traceback.format_exc())
            return
        
        bpy.ops.pose.rigify_generate()

        bpy.ops.kkbp.rigafter('INVOKE_DEFAULT')
        #make sure the new bones on the generated rig retain the KKBP outfit id entry
        rig = bpy.context.active_object
        rig['rig'] = True
        rig['name'] = c.get_name()
        for bone in rig.data.bones:
            if bpy.app.version[0] == 3:
                if bone.layers[0] == True or bone.layers[2] == True:
                    if rig.data.bones.get('ORG-' + bone.name):
                        if rig.data.bones['ORG-' + bone.name].get('KKBP outfit ID'):
                            bone['KKBP outfit ID'] = rig.data.bones['ORG-' + bone.name]['KKBP outfit ID']
                            if rig.data.bones.get('DEF-' + bone.name):
                                rig.data.bones['DEF-' + bone.name]['KKBP outfit ID'] = rig.data.bones['ORG-' + bone.name]['KKBP outfit ID']
            else:
                if bone.collections.get('0') or bone.collections.get('2') == True:
                    if rig.data.bones.get('ORG-' + bone.name):
                        if rig.data.bones['ORG-' + bone.name].get('KKBP outfit ID'):
                            bone['KKBP outfit ID'] = rig.data.bones['ORG-' + bone.name]['KKBP outfit ID']
                            if rig.data.bones.get('DEF-' + bone.name):
                                rig.data.bones['DEF-' + bone.name]['KKBP outfit ID'] = rig.data.bones['ORG-' + bone.name]['KKBP outfit ID']

        armature.hide_set(True)
        bpy.ops.object.select_all(action='DESELECT')

        #make sure everything is deselected in edit mode for the body
        body = c.get_body()
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active=body
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        rig.select_set(True)
        bpy.context.view_layer.objects.active=rig
        rig.show_in_front = True
        bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        bpy.context.tool_settings.mesh_select_mode = (False, False, True) #enable face select in edit mode
        return {'FINISHED'}

    def apply_sfw(self):
        if not bpy.context.scene.kkbp.sfw_mode:
            return
        c.kklog('Applying mesh adjustments...')
        #mark nsfw parts of mesh as freestyle faces so they don't show up in the outline
        body = c.get_body()
        c.switch(body, mode = 'OBJECT')
        def mark_group_as_freestyle(group_list):
            for group in group_list:
                group_found = body.vertex_groups.find(group)      
                if group_found > -1:
                    bpy.context.object.active_material_index = group_found
                    bpy.ops.object.vertex_group_select()
                else:
                    c.kklog('Group wasn\'t found when freestyling vertex groups: ' + group, 'warn')
            bpy.ops.mesh.mark_freestyle_face(clear=False)
        freestyle_list = [
            'cf_j_bnip02_L', 'cf_j_bnip02_R',
            'cf_s_bust03_L', 'cf_s_bust03_R']
        mark_group_as_freestyle(freestyle_list)
        bpy.ops.mesh.select_all(action = 'DESELECT')

        #delete nsfw parts of the mesh
        def delete_group_and_bone(ob, group_list):
            bpy.ops.mesh.select_all(action = 'DESELECT')
            for group in group_list:
                group_found = ob.vertex_groups.find(group)      
                if group_found > -1:
                    bpy.context.object.vertex_groups.active_index = group_found
                    bpy.ops.object.vertex_group_select()
                else:
                    c.kklog('Group wasn\'t found when deleting vertex groups: ' + group, 'warn')
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')

        delete_list = ['cf_s_bnip025_L', 'cf_s_bnip025_R', 'cf_s_bnip02_L', 'cf_s_bnip02_R',
        'cf_j_kokan', 'cf_j_ana', 'cf_d_ana', 'cf_d_kokan', 'cf_s_ana',
        'Vagina_Root', 'Vagina_B', 'Vagina_F', 'Vagina_001_L', 'Vagina_002_L',
        'Vagina_003_L', 'Vagina_004_L', 'Vagina_005_L',  'Vagina_001_R', 'Vagina_002_R',
        'Vagina_003_R', 'Vagina_004_R', 'Vagina_005_R']
        delete_group_and_bone(body, delete_list)
        #also do this on the clothes because the bra can show up
        delete_list = ['cf_s_bnip02_L', 'cf_s_bnip02_R', 'cf_s_bnip025_L', 'cf_s_bnip025_R', ]
        for ob in [o for o in bpy.data.objects if o.get('KKBP tag') == 'outfit']:
            c.switch(ob, 'EDIT')
            delete_group_and_bone(ob, delete_list)

        #force the sfw alpha mask on the body
        for mat_prefix in ['KK Body', 'Outline Body']:
            body_mat = body.material_slots[mat_prefix + ' ' + c.get_name()]
            body_mat.node_tree.nodes["combine"].inputs['Force custom mask'].default_value = 1
            new_group = body_mat.node_tree.nodes['combine'].node_tree.copy()
            body_mat.node_tree.nodes['combine'].node_tree = new_group
            if bpy.app.version[0] == 3:
                new_group.inputs['Force custom mask'].hide_value = True
            else:
                new_group.interface.items_tree['Force custom mask'].hide_value = True

        #get rid of the nsfw groups on the body
        body_mat = body.material_slots['KK Body ' + c.get_name()]
        body_mat.node_tree.nodes.remove(body_mat.node_tree.nodes['NSFWTextures'])
        body_mat.node_tree.nodes.remove(body_mat.node_tree.nodes['NSFWpos'])

        for nono in [
            'Nipple mask',
            'Nipple alpha',
            'Genital mask',
            'Underhair mask',
            'Genital intensity',
            'Genital saturation', 
            'Genital hue', 
            'Underhair color', 
            'Underhair intensity', 
            'Nipple base', 
            'Nipple base 2', 
            'Nipple shine', 
            'Nipple rim', 
            'Nipple alpha', 
            'Nipple texture', 
            'Genital mask', 
            'Underhair mask']:
            if bpy.app.version[0] == 3:
                body_mat.node_tree.nodes['light'].node_tree.inputs.remove(body_mat.node_tree.nodes['light'].node_tree.inputs[nono])
                body_mat.node_tree.nodes['dark' ].node_tree.inputs.remove(body_mat.node_tree.nodes['dark' ].node_tree.inputs[nono])
            else:
                body_mat.node_tree.nodes['light'].node_tree.interface.remove(body_mat.node_tree.nodes['light'].node_tree.interface.items_tree[nono])
                body_mat.node_tree.nodes['dark' ].node_tree.interface.remove(body_mat.node_tree.nodes['dark' ].node_tree.interface.items_tree[nono])

        bpy.data.materials['KK Body Outline'].node_tree.nodes['customToggle'].inputs[0].default_value = 1
        bpy.data.materials['KK Body Outline'].node_tree.nodes['customToggle'].inputs[0].hide = True

        #delete nsfw bones if sfw mode enebled
        rig = c.get_rig()
        if bpy.context.scene.kkbp.sfw_mode and bpy.context.scene.kkbp.armature_dropdown == 'B':
            if bpy.app.version[0] != 3:
                rig.data.collections_all['29'].is_visible = True
            def delete_bone(group_list):
                #delete bones too
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                rig.select_set(True)
                bpy.context.view_layer.objects.active = rig
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.armature.select_all(action='DESELECT')
                for bone in group_list:
                    if rig.data.bones.get(bone):
                        rig.data.edit_bones[bone].select = True
                        bpy.ops.kkbp.cats_merge_weights()
                    else:
                        c.kklog('Bone wasn\'t found when deleting bones: ' + bone, 'warn')
                bpy.ops.armature.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode = 'OBJECT')

            delete_list = ['cf_s_bnip025_L', 'cf_s_bnip025_R',
            'cf_j_kokan', 'cf_j_ana', 'cf_d_ana', 'cf_d_kokan', 'cf_s_ana',
            'cf_J_Vagina_root',
            'cf_J_Vagina_B',
            'cf_J_Vagina_F',
            'cf_J_Vagina_L.005',
            'cf_J_Vagina_R.005',
            'cf_J_Vagina_L.004',
            'cf_J_Vagina_L.001',
            'cf_J_Vagina_L.002',
            'cf_J_Vagina_L.003',
            'cf_J_Vagina_R.001',
            'cf_J_Vagina_R.002',
            'cf_J_Vagina_R.003',
            'cf_J_Vagina_R.004',
            'cf_j_bnip02root_L',
            'cf_j_bnip02_L',
            'cf_s_bnip01_L',
            #'cf_s_bust03_L',
            'cf_s_bust02_L',
            'cf_j_bnip02root_R',
            'cf_j_bnip02_R',
            'cf_s_bnip01_R',
            #'cf_s_bust03_R',
            'cf_s_bust02_R',]
            delete_bone(delete_list)
            if bpy.app.version[0] != 3:
                rig.data.collections_all['29'].is_visible = False
