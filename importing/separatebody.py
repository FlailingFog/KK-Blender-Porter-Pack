import bpy, json, time
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

        #delete the extra tongue material if there is one
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        def delete_material(mat_list):
            for mat in mat_list:
                mat_found = body.data.materials.find(mat)
                if mat_found > -1:
                    bpy.context.object.active_material_index = mat_found
                    bpy.ops.object.material_slot_select()
                else:
                    kklog('Material wasn\'t found when separating body materials: ' + mat, 'warn')
            bpy.ops.mesh.delete(type='VERT')
        delete_material(['cf_m_tang.001'])

        #check if there's a face material. If there isn't then the model most likely has a face02 face. Rename to correct name
        if body.data.materials.find('cf_m_face_00') == -1:
            for mat in body.data.materials:
                if 'cf_m_face_02 -' in mat.name:
                    mat.name = 'cf_m_face_00'

def add_freestyle_faces():
    body = bpy.data.objects['Body']
    #go into edit mode and deselect everything
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    #mark certain materials as freestyle faces
    def mark_as_freestyle(mat_list, search_type = 'exact'):
        for mat in mat_list:
            mat_found = body.data.materials.find(mat)      
            if mat_found > -1:
                bpy.context.object.active_material_index = mat_found
                bpy.ops.object.material_slot_select()
            else:
                kklog('Material wasn\'t found when separating body materials: ' + mat, 'warn')
        bpy.ops.mesh.mark_freestyle_face(clear=False)
    freestyle_list = [
        'cf_m_hitomi_00.001',
        'cf_m_hitomi_00',
        'cf_m_sirome_00.001',
        'cf_m_sirome_00',
        'cf_m_eyeline_kage',
        'cf_m_eyeline_down',
        'cf_m_eyeline_00_up',
        'cf_m_noseline_00',
        'cf_m_mayuge_00',]
    mark_as_freestyle(freestyle_list)
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')


def separate_material(object, mat_list, search_type = 'exact'):
    for mat in mat_list:
        mat_found = -1
        if search_type == 'fuzzy' and ('cm_m_' in mat or 'c_m_' in mat):
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
            kklog('Material wasn\'t found when separating body materials: ' + mat, 'warn')
    bpy.ops.mesh.separate(type='SELECTED')

