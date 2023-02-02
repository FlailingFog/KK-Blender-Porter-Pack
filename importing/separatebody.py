import bpy, json, time, traceback
from .importbuttons import kklog
from ..extras.linkshapekeys import link_keys

def clean_body():
        #Select the body and make it active
        bpy.ops.object.mode_set(mode = 'OBJECT')
        body = bpy.data.objects['Body']
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        
        #Make UV map names clearer
        body.data.uv_layers[0].name = 'uv_main'
        body.data.uv_layers[1].name = 'uv_nipple_and_shine'
        body.data.uv_layers[2].name = 'uv_underhair'
        body.data.uv_layers[3].name = 'uv_eyeshadow'

        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')

        #save body material listing to the body object using the SMR data
        json_file = open(bpy.context.scene.kkbp.import_dir + 'KK_SMRData.json')
        smr_data = json.load(json_file)
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
            #'bonelyfans',
            'o_tang_rigged'
            ]
        
        smr_postfix_map = {
            'cf_Ohitomi_R' : '.001',
            'cf_O_namida_M' : '.001',
            'cf_O_namida_S' : '.002',
        }
        
        #fill the dictionary on the body object with nothing
        body['KKBP materials'] = {}
        for mat in body_materials:
            body['KKBP materials'][mat] = ''
        #get a list of the body materials from the smr data then use it to fill the material dictionary on the body object
        smr_body_materials = [index for index in smr_data if index['CoordinateType'] == -1]
        for body_material in smr_body_materials:
            #skip bonelyfan mats
            if 'Bonelyfan' in body_material['SMRMaterialNames'][0]:
                continue
            #if this is the rigged tongue, put it in the right category
            if body_material['SMRPath'] == '/chaF_001/BodyTop/p_cf_body_00/cf_o_root/n_tang/o_tang':
                body['KKBP materials']['o_tang_rigged'] = body_material['SMRMaterialNames'][0] + '.001'
            else:
                body['KKBP materials'][body_material['SMRName']] = body_material['SMRMaterialNames'][0]
            
            #rename some materials if in smr mode
            if body_material['SMRName'] in smr_postfix_map and (bpy.context.scene.kkbp.categorize_dropdown == 'D' or 'cf_Ohitomi_R' not in body_material['SMRName']):
                mat_name = body_material['SMRMaterialNames'][0] + smr_postfix_map[body_material['SMRName']]  
                body['KKBP materials'][body_material['SMRName']] = mat_name
                
        if bpy.context.scene.kkbp.categorize_dropdown != 'D' and bpy.data.materials.get(body['KKBP materials']['o_tang_rigged']):
            #Separate rigged tongue from body object, parent it to the body so it's hidden in the outliner
            #link shapekeys of tongue to body even though it doesn't have them
            tongueMats = [body['KKBP materials']['o_tang_rigged']]
            separate_materials(body, tongueMats)
            tongue = bpy.data.objects['Body.001']
            tongue.name = 'Tongue (rigged)'
            tongue.parent = bpy.data.objects['Body']
            bpy.ops.object.mode_set(mode = 'OBJECT')
            link_keys(body, [tongue])
            tongue.hide = True

def add_freestyle_faces():
    body = bpy.data.objects['Body']
    #make sure the body is selected
    bpy.context.view_layer.objects.active = body
    #go into edit mode and deselect everything
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    #mark certain materials as freestyle faces
    def mark_as_freestyle(mat_list):
        for mat in mat_list:
            if mat:
                mat_found = body.data.materials.find(mat)
                if mat_found > -1:
                    bpy.context.object.active_material_index = mat_found
                    bpy.ops.object.material_slot_select()
                else:
                    kklog('Material wasn\'t found when freestyling body materials: ' + mat, 'warn')
        bpy.ops.mesh.mark_freestyle_face(clear=False)
    freestyle_list = [
        body['KKBP materials']['cf_Ohitomi_L02'] + '_' + 'cf_Ohitomi_L02',
        body['KKBP materials']['cf_Ohitomi_R02'] + '_' + 'cf_Ohitomi_R02',
        body['KKBP materials']['cf_Ohitomi_L'],
        body['KKBP materials']['cf_Ohitomi_R'],
        body['KKBP materials']['cf_O_eyeline_low'],
        body['KKBP materials']['cf_O_eyeline'],
        body['KKBP materials']['cf_O_noseline'],
        body['KKBP materials']['cf_O_mayuge']]
    mark_as_freestyle(freestyle_list)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

