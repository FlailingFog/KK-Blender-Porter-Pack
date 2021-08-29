'''
SEPARATE BODY SCRIPT
- Isolates the body
- Attempts to isolate the bonelyfans and shadowcast meshes as well
Usage:
- Run the script
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
            'cf_m_noseline_00',
            'cf_m_mayuge_00',
            'cf_m_face_00']
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
        
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(separate_body)

    # test call
    print((bpy.ops.kkb.separatebody('INVOKE_DEFAULT')))
