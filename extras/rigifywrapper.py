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

            armature.hide_set(True)
            bpy.ops.object.select_all(action='DESELECT')
            rig.select_set(True)
            bpy.context.view_layer.objects.active=rig
            rig.show_in_front = True
            bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
            bpy.context.tool_settings.mesh_select_mode = (False, False, True)
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