def separate_materials(object, mat_list, search_type = 'exact'):
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    #print(object)
    bpy.context.view_layer.objects.active = object
    bpy.ops.object.mode_set(mode = 'EDIT')
    #print(object)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    for mat in mat_list:
        mat_found = -1
        #print(mat)
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
            kklog('Material wasn\'t found when separating materials: ' + mat, 'warn')
    bpy.ops.mesh.separate(type='SELECTED')
    bpy.ops.object.mode_set(mode = 'OBJECT')


def index_exists(list, index):
    if 0 <= index < len(list):
        return True
    else:
        return False

def separate_everything(context):
    body = bpy.data.objects['Body']

    #Select all materials that use the hair renderer and don't have a normal map then separate
    json_file = open(context.scene.kkbp.import_dir + 'KK_MaterialData.json')
    material_data = json.load(json_file)
    json_file = open(context.scene.kkbp.import_dir + 'KK_TextureData.json')
    texture_data = json.load(json_file)
    #get all texture files
    texture_files = []
    for file in texture_data:
        texture_files.append(file['textureName'])

    for outfit in bpy.data.objects:
        if "Outfit" in outfit.name and "Hair" not in outfit.name:
            #selection stuff
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action = 'DESELECT')
            bpy.context.view_layer.objects.active = outfit
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'DESELECT')

            #delete the mask material if not in smr mode
            bpy.ops.mesh.delete(type='VERT')
            if bpy.context.scene.kkbp.categorize_dropdown != 'D':
                for mat in outfit.material_slots:
                    if 'm_Mask ' in mat.material.name:
                        if mat.material.name[7:].isnumeric():
                            bpy.context.object.active_material_index = outfit.data.materials.find(mat.material.name)
                            bpy.ops.object.material_slot_select()
                            bpy.ops.mesh.delete(type='VERT')
            bpy.ops.mesh.select_all(action = 'DESELECT')

            outfit['KKBP outfit ID'] = int(outfit.name[-1:])

            #make uv names match body's names
            outfit.data.uv_layers[0].name = 'uv_main'
            outfit.data.uv_layers[1].name = 'uv_nipple_and_shine'
            outfit.data.uv_layers[2].name = 'uv_underhair'
            outfit.data.uv_layers[3].name = 'uv_eyeshadow'
            
            hair_mat_list = []
            for mat in material_data:
                if mat['ShaderName'] in ["Shader Forge/main_hair_front", "Shader Forge/main_hair", 'Koikano/hair_main_sun_front', 'Koikano/hair_main_sun', 'xukmi/HairPlus', 'xukmi/HairFrontPlus']:
                    if (mat['MaterialName'] + '_HGLS.png') in texture_files or ((mat['MaterialName'] + '_NMP.png') not in texture_files and (mat['MaterialName'] + '_MT_CT.png') not in texture_files and (mat['MaterialName'] + '_MT.png') not in texture_files):
                        hair_mat_list.append(mat['MaterialName'])
            if len(hair_mat_list):
                #Only separate hair if not in pause mode
                if context.scene.kkbp.categorize_dropdown not in ['B']:
                    separate_materials(outfit, hair_mat_list)
                    bpy.data.objects[outfit.name + '.001'].name = 'Hair ' + outfit.name

                    #don't reparent hair if Categorize by SMR
                    if context.scene.kkbp.categorize_dropdown not in ['D']:
                        bpy.data.objects['Hair ' + outfit.name].parent = outfit

    bpy.context.view_layer.objects.active = body
    
    #Select any clothes pieces that are normally supposed to be hidden and hide them
    if context.scene.kkbp.categorize_dropdown in ['A', 'B']:
        #the KK_ReferenceInfoData json lists the clothes variations' object path in the ENUM order appended to the end of this file
        json_file = open(context.scene.kkbp.import_dir + 'KK_ReferenceInfoData.json')
        ref_data = json.load(json_file)
        #the smr json contains the link between the object path and the clothing material. The material is used for separation
        json_file = open(context.scene.kkbp.import_dir + 'KK_SMRData.json')
        smr_data = json.load(json_file)
        #the clothesdata json can identify what objects are the indoor shoes
        json_file = open(context.scene.kkbp.import_dir + 'KK_ClothesData.json')
        clothes_data = json.load(json_file)
        
        clothes_labels = {
            'Top shift':       [93, 97, 112, 114, 116],
            'Bottom shift':    [95, 99],
            'Bra shift':       [101, 118],
            'Underwear shift': [107],
            'Underwear hang':  [108],
            'Pantyhose shift': [110],}
            #'Top part shift'}
        
        #get the maximum enum number from referenceinfodata. This is usually 174 but the length can vary
        max_enum = 0
        temp_outfit_tracker = ref_data[0]['CoordinateType']
        for line in ref_data:
            if line['CoordinateType'] == temp_outfit_tracker:
                max_enum = line['ChaReference_RefObjKey']
            else:
                break

        #If there's multiple pieces to any clothing type, separate them into their own object using the smr data
        outfits = [outfit for outfit in bpy.data.objects if 'Outfit ' in outfit.name and 'Hair' not in outfit.name]
        for outfit in outfits:
            outfit_coordinate_index = int(outfit.name[-3:]) if len(outfits) > 1 else 0 #change to 0 for single outfit exports
            
            for clothes_piece in clothes_labels:
                materials_to_separate = []
                #go through each nuge piece in this label category
                for enum_index in clothes_labels[clothes_piece]:
                    enum_index += (max_enum + 1) * outfit_coordinate_index #shift based on outfit number
                    #kklog(enum_index)
                    #if this is the right outfit, then find the material this nuge piece uses
                    if ref_data[enum_index]['CoordinateType'] == outfit_coordinate_index:
                        game_path = ref_data[enum_index]['GameObjectPath']
                        #kklog('looking for ' + game_path)
                        for smr_index in smr_data:
                            #kklog(smr_index['SMRPath'])
                            if (game_path in smr_index['SMRPath']) and game_path != '':
                                if len(smr_index['SMRMaterialNames']) > 1:
                                    for mat in smr_index['SMRMaterialNames']:
                                        materials_to_separate.append(mat)
                                else:
                                    materials_to_separate.append(smr_index['SMRMaterialNames'][0])
                if materials_to_separate:
                    try:
                        print(materials_to_separate)
                        separate_materials(outfit, materials_to_separate)
                        bpy.data.objects[outfit.name + '.001'].parent = outfit
                        bpy.data.objects[outfit.name + '.001'].name = clothes_piece + ' ' + outfit.name
                        kklog('Separated {} alternate clothing pieces automatically'.format(materials_to_separate))
                    except:
                        bpy.ops.object.mode_set(mode = 'OBJECT')
                        kklog('Couldn\'t separate {} automatically'.format(materials_to_separate), 'warn')
            
            #always separate indoor shoes if present using the clothes data
            for index, clothes_index in enumerate(clothes_data):
                if clothes_index['CoordinateType'] == outfit_coordinate_index:
                    if (index - 12 * outfit_coordinate_index) % 7 == 0:
                        object = clothes_index['RendNormal01']
                        for smr_index in smr_data:
                            if (smr_index['SMRName'] == object):
                                materials_to_separate.append(smr_index['SMRMaterialNames'])

    #Separate hitbox materials, if any
    hit_box_list = []
    for mat in material_data:
        if mat['MaterialName'][0:6] == 'o_hit_' or mat['MaterialName'] == 'cf_O_face_atari_M' or mat['MaterialName'] == 'cf_O_face_atari_M.001':
            hit_box_list.append(mat['MaterialName'])
    #kklog(hit_box_list)
    if len(hit_box_list):
        separate_materials(body, hit_box_list)
        bpy.data.objects[body.name + '.001'].name = 'Hitboxes'
        if bpy.data.objects['Outfit 00'].material_slots.get('cf_O_face_atari_M.001'):
            #print('attempting to get the hitboxes off outfit 00')
            separate_materials(bpy.data.objects['Outfit 00'], hit_box_list, search_type='fuzzy')
            bpy.data.objects['Outfit 00.001'].name = 'Hitboxes again'
            bpy.data.objects['Hitboxes again']['KKBP outfit ID'] = None

    #Separate the shadowcast if any
    try:
        shad_mat_list = ['c_m_shadowcast', 'Standard']
        separate_materials(body, shad_mat_list, 'fuzzy')
        bpy.data.objects[body.name + '.001'].name = 'Shadowcast'
    except:
        pass
    
    #Separate the bonelyfans mesh if any
    try:
        bone_mat_list = ['Bonelyfans', 'Bonelyfans.001']
        separate_materials(body, bone_mat_list)
        bpy.data.objects[body.name + '.001'].name = 'Bonelyfans'
    except:
        pass

        #remove unused material slots on all objects
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.material_slot_remove_unused()
        
    def move_and_hide_collection (objects, new_collection):
        for object in objects:
            if bpy.data.objects.get(object):
                bpy.data.objects[object].select_set(True)
                bpy.context.view_layer.objects.active=bpy.data.objects[object]
        #move
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name=new_collection)
        #hide the new collection
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

    #move these to their own collection
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    move_and_hide_collection(['Shadowcast', 'Bonelyfans'], "Shadowcast Collection")
    move_and_hide_collection(['Hitboxes', 'Hitboxes again'], "Hitbox Collection")

