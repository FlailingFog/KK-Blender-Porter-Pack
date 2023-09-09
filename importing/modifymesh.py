'''
This file performs the following operations

·	Save all body materials to the body object under body['SMR materials']
          to allow mesh separations and material swaps to work
.   Separates the rigged tongue, hair, shift/hang state clothing,
          shadowcast, bonelyfans, hitboxes and puts them into their own collections
·	Delete mask material if present

·	Remove shapekeys on all objects except body / tears / gag eyes
·	Rename UV maps on body object and outfit objects
·	Translates all shapekey names to english
·	Combines shapekeys based on face part prefix and emotion suffix
·	Creates tear shapekeys
·	Creates gag eye shapekeys and drivers for shapekeys

·	Add a data transfer modifier to the body to use the shadowcast as a shading proxy
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
            self.get_body_material_names()
            self.separate_rigged_tongue()
            self.separate_hair()
            self.separate_alternate_clothing()
            self.separate_shad_bone()
            self.separate_hitboxes()
            self.delete_mask_quad()
            
            self.remove_unused_shapekeys()
            self.rename_uv_maps()
            self.translate_shapekeys()
            self.combine_shapekeys()
            self.create_tear_shapekeys()
            self.create_gag_eye_shapekeys()

            self.add_body_datatransfer()
            self.remove_body_seams()
            
            self.mark_body_freestyle_faces()
            self.tag_all_objects_for_next_operation()
            c.clean_orphaned_data()

            return {'FINISHED'}
        except Exception as error:
            c.handle_error(self, error)
            return {"CANCELLED"}

    # %% Main functions
    def get_body_material_names(self):
        '''Correlates the smr object name to the material slot name on the body'''
        self.body = bpy.data.objects['Model_mesh']
        c.switch(self.body, 'object')
        self.body.name = 'Body'

        #save the smr data to the body object as body['SMR materials']
        body_materials = [
            'cf_O_face',
            'cf_O_mayuge',
            'cf_O_noseline',
            'cf_O_tooth',
            'cf_O_eyeline',
            'cf_O_eyeline_low',
            'cf_O_namida_L',
            'cf_O_namida_M',
            'cf_O_namida_S',
            'cf_Ohitomi_L', #eyewhites
            'cf_Ohitomi_R',
            'cf_Ohitomi_L02', #pupils
            'cf_Ohitomi_R02',
            'cf_O_gag_eye_00',
            'cf_O_gag_eye_01',
            'cf_O_gag_eye_02',
            'o_tang',
            'o_body_a',
            'o_tang_rigged'
            ]
        self.body['SMR materials'] = {mat:{} for mat in body_materials}
        #get a list of the body materials from the smr json file then use it to fill the material dictionary on the body object
        smr_data = c.get_json_file('KK_SMRData.json')
        smr_body_materials = [index for index in smr_data if (index['CoordinateType'] == -1 and 'Bonelyfan' not in index['SMRMaterialNames'][0])]
        for body_material in smr_body_materials:
            #if this is the rigged tongue, put it in the right category
            if body_material['SMRPath'] == '/chaF_001/BodyTop/p_cf_body_00/cf_o_root/n_tang/o_tang':
                self.body['SMR materials']['o_tang_rigged'] = [tang_mat + '.001' for tang_mat in body_material['SMRMaterialNames']]
            else:
                self.body['SMR materials'][body_material['SMRName']] = body_material['SMRMaterialNames']
            #rename some materials if in smr mode
            smr_postfix_map = {
                    'cf_Ohitomi_R'  : '.001',
                    'cf_O_namida_M' : '.001',
                    'cf_O_namida_S' : '.002',
                    }
            if (body_material['SMRName'] in smr_postfix_map and 
               (bpy.context.scene.kkbp.categorize_dropdown == 'D' or 'cf_Ohitomi_R' not in body_material['SMRName'])):
                mat_name = body_material['SMRMaterialNames'][0] + smr_postfix_map[body_material['SMRName']]  
                self.body['SMR materials'][body_material['SMRName']] = [mat_name]
        c.print_timer('get_body_material_names')
        
    def separate_rigged_tongue(self):
        '''Separates the rigged tongue object'''
        if bpy.context.scene.kkbp.categorize_dropdown != 'D':
            if self.body['SMR materials']['o_tang_rigged']:
                tongue_mats = [mat for mat in self.body['SMR materials']['o_tang_rigged'] if bpy.data.materials.get(mat)]
                self.separate_materials(self.body, tongue_mats)
                if bpy.data.objects.get('Body.001'):
                    tongue = bpy.data.objects['Body.001']
                    tongue.name = 'Tongue (rigged)'
        c.print_timer('separate_rigged_tongue')

    def separate_hair(self):
        '''Separates the hair from the clothes object'''
        self.outfits = [o for o in bpy.data.objects if '_mesh' in o.name]
        self.hairs = []
        
        #Select all materials that are hair and separate for each outfit
        material_data = c.get_json_file('KK_MaterialData.json')
        # texture_data = c.get_json_file('KK_TextureData.json')
        # texture_files = []
        # for file in texture_data:
        #     texture_files.append(file['textureName'])
        for outfit in self.outfits:
            outfit_materials = [mat_slot.material.name for mat_slot in outfit.material_slots]
            hair_mat_list = []
            for line in material_data:
                # if mat['ShaderName'] in ["Shader Forge/main_hair_front", "Shader Forge/main_hair", 'Koikano/hair_main_sun_front', 'Koikano/hair_main_sun', 'xukmi/HairPlus', 'xukmi/HairFrontPlus']:
                #     if (mat['MaterialName'] + '_HGLS.png') in texture_files or ((mat['MaterialName'] + '_NMP.png') not in texture_files and (mat['MaterialName'] + '_MT_CT.png') not in texture_files and (mat['MaterialName'] + '_MT.png') not in texture_files):
                #         hair_mat_list.append(mat['MaterialName'])
                #only hair shaders have the HairGloss parameter, this should be able to replace commented out method shown above
                material_name = line['MaterialName']
                gloss_present = [name for name in line['ShaderPropNames'] if '_HairGloss ' in name]
                if gloss_present and material_name in outfit_materials:
                    hair_mat_list.append(material_name)
            if hair_mat_list:
                self.separate_materials(outfit, hair_mat_list)
                hair = bpy.data.objects[outfit.name + '.001']
                hair.name = 'Hair ' + outfit.name
                self.hairs.append(hair)
        c.print_timer('separate_hair')

    def separate_alternate_clothing(self):
        '''Separates any clothes pieces that are normally supposed to be hidden'''
        self.outfit_alternates = []
        if not bpy.context.scene.kkbp.categorize_dropdown in ['A', 'B']:
            return
        #the KK_ReferenceInfoData json lists the clothes variations' object paths in the ENUM order in the modifymesh markdown file
        ref_data = c.get_json_file('KK_ReferenceInfoData.json')
        #the smr json contains the link between the object path and the clothing material. The material is used for separation
        smr_data = c.get_json_file('KK_SMRData.json')
        #the clothesdata json can identify what objects are the indoor shoes
        clothes_data = c.get_json_file('KK_ClothesData.json')
        
        clothes_labels = {
            'Top shift':       [93, 97, 112, 114, 116],
            'Bottom shift':    [95, 99],
            'Bra shift':       [101, 118],
            'Underwear shift': [107],
            'Underwear hang':  [108],
            'Pantyhose shift': [110],}
        #get the maximum enum number from referenceinfodata. This is usually 174 but the length can vary
        max_enum = 0
        temp_outfit_tracker = ref_data[0]['CoordinateType']
        for line in ref_data:
            if line['CoordinateType'] == temp_outfit_tracker:
                max_enum = line['ChaReference_RefObjKey']
            else:
                break
        #If there's multiple pieces to any clothing type, separate them into their own object using the smr data
        for outfit in self.outfits:
            outfit_coordinate_index = (int(outfit.name[-7:-5])-1) if (len(self.outfits) > 1) else 0 #change index to 0 for single outfit exports
            for clothes_piece in clothes_labels:
                materials_to_separate = []
                #go through each nuge piece in this label category
                for enum_index in clothes_labels[clothes_piece]:
                    enum_index += (max_enum + 1) * outfit_coordinate_index #shift based on outfit number
                    #if this is the right outfit, then find the material this piece uses
                    if ref_data[enum_index]['CoordinateType'] == outfit_coordinate_index:
                        game_path = ref_data[enum_index]['GameObjectPath']
                        for smr_index in smr_data:
                            if (game_path in smr_index['SMRPath']) and game_path != '':
                                if len(smr_index['SMRMaterialNames']) > 1:
                                    for mat in smr_index['SMRMaterialNames']:
                                        materials_to_separate.append(mat)
                                else:
                                    materials_to_separate.append(smr_index['SMRMaterialNames'][0])
                #separate all found pieces
                if materials_to_separate:
                    try:
                        print(materials_to_separate)
                        self.separate_materials(outfit, materials_to_separate)
                        alt_piece = bpy.data.objects[outfit.name + '.001']
                        alt_piece.name = clothes_piece + ' ' + outfit.name
                        alt_piece['KKBP type'] = clothes_piece
                        self.outfit_alternates.append(alt_piece)
                        c.kklog('Separated {} alternate clothing pieces automatically'.format(materials_to_separate))
                    except:
                        bpy.ops.object.mode_set(mode = 'OBJECT')
                        c.kklog('Couldn\'t separate {} automatically'.format(materials_to_separate), 'warn')
            
            #always separate indoor shoes if present using the clothes data
            for index, clothes_index in enumerate(clothes_data):
                if clothes_index['CoordinateType'] == outfit_coordinate_index:
                    if (index - 12 * outfit_coordinate_index) % 7 == 0:
                        object = clothes_index['RendNormal01']
                        for smr_index in smr_data:
                            if (smr_index['SMRName'] == object):
                                materials_to_separate.append(smr_index['SMRMaterialNames'])
            self.separate_materials(outfit, materials_to_separate)
            if bpy.data.objects.get(outfit.name + '.001'):
                indoor_shoes = bpy.data.objects[outfit.name + '.001']
                indoor_shoes.name = clothes_piece + ' ' + outfit.name
                indoor_shoes['KKBP type'] = clothes_piece
                self.outfit_alternates.append(indoor_shoes)
            c.kklog('Separated {} alternate clothing pieces automatically'.format(materials_to_separate))
        c.print_timer('separate_alternate_clothing')

    def separate_shad_bone(self):
        '''Separate the shadowcast and bonelyfans meshes, if present'''
        try:
            shad_mat_list = ['c_m_shadowcast', 'Standard']
            self.separate_materials(self.body, shad_mat_list, 'fuzzy')
            bpy.data.objects[self.body.name + '.001'].name = 'Shadowcast'
        except:
            pass
        #Separate the bonelyfans mesh if any
        try:
            bone_mat_list = ['Bonelyfans', 'Bonelyfans.001']
            self.separate_materials(self.body, bone_mat_list)
            bpy.data.objects[self.body.name + '.001'].name = 'Bonelyfans'
        except:
            pass
        shadbone = [o for o in [bpy.data.objects.get('Shadowcast'), bpy.data.objects.get('Bonelyfans')] if o]
        self.move_and_hide_collection(shadbone, "Shadowcast Collection")
        c.print_timer('separate_shad_bone')
            
    def separate_hitboxes(self):
        '''Separate the hitbox mesh, if present'''
        self.hitboxes = []
        hitbox_list = []
        material_data = c.get_json_file('KK_MaterialData.json')
        for mat in material_data:
            if mat['MaterialName'][0:6] == 'o_hit_' or mat['MaterialName'] == 'cf_O_face_atari_M':
                hitbox_list.append(mat['MaterialName'])
        #attempt to separate hitbox list from body and all clothes objects
        if len(hitbox_list):
            self.separate_materials(self.body, hitbox_list)
            if bpy.data.objects.get(self.body.name + '.001'):
                hitbox = bpy.data.objects[self.body.name + '.001']
                hitbox.name = 'Hitboxes'
                self.hitboxes.append(hitbox)
            for outfit in self.outfits:
                hitbox_list = [mat_name + '.001' for mat_name in hitbox_list]
                self.separate_materials(outfit, hitbox_list)
                if bpy.data.objects.get(outfit.name + '.001'):
                    hitbox = bpy.data.objects[outfit.name + '.001']
                    hitbox.name = 'Hitboxes' + outfit.name
                    self.hitboxes.append(hitbox)
        self.move_and_hide_collection(self.hitboxes, "Hitbox Collection")
        c.print_timer('separate_hitboxes')

    def delete_mask_quad(self):
        '''delete the mask material if not in smr mode'''
        if bpy.context.scene.kkbp.categorize_dropdown != 'D':
            for outfit in self.outfits:
                for mat in outfit.material_slots:
                    if 'm_Mask ' in mat.material.name:
                        if mat.material.name[7:].isnumeric():
                            self.delete_material(outfit, [mat])
        c.print_timer('delete_mask_quad')

    def remove_unused_shapekeys(self):
        '''remove shapekeys on all objects except the body because that needs them'''
        if bpy.context.scene.kkbp.shapekeys_dropdown not in ['A', 'B']:
            return
        for obj in bpy.data.objects:
            if obj.name != self.body.name and obj.type == 'MESH':
                if not obj.data.shape_keys:
                    continue
                for key in obj.data.shape_keys.key_blocks.keys():
                    obj.shape_key_remove(obj.data.shape_keys.key_blocks[key])
        c.print_timer('remove_unused_shapekeys')

    def rename_uv_maps(self):
        #Make UV map names clearer
        self.body.data.uv_layers[0].name = 'uv_main'
        self.body.data.uv_layers[1].name = 'uv_nipple_and_shine'
        self.body.data.uv_layers[2].name = 'uv_underhair'
        self.body.data.uv_layers[3].name = 'uv_eyeshadow'

        for outfit in self.outfits:
            outfit.data.uv_layers[0].name = 'uv_main'
            outfit.data.uv_layers[1].name = 'uv_nipple_and_shine'
            outfit.data.uv_layers[2].name = 'uv_underhair'
            outfit.data.uv_layers[3].name = 'uv_eyeshadow'
        
        for hair in self.hairs:
            hair.data.uv_layers[0].name = 'uv_main'
            hair.data.uv_layers[1].name = 'uv_nipple_and_shine'
            hair.data.uv_layers[2].name = 'uv_underhair'
            hair.data.uv_layers[3].name = 'uv_eyeshadow'
        
        for alt in self.outfit_alternates:
            alt.data.uv_layers[0].name = 'uv_main'
            alt.data.uv_layers[1].name = 'uv_nipple_and_shine'
            alt.data.uv_layers[2].name = 'uv_underhair'
            alt.data.uv_layers[3].name = 'uv_eyeshadow'
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

        self.body.active_shape_key_index = 0
        
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
                        self.body.active_shape_key_index = self.body.data.shape_keys.key_blocks.keys().index(keyblock.name)
                        bpy.ops.object.shape_key_remove() #no non-ops way to do this?
                except:
                    #or not
                    c.kklog("Couldn't delete shapekey: " + keyblock.name, 'error')
                    pass
        c.print_timer('translate_shapekeys')

    def combine_shapekeys(self):
        '''Creates new, full shapekeys using the existing partial shapekeys, and Deletes the partial shapekeys if user didn't elect to keep them in the panel'''
        if not bpy.context.scene.kkbp.shapekeys_dropdown in ['A', 'B']:
            return
        
        #make the basis shapekey active
        self.body.active_shape_key_index = 0

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
        shapekey_block = bpy.data.shape_keys[self.body.data.shape_keys.name].key_blocks
        
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
                #print(counter)
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
                        self.body.shape_key_add(name=('KK ' + cat + emotion))
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
                        self.body.shape_key_remove(remove_shapekey)
                except:
                    c.kklog('Couldn\'t remove shapekey ' + remove_shapekey.name, 'error')
                    pass
        else:
            c.kklog('Original shapekeys were not deleted', 'warn')
        #make the basis shapekey active
        self.body.active_shape_key_index = 0
        #and reset the pivot point to median
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        c.print_timer('combine_shapekeys')

    def create_tear_shapekeys(self):
        '''Separate tears from body and create tear shapekeys'''
        if bpy.context.scene.kkbp.shapekeys_dropdown not in ['A', 'B']:
            return
        #Create a reverse shapekey for each tear material
        armature = bpy.data.objects['Model_arm']
        c.switch(self.body, 'edit')
        #Move tears and gag backwards on the basis shapekey
        #use head mesh as reference location
        bpy.context.object.active_material_index = self.body.data.materials.find(self.body['SMR materials']['cf_O_face'][0])
        bpy.ops.object.material_slot_select()
        #refresh selection, then get head location
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        selected_verts = [v.co.y for v in self.body.data.vertices if v.select]
        loc = 0
        for y in selected_verts:
            loc+=y
        middle_of_head = loc / len(selected_verts)
        c.switch(self.body, 'edit')
        tear_mats = {
            'cf_O_namida_L'     :     "Tears big",
            'cf_O_namida_M'     :     "Tears med",
            'cf_O_namida_S'     :     'Tears small',
            'cf_O_gag_eye_00'   :     "Gag eye 00",
            'cf_O_gag_eye_01'   :     "Gag eye 01",
            'cf_O_gag_eye_02'   :     "Gag eye 02",
        }
        for cat in tear_mats:
            mats = self.body['SMR materials'][cat]
            for mat in mats:
                bpy.context.object.active_material_index = self.body.data.materials.find(mat)
                bpy.ops.object.material_slot_select()
        #refresh selection, then move tears a random amount backwards
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        selected_verts = [v for v in self.body.data.vertices if v.select]
        amount_to_move_tears_back = 2 * (selected_verts[0].co.y - middle_of_head)
        self.body['debug'] = amount_to_move_tears_back
        bpy.ops.transform.translate(value=(0, abs(amount_to_move_tears_back), 0))

        #move the tears forwards again the same amount in individual shapekeys
        for cat in tear_mats:
            mats = self.body['SMR materials'][cat]
            for mat in mats:
                c.switch(self.body, 'object')
                bpy.ops.object.shape_key_add(from_mix=False)
                last_shapekey = len(self.body.data.shape_keys.key_blocks)-1
                self.body.data.shape_keys.key_blocks[-1].name = tear_mats[cat]
                bpy.context.object.active_shape_key_index = last_shapekey
                c.switch(self.body, 'edit')
                bpy.context.object.active_material_index = self.body.data.materials.find(mat)
                if self.body.data.materials.find(mat) == -1:
                    bpy.context.object.active_material_index += 1
                else:
                    bpy.context.object.active_material_index = self.body.data.materials.find(mat)
                bpy.ops.object.material_slot_select()
                #find a random vertex location of the tear and move it forwards
                c.switch(self.body, 'object')
                selected_verts = [v for v in self.body.data.vertices if v.select]
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.transform.translate(value=(0, -1 * abs(amount_to_move_tears_back), 0))
                c.switch(self.body, 'object')
                bpy.ops.object.shape_key_move(type='TOP' if self.body['SMR materials']['cf_O_namida_L'][0] in mat else 'BOTTOM')

        #Move the Eye, eyewhite and eyeline materials back on the KK gageye shapekey
        bpy.context.object.active_shape_key_index = bpy.context.object.data.shape_keys.key_blocks.find('KK Eyes_gageye')
        c.switch(self.body, 'edit')
        for cat in [
            self.body['SMR materials']['cf_Ohitomi_L'],
            self.body['SMR materials']['cf_Ohitomi_R'], 
            self.body['SMR materials']['cf_Ohitomi_L02'],
            self.body['SMR materials']['cf_Ohitomi_R02'],
            self.body['SMR materials']['cf_O_eyeline'],
            self.body['SMR materials']['cf_O_eyeline_low']]:
            for mat in cat:
                bpy.context.object.active_material_index = self.body.data.materials.find(mat)
                bpy.ops.object.material_slot_select()
        #find a random vertex location of the eye and move it backwards
        c.switch(self.body, 'object')
        selected_verts = [v for v in self.body.data.vertices if v.select]
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.transform.translate(value=(0, 2.5 * abs(amount_to_move_tears_back), 0))
        c.switch(self.body, 'object')

        #Merge the tear materials
        c.switch(self.body, 'edit')
        tear_mats = []
        tear_mats.extend(self.body['SMR materials']['cf_O_namida_M'])
        tear_mats.extend(self.body['SMR materials']['cf_O_namida_S'])
        for mat in tear_mats:
            bpy.context.object.active_material_index = self.body.data.materials.find(mat)
            bpy.ops.object.material_slot_select()
            bpy.context.object.active_material_index = self.body.data.materials.find(self.body['SMR materials']['cf_O_namida_L'][0])
            bpy.ops.object.material_slot_assign()
            bpy.ops.mesh.select_all(action='DESELECT')

        #make a vertex group that does not contain the tears
        bpy.ops.object.vertex_group_add()
        bpy.ops.mesh.select_all(action='SELECT')
        self.body.vertex_groups.active.name = "Body without Tears"
        bpy.context.object.active_material_index = self.body.data.materials.find(self.body['SMR materials']['cf_O_namida_L'][0])
        bpy.ops.object.material_slot_deselect()
        bpy.ops.object.vertex_group_assign()

        #Separate tears from body object
        #link shapekeys of tears to body
        tear_mats = []
        tear_mats.extend(self.body['SMR materials']['cf_O_namida_L'])
        self.separate_materials(self.body, tear_mats)
        tears = bpy.data.objects['Body.001']
        tears.name = 'Tears'
        bpy.ops.object.mode_set(mode = 'OBJECT')
        link_keys(self.body, [tears])
        c.print_timer('create_tear_shapekeys')

    def create_gag_eye_shapekeys(self):
        '''Separate gag eyes from body and create gag eye shapekeys'''
        if bpy.context.scene.kkbp.shapekeys_dropdown not in ['A', 'B']:
            return
        bpy.context.view_layer.objects.active=self.body
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
            last_shapekey = len(self.body.data.shape_keys.key_blocks)-1
            self.body.data.shape_keys.key_blocks[-1].name = key
            bpy.context.object.active_shape_key_index = last_shapekey
            bpy.ops.object.shape_key_move(type='TOP')
        
        bpy.context.object.active_shape_key_index = 0
        #make most gag eye shapekeys activate the body's gag key if the KK gageeye shapekey was created
        if bpy.data.shape_keys[0].key_blocks.get('KK Eyes_gageye'):
            skey_driver = bpy.data.shape_keys[0].key_blocks['KK Eyes_gageye'].driver_add('value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
            condition = [key.replace(' ', '') for key in gag_keys if 'Fiery' not in key]
            skey_driver.driver.expression = '1 if ' + ' or '.join(condition) + ' else 0'

            #make certain gag eye shapekeys activate the correct gag show key
            skey_driver = bpy.data.shape_keys[0].key_blocks['Gag eye 00'].driver_add('value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
            skey_driver.driver.expression = '1 if CircleEyes1 or CircleEyes2 or VerticalLine or CartoonyClosed or HorizontalLine else 0'

            #make certain gag eye shapekeys activate the correct gag show key
            skey_driver = bpy.data.shape_keys[0].key_blocks['Gag eye 01'].driver_add('value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
            skey_driver.driver.expression = '1 if HeartEyes or SpiralEyes else 0'

            #make certain gag eye shapekeys activate the correct gag show key
            skey_driver = bpy.data.shape_keys[0].key_blocks['Gag eye 02'].driver_add('value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
            skey_driver.driver.expression = '1 if FieryEyes or CartoonyWink or CartoonyCrying else 0'

            #make a vertex group that does not contain the gag_eyes
            bpy.ops.object.vertex_group_add()
            c.switch(self.body, 'edit')
            bpy.ops.mesh.select_all(action='SELECT')
            self.body.vertex_groups.active.name = "Body without Gag eyes"
            for gag_cat in [self.body['SMR materials']['cf_O_gag_eye_00'], self.body['SMR materials']['cf_O_gag_eye_01'], self.body['SMR materials']['cf_O_gag_eye_02']]:
                for gag_mat in gag_cat:
                    bpy.context.object.active_material_index = self.body.data.materials.find(gag_mat)
                    bpy.ops.object.material_slot_deselect()
            bpy.ops.object.vertex_group_assign()

            #Separate gag from body object
            #link shapekeys of gag to body
            gag_mat = []
            gag_mat.extend(self.body['SMR materials']['cf_O_gag_eye_00'])
            gag_mat.extend(self.body['SMR materials']['cf_O_gag_eye_01'])
            gag_mat.extend(self.body['SMR materials']['cf_O_gag_eye_02'])
            self.separate_materials(self.body, gag_mat)
            gag = bpy.data.objects['Body.001']
            gag.name = 'Gag Eyes'
            c.switch(self.body, 'object')
            link_keys(self.body, [gag])
        c.print_timer('create_gag_eye_shapekeys')

    def add_body_datatransfer(self):
        '''Give the body an inactive data transfer modifier for a cheap shading proxy'''
        mod = self.body.modifiers.new(type='DATA_TRANSFER', name = 'Shadowcast shading proxy')
        mod.show_expanded = False
        mod.show_viewport = False
        mod.show_render = False
        if bpy.data.objects.get('Shadowcast'):
            mod.object = bpy.data.objects['Shadowcast']
        mod.use_loop_data = True
        mod.data_types_loops = {'CUSTOM_NORMAL'}
        mod.loop_mapping = 'POLYINTERP_LNORPROJ'
        c.print_timer('add_body_datatransfer')

    def remove_body_seams(self):
        '''merge certain materials for the body object to prevent odd shading issues later on'''
        if not bpy.context.scene.kkbp.fix_seams:
            return
        c.switch(self.body, 'edit')
        select_list = [
            self.body['SMR materials']['cf_O_face'],
            self.body['SMR materials']['o_body_a'],
            ]
        bpy.context.tool_settings.mesh_select_mode = (True, False, False) #enable vertex select in edit mode
        for cat in select_list:
            for mat in cat:
                bpy.context.object.active_material_index = self.body.data.materials.find(mat)
                bpy.ops.object.material_slot_select()
        bpy.ops.mesh.remove_doubles(threshold=0.00001)

        #This still messes with the weights. Maybe it's possible to save the 3D positions, weights, and UV positions for each duplicate vertex
        # then delete and make new vertices with saved info 
        # The vertices on the body object seem to be consistent across imports according to https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/82
        c.print_timer('remove_body_seams')

    def mark_body_freestyle_faces(self):
        c.switch(self.body, 'edit')
        #mark certain materials as freestyle faces
        def mark_as_freestyle(mat_list):
            for mat in mat_list:
                if mat:
                    mat_found = self.body.data.materials.find(mat)
                    if mat_found > -1:
                        bpy.context.object.active_material_index = mat_found
                        bpy.ops.object.material_slot_select()
                    else:
                        c.kklog('Material wasn\'t found when freestyling body materials: ' + mat, 'warn')
            bpy.ops.mesh.mark_freestyle_face(clear=False)
        freestyle_list = []
        freestyle_list.extend(self.body['SMR materials']['cf_Ohitomi_L02'])
        freestyle_list.extend(self.body['SMR materials']['cf_Ohitomi_R02'])
        freestyle_list.extend(self.body['SMR materials']['cf_Ohitomi_L'])
        freestyle_list.extend(self.body['SMR materials']['cf_Ohitomi_R'])
        freestyle_list.extend(self.body['SMR materials']['cf_O_eyeline_low'])
        freestyle_list.extend(self.body['SMR materials']['cf_O_eyeline'])
        freestyle_list.extend(self.body['SMR materials']['cf_O_noseline'])
        freestyle_list.extend(self.body['SMR materials']['cf_O_mayuge'])
        mark_as_freestyle(freestyle_list)
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        c.print_timer('mark_body_freestyle_faces')

    def tag_all_objects_for_next_operation(self):
        '''Gives each object a tag so they can be identified by other scripts'''
        self.body['KKBP tag'] = 'body'
        for outfit in self.outfits:
            outfit['KKBP tag'] = 'outfit'
        for alt in self.outfit_alternates:
            alt['KKBP tag'] = 'alt'
        for hair in self.hairs:
            hair['KKBP tag'] = 'hair'
        for hb in self.hitboxes:
            hb['KKBP tag'] = 'hitbox'
        c.print_timer('tag_all_objects_for_next_operation')


    # %% Supporting functions
    def move_and_hide_collection (self, objects, new_collection):
        '''Move the objects into their own collection and hide them'''
        if not objects:
            return
        
        c.switch(objects[0], 'object')
        for object in objects:
            object.select_set(True)
            bpy.context.view_layer.objects.active=object
        #move
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name=new_collection)
        #then hide the new collection
        try:
            bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children[new_collection]
            bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
        except:
            try:
                #maybe the collection is in the default Collection collection
                bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children['Collection'].children[new_collection]
                bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
            except:
                #maybe the collection is already hidden, or doesn't exist
                pass

    def separate_materials(self, object, mat_list, search_type = 'exact'):
        '''Separates the materials in the mat_list on object, and creates a new object'''
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
        except:
            c.kklog('Nothing was selected when separating materials from : ' + object.name, 'warn')
        bpy.ops.object.mode_set(mode = 'OBJECT')

    def delete_material(self, object, mat_list):
        for mat in mat_list:
            if object.data.materials.find(mat.name) > -1:
                c.switch(object, 'edit')
                bpy.context.object.active_material_index = object.data.materials.find(mat.name)
                bpy.ops.object.material_slot_select()
                bpy.ops.mesh.delete(type='VERT')


if __name__ == "__main__":
    bpy.utils.register_class(modify_mesh)

    # test call
    print((bpy.ops.kkbp.modifymesh('INVOKE_DEFAULT')))