def separate_everything(context):
    body = bpy.data.objects['Body']
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    #Select all body related materials, then separate it from everything else
    body_mat_list = [
        'cf_m_tang',
        'cf_m_eyeline_kage',
        'cf_m_namida_00',
        'cf_m_namida_00.001',
        'cf_m_namida_00.002',
        'cf_m_hitomi_00.001',
        'cf_m_hitomi_00',
        'cf_m_sirome_00.001',
        'cf_m_sirome_00',
        'cf_m_eyeline_down',
        'cf_m_eyeline_00_up',
        'cf_m_tooth',
        'cf_m_tooth.001',
        'cf_m_noseline_00',
        'cf_m_mayuge_00',
        'cf_m_face_00',
        'cf_m_face_00.001',
        'cm_m_body',
        'cf_m_body']
    separate_material(body, body_mat_list, 'fuzzy')
    bpy.data.objects['Body'].name = 'Clothes'
    bpy.data.objects['Body.001'].name = 'Body'
    clothes = bpy.data.objects['Clothes']
    body = bpy.data.objects['Body']

    #Select all materials that use the hair renderer
    json_file = open(context.scene.kkbp.import_dir[:-9] + 'KK_MaterialData.json')
    material_data = json.load(json_file)
    hair_mat_list = []
    for mat in material_data:
        if mat['ShaderName'] in ["Shader Forge/main_hair_front", "Shader Forge/main_hair", 'Koikano/hair_main_sun_front', 'Koikano/hair_main_sun', 'xukmi/HairPlus', 'xukmi/HairFrontPlus']:
            hair_mat_list.append(mat['MaterialName'])
    if len(hair_mat_list):
        separate_material(clothes, hair_mat_list)
    else:
        context.scene.kkbp.has_hair_bool = False
    bpy.data.objects['Clothes.001'].name = 'Hair'

    if context.scene.kkbp.categorize_dropdown in ['A', 'B']:
        #Select any clothes pieces that are normally supposed to be hidden and hide them
        json_file = open(context.scene.kkbp.import_dir[:-9] + 'KK_ClothesData.json')
        clothes_data = json.load(json_file)
        json_file = open(context.scene.kkbp.import_dir[:-9] + 'KK_SMRData.json')
        smr_data = json.load(json_file)

        clothes_labels = [
            'Top',
            'Bottom',
            'Bra',
            'Underwear',
            'Gloves',
            'Pantyhose',
            'Legwear',
            'Indoor shoes',
            'Outdoor shoes',
            'Top part A',
            'Top part B',
            'Top part C']

        #If there's multiple pieces to any clothing types, separate them into their own object using the smr data
        for clothes_index in [1, 2, 3, 4, 5, 6, 8]:
            if len(clothes_data[clothes_index]['RendNormal01']) > 1:
                for subpart_object_name in clothes_data[clothes_index]['RendNormal01']:
                    if '_a' not in subpart_object_name:
                        for smr_index in smr_data:
                            if smr_index['SMRName'] == subpart_object_name:
                                separate_material(clothes, smr_index['SMRMaterialNames'])
                                bpy.data.objects['Clothes.001'].name = clothes_labels[clothes_index] + ' alt ' + ('B' if '_b ' in subpart_object_name else 'C')
        
        #Always separate indoor shoes
        indoor_shoes_name = clothes_data[7]['RendNormal01']
        if indoor_shoes_name:
            for smr_index in smr_data:
                if smr_index['SMRName'] == indoor_shoes_name:
                    separate_material(clothes, smr_index['SMRMaterialNames'])
                    bpy.data.objects['Clothes.001'].name = clothes_labels[7]
                    bpy.data.objects[clothes_labels[7]].hide_render = True
                    bpy.data.objects[clothes_labels[7]].hide_viewport = True
        
        #If there's multiple pieces to the top, separate them into their own object, but make sure to group them correctly
        grouping = {'B':[], 'C':[]}
        for clothes_index in [0, 9, 10, 11]:
            print(clothes_index)
            for cat in ['RendNormal01', 'RendEmblem01', 'RendEmblem02']:
                if len(clothes_data[clothes_index][cat]) > 1 or (len(clothes_data[clothes_index][cat]) == 1 and cat not in 'RendNormal01'):
                    clothes_to_separate = clothes_data[clothes_index][cat]
                    if cat not in 'RendNormal01':
                        clothes_to_separate = [clothes_to_separate]
                    for subpart_object_name in clothes_to_separate:
                        if '_a ' not in subpart_object_name:
                            for smr_index in smr_data:
                                if smr_index['SMRName'] == subpart_object_name and '_b ' in subpart_object_name:
                                    for item in smr_index['SMRMaterialNames']:
                                        print(item)
                                        grouping['B'].append(item)
                                if smr_index['SMRName'] == subpart_object_name and '_c ' in subpart_object_name:
                                    for item in smr_index['SMRMaterialNames']:
                                        grouping['C'].append(item)
        if grouping['B']:
            print(grouping['B'])
            separate_material(clothes, grouping['B'])
            bpy.data.objects['Clothes.001'].name = 'Top alt B'
        if grouping['C']:
            print(grouping['C'])
            separate_material(clothes, grouping['C'])
            bpy.data.objects['Clothes.001'].name = 'Top alt C'

    #Separate hitbox materials, if any
    hit_box_list = []
    for mat in material_data:
        if mat['MaterialName'][0:6] == 'o_hit_' or mat['MaterialName'] == 'cf_O_face_atari_M':
            hit_box_list.append(mat['MaterialName'])
    if len(hit_box_list):
        separate_material(clothes, hit_box_list)
        bpy.data.objects['Clothes.001'].name = 'Hitboxes'

    #Separate the shadowcast if any
    try:
        bpy.ops.mesh.select_all(action = 'DESELECT')
        shad_mat_list = ['c_m_shadowcast', 'Standard']
        separate_material(clothes, shad_mat_list, 'fuzzy')
        bpy.data.objects['Clothes.001'].name = 'Shadowcast'
    except:
        pass
    
    #Separate the bonelyfans mesh if any
    try:
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bone_mat_list = ['Bonelyfans', 'Bonelyfans.001']
        separate_material(clothes, bone_mat_list)
        bpy.data.objects['Clothes.001'].name = 'Bonelyfans'
    except:
        pass

        #remove unused material slots on all objects
        bpy.ops.object.mode_set(mode = 'OBJECT')
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
    move_and_hide_collection(['Hitboxes'], "Hitbox Collection")

