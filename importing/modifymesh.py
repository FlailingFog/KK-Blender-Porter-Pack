'''
This file performs the following operations

.   Separates the rigged tongue, hair, shift/hang state clothing,
        hitboxes, and puts them into their own collections
·	Delete mask material, shadowcast mesh, and bonelyfans mesh if present

·	Remove shapekeys on all objects except body / tears / gag eyes
·	Rename UV maps on body object and outfit objects
·	Translates all shapekey names to english
·	Combines shapekeys based on face part prefix and emotion suffix
·	Creates tear shapekeys
·	Creates gag eye shapekeys and drivers for shapekeys

.   Removes doubles on body object to prevent seams (if selected)

·	Mark certain body materials as freestyle faces for freestyle exclusion
'''

import bpy
from .. import common as c
from ..extras.linkshapekeys import link_keys

class modify_mesh(bpy.types.Operator):
    bl_idname = "kkbp.modifymesh"
    bl_label = bl_idname
    bl_description = bl_idname
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            self.rename_uv_maps()

            self.separate_rigged_tongue()
            self.separate_hair()
            self.separate_alternate_clothing()
            self.delete_shad_bone()
            self.separate_hitboxes()
            self.delete_mask_quad()

            self.remove_unused_shapekeys()
            self.translate_shapekeys()
            self.combine_shapekeys()
            self.create_tear_shapekeys()
            self.create_gag_eye_shapekeys()

            self.remove_body_seams()
            self.mark_body_freestyle_faces()
            c.clean_orphaned_data()

            return {'FINISHED'}
        except Exception as error:
            c.handle_error(self, error)
            return {"CANCELLED"}

    # %% Main functions
    def separate_rigged_tongue(self):
        """
        Separates the rigged tongue object from the main body mesh.
        If no rigged tongue, create one if general tongue exists
        """

        rigged_tongue_material = None
        general_tongue_material = None
        tongue_datas = c.json_file_manager.get_material_info_by_smr('o_tang')

        if tongue_datas is None:
            c.kklog('No tongue', 'warn')
            c.print_timer('Skipped')
            # A way to fix is to prepare a tongue as prefab.The tongue is copied from other converted kk model, keeping original vertex weight info
            # When missing tongue, add it to file.As each skeleton structure have little difference, it should work well
            return

        for item in tongue_datas:
            if item['SMRPath'].endswith('N_cf_haed/o_tang'):
                general_tongue_material = item['MaterialInformation'][0]['MaterialName']
            else:
                rigged_tongue_material = item['MaterialInformation'][0]['MaterialName']

        if rigged_tongue_material == general_tongue_material:
            rigged_tongue_material += '.001'

        #  if rigged tongue not exist,
        #  rename tongue material to .001, duplicate tongue material and rename to general name, separate mesh by .001,
        #  duplicate tongue mesh as general tongue and join back to body
        if rigged_tongue_material is None or general_tongue_material is None:
            if general_tongue_material:
                base_name = general_tongue_material

            else:
                base_name = rigged_tongue_material
                general_tongue_material = base_name
            rigged_tongue_material = base_name + '.001'

            ori_material = bpy.data.materials[general_tongue_material]


            # rename former material to .001, so we do not need to change the faces' s material to new one
            ori_material['name'] = rigged_tongue_material
            ori_material['id'] = rigged_tongue_material
            ori_material.name = rigged_tongue_material

            new_material = ori_material.copy()

            new_material['name'] = general_tongue_material
            new_material['id'] = general_tongue_material
            new_material.name = general_tongue_material

            tongue = self.separate_materials(c.get_body(), [rigged_tongue_material], 'Tongue (rigged) ' + c.get_name())

            c.get_body().data.materials.append(new_material)

            # copy the tongue mesh and join it back to body
            bpy.ops.object.mode_set(mode='OBJECT')
            tongue_copy = tongue.copy()
            tongue_copy.data = tongue.data.copy()
            bpy.context.collection.objects.link(tongue_copy)
            bpy.ops.object.select_all(action='DESELECT')
            tongue_copy.select_set(True)
            c.get_body().select_set(True)
            bpy.context.view_layer.objects.active = c.get_body()
            bpy.ops.object.join()

            tongue['tongue'] = True

            # tongue.modifiers.clear()
            # for vg in list(tongue.vertex_groups):
            #     tongue.vertex_groups.remove(vg)
        else:
            tongue = self.separate_materials(c.get_body(), [rigged_tongue_material], 'Tongue (rigged) ' + c.get_name())
            tongue['tongue'] = True

        # Now remap the rigged tongue material with the original to allow the rigged tongue and the tongue on the body to share the same material
        if bpy.data.materials.get(rigged_tongue_material):
            bpy.data.materials[rigged_tongue_material].user_remap(
                bpy.data.materials[general_tongue_material])
            bpy.data.materials.remove(bpy.data.materials[rigged_tongue_material])
        c.print_timer('separate_rigged_tongue')

    def separate_hair(self):
        '''Separates the hair from the clothes object'''
        outfits = c.get_outfits()

        #Separate the hair from each outfit
        # material_data = c.json_file_manager.get_json_file('KK_MaterialDataComplete.json')
        material_data = c.json_file_manager.get_materials_info()
        hair_materials = [
            material['MaterialName']
            for obj in material_data.values()
            for sub_obj in obj
            for material in sub_obj['MaterialInformation']
            if material['isHair']
        ]
        for outfit in outfits:
            #find all the hair mats for this outfit
            cur_hair_mat_list = []
            outfit_materials = [mat_slot.material.name for mat_slot in outfit.material_slots]

            for material in hair_materials:
            # some hair materials are repeated. The order goes 'hair_material', 'hair_material 00', 'hair_material 01', etc. Check for those too.
                cur_hair_mat_list.extend([m for m in outfit_materials if material in m])

            if cur_hair_mat_list:
                hair_object = self.separate_materials(outfit, cur_hair_mat_list, 'Hair ' + outfit.name)
                hair_object['hair'] = True
                hair_object['outfit'] = False
        c.print_timer('separate_hair')

    def separate_alternate_clothing(self):
        '''Separates the alternate clothing pieces then hides them'''

        #These are the enum indexes that need to be separated
        clothes_labels = {
            999:            'Indoor shoes',
            93:             'Top shift',
            97:             'Top shift',
            112:            'Top shift',
            114:            'Top shift',
            116:            'Top shift',
            120:            'Top shift',
            95:             'Bottom shift',
            99:             'Bottom shift',
            101:            'Bra shift',
            118:            'Bra shift',
            107:            'Underwear shift',
            108:            'Underwear hang',
            110:            'Pantyhose shift',
        }

        material_data = c.json_file_manager.get_materials_info()
        for outfit in c.get_outfits():
            for label in clothes_labels:
                materials_to_separate = []
                for smr_name, smr_items in material_data.items():
                    for smr_item in smr_items:
                        if label == smr_item['EnumIndex']:
                            materials_to_separate.extend(c.get_material_names(smr_name))

                if materials_to_separate:
                    alt_clothes = self.separate_materials(outfit, materials_to_separate, clothes_labels[label] + ' ' + outfit['id'] + ' ' + c.get_name())
                    if alt_clothes:
                        alt_clothes['alt'] = True
                        alt_clothes['outfit'] = False
                        c.kklog('Separated {} alternate clothing {} automatically'.format(materials_to_separate, clothes_labels[label]))
        c.print_timer('separate_alternate_clothing')

    def delete_shad_bone(self):
        '''Delete the shadowcast and bonelyfans meshes, if present'''
        mat_list = ['c_m_shadowcast', 'Standard']
        shadowcast = self.separate_materials(c.get_body(), mat_list, 'shadowcast', search_type = 'fuzzy')
        if shadowcast:
            bpy.data.objects.remove(shadowcast)

        #Delete the bonelyfans mesh if any
        # mat_list = ['Bonelyfans', 'Bonelyfans.001']
        mat_list = c.get_material_names('Highlight_o_body_a_rend')
        mat_list.extend(c.get_material_names('Highlight_cf_O_face_rend'))
        mat_list = list(set(mat_list))
        extended = []
        for mat in mat_list:
            index = 1
            while bpy.data.materials.get((name := f'{mat}.{index:03d}')):
                index += 1
                extended.append(name)

        mat_list.extend(extended)
        bonely = self.separate_materials(c.get_body(), mat_list, 'bonelyfans')
        if bonely:
            bpy.data.objects.remove(bonely)
        c.print_timer('delete_shad_bone')

    def separate_hitboxes(self):
        '''Separate the hitbox mesh, if present'''
        material_data = c.json_file_manager.get_materials_info()
        hitbox_names = []
        for smr_name, smr_infos in material_data.items():
            if smr_name.startswith('o_hit'):
                hitbox_names.extend([
                    item['MaterialName']
                    for smr_info in smr_infos
                    for item in smr_info['MaterialInformation']
                ])

        hitbox_names = list(set(hitbox_names))
        # first remap all of the duplicate hitbox materials to share the same material name, or some separations will be missed
        for hitbox_name in hitbox_names:
            index = 1
            while bpy.data.materials.get((hitbox := f'{hitbox_name}.{index:03d}')):
                bpy.data.materials[hitbox].user_remap(bpy.data.materials[hitbox_name])
                bpy.data.materials.remove(bpy.data.materials[hitbox])
                index += 1
        hitbox = self.separate_materials(c.get_body(), hitbox_names, 'Hitboxes Body ' + c.get_name())
        if hitbox:
            hitbox['hitbox'] = True
            hitbox['body'] = False
        for outfit in c.get_outfits():
            hitbox = self.separate_materials(outfit, hitbox_names, 'Hitboxes ' + outfit['id'] + ' ' + c.get_name())
            if hitbox:
                hitbox['hitbox'] = True
                hitbox['outfit'] = False
        c.move_and_hide_collection(c.get_hitboxes(), "Hitboxes " + c.get_name())
        c.print_timer('separate_hitboxes')

    def delete_mask_quad(self):
        '''delete the mask material if not in smr mode'''
        material_names = []
        material_data = c.json_file_manager.get_materials_info()
        for smr_name, smr_infos in material_data.items():
            if smr_name.startswith('o_Mask'):
                material_names.extend([
                    item['MaterialName']
                    for smr_info in smr_infos
                    for item in smr_info['MaterialInformation']
                    if item['ShaderName'] == "Shader Forge/AlphaMaskMultiply"
                ])
        material_names = set(material_names)

        for outfit in c.get_outfits():
            for mat in outfit.material_slots:
                if mat.name in material_names:
                    self.delete_materials(outfit, [mat])
        c.print_timer('delete_mask_quad')

    def remove_unused_shapekeys(self):
        '''remove shapekeys on all hair and clothes objects'''
        if bpy.context.scene.kkbp.shapekeys_dropdown not in ['A', 'B']:
            return
        object_list = c.get_outfits()
        object_list.extend(c.get_alts())
        object_list.extend(c.get_hairs())
        object_list.extend(c.get_hitboxes())
        object_list = [o for o in object_list if o.data.shape_keys]
        for obj in object_list:
            for key in obj.data.shape_keys.key_blocks.keys():
                obj.shape_key_remove(obj.data.shape_keys.key_blocks[key])
        c.print_timer('remove_unused_shapekeys')

    def rename_uv_maps(self):
        #Make UV map names clearer
        c.get_body().data.uv_layers[0].name = 'uv_main'
        c.get_body().data.uv_layers[1].name = 'uv_nipple_and_shine'
        c.get_body().data.uv_layers[2].name = 'uv_underhair'
        c.get_body().data.uv_layers[3].name = 'uv_eyeshadow'

        for outfit in c.get_outfits():
            outfit.data.uv_layers[0].name = 'uv_main'
            outfit.data.uv_layers[1].name = 'uv_nipple_and_shine'
            outfit.data.uv_layers[2].name = 'uv_underhair'
            outfit.data.uv_layers[3].name = 'uv_eyeshadow'
        c.print_timer('rename_uv_maps')

    def translate_shapekeys(self):
        '''Renames the face shapekeys to english'''
        if not bpy.context.scene.kkbp.shapekeys_dropdown in ['A', 'B']:
            return
        translation_dict = {
            #Prefixes
            "eye_face.f00":         "Eyes",
            "kuti_face.f00":        "Lips",
            "eye_siroL.sL00":       "EyeWhitesL",
            "eye_siroR.sR00":       "EyeWhitesR",
            "eye_line_u.elu00":     "Eyelashes1",
            "eye_line_l.ell00":     "Eyelashes2",
            "eye_naM.naM00":        "EyelashesPos",
            "eye_nose.nl00":        "NoseTop",
            "kuti_nose.nl00":       "NoseBot",
            "kuti_ha.ha00":         "Teeth",
            "kuti_yaeba.y00":       "Fangs",
            "kuti_sita.t00":        "Tongue",
            "mayuge.mayu00":        "KK Eyebrows",
            "eye_naL.naL00":        "Tear_big",
            "eye_naM.naM00":        "Tear_med",
            "eye_naS.naS00":        "Tear_small",

            #Prefixes (Yelan headmod exception)
            "namida_l":             "Tear_big",
            "namida_m":             "Tear_med",
            "namida_s":             "Tear_small",
            'tang.':                'Tongue',

            #Emotions (eyes and mouth)
            "_def_":                "_default_",
            "_egao_":               "_smile_",
            "_bisyou_":             "_smile_sharp_",
            "_uresi_ss_":           "_happy_slight_",
            "_uresi_s_":            "_happy_moderate_",
            "_uresi_":              "_happy_broad_",
            "_doki_ss_":            "_doki_slight_",
            "_doki_s_":             "_doki_moderate_",
            "_ikari_":              "_angry_",
            "_ikari02_":            "_angry_2_",
            "_sinken_":             "_serious_",
            "_sinken02_":           "_serious_1_",
            "_sinken03_":           "_serious_2_",
            "_keno_":               "_hate_",
            "_sabisi_":             "_lonely_",
            "_aseri_":              "_impatient_",
            "_huan_":               "_displeased_",
            "_human_":              "_displeased_",
            "_akire_":              "_amazed_",
            "_odoro_":              "_shocked_",
            "_odoro_s_":            "_shocked_moderate_",
            "_doya_":               "_smug_",
            "_pero_":               "_lick_",
            "_name_":               "_eating_",
            "_tabe_":               "_eating_2_",
            "_kuwae_":              "_hold_in_mouth_",
            "_kisu_":               "_kiss_",
            "_name02_":             "_tongue_out_",
            "_mogu_":               "_chewing_",
            "_niko_":               "_cartoon_mouth_",
            "_san_":                "_triangle_",

            #Emotions (Eyes)
            "_winkl_":              "_wink_left_",
            "_winkr_":              "_wink_right_",
            "_setunai_":            "_distress_",
            "_tere_":               "_shy_",
            "_tmara_":              "_bored_",
            "_tumara_":             "_bored_",
            "_kurusi_":             "_pain_",
            "_sian_":               "_thinking_",
            "_kanasi_":             "_sad_",
            "_naki_":               "_crying_",
            "_rakutan_":            "_dejected_",
            "_komaru_":             "_worried_",
            "_gag":                 "_gageye",
            "_gyul_":               "_squeeze_left_",
            "_gyur_":               "_squeeze_right_",
            "_gyu_":                "_squeeze_",
            "_gyul02_":             "_squeeze_left_2_",
            "_gyur02_":             "_squeeze_right_2_",
            "_gyu02_":              "_squeeze_2_",

        #Emotions (Eyebrows)
            "_koma_":               "_worried_",
            "_gimoL_":              "_doubt_left_",
            "_gimoR_":              "_doubt_right_",
            "_sianL_":              "_thinking_left_",
            "_sianR_":              "_thinking_right_",
            "_oko_":                "_angry_",
            "_oko2L_":              "_angry_left_",
            "_oko2R_":              "_angry_right_",

        #Emotions extra
            "_s_":                  "_small_",
            "_l_":                  "_big_",

            #Emotions Yelan headmod exception
            'T_Default':            '_default_op',
        }

        c.get_body().active_shape_key_index = 0

        originalExists = False
        for shapekey in bpy.data.shape_keys:
            for keyblock in shapekey.key_blocks:
                #check if the original shapekeys still exists
                if 'Basis' not in keyblock.name:
                    if 'Lips' in keyblock.name:
                        originalExists = True

        #rename original shapekeys
        for shapekey in bpy.data.shape_keys:
            for keyblock in shapekey.key_blocks:
                for key in translation_dict:
                    if 'gageye' not in keyblock.name:
                        keyblock.name = keyblock.name.replace(key, translation_dict[key])
                try:
                    #delete the KK shapekeys if the original shapekeys still exist
                    if originalExists and 'KK ' in keyblock.name and 'KK Eyebrows' not in keyblock.name:
                        c.get_body().active_shape_key_index = c.get_body().data.shape_keys.key_blocks.keys().index(keyblock.name)
                        bpy.ops.object.shape_key_remove() #only way to do this is with ops?
                except:
                    #or not
                    c.kklog("Couldn't delete shapekey: " + keyblock.name, 'error')
                    pass
        c.print_timer('translate_shapekeys')

    def combine_shapekeys(self):
        '''Creates new, full shapekeys using the existing partial shapekeys, and deletes the partial shapekeys if user didn't elect to keep them in the panel'''
        if not bpy.context.scene.kkbp.shapekeys_dropdown in ['A', 'B']:
            return

        #make the basis shapekey active
        c.switch(c.get_body(), 'object')
        c.get_body().active_shape_key_index = 0

        def whatCat(keyName):
            #Eyelashes1 is used because I couldn't see a difference between the other one and they overlap if both are used
            #EyelashPos is unused because Eyelashes work better and it overlaps with Eyelashes
            eyes = [keyName.find("Eyes"),
            keyName.find("NoseT"),
            keyName.find("Eyelashes1"),
            keyName.find("EyeWhites"),
            keyName.find('Tear_big'),
            keyName.find('Tear_med'),
            keyName.find('Tear_small')]
            if not all(v == -1 for v in eyes):
                return 'Eyes'
            mouth = [keyName.find("NoseB"),
            keyName.find("Lips"),
            keyName.find("Tongue"),
            keyName.find("Teeth"),
            keyName.find("Fangs")]
            if not all(v==-1 for v in mouth):
                return 'Mouth'
            return 'None'

        #setup two arrays to keep track of the shapekeys that have been used
        #and the shapekeys currently in use
        used = []
        inUse = []
        #These mouth shapekeys require the default teeth and tongue shapekeys to be active
        correctionList = ['_u_small_op', '_u_big_op', '_e_big_op', '_o_small_op', '_o_big_op', '_neko_op', '_triangle_op']
        shapekey_block = bpy.data.shape_keys[c.get_body().data.shape_keys.name].key_blocks

        ACTIVE = 0.9
        def activate_shapekey(key_act):
            if shapekey_block.get(key_act) != None:
                shapekey_block[key_act].value = ACTIVE
        #go through the keyblock list twice
        #Do eye shapekeys first then mouth shapekeys
        for type in ['Eyes_', 'Lips_']:
            counter = len(shapekey_block)
            for current_keyblock in shapekey_block:
                counter = counter - 1
                if (counter == 0):
                    break
                #categorize the shapekey (eye or mouth)
                cat = whatCat(current_keyblock.name)
                #get the emotion from the shapekey name
                if (cat != 'None') and ('KK' not in current_keyblock.name) and (type in current_keyblock.name):
                    emotion = current_keyblock.name[current_keyblock.name.find("_"):]
                    #go through every shapekey to check if any match the current shapekey's emotion
                    for supporting_shapekey in shapekey_block:
                        #If the's emotion matches the current one and is the correct category...
                        if emotion in supporting_shapekey.name and cat == whatCat(supporting_shapekey.name):
                            #and this key has hasn't been used yet activate it, else skip to the next
                            if (supporting_shapekey.name not in used):
                                supporting_shapekey.value = ACTIVE
                                inUse.append(supporting_shapekey.name)
                    #The shapekeys for the current emotion are now all active
                    #Some need manual corrections
                    correction_needed = False
                    for cor in correctionList:
                        if cor in current_keyblock.name:
                            correction_needed = True
                    if correction_needed:
                        activate_shapekey('Fangs_default_op')
                        activate_shapekey('Teeth_default_op')
                        activate_shapekey('Tongue_default_op')
                    if ('_e_small_op' in current_keyblock.name):
                        activate_shapekey('Fangs_default_op')
                        activate_shapekey('Lips_e_small_op')
                    if ('_cartoon_mouth_op' in current_keyblock.name):
                        activate_shapekey('Tongue_default_op')
                        activate_shapekey('Lips_cartoon_mouth_op')
                    if ('_smile_sharp_op' in current_keyblock.name and cat == 'Mouth'):
                        if shapekey_block.get('Teeth_smile_sharp_op1') != None:
                            shapekey_block['Teeth_smile_sharp_op1'].value = 0
                        activate_shapekey('Lips_smile_sharp_op')
                    if ('_eating_2_op' in current_keyblock.name):
                        activate_shapekey('Fangs_default_op')
                        activate_shapekey('Teeth_tongue_out_op')
                        activate_shapekey('Tongue_serious_2_op')
                        activate_shapekey('Lips_eating_2_op')
                    if ('_i_big_op' in current_keyblock.name):
                        activate_shapekey('Teeth_i_big_cl')
                        activate_shapekey('Fangs_default_op')
                        activate_shapekey('Lips_i_big_op')
                    if ('_i_small_op' in current_keyblock.name):
                        activate_shapekey('Teeth_i_small_cl')
                        activate_shapekey('Fangs_default_op')
                        activate_shapekey('Lips_i_small_op')
                    if (current_keyblock.name not in used):
                        c.get_body().shape_key_add(name=('KK ' + cat + emotion))
                    #make sure this shapekey set isn't used again
                    used.extend(inUse)
                    inUse =[]
                    #reset all shapekey values
                    for reset_keyblock in shapekey_block:
                        reset_keyblock.value = 0
                #lazy crash prevention
                if counter % 20 == 0:
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        #Delete all shapekeys that don't have a "KK" in their name
        #Don't delete the Basis shapekey though
        #If no KK shapekeys were generated, something went wrong so don't delete any shapekeys
        keep_partial_shapekeys = bpy.context.scene.kkbp.shapekeys_dropdown == 'B'
        it_worked = True if [key for key in shapekey_block if 'KK ' in key.name] else False
        if it_worked and not keep_partial_shapekeys:
            for remove_shapekey in shapekey_block:
                try:
                    if ('KK ' not in remove_shapekey.name and remove_shapekey.name != shapekey_block[0].name):
                        c.get_body().shape_key_remove(remove_shapekey)
                except:
                    c.kklog('Couldn\'t remove shapekey ' + remove_shapekey.name, 'error')
                    pass
        else:
            c.kklog('Original shapekeys were not deleted', 'warn')
        #make the basis shapekey active
        c.get_body().active_shape_key_index = 0
        #and reset the pivot point to median
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        c.print_timer('combine_shapekeys')

    def create_tear_shapekeys(self):
        '''Separate tears from body and create tear shapekeys'''
        if bpy.context.scene.kkbp.shapekeys_dropdown not in ['A', 'B']:
            return
        # check if the tear material even exists
        try:
            tear_material_name = c.get_material_names('cf_O_namida_L')[0]
        except:
            c.kklog('Tear material did not exist.', 'warn')
            return
        # Create a reverse shapekey for each tear material
        c.switch(c.get_body(), 'edit')
        # Move tears and gag backwards on the basis shapekey
        # use head mesh as reference location
        face_material = c.get_material_names('cf_O_face')
        if face_material:
            bpy.context.object.active_material_index = c.get_body().data.materials.find(face_material[0])
        bpy.ops.object.material_slot_select()
        # refresh selection, then get head location
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        selected_verts = [v.co.y for v in c.get_body().data.vertices if v.select]
        loc = 0
        for y in selected_verts:
            loc += y
        middle_of_head = loc / len(selected_verts)
        c.switch(c.get_body(), 'edit')
        tear_mats = {
            'cf_O_namida_L': ("Tears big", []),
            'cf_O_namida_M': ("Tears med", []),
            'cf_O_namida_S': ('Tears small', []),
            'cf_O_gag_eye_00': ("Gag eye 00", []),
            'cf_O_gag_eye_01': ("Gag eye 01", []),
            'cf_O_gag_eye_02': ("Gag eye 02", []),
        }
        for cat, cat_data in tear_mats.items():
            mats = c.get_material_names(cat)
            if (m_flag := ('M' in cat)) or 'S' in cat:
                mats = [m + ('.001' if m_flag else '.002') for m in
                        mats]  # tears share a material name, so add a .001
            for mat in mats:
                bpy.context.object.active_material_index = c.get_body().data.materials.find(mat)
                bpy.ops.object.material_slot_select()
            cat_data[1].extend(mats)

        # refresh selection, then move tears a random amount backwards
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        selected_verts = [v for v in c.get_body().data.vertices if v.select]
        amount_to_move_tears_back = 2 * (selected_verts[0].co.y - middle_of_head)
        bpy.ops.transform.translate(value=(0, abs(amount_to_move_tears_back), 0))

        # move the tears forwards again the same amount in individual new shapekeys
        for cat, cat_data in tear_mats.items():
            for mat in cat_data[1]:
                c.switch(c.get_body(), 'object')
                bpy.ops.object.shape_key_add(from_mix=False)
                c.get_body().data.shape_keys.key_blocks[-1].name = cat_data[0]
                # c.get_body().data.shape_keys.key_blocks[-1].name = tear_mats[cat]
                last_shapekey = len(c.get_body().data.shape_keys.key_blocks) - 1
                bpy.context.object.active_shape_key_index = last_shapekey
                c.switch(c.get_body(), 'edit')
                bpy.context.object.active_material_index = c.get_body().data.materials.find(mat)
                if c.get_body().data.materials.find(mat) == -1:
                    bpy.context.object.active_material_index += 1
                else:
                    bpy.context.object.active_material_index = c.get_body().data.materials.find(mat)
                bpy.ops.object.material_slot_select()
                # find a random vertex location of the tear and move it forwards
                c.switch(c.get_body(), 'object')
                selected_verts = [v for v in c.get_body().data.vertices if v.select]  # Why?
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.transform.translate(value=(0, -1 * abs(amount_to_move_tears_back), 0))
                c.switch(c.get_body(), 'object')
                bpy.ops.object.shape_key_move(type='TOP' if tear_material_name in mat else 'BOTTOM')

        # Move the Eye, eyewhite and eyeline materials back on the KK gageye shapekey
        bpy.context.object.active_shape_key_index = bpy.context.object.data.shape_keys.key_blocks.find('KK Eyes_gageye')
        c.switch(c.get_body(), 'edit')
        for cat in [
            'cf_Ohitomi_L',
            'cf_Ohitomi_R',
            'cf_Ohitomi_L02',
            'cf_Ohitomi_R02',
            'cf_O_eyeline',
            'cf_O_eyeline_low']:
            mats = c.get_material_names(cat)
            # also append the duplicated eyewhite material
            mats.append('cf_m_sirome_00.001')
            for mat in mats:
                bpy.context.object.active_material_index = c.get_body().data.materials.find(mat)
                bpy.ops.object.material_slot_select()
        # find a random vertex location of the eye and move it backwards
        c.switch(c.get_body(), 'object')
        selected_verts = [v for v in c.get_body().data.vertices if v.select]  # Why ?
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.translate(value=(0, 2.5 * abs(amount_to_move_tears_back), 0))
        c.switch(c.get_body(), 'object')

        # Merge the tear materials
        c.switch(c.get_body(), 'edit')

        to_merge_materials = tear_mats['cf_O_namida_L'][1]
        to_merge_materials.extend(tear_mats['cf_O_namida_M'][1])
        to_merge_materials.extend(tear_mats['cf_O_namida_S'][1])

        for mat in to_merge_materials:
            bpy.context.object.active_material_index = c.get_body().data.materials.find(mat)
            bpy.ops.object.material_slot_select()
            bpy.context.object.active_material_index = c.get_body().data.materials.find(tear_material_name)
            bpy.ops.object.material_slot_assign()
            bpy.ops.mesh.select_all(action='DESELECT')

        # make a vertex group that does not contain the tears
        bpy.ops.object.vertex_group_add()
        bpy.ops.mesh.select_all(action='SELECT')
        c.get_body().vertex_groups.active.name = "Body without Tears"
        bpy.context.object.active_material_index = c.get_body().data.materials.find(tear_material_name)
        bpy.ops.object.material_slot_deselect()
        bpy.context.object.active_material_index = c.get_body().data.materials.find(tear_material_name + '.001')
        bpy.ops.object.material_slot_deselect()
        bpy.context.object.active_material_index = c.get_body().data.materials.find(tear_material_name + '.002')
        bpy.ops.object.material_slot_deselect()
        bpy.ops.object.vertex_group_assign()

        # Separate tears from body object
        # link shapekeys of tears to body
        tears = self.separate_materials(c.get_body(), to_merge_materials, 'Tears ' + c.get_name())
        tears['tears'] = True
        bpy.ops.object.mode_set(mode='OBJECT')
        link_keys(c.get_body(), [tears])
        c.print_timer('create_tear_shapekeys')

    def create_gag_eye_shapekeys(self):
        '''Separate gag eyes from body and create gag eye shapekeys'''
        if bpy.context.scene.kkbp.shapekeys_dropdown not in ['A', 'B'] or len(c.get_material_names('cf_O_gag_eye_00')) == 0:
            return
        bpy.context.view_layer.objects.active=c.get_body()
        gag_keys = [
            'Circle Eyes 1',
            'Circle Eyes 2',
            'Spiral Eyes',
            'Heart Eyes',
            'Fiery Eyes',
            'Cartoony Wink',
            'Vertical Line',
            'Cartoony Closed',
            'Horizontal Line',
            'Cartoony Crying'
        ]
        for key in gag_keys:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.shape_key_add(from_mix=False)
            last_shapekey = len(c.get_body().data.shape_keys.key_blocks)-1
            c.get_body().data.shape_keys.key_blocks[-1].name = key
            bpy.context.object.active_shape_key_index = last_shapekey
            bpy.ops.object.shape_key_move(type='TOP')

        def create_gag_eye_driver(keyblock: str, condition: str):
            '''creates a gag eye driver'''
            skey_driver = bpy.data.shape_keys[0].key_blocks[keyblock].driver_add('value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = c.get_body().data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value'
            skey_driver.driver.expression = condition

        bpy.context.object.active_shape_key_index = 0
        #make most gag eye shapekeys activate the body's gag key if the KK gageeye shapekey was created
        if bpy.data.shape_keys[0].key_blocks.get('KK Eyes_gageye'):
            condition = [key.replace(' ', '') for key in gag_keys if 'Fiery' not in key]
            create_gag_eye_driver('KK Eyes_gageye', '1 if ' + ' or '.join(condition) + ' else 0' )
            create_gag_eye_driver('Gag eye 00', '1 if CircleEyes1 or CircleEyes2 or VerticalLine or CartoonyClosed or HorizontalLine else 0' )
            create_gag_eye_driver('Gag eye 01', '1 if HeartEyes or SpiralEyes else 0' )
            create_gag_eye_driver('Gag eye 02', '1 if FieryEyes or CartoonyWink or CartoonyCrying else 0' )

            #make a vertex group that does not contain the gag_eyes
            bpy.ops.object.vertex_group_add()
            c.switch(c.get_body(), 'edit')
            bpy.ops.mesh.select_all(action='SELECT')
            c.get_body().vertex_groups.active.name = "Body without Gag eyes"

            gag_eye_materials = []

            gag_eye_data = c.json_file_manager.get_material_info_by_smr('cf_O_gag_eye_00')
            gag_eye_materials.extend([
                item['MaterialName']
                for smr_info in gag_eye_data
                for item in smr_info['MaterialInformation']
            ])

            gag_eye_data = c.json_file_manager.get_material_info_by_smr('cf_O_gag_eye_01')
            gag_eye_materials.extend([
                item['MaterialName']
                for smr_info in gag_eye_data
                for item in smr_info['MaterialInformation']
            ])

            gag_eye_data = c.json_file_manager.get_material_info_by_smr('cf_O_gag_eye_02')
            gag_eye_materials.extend([
                item['MaterialName']
                for smr_info in gag_eye_data
                for item in smr_info['MaterialInformation']
            ])

            gag_eye_materials = list(set(gag_eye_materials))

            for material_name in gag_eye_materials:
                bpy.context.object.active_material_index = c.get_body().data.materials.find(material_name)
                bpy.ops.object.material_slot_deselect()

            bpy.ops.object.vertex_group_assign()

            # Separate gag from body object
            # link shapekeys of gag to body
            if gag_eye_materials:
                gag_eye = self.separate_materials(c.get_body(), gag_eye_materials, 'Gag Eyes ' + c.get_name())
                gag_eye['gag'] = True
                gag_eye['body'] = False
                c.switch(c.get_body(), 'object')
                link_keys(c.get_body(), [gag_eye])

            c.print_timer('create gag_eye_shapekeys')
            return
        c.print_timer('ignored gag_eye_shapekeys')

    def remove_body_seams(self):
        '''merge certain materials for the body object to prevent odd shading issues later on'''
        if not bpy.context.scene.kkbp.fix_seams:
            return
        c.switch(c.get_body(), 'edit')
        mats = c.get_material_names('cf_O_face')
        mats.extend(c.get_material_names('o_body_a'))

        bpy.context.tool_settings.mesh_select_mode = (True, False, False) #enable vertex select in edit mode
        for mat in mats:
            bpy.context.object.active_material_index = c.get_body().data.materials.find(mat)
            bpy.ops.object.material_slot_select()
        bpy.ops.mesh.remove_doubles(threshold=0.00001)

        # This operation still messes with the weights.
        # Maybe it's possible to save the 3D positions, weights, and UV positions for each duplicate vertex
        # then delete and make new vertices with saved info 
        # The vertices on the body object seem to be consistent across imports according to https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/82
        c.print_timer('remove_body_seams')

    def mark_body_freestyle_faces(self):
        c.switch(c.get_body(), 'edit')
        #mark certain materials as freestyle faces
        def mark_as_freestyle(mat_list: bpy.types.Material):
            for mat in mat_list:
                mat_found = c.get_body().data.materials.find(mat)
                if mat_found > -1:
                    bpy.context.object.active_material_index = mat_found
                    bpy.ops.object.material_slot_select()
                else:
                    c.kklog('Material wasn\'t found when freestyling body materials: ' + mat, 'warn')
            bpy.ops.mesh.mark_freestyle_face(clear=False)
        freestyle_list = [
        'cf_Ohitomi_L02',
        'cf_Ohitomi_R02',
        'cf_Ohitomi_L',
        'cf_Ohitomi_R',
        'cf_O_eyeline_low',
        'cf_O_eyeline',
        'cf_O_noseline',
        'cf_O_mayuge',]
        mats = []
        for mat in freestyle_list:
            mats.extend(c.get_material_names(mat))
        mark_as_freestyle(mats)
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        c.print_timer('mark_body_freestyle_faces')


    def separate_materials(self, object: bpy.types.Object, mat_list: list[bpy.types.Material], new_object_name: str, search_type = 'exact') -> bpy.types.Object:
        '''Separates the materials in the mat_list on object, and renames the separated object to "new_object_name". 
        Returns the separated object, or None if there was an error'''
        c.switch(object, 'edit')
        for mat in mat_list:
            mat_found = -1
            if search_type == 'fuzzy' and ('cm_m_' in mat or 'c_m_' in mat or 'o_hit_' in mat or mat == 'cf_O_face_atari_M'):
                for matindex in range(0, len(object.data.materials), 1):
                    if mat in object.data.materials[matindex].name:
                        mat_found = matindex
            else:
                mat_found = object.data.materials.find(mat)
            if mat_found > -1:
                bpy.context.object.active_material_index = mat_found
                #moves the materials in a specific order to prevent transparency issues on body
                def moveUp():
                    return bpy.ops.object.material_slot_move(direction='UP')
                while moveUp() != {"CANCELLED"}:
                    pass
                bpy.ops.object.material_slot_select()
            else:
                c.kklog('Material wasn\'t found when separating materials: ' + mat, 'warn')
        try:
            bpy.ops.mesh.separate(type='SELECTED')
            new_object = bpy.context.selected_objects[1]
            new_object.name = new_object_name
            return new_object
        except:
            c.kklog('Nothing was selected when separating materials from: ' + object.name, 'warn')
            bpy.ops.object.mode_set(mode = 'OBJECT')
            return None

    def delete_materials(self, object: bpy.types.Object, mat_list: bpy.types.Material):
        '''Deletes the materials in mat_list from object'''
        for mat in mat_list:
            if object.data.materials.find(mat.name) > -1:
                c.switch(object, 'edit')
                bpy.context.object.active_material_index = object.data.materials.find(mat.name)
                bpy.ops.object.material_slot_select()
                bpy.ops.mesh.delete(type='VERT')


