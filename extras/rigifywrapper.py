'''
Wrapper for the rigifyscripts folder
'''
import bpy
import bmesh
import math
from math import radians
import statistics
from mathutils import Matrix, Vector, Euler
import traceback
import sys

from typing import NamedTuple
import mathutils

from pathlib import Path

class rigify_convert(bpy.types.Operator):
    bl_idname = "kkb.rigifyconvert"
    bl_label = "Convert for rigify"
    bl_description = """Converts the armature to be Rigify compatible.
    The first time you click the button, the armature will be converted to a metarig.
    Every time after you click the button, a Rigify rig will be generated and a cleanup script will be run"""
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #Make the armature active
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        armature = bpy.data.objects['Armature']
        armature.hide = False
        armature.select_set(True)
        bpy.context.view_layer.objects.active=armature

        if armature.data.bones.get('Eyes handle'):
            bpy.ops.pose.rigify_generate()
            
            after = Path( __file__ ).parent
            after = after.joinpath('rigifyscripts', 'After Each Rigify Generate - Public.py')
            text = bpy.data.texts.load(str(after))
            exec(text.as_string())
            
            #make sure things are parented correctly and hide original armature
            rig = bpy.data.objects['rig']
            if len(armature.children):
                for child in armature.children:
                    if child.name != 'Bonelyfans' and child.name != 'Shadowcast':
                        bpy.ops.object.select_all(action='DESELECT')
                        child.parent = None
                        child.select_set(True)
                        rig.select_set(True)
                        bpy.context.view_layer.objects.active=rig
                        bpy.ops.object.parent_set(type='ARMATURE_NAME')
            armature.hide = True
            bpy.ops.object.select_all(action='DESELECT')
            rig.select_set(True)
            bpy.context.view_layer.objects.active=rig
            rig.show_in_front = True

        else:
            common = Path( __file__ ).parent
            common = common.joinpath('rigifyscripts', 'Koikatsu Commons.py')
            text = bpy.data.texts.load(str(common))

            before = Path( __file__ ).parent
            before = before.joinpath('rigifyscripts', 'Before First Rigify Generate - Public.py')
            text = bpy.data.texts.load(str(before))
            exec(text.as_string())

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(rigify_convert)

    # test call
    print((bpy.ops.kkb.rigifyconvert('INVOKE_DEFAULT')))

