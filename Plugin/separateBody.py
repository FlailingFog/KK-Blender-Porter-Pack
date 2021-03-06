'''
SEPARATE BODY SCRIPT
- Isolates the body
Usage:
- Run the script
'''

import bpy

class separate_Body(bpy.types.Operator):
    bl_idname = "kkb.separatebody"
    bl_label = "The separate body script"
    bl_description = "I wonder what this does"
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

        #Select all body related materials
        bodyMatList = ['cf_m_face_00', 'cf_m_mayuge_00', 'cf_m_noseline_00', 'cf_m_eyeline_00_up', 'cf_m_eyeline_down', 'cf_m_sirome_00', 'cf_m_sirome_00.001', 'cf_m_hitomi_00', 'cf_m_hitomi_00.001', 'cf_m_body', 'cf_m_tooth', 'cf_m_tang']

        for bodyMat in bodyMatList:
            try:
                bpy.context.object.active_material_index = body.data.materials.find(bodyMat)
                bpy.ops.object.material_slot_select()
            except:
                print('material wasn\'t found: ' + bodyMat)

        #Separate the body from everything else
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        #rename objects, remove unused material slots
        bpy.context.selected_objects[0].name = 'Clothes'
        bpy.context.selected_objects[1].name = 'Body'

        bpy.ops.object.material_slot_remove_unused()
                    
        return {'FINISHED'}
