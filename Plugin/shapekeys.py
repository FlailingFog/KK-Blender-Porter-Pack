'''
AFTER CATS (SHAPEKEYS) SCRIPT
- Renames the face shapekeys to english
- Creates new, full shapekeys using the existing partial shapekeys
- Deletes the partial shapekeys if debugMode is not set to True (the first variable below this description)
Usage:
- Make sure the Fix Model button has already been used in CATS
- Run the script
Tested in Blender 2.91
'''

import bpy
import bmesh

class shape_keys(bpy.types.Operator):
    bl_idname = "kkb.shapekeys"
    bl_label = "The shapekeys script"
    bl_description = "Fixes the shapekeys"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #Enable debug mode to prevent the shapekey list from being cleaned out after the KK shapekeys are created
        scene = context.scene.placeholder
        debugMode = scene.shapekey_bool

        #########################
        #Translate most of the shapekeys

        def renameCategory(keyName):
            keyName = keyName.replace("eye_face.f00", "Eyes")
            keyName = keyName.replace("kuti_face.f00", "Lips")
            keyName = keyName.replace("eye_siroL.sL00", "EyeWhitesL")
            keyName = keyName.replace("eye_siroR.sR00", "EyeWhitesR")
            keyName = keyName.replace("eye_line_u.elu00", "Eyelashes1")
            keyName = keyName.replace("eye_line_l.ell00", "Eyelashes2")
            keyName = keyName.replace("eye_naM.naM00", "EyelashesPos")
            keyName = keyName.replace("eye_nose.nl00", "NoseTop")
            keyName = keyName.replace("kuti_nose.nl00", "NoseBot")
            keyName = keyName.replace("kuti_ha.ha00", "Teeth")
            keyName = keyName.replace("kuti_yaeba.y00", "Fangs")
            keyName = keyName.replace("kuti_sita.t00", "Tongue")
            keyName = keyName.replace("mayuge.mayu00", "KK Eyebrows")
            
            #Exception if a previous version of the script was already run
            if keyName.find('Eyebrows_') > -1 and keyName.find('KK Eyebrows_') == -1:
                keyName = keyName.replace('Eyebrows_', 'KK Eyebrows_')
                
            return keyName 

        def renameEmotion(keyName):
            keyName = keyName.replace("_def_", "_default_")
            keyName = keyName.replace("_egao_", "_smile_")
            keyName = keyName.replace("_bisyou_", "_smile_sharp_")
            keyName = keyName.replace("_uresi_ss_", "_happy_slight_")
            keyName = keyName.replace("_uresi_s_", "_happy_moderate_")
            keyName = keyName.replace("_uresi_", "_happy_broad_")
            keyName = keyName.replace("_doki_ss_", "_doki_slight_")
            keyName = keyName.replace("_doki_s_", "_doki_moderate_")
            keyName = keyName.replace("_ikari_", "_angry_")
            keyName = keyName.replace("_ikari02_", "_angry_2_")
            keyName = keyName.replace("_sinken_", "_serious_")
            keyName = keyName.replace("_sinken02_", "_serious_1_")
            keyName = keyName.replace("_sinken03_", "_serious_2_")
            keyName = keyName.replace("_keno_", "_hate_")
            keyName = keyName.replace("_sabisi_", "_lonely_")
            keyName = keyName.replace("_aseri_", "_impatient_")
            keyName = keyName.replace("_huan_", "_displeased_")
            keyName = keyName.replace("_human_", "_displeased_")
            keyName = keyName.replace("_akire_", "_amazed_")
            keyName = keyName.replace("_odoro_", "_shocked_")
            keyName = keyName.replace("_odoro_s_", "_shocked_moderate_")
            keyName = keyName.replace("_doya_", "_smug_")
            keyName = keyName.replace("_pero_", "_lick_")
            keyName = keyName.replace("_name_", "_eating_")
            keyName = keyName.replace("_tabe_", "_eating_2_")
            keyName = keyName.replace("_kuwae_", "_hold_in_mouth_")
            keyName = keyName.replace("_kisu_", "_kiss_")
            keyName = keyName.replace("_name02_", "_tongue_out_")
            keyName = keyName.replace("_mogu_", "_chewing_")
            keyName = keyName.replace("_niko_", "_cartoon_mouth_")
            keyName = keyName.replace("_san_", "_triangle_")
            
            keyName = keyName.replace("_winkl_", "_wink_left_")
            keyName = keyName.replace("_winkr_", "_wink_right_")
            keyName = keyName.replace("_setunai_", "_distress_")
            keyName = keyName.replace("_tere_", "_shy_")
            keyName = keyName.replace("_tmara_", "_bored_")
            keyName = keyName.replace("_tumara_", "_bored_")
            keyName = keyName.replace("_kurusi_", "_pain_")
            keyName = keyName.replace("_sian_", "_thinking_")
            keyName = keyName.replace("_kanasi_", "_sad_")
            keyName = keyName.replace("_naki_", "_crying_")
            keyName = keyName.replace("_rakutan_", "_dejected_")
            keyName = keyName.replace("_komaru_", "_worried_")
            if 'gageye' not in keyName:
                keyName = keyName.replace("_gag", "_gageye")
            keyName = keyName.replace("_gyul_", "_squeeze_left_")
            keyName = keyName.replace("_gyur_", "_squeeze_right_")
            keyName = keyName.replace("_gyu_", "_squeeze_")
            keyName = keyName.replace("_gyul02_", "_squeeze_left_2_")
            keyName = keyName.replace("_gyur02_", "_squeeze_right_2_")
            keyName = keyName.replace("_gyu02_", "_squeeze_2_")
            
            keyName = keyName.replace("_koma_", "_worried_")
            keyName = keyName.replace("_gimoL_", "_doubt_left_")
            keyName = keyName.replace("_gimoR_", "_doubt_right_")
            keyName = keyName.replace("_sianL_", "_thinking_left_")
            keyName = keyName.replace("_sianR_", "_thinking_right_")
            keyName = keyName.replace("_oko_", "_angry_")
            keyName = keyName.replace("_oko2L_", "_angry_left_")
            keyName = keyName.replace("_oko2R_", "_angry_right_")
                
            keyName = keyName.replace("_s_", "_small_")
            keyName = keyName.replace("_l_", "_big_")
                
            return keyName 

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
                keyblock.name = renameCategory(keyblock.name)
                keyblock.name = renameEmotion(keyblock.name)
                
                try:
                    #delete the KK shapekeys if the original shapekeys still exist
                    #fucking thing doesn't even work
                    if originalExists and 'KK ' in keyblock.name and 'KK Eyebrows' not in keyblock.name:
                        body.active_shape_key_index = body.data.shape_keys.key_blocks.keys().index(keyblock.name)
                        bpy.ops.object.shape_key_remove()

                    #delete the 'bounse' shapekey that sometimes appears on import
                    if 'bounse' in keyblock.name:
                        body.active_shape_key_index = body.data.shape_keys.key_blocks.keys().index(keyblock.name)
                        bpy.ops.object.shape_key_remove()
                except:
                    #or not
                    print("couldn't delete key: " + keyblock.name)
                    pass
        
        ########################################################
        #Fix the eyewhites/sirome shapekeys

        body = bpy.data.objects['Body']
        body.active_shape_key_index = 0
        
        #Remove the "Instance" tag on all materials
        materialCount = len(body.data.materials.values())-1
        currentMat=0
        while currentMat <= materialCount:
            body.data.materials[currentMat].name = body.data.materials[currentMat].name.replace(' (Instance)','')
            currentMat+=1
            
        #Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        #Select the Body object
        body.select_set(True)
        #and make it active
        bpy.context.view_layer.objects.active = body

        bpy.context.object.active_material_index = body.data.materials.find('cf_m_sirome_00')

        #merge the sirome materials into one
        try:
            while body.data.materials.find('cf_m_sirome_00') > body.data.materials.find('cf_m_sirome_00.001') and body.data.materials.find('cf_m_sirome_00.001') != -1:
                bpy.ops.object.material_slot_move(direction='UP')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.context.object.active_material_index = body.data.materials.find('cf_m_sirome_00.001')
            bpy.ops.material_slot_select()
            bpy.context.object.active_material_index = body.data.materials.find('cf_m_sirome_00')
            bpy.ops.material_slot_assign()

        except:
            #the sirome material was already merged
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
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

        #and mirror it on the x axis to recreate the right eyewhites
        bm = bmesh.from_edit_mesh(body.data)
        vgVerts = [v for v in bm.verts if v.select]

        for v in vgVerts:
            v.co.x *=-1

        bm.select_flush_mode()   
        body.data.update()
        
        #remove eyewhiter vertices from eyewhiteL group
        bpy.ops.object.vertex_group_remove_from()
        
        #make eyewhiter vertex group
        bpy.ops.object.vertex_group_add()
        bpy.ops.object.vertex_group_assign()
        body.vertex_groups.active.name = "EyewhitesR"
        
        #then recalculate normals for the right group to avoid outline issues later on
        bpy.ops.mesh.normals_make_consistent(inside=False)

        bpy.ops.object.mode_set(mode = 'OBJECT')

        #make eyewhiteL shapekeys only affect the eyewhiteL vertex group
        #ditto for right
        for shapekey in bpy.data.shape_keys:
            for keyblock in shapekey.key_blocks:
                if 'EyeWhitesL_' in keyblock.name:
                    keyblock.vertex_group = 'EyewhitesL'
                elif 'EyeWhitesR_' in keyblock.name:
                    keyblock.vertex_group = 'EyewhitesR'

        ########################################################
        #Combine the shapekeys

        #make the basis shapekey active
        body.active_shape_key_index = 0

        def whatCat(keyName):
            #Eyelashes1 is used because I couldn't see a difference between the other one and they overlap if both are used
            #EyelashPos is unused because Eyelashes work better and it overlaps with Eyelashes
            #eye_nal is unused because it apparently screws with face accessories
            
            eyes = [keyName.find("Eyes"), keyName.find("NoseT"), keyName.find("Eyelashes1"), keyName.find("EyeWhitesL"), keyName.find("EyeWhitesR")]
            if not all(v == -1 for v in eyes):
                return 'Eyes'
            
            mouth = [keyName.find("NoseB"), keyName.find("Lips"), keyName.find("Tongue"), keyName.find("Teeth"), keyName.find("Fangs")]
            if not all(v==-1 for v in mouth):
                return 'Mouth'
            
            return 'None'

        #setup two arrays to keep track of the shapekeys that have been used
        #and the shapekeys currently in use
        used = []
        inUse = []

        #These shapekeys require the default teeth and tongue shapekeys to be active
        correctionList = ['Lips_u_small_op', 'Lips_u_big_op', 'Lips_e_big_op', 'Lips_o_small_op', 'Lips_o_big_op', 'Lips_neko_op', 'Lips_triangle_op']

        counter = len(bpy.data.shape_keys[0].key_blocks)

        ACTIVE = 0.9

        for shapekey in bpy.data.shape_keys:
            for keyblock in shapekey.key_blocks:
                
                counter = counter - 1
                print(counter)
                if (counter == 0):
                    break
                
                #What category is this shapekey (mouth, eyes or neither)?
                cat = whatCat(keyblock.name)
                
                #get the emotion for mouth or eyes from the shapekey name
                if not (cat.find('None') == 0):
                    emotion = keyblock.name[keyblock.name.find("_"):]
                    
                    #assign each keyblock a category and emotion combo
                    for keyblockCheck in shapekey.key_blocks:
                        
                        #does this key match my current emotion?
                        if (keyblockCheck.name.find(emotion) > -1):
                            
                            #does this key match my current category?
                            if whatCat(keyblock.name) == whatCat(keyblockCheck.name):
                                
                                #I haven't already used this key right?
                                if (keyblockCheck.name not in used):
                                    keyblockCheck.value = ACTIVE
                                    inUse.append(keyblockCheck.name)
                                    
                    #Manual corrections
                    if (keyblock.name in correctionList):
                        try:
                            shapekey.key_blocks['Fangs_default_op'].value = ACTIVE
                        except:
                            #this character doesn't have fangs
                            pass
                        shapekey.key_blocks['Teeth_default_op'].value = ACTIVE
                        shapekey.key_blocks['Tongue_default_op'].value = ACTIVE
                    
                    if (keyblock.name == 'Lips_e_small_op'):
                        try:
                            shapekey.key_blocks['Fangs_default_op'].value = ACTIVE
                        except:
                            #this character doesn't have fangs
                            pass
                        
                    if (keyblock.name == 'Lips_cartoon_mouth_op'):
                        shapekey.key_blocks['Tongue_default_op'].value = ACTIVE
                    
                    if (keyblock.name == 'Lips_smile_sharp_op'):
                        try:
                            #Someone had an issue with this shapekey so into a try catch it goes
                            shapekey.key_blocks['Teeth_smile_sharp_op1'].value = 0
                        except:
                            pass
                    
                    if (keyblock.name == 'Lips_eating_2_op'):
                        try:
                            shapekey.key_blocks['Fangs_default_op'].value = ACTIVE
                        except:
                            #this character doesn't have fangs
                            pass
                        shapekey.key_blocks['Teeth_tongue_out_op'].value = ACTIVE
                        shapekey.key_blocks['Tongue_serious_2_op'].value = ACTIVE
                        
                    if (keyblock.name == 'Lips_i_big_op'):
                        shapekey.key_blocks['Teeth_i_big_cl'].value = ACTIVE
                        try:
                            shapekey.key_blocks['Fangs_default_op'].value = ACTIVE
                        except:
                            #this character doesn't have fangs
                            pass
                        
                    if (keyblock.name == 'Lips_i_small_op'):
                        shapekey.key_blocks['Teeth_i_small_cl'].value = ACTIVE
                        try:
                            shapekey.key_blocks['Fangs_default_op'].value = ACTIVE
                        except:
                            #this character doesn't have fangs
                            pass
                        
                    if (keyblock.name not in used):
                        #print('Creating combined shapekey')
                        bpy.data.objects['Body'].shape_key_add(name=('KK ' + cat + emotion))
                        #print('appended this to used ' + keyblock.name)
                        
                    for thing in inUse:
                        used.append(thing)
                        
                    #reset shapekey values
                    for keyblock in shapekey.key_blocks:
                        keyblock.value = 0
                            
                    inUse =[]

        #Delete all shapekeys that don't have a "KK" in their name
        if not debugMode:
            for shapekey in bpy.data.shape_keys:
                for keyblock in shapekey.key_blocks:
                    try:
                        if (keyblock.name.find('KK ') == -1 and keyblock.name.find('Basis') != 0 and shapekey.user.name == 'Model'):
                            bpy.data.objects['Body'].shape_key_remove(keyblock)
                            #print(keyblock.name)
                    except:
                        #The script tried to remove a shapekey on a non-body object
                        #shapekeys are only used for the face so this is okay
                        pass
        
        #make the basis shapekey active
        body.active_shape_key_index = 0
        
        #and reset the pivot point to median
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(shape_keys)

    # test call
    print((bpy.ops.kkb.shapekeys('INVOKE_DEFAULT')))
