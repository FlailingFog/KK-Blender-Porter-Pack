'''
SEPARATE BODY SCRIPT
- Isolates the body
- Attempts to isolate the bonelyfans and shadowcast meshes
- Combines duplicated material slots
'''

import bpy

class separate_body(bpy.types.Operator):
    bl_idname = "kkb.separatebody"
    bl_label = "The separate body script"
    bl_description = "Separates the Body, shadowcast and bonelyfans into separate objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        #Select the body and make it active
        bpy.ops.object.mode_set(mode = 'OBJECT')
        body = bpy.data.objects['Body']
        bpy.ops.object.select_all(action='DESELECT')
        body.select_set(True)
        bpy.context.view_layer.objects.active = body

        #Remove the "Instance" tag on all materials
        materialCount = len(body.data.materials.values())-1
        currentMat=0
        while currentMat <= materialCount:
            body.data.materials[currentMat].name = body.data.materials[currentMat].name.replace(' (Instance)','')
            currentMat+=1

        #go into edit mode and deselect everything
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        
        def separateMaterial(matList):
            for mat in matList:
                try:
                    bpy.context.object.active_material_index = body.data.materials.find(mat)
                    
                    #moves the materials in a specific order to match the pmx file
                    def moveUp():
                        return bpy.ops.object.material_slot_move(direction='UP')
                    while moveUp() != {"CANCELLED"}:
                        pass
                    
                    bpy.ops.object.material_slot_select()
                except:
                    print('material wasn\'t found: ' + mat)
            bpy.ops.mesh.separate(type='SELECTED')
                    
        #Select all body related materials, then separate it from everything else
        #This puts hair/clothes in position 1 and the body in position 2
        bodyMatList = [
            'cm_m_body.001',
            'cf_m_body.001',
            'cm_m_body',
            'cf_m_body',
            'cf_m_tang',
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
            'cf_m_face_00.001']
        separateMaterial(bodyMatList)

        #Separate the shadowcast if any, placing it in position 3
        try:
            bpy.ops.mesh.select_all(action = 'DESELECT')
            shadMatList = ['c_m_shadowcast', 'Standard']
            separateMaterial(shadMatList)
        except:
            pass
        
        #Separate the bonelyfans mesh if any, placing it in position 4
        try:
            bpy.ops.mesh.select_all(action = 'DESELECT')
            boneMatList = ['Bonelyfans', 'Bonelyfans.001']
            separateMaterial(boneMatList)
        except:
            pass
        
        #rename objects, remove unused material slots
        rename = bpy.context.selected_objects
        rename[0].name = 'Clothes'
        rename[1].name = 'Body'
        try:
            rename[2].name = 'Shadowcast'
            rename[3].name = 'Bonelyfans'
        except:
            pass

        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.material_slot_remove_unused()
        
        #and move the shadowcast/bonelyfans to their own collection
        bpy.ops.object.select_all(action='DESELECT')
        try:
            rename[2].select_set(True)
        except:
            pass
        try:
            rename[3].select_set(True)
        except:
            pass
        
        bpy.ops.object.move_to_collection(collection_index=0, is_new=True, new_collection_name="Shadowcast Collection")
        
        #hide the new collection
        try:
            bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children['Shadowcast Collection']
            bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
        except:
            try:
                #maybe the collection is in the default Collection collection
                bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children['Collection'].children['Shadowcast Collection']
                bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
            except:
                #maybe the collection is already hidden
                pass
        
        #also, merge certain materials for the body object to prevent odd shading issues later on
        bpy.ops.object.select_all(action='DESELECT')
        body = bpy.data.objects['Body']
        body.select_set(True)
        bpy.context.view_layer.objects.active = body
        bpy.ops.object.mode_set(mode = 'EDIT')
        
        merge_list = [
            'cm_m_body.001',
            'cf_m_body.001',
            'cm_m_body',
            'cf_m_body',
            'cf_m_face_00',
            'cf_m_face_00.001']
        for mat in merge_list:
            bpy.context.object.active_material_index = body.data.materials.find(mat)
            bpy.ops.object.material_slot_select()
        bpy.ops.mesh.remove_doubles(threshold=0.0001)

        #then combine duplicated material slots
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.material_slot_remove_unused()
        clothes = bpy.data.objects['Clothes']
        bpy.ops.object.select_all(action='DESELECT')
        clothes.select_set(True)
        bpy.context.view_layer.objects.active=clothes
        bpy.ops.object.mode_set(mode='EDIT')

        #remap duplicate materials to the base one
        material_list = clothes.data.materials
        for mat in material_list:
            if '.' in mat.name:
                base_name, dupe_number = mat.name.split('.',2)
                if int(dupe_number):
                    mat.user_remap(material_list[base_name])
                    bpy.data.materials.remove(mat)
        
        #Clean material slots by going through each slot and reassigning the slots that are repeated
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
                    print("moving duplicate material {} in slot {} to the original slot {}".format(material_name, repeated_slot, repeats[material_name][0]))
                    clothes.active_material_index = repeated_slot
                    bpy.ops.object.material_slot_select()
                    clothes.active_material_index = repeats[material_name][0]
                    bpy.ops.object.material_slot_assign()
                    bpy.ops.mesh.select_all(action='DESELECT')

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.material_slot_remove_unused()

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

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(separate_body)

    # test call
    print((bpy.ops.kkb.separatebody('INVOKE_DEFAULT')))