#merge certain materials for the body object to prevent odd shading issues later on
def fix_body_seams():
    bpy.ops.object.select_all(action='DESELECT')
    body = bpy.data.objects['Body']
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    select_list = [
        body['KKBP materials']['cf_O_face'],
        body['KKBP materials']['o_body_a'],
        ]
    bpy.context.tool_settings.mesh_select_mode = (True, False, False) #enable vertex select in edit mode
    #bpy.ops.mesh.select_non_manifold()
    for mat in select_list:
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
    bpy.ops.mesh.remove_doubles(threshold=0.00001)
    #bpy.context.tool_settings.mesh_select_mode = (False, False, True) #enable face select in edit mode

    #This still messes with the weights. Maybe it's possible to save the 3D positions, weights, and UV positions for each duplicate vertex
    # then delete and make new vertices with saved info 
    #The vertices on the body object seem to be consistent across imports from https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/82

def make_tear_and_gag_shapekeys():
    #Create a reverse shapekey for each tear and gag material
    body = bpy.data.objects['Body']
    armature = bpy.data.objects['Armature']
    bpy.context.view_layer.objects.active = body
    
    #Move tears and gag backwards on the basis shapekey
    tear_mats = {
        body['KKBP materials']['cf_O_namida_L']:   "Tears big",
        body['KKBP materials']['cf_O_namida_M']:   "Tears med",
        body['KKBP materials']['cf_O_namida_S']:   'Tears small',
        body['KKBP materials']['cf_O_gag_eye_00']:     "Gag eye 00",
        body['KKBP materials']['cf_O_gag_eye_01']:     "Gag eye 01",
        body['KKBP materials']['cf_O_gag_eye_02']:     "Gag eye 02",
    }
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    for mat in tear_mats:
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
    #refresh selection, then move tears a random amount backwards
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.mode_set(mode = 'EDIT')
    selected_verts = [v for v in body.data.vertices if v.select]
    amount_to_move_tears_back = selected_verts[0].co.y - armature.data.bones['cf_j_head'].head.y
    bpy.ops.transform.translate(value=(0, abs(amount_to_move_tears_back), 0))

    #move the tears forwards again the same amount in individual shapekeys
    for mat in tear_mats:
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.shape_key_add(from_mix=False)
        last_shapekey = len(body.data.shape_keys.key_blocks)-1
        body.data.shape_keys.key_blocks[-1].name = tear_mats[mat]
        bpy.context.object.active_shape_key_index = last_shapekey
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        if body.data.materials.find(mat) == -1:
            bpy.context.object.active_material_index += 1
        else:
            bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
        #find a random vertex location of the tear and move it forwards
        bpy.ops.object.mode_set(mode = 'OBJECT')
        selected_verts = [v for v in body.data.vertices if v.select]
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.transform.translate(value=(0, -1 * abs(amount_to_move_tears_back), 0))
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.shape_key_move(type='TOP' if body['KKBP materials']['cf_O_namida_L'] in mat else 'BOTTOM')

    #Move the Eye, eyewhite and eyeline materials back on the KK gageye shapekey
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.context.object.active_shape_key_index = bpy.context.object.data.shape_keys.key_blocks.find('KK Eyes_gageye')
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    for mat in [
        body['KKBP materials']['cf_Ohitomi_L'],
        body['KKBP materials']['cf_Ohitomi_R'], 
        body['KKBP materials']['cf_Ohitomi_L02'] + '_' + 'cf_Ohitomi_L02',
        body['KKBP materials']['cf_Ohitomi_R02'] + '_' + 'cf_Ohitomi_R02',
        body['KKBP materials']['cf_O_eyeline'],
        body['KKBP materials']['cf_O_eyeline_low']]:
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
    #find a random vertex location of the eye and move it backwards
    bpy.ops.object.mode_set(mode = 'OBJECT')
    selected_verts = [v for v in body.data.vertices if v.select]
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.transform.translate(value=(0, 2 * abs(amount_to_move_tears_back), 0))
    bpy.ops.object.mode_set(mode = 'OBJECT')

    #Merge the tear materials
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    tear_mats = [body['KKBP materials']['cf_O_namida_M'], body['KKBP materials']['cf_O_namida_S']]
    for mat in tear_mats:
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
        bpy.context.object.active_material_index = body.data.materials.find(body['KKBP materials']['cf_O_namida_L'])
        bpy.ops.object.material_slot_assign()
        bpy.ops.mesh.select_all(action='DESELECT')

    #make a vertex group that does not contain the tears
    bpy.ops.object.vertex_group_add()
    bpy.ops.mesh.select_all(action='SELECT')
    body.vertex_groups.active.name = "Body without Tears"
    bpy.context.object.active_material_index = body.data.materials.find(body['KKBP materials']['cf_O_namida_L'])
    bpy.ops.object.material_slot_deselect()
    bpy.ops.object.vertex_group_assign()

    #Separate tears from body object, parent it to the body so it's hidden in the outliner
    #link shapekeys of tears to body
    tearMats = [body['KKBP materials']['cf_O_namida_L']]
    separate_materials(body, tearMats)
    tears = bpy.data.objects['Body.001']
    tears.name = 'Tears'
    tears.parent = bpy.data.objects['Body']
    bpy.ops.object.mode_set(mode = 'OBJECT')
    link_keys(body, [tears])

    #create real gag eye shapekeys
    bpy.context.view_layer.objects.active=body
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
        last_shapekey = len(body.data.shape_keys.key_blocks)-1
        body.data.shape_keys.key_blocks[-1].name = key
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
            newVar.targets[0].id = body.data.shape_keys
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
            newVar.targets[0].id = body.data.shape_keys
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
            newVar.targets[0].id = body.data.shape_keys
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
            newVar.targets[0].id = body.data.shape_keys
            newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
        skey_driver.driver.expression = '1 if FieryEyes or CartoonyWink or CartoonyCrying else 0'

        #make a vertex group that does not contain the gag_eyes
        bpy.ops.object.vertex_group_add()
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        body.vertex_groups.active.name = "Body without Gag eyes"
        for gag_mat in [body['KKBP materials']['cf_O_gag_eye_00'], body['KKBP materials']['cf_O_gag_eye_01'], body['KKBP materials']['cf_O_gag_eye_02']]:
            bpy.context.object.active_material_index = body.data.materials.find(gag_mat)
            bpy.ops.object.material_slot_deselect()
        bpy.ops.object.vertex_group_assign()

        #Separate gag from body object, parent it to the body so it's hidden in the outliner
        #link shapekeys of gag to body
        gag_mat = [body['KKBP materials']['cf_O_gag_eye_00'], body['KKBP materials']['cf_O_gag_eye_01'], body['KKBP materials']['cf_O_gag_eye_02']]
        separate_materials(body, gag_mat)
        gag = bpy.data.objects['Body.001']
        gag.name = 'Gag Eyes'
        gag.parent = bpy.data.objects['Body']
        bpy.ops.object.mode_set(mode = 'OBJECT')
        link_keys(body, [gag])

