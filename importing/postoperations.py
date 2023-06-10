'''
This file performs the following operations

·	Hide all alternate clothing pieces and indoor shoes and other outfits
    (show only the first outfit if it's present, if not, count up until the
    first outfit collection is found and use that one)

.   (Rigify) Applies Rigify conversion script
.   (Cycles) Applies Cycles conversion script
.   (LBS) Applies LBS conversion script
.   (SFW) Runs SFW cleanup script

·	Clean orphaned data as long as users = 0 and fake user = False
.   Sets viewport shading to material
'''

import bpy, traceback
from .. import common as c

class post_operations(bpy.types.Operator):
    bl_idname = "kkbp.postoperations"
    bl_label = bl_idname
    bl_description = bl_idname
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            self.retreive_stored_tags()
            self.hide_unused_objects()

            self.apply_cycles()
            self.apply_lbs()
            self.apply_rigify()
            self.apply_sfw()
            
            c.clean_orphaned_data()
            c.set_viewport_shading('MATERIAL')

            return {'FINISHED'}
        except Exception as error:
            c.handle_error(self, error)
            return {"CANCELLED"}

    # %% Main functions
    def retreive_stored_tags(self):
        '''Gets the tag from each object to repopulate the class variables below'''
        self.hairs = []
        self.outfits = []
        self.outfit_alternates = []
        self.hitboxes = []
        for object in [o for o in bpy.data.objects if o.type == 'MESH']:
            if object['KKBP tag'] == 'body':
                self.body = object
            elif object['KKBP tag'] == 'outfit':
                self.outfits.append(object)
            elif object['KKBP tag'] == 'alt':
                self.outfit_alternates.append(object)
            elif object['KKBP tag'] == 'hair':
                self.hairs.append(object)
            elif object['KKBP tag'] == 'hitbox':
                self.hitboxes.append(object)
        for object in [o for o in bpy.data.objects if o.type == 'ARMATURE']:
            if object['KKBP tag'] == 'armature':
                self.armature = object
    
    def hide_unused_objects(self):
        bpy.data.objects['Armature'].hide = False
        #hide all outfits except the first found
        outfit = None
        if bpy.data.objects.get('Outfit 00'):
            outfit = bpy.data.objects.get('Outfit 00')
        else:
            #check the other outfit numbers and return the first one found
            for ob in bpy.data.objects:
                if ob.get('KKBP outfit ID') and ob in self.outfits:
                    outfit = ob
                    break
        if outfit:
            outfit.hide = False
            for child in outfit.children:
                child.hide = False
        for type in [self.outfits, self.outfit_alternates]:
            for clothes_object in type:
                if clothes_object != ob:
                    clothes_object.hide = True
                    for child in clothes_object:
                        child.hide = True
        #hide rigged tongue and all clothes alts
        if bpy.data.objects.get('Tongue (Rigged)'):
            bpy.data.objects['Tongue (Rigged)'].hide = True
        for object in self.outfit_alternates:
            object.hide = True

    def apply_cycles(self):
        if not bpy.context.scene.kkbp.shader_dropdown == 'B':
            return
        c.kklog('\nConverting to Rigify...')
        c.import_from_library_file('NodeTree', ['Raw Shading (face)', 'Cycles', 'Cycles no shadows', 'LBS', 'LBS face normals'], bpy.context.scene.kkbp.use_material_fake_user)

        c.kklog('Applying Cycles adjustments...')
        #taken from https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/234
        #remove outline modifier
        for o in bpy.context.view_layer.objects:
            for m in o.modifiers:
                if(m.name == "Outline Modifier"):
                    m.show_viewport = False
                    m.show_render = False
                    
        ####fix the eyelash mesh overlap
        # deselect everything and make body active object
        body = bpy.data.objects['Body']
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
        #delete nose if no texture loaded in
        if not bpy.data.node_groups['Nose'].nodes[1].image:
            object.active_material_index = 2
            obj.material_slot_select()
            mesh.delete(type='VERT')
        mesh.select_all(action='DESELECT')

        #add cycles node group
        for tree in [mat.node_tree for mat in bpy.data.materials if 'KK ' in mat.name]:
            nodes = tree.nodes
            links = tree.links
            if nodes.get('Rim') and nodes.get('Shader'):
                nodes['Rim'].node_tree = bpy.data.node_groups['Cycles']
                links.new(nodes['Shader'].outputs['Color out light'], nodes['Rim'].inputs[0])
                links.new(nodes['Shader'].outputs['Color out dark'], nodes['Rim'].inputs[1])
                links.new(nodes['Shader'].outputs[3], nodes['Rim'].inputs[2])
            #disable detail shine color too
            if nodes.get('Shader'):
                if nodes['Shader'].node_tree.nodes.get('colorsLight'):
                    if nodes['Shader'].node_tree.nodes['colorsLight'].inputs.get('Detail intensity (shine)'):
                        nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Detail intensity (shine)'].default_value = 0
                        nodes['Shader'].node_tree.nodes['colorsDark']. inputs['Detail intensity (shine)'].default_value = 0
        #remove linemask and blush on face material
        for type in ['colorsLight', 'colorsDark']:
            bpy.data.node_groups['Face Shader'].nodes[type].inputs['Linemask intensity'].default_value = 0
            bpy.data.node_groups['Face Shader'].nodes[type].inputs['Blush intensity'].default_value = 0
        #set eyeline up and eyebrows as shadowless
        for mat in [bpy.data.materials['KK Eyebrows (mayuge)'], bpy.data.materials['KK Eyeline up']]:
            mat.node_tree.nodes['Rim'].node_tree = bpy.data.node_groups['Cycles no shadows']
        
        #put face's color out in a mix shader with the cycles face mask
        #mute shader to rgb nodes for clothing items
        for node in [n for n in bpy.data.node_groups['General overlays'].nodes if 'Shader to RGB' in n.name]:
            node.mute = True

        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.preview_samples = 10
        mesh.select_all(action='DESELECT')
        obj.mode_set(mode='OBJECT')

    def apply_lbs(self):
        if not bpy.context.scene.kkbp.shader_dropdown == 'C':
            return
        c.import_from_library_file('NodeTree', ['Raw Shading (face)', 'Cycles', 'Cycles no shadows', 'LBS', 'LBS face normals'], bpy.context.scene.kkbp.use_material_fake_user)

        c.kklog('Applying Lightning Boy Shader adjustments...')
        #Import lbs node group and replace rim group with the lbs group
        keep_list = ['KK Eyebrows (mayuge)', 'KK EyeL (hitomi)', 'KK EyeR (hitomi)', 'KK Eyeline up']
        for tree in [mat.node_tree for mat in bpy.data.materials if ('KK ' in mat.name and mat.name not in keep_list)]:
            nodes = tree.nodes
            links = tree.links
            if nodes.get('Rim') and nodes.get('Shader'):
                nodes['Rim'].node_tree = bpy.data.node_groups['LBS']
                links.new(nodes['Shader'].outputs['Color out light'], nodes['Rim'].inputs['Color light'])
                links.new(nodes['Shader'].outputs['Color out dark'], nodes['Rim'].inputs['Color dark'])
                links.new(nodes['Shader'].outputs[3], nodes['Rim'].inputs[2])
                #if nodes['Shader'].node_tree.name != 'Body Shader':
                #    links.new(nodes['RawShade'].outputs['Normal passthrough'], nodes['Rim'].inputs[3])
        #construct LBS node group from scratch because it can't be included with the KK shader
        nodes = bpy.data.node_groups['LBS'].nodes
        links = bpy.data.node_groups['LBS'].links
        try:
            LBS = nodes.new('LBSShaderNode')
        except:
            #stop if Lightning Boy Shader is not installed
            c.kklog("An error occured when adding a Lightning Boy Shader node. Make sure it's installed. Skipping operation...", 'error')
            return
        def expand(node):
            node.hide = False
            for sock in node.inputs:
                sock.hide = False
        LBS.initialize_group = ".Lightning Boy Shader"
        LBS.inputs['.transparency'].default_value = 0.001
        LBS.inputs['.transparency'].enabled = False
        LBS.inputs[0].enabled = False
        LBS.layers = 4
        LBS.location = 444.6600, 61.8538
        expand(LBS)
        output = [out for out in nodes if out.type == 'GROUP_OUTPUT'][0]
        output.location = 694.6600, -10.6462
        input =  [out for out in nodes if out.type == 'GROUP_INPUT'][0]
        input.location = -538.7341, 24.3778
        reroute_alpha = nodes.new('NodeReroute')
        reroute_alpha.location = 121.4401, -429.1375
        links.new(input.outputs[2], reroute_alpha.inputs[0])
        links.new(reroute_alpha.outputs[0], LBS.inputs[-3]) #connect alpha through reroute
        reroute_dark = nodes.new('NodeReroute')
        reroute_dark.location = 121.4401, -398.1375
        links.new(input.outputs[1], reroute_dark.inputs[0])
        links.new(reroute_dark.outputs[0], LBS.inputs[-4]) #connect dark
        links.new(LBS.outputs[0], output.inputs[0]) #connect LBS out

        key = nodes.new('LBSBaseNode')
        key.initialize_group = '.Key Light*'
        key.location = 49.4401, -144.1374
        expand(key)
        links.new(input.outputs['Color light'], key.inputs[0])
        links.new(input.outputs['Normal'], key.inputs[5])
        links.new(key.outputs[0], LBS.inputs[-5]) #connect light

        ao = nodes.new('LBSBaseNode')
        ao.initialize_group = '.Ambient Occlusion (SS)'
        ao.location = 49.4401, 109.8626
        expand(ao)
        links.new(input.outputs['Color dark'], ao.inputs[0])
        links.new(ao.outputs[0], LBS.inputs[-6]) #connect light

        rim = nodes.new('LBSBaseNode')
        rim.initialize_group = '.2D Rim Light*'
        rim.location = 49.4401, 423.8625
        expand(rim)
        curves = [out for out in nodes if out.type == 'CURVE_RGB'][0]
        curves.location = -215.5599, 289.3625
        links.new(input.outputs['Color light'], curves.inputs[0])
        links.new(curves.outputs[0], rim.inputs[0])
        links.new(rim.outputs[0], LBS.inputs[-7]) #connect 2d rim

        #turn on ambient occlusion and bloom in render settings
        bpy.context.scene.eevee.use_gtao = True

        #turn on bloom in render settings
        bpy.context.scene.eevee.use_bloom = True

        #face has special normal setup to work with gfn. make a copy and add the normals inside of the copy
        #this group prevents Amb Occ issues around nose, and mouth interior
        face_nodes = bpy.data.node_groups['LBS'].copy()
        face_nodes.use_fake_user = True
        face_nodes.name = 'LBS (Face)'
        nodes = bpy.data.node_groups['LBS (Face)'].nodes
        links = bpy.data.node_groups['LBS (Face)'].links
        face_norms = nodes.new('ShaderNodeGroup')
        face_norms.node_tree = bpy.data.node_groups['LBS face normals']
        face_norms.location = 410, 190
        links.new(face_norms.outputs[0], rim.inputs[-1])
        links.new(face_norms.outputs[0], key.inputs[-1])

        #select entire face and body and reset vectors to prevent Amb Occ seam around the neck 
        body = bpy.data.objects['Body']
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active=body
        bpy.ops.object.mode_set(mode = 'EDIT')
        body.active_material_index = 1
        bpy.ops.object.material_slot_select()
        bpy.ops.mesh.normals_tools(mode='RESET')
        bpy.ops.object.mode_set(mode = 'OBJECT')
    
    def apply_rigify(self):
        if not bpy.context.scene.kkbp.armature_dropdown == 'B':
            return
        c.switch(self.armature, 'object')
        try:
            bpy.ops.kkbp.rigbefore('INVOKE_DEFAULT')
        except:
            if 'Calling operator "bpy.ops.pose.rigify_layer_init" error, could not be found' in traceback.format_exc():
                c.kklog("There was an issue preparing the rigify metarig. \nMake sure the Rigify addon is installed and enabled. Skipping operation...", 'error')
            c.kklog(traceback.format_exc())
            return
        
        bpy.ops.pose.rigify_generate()
        bpy.ops.kkbp.rigafter('INVOKE_DEFAULT')
        #make sure the new bones on the generated rig retain the KKBP outfit id entry
        rig = bpy.context.active_object
        for bone in rig.data.bones:
            if bone.layers[0] == True or bone.layers[2] == True:
                if rig.data.bones.get('ORG-' + bone.name):
                    if rig.data.bones['ORG-' + bone.name].get('KKBP outfit ID'):
                        bone['KKBP outfit ID'] = rig.data.bones['ORG-' + bone.name]['KKBP outfit ID']
                        if rig.data.bones.get('DEF-' + bone.name):
                            rig.data.bones['DEF-' + bone.name]['KKBP outfit ID'] = rig.data.bones['ORG-' + bone.name]['KKBP outfit ID']

        #make sure the gfn empty is reparented to the head bone
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = rig
        empty = bpy.data.objects['GFN Empty']
        empty.hide = False
        empty.select_set(True)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        rig.data.bones['head'].select = True
        rig.data.bones.active = rig.data.bones['head']
        bpy.ops.object.parent_set(type='BONE')
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.node_groups['Generated Face Normals'].nodes['GFNEmpty'].object = empty
        bpy.context.view_layer.objects.active = empty
        empty.select_set(True)
        bpy.ops.object.move_to_collection(collection_index=1)
        empty.hide = True
        empty.hide_render = True

        self.armature.hide_set(True)
        bpy.ops.object.select_all(action='DESELECT')

        #make sure everything is deselected in edit mode for the body
        body = bpy.data.objects['Body']
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
        self.rig = rig
        return {'FINISHED'}

    def apply_sfw(self):
        if not bpy.context.scene.kkbp.sfw_mode:
            return
        #delete nsfw parts of the mesh
        body = bpy.data.objects['Body']
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active=body
        bpy.ops.object.mode_set(mode = 'EDIT')
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

        def delete_group_and_bone(group_list):
            #delete vertex groups
            bpy.ops.mesh.select_all(action = 'DESELECT')
            for group in group_list:
                group_found = body.vertex_groups.find(group)      
                if group_found > -1:
                    bpy.context.object.vertex_groups.active_index = group_found
                    bpy.ops.object.vertex_group_select()
                else:
                    c.kklog('Group wasn\'t found when deleting vertex groups: ' + group, 'warn')
            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')

        delete_list = ['cf_s_bnip025_L', 'cf_s_bnip025_R',
        'cf_j_kokan', 'cf_j_ana', 'cf_d_ana', 'cf_d_kokan', 'cf_s_ana',
        'Vagina_Root', 'Vagina_B', 'Vagina_F', 'Vagina_001_L', 'Vagina_002_L',
        'Vagina_003_L', 'Vagina_004_L', 'Vagina_005_L',  'Vagina_001_R', 'Vagina_002_R',
        'Vagina_003_R', 'Vagina_004_R', 'Vagina_005_R']
        delete_group_and_bone(delete_list)

        #reload the sfw alpha mask
        body_material = bpy.data.objects['Body'].material_slots['KK Body'].material
        body_material.node_tree.nodes['Gentex'].node_tree.nodes['Bodyalphacustom'].image = bpy.data.images['Template: SFW alpha mask.png']
        bpy.data.node_groups["Body Shader"].nodes["BodyTransp"].inputs[0].default_value = 1 #why do i have to do it this way
        bpy.data.node_groups["Body Shader"].nodes["BodyTransp"].inputs[1].default_value = 1
        body_material.node_tree.nodes['Shader'].node_tree.nodes['BodyTransp'].node_tree.inputs[0].hide_value = True
        body_material.node_tree.nodes['Shader'].node_tree.nodes['BodyTransp'].node_tree.inputs[1].hide_value = True

        #get rid of the nsfw groups on the body
        body_material.node_tree.nodes.remove(body_material.node_tree.nodes['NSFWTextures'])
        body_material.node_tree.nodes.remove(body_material.node_tree.nodes['NSFWpos'])

        body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Nipple mask'])
        body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Nipple alpha'])
        body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Genital mask'])
        body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Underhair mask'])

        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital intensity'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital saturation'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital hue'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Underhair color'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Underhair intensity'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple base'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple base 2'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple shine'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple rim'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple alpha'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple texture'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital mask'])
        body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Underhair mask'])

        bpy.data.materials['KK Body'].node_tree.nodes['Gentex'].node_tree.nodes['Bodyalphacustom'].image = bpy.data.images['Template: SFW alpha mask.png']
        bpy.data.materials['KK Body Outline'].node_tree.nodes['customToggle'].inputs[0].default_value = 1
        bpy.data.materials['KK Body Outline'].node_tree.nodes['customToggle'].inputs[0].hide = True

        #delete nsfw bones if sfw mode enebled
        if bpy.context.scene.kkbp.sfw_mode and bpy.context.scene.kkbp.shader_dropdown == 'B':
            def delete_bone(group_list):
                #delete bones too
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                self.rig.select_set(True)
                bpy.context.view_layer.objects.active = rig
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.armature.select_all(action='DESELECT')
                for bone in group_list:
                    if self.rig.data.bones.get(bone):
                        self.rig.data.edit_bones[bone].select = True
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

    # %% Supporting functions

if __name__ == "__main__":
    bpy.utils.register_class(post_operations)

    # test call
    print((bpy.ops.kkbp.postoperations('INVOKE_DEFAULT')))