#merge certain materials for the body object to prevent odd shading issues later on
def fix_body_seams():
    bpy.ops.object.select_all(action='DESELECT')
    body = bpy.data.objects['Body']
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.mode_set(mode = 'EDIT')
    seam_list = [
        'cm_m_body',
        'cf_m_body',
        'cf_m_face_00',
        'cf_m_face_00.001']
    for mat in seam_list:
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
    bpy.ops.mesh.remove_doubles(threshold=0.00001)

def make_tear_shapekeys():
    body = bpy.data.objects['Body']
    #Create a reverse shapekey for each tear material
    armature = bpy.data.objects['Armature']
    tear_mats = ['cf_m_namida_00.002', 'cf_m_namida_00.001', 'cf_m_namida_00']
    for mat in tear_mats:
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.shape_key_add(from_mix=False)
        last_shapekey = len(body.data.shape_keys.key_blocks)-1
        if '.002' in mat:
            body.data.shape_keys.key_blocks["Key " + str(last_shapekey)].name = "Tear small"
            bpy.context.object.active_shape_key_index = last_shapekey
        elif '.001' in mat:
            body.data.shape_keys.key_blocks["Key " + str(last_shapekey)].name = "Tear med"
            bpy.context.object.active_shape_key_index = last_shapekey
        else:
            body.data.shape_keys.key_blocks["Key " + str(last_shapekey)].name = "Tear big"
            bpy.context.object.active_shape_key_index = last_shapekey
        
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
        #find a random vertex location of the tear
        bpy.ops.object.mode_set(mode = 'OBJECT')
        selected_verts = [v for v in body.data.vertices if v.select]
        bpy.ops.object.mode_set(mode = 'EDIT')
        amount_to_move_tears_back = selected_verts[0].co.y - armature.data.bones['cf_j_head'].head.y
        #create a new shapekey for the tear
        bpy.ops.transform.translate(value=(0, abs(amount_to_move_tears_back), 0))
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.cats_shapekey.shape_key_to_basis()
    body.data.shape_keys.key_blocks["Tear big - Reverted"].name = "KK Tears big"
    body.data.shape_keys.key_blocks["Tear med - Reverted"].name = "KK Tears med"
    body.data.shape_keys.key_blocks["Tear small - Reverted"].name = "KK Tears small"

    #Merge the tear materials
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    tear_mats = ['cf_m_namida_00.001', 'cf_m_namida_00.002']
    for mat in tear_mats:
        bpy.context.object.active_material_index = body.data.materials.find(mat)
        bpy.ops.object.material_slot_select()
        bpy.context.object.active_material_index = body.data.materials.find('cf_m_namida_00')
        bpy.ops.object.material_slot_assign()
        bpy.ops.mesh.select_all(action='DESELECT')

    #make a vertex group that does not contain the tears
    bpy.ops.object.vertex_group_add()
    bpy.ops.mesh.select_all(action='SELECT')
    body.vertex_groups.active.name = "Body without Tears"
    bpy.context.object.active_material_index = body.data.materials.find('cf_m_namida_00')
    bpy.ops.object.material_slot_deselect()
    bpy.ops.object.vertex_group_assign()

    #Separate tears from body object, parent it to the body so it's hidden in the outliner
    #link shapekeys of tears to body
    tearMats = [
        'cf_m_namida_00']
    bpy.ops.mesh.select_all(action='DESELECT')
    separate_material(body, tearMats)
    tears = bpy.data.objects['Body.001']
    tears.name = 'Tears'
    tears.parent = bpy.data.objects['Body']
    bpy.ops.object.mode_set(mode = 'OBJECT')
    link_keys(body, [tears])

