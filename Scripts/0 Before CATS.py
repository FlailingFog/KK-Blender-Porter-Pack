'''
BEFORE CATS SCRIPT
- Adds "_twist" to the end of these bone names so CATS doesn't eat them up
'''

import bpy

wantlist = ['cf_s_elboback_R', 'cf_s_elboback_L', 'cf_s_forearm01_R', 'cf_s_forearm01_L', 'cf_s_kneeB_R', 'cf_s_kneeB_L', 'cf_s_wrist_R', 'cf_s_wrist_L', 'cf_d_wrist_R', 'cf_d_wrist_L', 'cf_s_leg_R', 'cf_s_leg_L']

for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
    for bone in armature.data.bones:
        if bone.name in wantlist:
            bone.name = bone.name + '_twist'