def remove_duplicate_slots():
    body = bpy.data.objects['Body']
    for obj in bpy.data.objects:
        if 'Body' == obj.name or 'Indoor shoes Outfit ' in obj.name or 'Outfit ' in obj.name or 'Hair' in obj.name:
            #combine duplicated material slots
            mesh = obj
            bpy.ops.object.select_all(action='DESELECT')
            mesh.select_set(True)
            bpy.context.view_layer.objects.active=mesh
            bpy.ops.object.material_slot_remove_unused()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            
            #remap duplicate materials to the base one
            material_list = mesh.data.materials
            for mat in material_list:
                mat_name_list = [
                    body['KKBP materials']['cf_Ohitomi_L02'] + '_' + 'cf_Ohitomi_L02',
                    body['KKBP materials']['cf_Ohitomi_R02'] + '_' + 'cf_Ohitomi_R02',
                    body['KKBP materials']['cf_Ohitomi_L'],
                    body['KKBP materials']['cf_Ohitomi_R'],
                    body['KKBP materials']['cf_O_namida_L'],
                    body['KKBP materials']['cf_O_namida_M'],
                    body['KKBP materials']['cf_O_namida_S'],
                    body['KKBP materials']['o_tang'],
                    body['KKBP materials']['o_tang_rigged'],
                ]
                #don't merge the above materials if categorize by SMR is chosen.
                eye_flag = mat.name not in mat_name_list if bpy.context.scene.kkbp.categorize_dropdown == 'D' else True
                
                if '.' in mat.name[-4:] and eye_flag:
                    try:
                        #the material name is normal
                        base_name, dupe_number = mat.name.split('.',2)
                    except:
                        #someone (not naming names) left a .### in the material name
                        base_name, rest_of_base_name, dupe_number = mat.name.split('.',2)
                        base_name = base_name + rest_of_base_name
                    #remap material if it's a dupe, but don't touch the eye dupe
                    if material_list.get(base_name) and int(dupe_number) and 'cf_m_hitomi_00' not in base_name and body['KKBP materials']['o_tang'] not in base_name:
                        mat.user_remap(material_list[base_name])
                        bpy.data.materials.remove(mat)
                    else:
                        kklog("Somehow found a false duplicate material but didn't merge: " + mat.name, 'warn')
             
            #then clean material slots by going through each slot and reassigning the slots that are repeated
            repeats = {}
            for index, mat in enumerate(material_list):
                if mat.name not in repeats:
                    repeats[mat.name] = [index]
                    # print("First entry of {} in slot {}".format(mat.name, index))
                else:
                    repeats[mat.name].append(index)
                    # print("Additional entry of {} in slot {}".format(mat.name, index))
            
            for material_name in list(repeats.keys()):
                if len(repeats[material_name]) > 1:
                    for repeated_slot in repeats[material_name]:
                        #don't touch the first slot
                        if repeated_slot == repeats[material_name][0]:
                            continue
                        kklog("Moving duplicate material {} in slot {} to the original slot {}".format(material_name, repeated_slot, repeats[material_name][0]))
                        mesh.active_material_index = repeated_slot
                        bpy.ops.object.material_slot_select()
                        mesh.active_material_index = repeats[material_name][0]
                        bpy.ops.object.material_slot_assign()
                        bpy.ops.mesh.select_all(action='DESELECT')

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.material_slot_remove_unused()

