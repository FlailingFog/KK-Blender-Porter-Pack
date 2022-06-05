'''
SHAPEKEYS SCRIPT
- Renames the face shapekeys to english
- Creates new, full shapekeys using the existing partial shapekeys
- Deletes the partial shapekeys if keep_partial_shapekeys is not set to True
'''

import bpy, time
import bmesh
from .importbuttons import kklog

################################
#Translate most of the shapekeys
def translate_shapekeys():

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

    body = bpy.data.objects['Body']
    body.active_shape_key_index = 0
    
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
                    body.active_shape_key_index = body.data.shape_keys.key_blocks.keys().index(keyblock.name)
                    bpy.ops.object.shape_key_remove()

                #delete the 'bounse' shapekey that sometimes appears on pmx imports
                if 'bounse' in keyblock.name:
                    body.active_shape_key_index = body.data.shape_keys.key_blocks.keys().index(keyblock.name)
                    bpy.ops.object.shape_key_remove()
            except:
                #or not
                kklog("Couldn't delete shapekey: " + keyblock.name, 'error')
                pass
    

########################################################
#Fix the right eyewhites/sirome shapekeys for pmx imports only
def fix_eyewhite_shapekeys():
    armature = bpy.data.objects['Armature']

    bpy.ops.object.mode_set(mode = 'OBJECT')
    body = bpy.data.objects['Body']
    body.active_shape_key_index = 0

    #Remove the ### tag on the second eyewhite material
    for mat in body.data.materials:
        if 'cf_m_sirome_00' in mat.name and len(mat.name) > 15:
            mat.name = 'cf_m_sirome_00.001'

    #Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    #Select the Body object
    body.select_set(True)
    #and make it active
    bpy.context.view_layer.objects.active = body

    #merge the sirome materials into one
    try:
        #loop through all materials and get the two sirome materials
        currentMat=0
        eyewhitePos=0
        eyewhiteMats = [None,None]
        materialCount = len(body.data.materials.values())-1
        while currentMat <= materialCount:
            if 'cf_m_sirome_00' in body.data.materials[currentMat].name:
                eyewhiteMats[eyewhitePos] = body.data.materials[currentMat].name
                eyewhitePos+=1
            currentMat+=1

        bpy.context.object.active_material_index = body.data.materials.find(eyewhiteMats[0])
        #The script will fail here if the sirome material was already merged
        while body.data.materials.find(eyewhiteMats[0]) > body.data.materials.find(eyewhiteMats[1]) and body.data.materials.find(eyewhiteMats[1]) != -1:
            bpy.ops.object.material_slot_move(direction='UP')

        body.data.materials[body.data.materials.find(eyewhiteMats[0])].name = 'cf_m_sirome_00.temp'
        body.data.materials[body.data.materials.find(eyewhiteMats[1])].name = 'cf_m_sirome_00'
        body.data.materials[body.data.materials.find('cf_m_sirome_00.temp')].name = 'cf_m_sirome_00.001'

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.context.object.active_material_index = body.data.materials.find(eyewhiteMats[0])
        bpy.ops.object.material_slot_select()
        bpy.context.object.active_material_index = body.data.materials.find(eyewhiteMats[1])
        bpy.ops.object.material_slot_assign()

    except:
        #the sirome material was already merged
        body.data.materials[body.data.materials.find(eyewhiteMats[0])].name = 'cf_m_sirome_00'
        pass

    #delete the right eyewhites mesh
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.context.object.active_material_index = body.data.materials.find('cf_m_sirome_00')
    bpy.ops.object.material_slot_select()

    #refresh the selection
    #bpy.ops.object.mode_set(mode = 'OBJECT')
    #bpy.ops.object.mode_set(mode = 'EDIT')
    bm = bmesh.from_edit_mesh(body.data)
    bm.select_flush_mode()   
    body.data.update()

    bm = bmesh.from_edit_mesh(body.data)
    vgVerts = [v for v in bm.verts if v.select]

    for v in vgVerts:
        v.select = (v.co.x < 0)

    vgVerts = [v for v in bm.verts if v.select]

    bm.select_flush_mode()   
    body.data.update()

    bmesh.ops.delete(bm, geom=vgVerts, context='VERTS')
    bmesh.update_edit_mesh(body.data)

    #assign the left eyewhites into a vertex group
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.context.object.active_material_index = body.data.materials.find('cf_m_sirome_00')
    bpy.ops.object.material_slot_select()

    bm = bmesh.from_edit_mesh(body.data)
    vgVerts = [v for v in bm.verts if v.select]

    bpy.ops.object.vertex_group_add()
    bpy.ops.object.vertex_group_assign()
    body.vertex_groups.active.name = "EyewhitesL"

    #duplicate the left eyewhites
    bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
    bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    #and mirror it on the x axis to recreate the right eyewhites
    bm = bmesh.from_edit_mesh(body.data)
    vgVerts = [v for v in bm.verts if v.select]

    for v in vgVerts:
        v.co.x *=-1

    bm.select_flush_mode()
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    body.data.update()

    #remove eyewhiter vertices from eyewhiteL group
    bpy.ops.object.vertex_group_remove_from()

    #make eyewhiter vertex group
    bpy.ops.object.vertex_group_add()
    bpy.ops.object.vertex_group_assign()
    body.vertex_groups.active.name = "EyewhitesR"

    #then recalculate normals for the right group to avoid outline issues later on
    bpy.ops.object.material_slot_select()
    #why is this so fucking finicky
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.object.mode_set(mode = 'OBJECT')

    #make eyewhiteL shapekeys only affect the eyewhiteL vertex group
    #ditto for right
    for shapekey in bpy.data.shape_keys:
        for keyblock in shapekey.key_blocks:
            if 'EyeWhitesL_' in keyblock.name:
                keyblock.vertex_group = 'EyewhitesL'
            elif 'EyeWhitesR_' in keyblock.name:
                keyblock.vertex_group = 'EyewhitesR'

######################
#Combine the shapekeys
def combine_shapekeys(keep_partial_shapekeys):
    #make the basis shapekey active
    body = bpy.data.objects['Body']
    body.active_shape_key_index = 0

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
    shapekey_block = bpy.data.shape_keys[body.data.shape_keys.name].key_blocks

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
                for c in correctionList:
                    if c in current_keyblock.name:
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
                    bpy.data.objects['Body'].shape_key_add(name=('KK ' + cat + emotion))

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
    if not keep_partial_shapekeys:
        for remove_shapekey in shapekey_block:
            try:
                if ('KK ' not in remove_shapekey.name and remove_shapekey.name != shapekey_block[0].name):
                    body.shape_key_remove(remove_shapekey)
            except:
                #I don't know if this needs to be in a try catch anymore
                kklog('Couldn\'t remove shapekey ' + remove_shapekey.name, 'error')
                pass
    
    #make the basis shapekey active
    body.active_shape_key_index = 0
    
    #and reset the pivot point to median
    bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        

class shape_keys(bpy.types.Operator):
    bl_idname = "kkb.shapekeys"
    bl_label = "The shapekeys script"
    bl_description = "Fixes the shapekeys"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        last_step = time.time()
        scene = context.scene.kkbp
        
        if scene.shapekeys_dropdown in ['A', 'B'] :
            keep_partial_shapekeys = scene.shapekeys_dropdown == 'B'

            kklog('\nTranslating and combining shapekeys...', type = 'timed')
            translate_shapekeys()
            combine_shapekeys(keep_partial_shapekeys)
            
            kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(shape_keys)

    # test call
    print((bpy.ops.kkb.shapekeys('INVOKE_DEFAULT')))
