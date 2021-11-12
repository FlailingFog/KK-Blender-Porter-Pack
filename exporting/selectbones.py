'''
SELECT BONES SCRIPT
- Selects bones that aren't needed. This is useful for reducing the bone count with the "Merge Weights" option in CATS

Usage:
- Make sure all the hair / accessory bones you want to keep are visible in pose mode
- Run the script
- Use the "Merge Weights to Parent" option in CATS (under Model Options)
'''

import bpy
from ..importing.finalizepmx import kklog

class select_bones(bpy.types.Operator):
    bl_idname = "kkb.selectbones"
    bl_label = "Preps things for export"
    bl_description = "Check the dropdown for more info"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene.placeholder
        prep_type = scene.prep_dropdown

        kklog('\nPrepping for export...')
        #Combine all objects
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.view_layer.objects.active=bpy.data.objects['Body']
        body = bpy.context.view_layer.objects.active
        bpy.ops.object.join()
        
        body.modifiers['Outline Modifier'].show_render = False
        body.modifiers['Outline Modifier'].show_viewport = False

        #Select the armature and make it active
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Armature'].hide = False
        bpy.data.objects['Armature'].select_set(True)
        bpy.context.view_layer.objects.active=bpy.data.objects['Armature']
        bpy.ops.object.mode_set(mode='POSE')

        if prep_type in ['A', 'B']:
            #show all bones on the armature
            allLayers = [True, True, True, True, True, True, True, True,
                        True, True, True, True, True, True, True, True,
                        True, True, True, True, True, True, True, True,
                        True, True, True, True, True, True, True, True]
            bpy.data.objects['Armature'].data.layers = allLayers
            bpy.ops.pose.select_all(action='DESELECT')

            #Select bones on layer 11
            armature = bpy.data.objects['Armature']
            for bone in armature.data.bones:
                if bone.layers[10]==True:
                    bone.select = True
            
            kklog('Using CATS to simplify bones...')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.cats_manual.merge_weights()

        if prep_type == 'A':
            
            bpy.context.object.data.edit_bones['Hips'].parent = None

            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')

            #Select bones on layer 3/5/12/13
            armature = bpy.data.objects['Armature']
            for bone in armature.data.bones:
                if bone.layers[11]==True or bone.layers[12] == True or bone.layers[2] == True or bone.layers[4] == True:
                    bone.select = True
            
            kklog('Using CATS to simplify more bones...')
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.cats_manual.merge_weights()

        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    

if __name__ == "__main__":
    bpy.utils.register_class(select_bones)

    # test call
    print((bpy.ops.kkb.selectbones('INVOKE_DEFAULT')))