def cleanup():
    #remove shapekeys on all objects except the body/tears because only those need them
    for obj in bpy.data.objects:
        if obj.name not in ['Body','Tears','Gag Eyes'] and obj.type == 'MESH':
            if not obj.data.shape_keys:
                continue
            
            for key in obj.data.shape_keys.key_blocks.keys():
                obj.shape_key_remove(obj.data.shape_keys.key_blocks[key])

    #try to make sure we are in object mode
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
    except:
        pass
    
    #then make sure body is the active context
    bpy.context.view_layer.objects.active = bpy.data.objects['Body']
    
    #remove unused material slots for all visible objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.material_slot_remove_unused()
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
        #if ' alt ' in obj.name or 'Indoor shoes' in obj.name:
            #obj.hide = True
            #obj.hide_render = True
    bpy.ops.object.select_all(action='DESELECT')

    #and clean up the oprhaned data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)

    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)
    
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

class separate_body(bpy.types.Operator):
    bl_idname = "kkb.separatebody"
    bl_label = "The separate body script"
    bl_description = "Separates the Body, shadowcast and bonelyfans into separate objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            last_step = time.time()
            kklog('\nSeparating body, clothes, hair, hitboxes and shadowcast, then removing duplicate materials...')
            
            clean_body()
            #make tear and gageye shapekeys if shapekey modifications are enabled
            if context.scene.kkbp.shapekeys_dropdown != 'C':
                make_tear_and_gag_shapekeys()
            add_freestyle_faces()
            remove_duplicate_slots()
            separate_everything(context)
            if context.scene.kkbp.fix_seams:
                fix_body_seams()
            cleanup()

            kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            return{'FINISHED'}

        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(separate_body)

    # test call
    print((bpy.ops.kkb.separatebody('INVOKE_DEFAULT')))