def remove_duplicate_slots():
    #combine duplicated material slots
    bpy.ops.object.material_slot_remove_unused()
    body = bpy.data.objects['Body']
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active=body
    bpy.ops.object.mode_set(mode='EDIT')

    #remap duplicate materials to the base one
    material_list = body.data.materials
    for mat in material_list:
        #don't merge the eye materials if categorize by SMR is chosen.
        eye_flag = False if ('cf_m_hitomi_00' in mat.name or 'cf_m_sirome_00' in mat.name) and bpy.context.scene.kkbp.categorize_dropdown == 'D' else True
        
        if '.' in mat.name[-4:] and 'cf_m_namida_00' not in mat.name and eye_flag:
            base_name, dupe_number = mat.name.split('.',2)
            if material_list.get(base_name) and int(dupe_number):
                mat.user_remap(material_list[base_name])
                bpy.data.materials.remove(mat)
            else:
                kklog("Somehow found a false duplicate material but didn't merge: " + mat.name, 'warn')
    
    #then clean material slots by going through each slot and reassigning the slots that are repeated
    repeats = {}
    for index, mat in enumerate(material_list):
        if mat.name not in repeats:
            repeats[mat.name] = [index]
            #print("First entry of {} in slot {}".format(mat.name, index))
        else:
            repeats[mat.name].append(index)
            #print("Additional entry of {} in slot {}".format(mat.name, index))
    
    for material_name in list(repeats.keys()):
        if len(repeats[material_name]) > 1:
            for repeated_slot in repeats[material_name]:
                #don't touch the first slot
                if repeated_slot == repeats[material_name][0]:
                    continue
                kklog("Moving duplicate material {} in slot {} to the original slot {}".format(material_name, repeated_slot, repeats[material_name][0]))
                body.active_material_index = repeated_slot
                bpy.ops.object.material_slot_select()
                body.active_material_index = repeats[material_name][0]
                bpy.ops.object.material_slot_assign()
                bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.material_slot_remove_unused()

def cleanup():
    #remove shapekeys on all objects except the body because only the body needs them
    for obj in bpy.data.objects:
        if obj.name not in 'Body' and obj.type == 'MESH':
            for key in obj.data.shape_keys.key_blocks.keys():
                obj.shape_key_remove(obj.data.shape_keys.key_blocks[key])

    #make sure we are in object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    #remove unused material slots for all visible objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.material_slot_remove_unused()
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
        if ' alt ' in obj.name:
            obj.hide = True
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
        last_step = time.time()
        kklog('\nSeparating body, clothes, hair, hitboxes and shadowcast, then removing duplicate materials...')
        
        clean_body()
        add_freestyle_faces()
        remove_duplicate_slots()
        separate_everything(context)
        if context.scene.kkbp.fix_seams:
            fix_body_seams()
           
        #make tear shapekeys only if they exist 
        if context.scene.kkbp.shapekeys_dropdown != 'C':
            make_tear_shapekeys()
            
        cleanup()

        kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(separate_body)

    # test call
    print((bpy.ops.kkb.separatebody('INVOKE_DEFAULT')))
