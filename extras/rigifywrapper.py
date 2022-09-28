'''
Wrapper for the rigifyscripts folder
'''
import bpy
import bmesh
import math
from math import radians
import statistics
from ..importing.importbuttons import kklog
from mathutils import Matrix, Vector, Euler
import traceback
import sys

from typing import NamedTuple
import mathutils

from pathlib import Path

class rigify_convert(bpy.types.Operator):
    bl_idname = "kkb.rigifyconvert"
    bl_label = "Convert for rigify"
    bl_description = """Runs several scripts to convert a KKBP armature to be Rigify compatible"""
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            kklog('\nConverting to Rigify...')
            #Make the armature active
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            armature = bpy.data.objects['Armature']
            armature.hide_set(False)
            armature.select_set(True)
            bpy.context.view_layer.objects.active=armature

            bpy.ops.kkb.rigbefore('INVOKE_DEFAULT')

            bpy.ops.pose.rigify_generate()
            
            bpy.ops.kkb.rigafter('INVOKE_DEFAULT')
            
            #make sure things are parented correctly and hide original armature
            rig = bpy.context.active_object
            armature = bpy.data.objects['Armature']
            for child in armature.children:
                if child.name in ['Body'] or 'Outfit ' in child.name:
                    print(child.name)
                    #do for children first
                    for ob in child.children:
                        if ob.name in ['Tears'] or 'Outfit ' in ob.name:
                            print(ob.name)
                            hidden = ob.hide
                            parent = ob.parent
                            ob.hide = False 
                            bpy.ops.object.select_all(action='DESELECT')
                            ob.parent = None
                            ob.select_set(True)
                            rig.select_set(True)
                            bpy.context.view_layer.objects.active=rig
                            bpy.ops.object.parent_set(type='ARMATURE_NAME')
                            ob.hide = hidden
                            ob.parent = parent
                    hidden = child.hide
                    child.hide = False 
                    bpy.ops.object.select_all(action='DESELECT')
                    child.parent = None
                    child.select_set(True)
                    rig.select_set(True)
                    bpy.context.view_layer.objects.active=rig
                    bpy.ops.object.parent_set(type='ARMATURE_NAME')
                    child.hide = hidden

                    #find the last created armature modifier, replace it with the existing one
                    child.modifiers[0].object = child.modifiers[-1].object
                    child.modifiers.remove(child.modifiers[-1])
                    child.modifiers[0].name = 'Rigify Armature'

            #make sure the new bones on the generated rig retain the KKBP outfit id entry
            for bone in rig.data.bones:
                if bone.layers[0] == True or bone.layers[2] == True:
                    if rig.data.bones.get('ORG-' + bone.name):
                        if rig.data.bones['ORG-' + bone.name].get('KKBP outfit ID'):
                            bone['KKBP outfit ID'] = rig.data.bones['ORG-' + bone.name]['KKBP outfit ID']
                            if rig.data.bones.get('DEF-' + bone.name):
                                rig.data.bones['DEF-' + bone.name]['KKBP outfit ID'] = rig.data.bones['ORG-' + bone.name]['KKBP outfit ID']

            #make sure the gfn empty is reparented to the head bone
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = rig
            empty = bpy.data.objects['GFN Empty']
            empty.hide = False
            empty.select_set(True)
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')
            rig.data.bones['head'].select = True
            rig.data.bones.active = rig.data.bones['head']
            bpy.ops.object.parent_set(type='BONE')
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.node_groups['Generated Face Normals'].nodes['GFNEmpty'].object = empty
            bpy.context.view_layer.objects.active = empty
            empty.select_set(True)
            bpy.ops.object.move_to_collection(collection_index=1)
            empty.hide = True
            empty.hide_render = True

            #delete nsfw bones if sfw mode enebled
            if bpy.context.scene.kkbp.sfw_mode:
                def delete_group_and_bone(group_list):
                    #delete bones too
                    bpy.ops.object.mode_set(mode = 'OBJECT')
                    bpy.ops.object.select_all(action='DESELECT')
                    rig.select_set(True)
                    bpy.context.view_layer.objects.active = rig
                    bpy.ops.object.mode_set(mode = 'EDIT')
                    bpy.ops.armature.select_all(action='DESELECT')
                    for bone in group_list:
                        if rig.data.bones.get(bone):
                            rig.data.edit_bones[bone].select = True
                            bpy.ops.armature.delete()
                        else:
                            kklog('Bone wasn\'t found when deleting bones: ' + bone, 'warn')
                    bpy.ops.armature.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode = 'OBJECT')

                delete_list = ['cf_s_bnip025_L', 'cf_s_bnip025_R',
                'cf_j_kokan', 'cf_j_ana', 'cf_d_ana', 'cf_d_kokan', 'cf_s_ana',
                'cf_J_Vagina_root',
                'cf_J_Vagina_B',
                'cf_J_Vagina_F',
                'cf_J_Vagina_L.005',
                'cf_J_Vagina_R.005',
                'cf_J_Vagina_L.004',
                'cf_J_Vagina_L.001',
                'cf_J_Vagina_L.002',
                'cf_J_Vagina_L.003',
                'cf_J_Vagina_R.001',
                'cf_J_Vagina_R.002',
                'cf_J_Vagina_R.003',
                'cf_J_Vagina_R.004',
                'cf_j_bnip02root_L',
                'cf_j_bnip02_L',
                'cf_s_bnip01_L',
                'cf_s_bust03_L',
                'cf_s_bust02_L',
                'cf_j_bnip02root_R',
                'cf_j_bnip02_R',
                'cf_s_bnip01_R',
                'cf_s_bust03_R',
                'cf_s_bust02_R',]
                delete_group_and_bone(delete_list)

            armature.hide_set(True)
            bpy.ops.object.select_all(action='DESELECT')
            rig.select_set(True)
            bpy.context.view_layer.objects.active=rig
            rig.show_in_front = True
            bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
            bpy.context.tool_settings.mesh_select_mode = (False, False, True) #enable face select in edit mode
            return {'FINISHED'}
            
        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(rigify_convert)

    # test call
    print((bpy.ops.kkb.rigifyconvert('INVOKE_DEFAULT')))