#ENUM order that corresponds to ChaReference_RefObjKey value in KK_ReferenceInfoData.json
'''HeadParent,
HairParent,
a_n_hair_pony,
a_n_hair_twin_L,
a_n_hair_twin_R,
a_n_hair_pin,
a_n_hair_pin_R,
a_n_headtop,
a_n_headflont,
a_n_head,
a_n_headside,
a_n_megane,
a_n_earrings_L,
a_n_earrings_R,
a_n_nose,
a_n_mouth,
a_n_neck,
a_n_bust_f,
a_n_bust,
a_n_nip_L,
a_n_nip_R,
a_n_back,
a_n_back_L,
a_n_back_R,
a_n_waist,
a_n_waist_f,
a_n_waist_b,
a_n_waist_L,
a_n_waist_R,
a_n_leg_L,
a_n_leg_R,
a_n_knee_L,
a_n_knee_R,
a_n_ankle_L,
a_n_ankle_R,
a_n_heel_L,
a_n_heel_R,
a_n_shoulder_L,
a_n_shoulder_R,
a_n_elbo_L,
a_n_elbo_R,
a_n_arm_L,
a_n_arm_R,
a_n_wrist_L,
a_n_wrist_R,
a_n_hand_L,
a_n_hand_R,
a_n_ind_L,
a_n_ind_R,
a_n_mid_L,
a_n_mid_R,
a_n_ring_L,
a_n_ring_R,
a_n_dan,
a_n_kokan,
a_n_ana,
k_f_handL_00,
k_f_handR_00,
k_f_shoulderL_00,
k_f_shoulderR_00,
ObjEyeline,
ObjEyelineLow,
ObjEyebrow,
ObjNoseline,
ObjEyeL,
ObjEyeR,
ObjEyeWL,
ObjEyeWR,
ObjFace,
ObjDoubleTooth,
ObjBody,
ObjNip,
N_FaceSpecial,
CORRECT_ARM_L,
CORRECT_ARM_R,
CORRECT_HAND_L,
CORRECT_HAND_R,
CORRECT_TONGUE_TOP,
CORRECT_MOUTH_TARGET,
CORRECT_MOUTH_TARGET02,
CORRECT_HEAD_DBCOL,
S_ANA,
S_TongueF,
S_TongueB,
S_Son,
S_SimpleTop,
S_SimpleBody,
S_SimpleTongue,
S_MNPA,
S_MNPB,
S_MOZ_ALL,
S_GOMU,
S_CTOP_T_DEF,
S_CTOP_T_NUGE,
S_CTOP_B_DEF,
S_CTOP_B_NUGE,
S_CBOT_T_DEF,
S_CBOT_T_NUGE,
S_CBOT_B_DEF,
S_CBOT_B_NUGE,
S_UWT_T_DEF,
S_UWT_T_NUGE,
S_UWT_B_DEF,
S_UWT_B_NUGE,
S_UWB_T_DEF,
S_UWB_T_NUGE,
S_UWB_B_DEF,
S_UWB_B_NUGE,
S_UWB_B_NUGE2,
S_PANST_DEF,
S_PANST_NUGE,
S_TPARTS_00_DEF,
S_TPARTS_00_NUGE,
S_TPARTS_01_DEF,
S_TPARTS_01_NUGE,
S_TPARTS_02_DEF,
S_TPARTS_02_NUGE,
ObjBraDef,
ObjBraNuge,
ObjInnerDef,
ObjInnerNuge,
S_TEARS_01,
S_TEARS_02,
S_TEARS_03,
N_EyeBase,
N_Hitomi,
N_Gag00,
N_Gag01,
N_Gag02,
DB_SKIRT_TOP,
DB_SKIRT_TOPA,
DB_SKIRT_TOPB,
DB_SKIRT_BOT,
F_ADJUSTWIDTHSCALE,
A_ROOTBONE,
BUSTUP_TARGET,
NECK_LOOK_TARGET'''