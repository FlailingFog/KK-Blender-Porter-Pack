import bpy
from mathutils import Vector, Quaternion

def rename_bones():
    armature = bpy.context.object
    
    #rename core bones to match unity bone names
    unity_rename_dict = {
    'cf_j_root':'Center',
    'cf_j_hips':'Hips',
    'cf_j_waist01':'Pelvis',
    'cf_j_spine01':'Spine',
    'cf_j_spine02':'Chest',
    'cf_j_spine03':'Upper Chest',
    'cf_j_neck':'Neck',
    'cf_j_head':'Head',
    'cf_j_shoulder_L':'Left shoulder',
    'cf_j_shoulder_R':'Right shoulder',
    'cf_j_arm00_L':'Left arm',
    'cf_j_arm00_R':'Right arm',
    'cf_j_forearm01_L':'Left elbow',
    'cf_j_forearm01_R':'Right elbow',
    'cf_j_hand_R':'Right wrist',
    'cf_j_hand_L':'Left wrist',

    'cf_j_thumb01_L':'Thumb0_L',
    'cf_j_thumb02_L':'Thumb1_L',
    'cf_j_thumb03_L':'Thumb2_L',
    'cf_j_ring01_L':'RingFinger1_L',
    'cf_j_ring02_L':'RingFinger2_L',
    'cf_j_ring03_L':'RingFinger3_L',
    'cf_j_middle01_L':'MiddleFinger1_L',
    'cf_j_middle02_L':'MiddleFinger2_L',
    'cf_j_middle03_L':'MiddleFinger3_L',
    'cf_j_little01_L':'LittleFinger1_L',
    'cf_j_little02_L':'LittleFinger2_L',
    'cf_j_little03_L':'LittleFinger3_L',
    'cf_j_index01_L':'IndexFinger1_L',
    'cf_j_index02_L':'IndexFinger2_L',
    'cf_j_index03_L':'IndexFinger3_L',

    'cf_j_thumb01_R':'Thumb0_R',
    'cf_j_thumb02_R':'Thumb1_R',
    'cf_j_thumb03_R':'Thumb2_R',
    'cf_j_ring01_R':'RingFinger1_R',
    'cf_j_ring02_R':'RingFinger2_R',
    'cf_j_ring03_R':'RingFinger3_R',
    'cf_j_middle01_R':'MiddleFinger1_R',
    'cf_j_middle02_R':'MiddleFinger2_R',
    'cf_j_middle03_R':'MiddleFinger3_R',
    'cf_j_little01_R':'LittleFinger1_R',
    'cf_j_little02_R':'LittleFinger2_R',
    'cf_j_little03_R':'LittleFinger3_R',
    'cf_j_index01_R':'IndexFinger1_R',
    'cf_j_index02_R':'IndexFinger2_R',
    'cf_j_index03_R':'IndexFinger3_R',

    'cf_j_thigh00_L':'Left leg',
    'cf_j_thigh00_R':'Right leg',
    'cf_j_leg01_L':'Left knee',
    'cf_j_leg01_R':'Right knee',
    'cf_j_foot_L':'Left ankle',
    'cf_j_foot_R':'Right ankle',
    'cf_j_toes_L':'Left toe',
    'cf_j_toes_R':'Right toe'
    }
    
    for bone in armature.data.bones:
        if bone.name in unity_rename_dict:
            bone.name = unity_rename_dict[bone.name]
    
    #move armature bones that didn't have animation data up a level
    bpy.ops.object.mode_set(mode='EDIT')
    armature.data.edit_bones['Hips'].parent = armature.data.edit_bones['Center']
    armature.data.edit_bones['cf_pv_root'].parent = armature.data.edit_bones['Center']
    armature.data.edit_bones['Center'].parent = None

    bpy.ops.object.mode_set(mode='POSE')
    
    #bpy.ops.armature.select_all(action='DESELECT')
        
    bpy.ops.object.mode_set(mode='OBJECT')
    
    
    #this script will copy the animation data from the active Object to the selected object:
    active_obj = bpy.context.object
    ad = bpy.context.object.animation_data

    properties = [p.identifier for p in ad.bl_rna.properties if not p.is_readonly]
    objects = [o for o in bpy.context.selected_objects if o.type == active_obj.type]
    objects.remove(active_obj)

    for obj in objects :
        if obj.animation_data == None :
            obj.animation_data_create()
        ad2 = obj.animation_data
        for prop in properties:
            setattr(ad2, prop, getattr(ad, prop))

    #then swap the x and y rotation channels because the bone has been rotated
    #Find each rotation
    myaction = bpy.context.active_object.animation_data.action
    fcurves = myaction.fcurves
    
    def flip_animation(bone_to_flip):
        bone = objects[0].pose.bones[bone_to_flip]
        dpath = bone.path_from_id("rotation_quaternion")

        #get X channel and y channel
        wchan = fcurves.find(dpath, index=0).keyframe_points
        xchan = fcurves.find(dpath, index=1).keyframe_points
        ychan = fcurves.find(dpath, index=2).keyframe_points
        zchan = fcurves.find(dpath, index=3).keyframe_points
        
        index = 0
        while index < len(ychan):
            quaternion_axis_swapped = Quaternion((
            -wchan[index].co[1],
            -ychan[index].co[1],
            xchan[index].co[1],
            zchan[index].co[1])) #euler_representation.to_quaternion()
            
            wchan[index].co[1] = quaternion_axis_swapped.w
            xchan[index].co[1] = quaternion_axis_swapped.x
            ychan[index].co[1] = quaternion_axis_swapped.y
            zchan[index].co[1] = quaternion_axis_swapped.z
            print(quaternion_axis_swapped)
            index += 1
    
    flip_animation('Left elbow')
    flip_animation('Right elbow')

#disable all IKs and rotation locks

if __name__ == "__main__":
    rename_bones()