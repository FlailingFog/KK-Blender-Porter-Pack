import bpy, json, time, traceback
from .. import common as c
from ..extras.linkshapekeys import link_keys

def clean_body():
        
        #change armature modifier
        body.modifiers[0].show_in_editmode = True
        body.modifiers[0].show_on_cage = True
        body.modifiers[0].show_expanded = False

def separate_everything(context):
    body = bpy.data.objects['Body']

    hair['KKBP outfit ID'] = int(outfit.name[-1:])

    #don't reparent hair if Categorize by SMR
    if context.scene.kkbp.categorize_dropdown not in ['D']:
        bpy.data.objects['Hair ' + outfit.name].parent = outfit

    bpy.context.view_layer.objects.active = body
    #remove unused material slots on all objects
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.material_slot_remove_unused()
            


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
                    body['SMR materials']['cf_Ohitomi_L02'],
                    body['SMR materials']['cf_Ohitomi_R02'],
                    body['SMR materials']['cf_Ohitomi_L'],
                    body['SMR materials']['cf_Ohitomi_R'],
                    body['SMR materials']['cf_O_namida_L'],
                    body['SMR materials']['cf_O_namida_M'],
                    body['SMR materials']['cf_O_namida_S'],
                    body['SMR materials']['o_tang'],
                    body['SMR materials']['o_tang_rigged'],
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
                    if material_list.get(base_name) and int(dupe_number) and 'cf_m_hitomi_00' not in base_name and body['SMR materials']['o_tang'] not in base_name:
                        mat.user_remap(material_list[base_name])
                        bpy.data.materials.remove(mat)
                    else:
                        c.kklog("Somehow found a false duplicate material but didn't merge: " + mat.name, 'warn')
             
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
                        c.kklog("Moving duplicate material {} in slot {} to the original slot {}".format(material_name, repeated_slot, repeats[material_name][0]))
                        mesh.active_material_index = repeated_slot
                        bpy.ops.object.material_slot_select()
                        mesh.active_material_index = repeats[material_name][0]
                        bpy.ops.object.material_slot_assign()
                        bpy.ops.mesh.select_all(action='DESELECT')

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.material_slot_remove_unused()


class separate_body(bpy.types.Operator):
    bl_idname = "kkbp.separatebody"
    bl_label = "The separate body script"
    bl_description = "Separates the Body, shadowcast and bonelyfans into separate objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            last_step = time.time()
            c.kklog('\nSeparating body, clothes, hair, hitboxes and shadowcast, then removing duplicate materials...')
            
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

            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            return{'FINISHED'}

        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
