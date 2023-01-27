import bpy
from bpy.props import StringProperty
from mathutils import Quaternion

def modify_animation_armature(animation_armature):
    #move armature bones that didn't have animation data up a level
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    #animation_armature = bpy.data.objects['Animation Armature']
    animation_armature.select_set(True)
    bpy.context.view_layer.objects.active = animation_armature

    bpy.ops.object.mode_set(mode='EDIT')
    animation_armature.data.edit_bones['torso'].parent = None

    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
def apply_animation(source_arm, target_arm):
    '''Copies animation data from source_arm to target_arm'''
    #stolen from https://blender.stackexchange.com/questions/27136/
    #this script will copy the animation data from the active Object to the selected object:
    armature = target_arm
    animation_armature = source_arm

    properties = [p.identifier for p in animation_armature.animation_data.bl_rna.properties if not p.is_readonly]

    if armature.animation_data == None :
        armature.animation_data_create()
    for prop in properties:
        setattr(armature.animation_data, prop, getattr(animation_armature.animation_data, prop))

def correct_animation(rigify_armature):
    #find each bone rotation
    armature = rigify_armature
    myaction = armature.animation_data.action
    fcurves = myaction.fcurves

    #pmx armatures have swapped x and y rotation channels because the bone has been rotated
    # the y and z channels are swapped for fbx armatures 
    def flip_animation(bone_to_flip):
        bone = armature.pose.bones[bone_to_flip]
        dpath = bone.path_from_id("rotation_quaternion")

        #get the quaternion rotation channels...
        wchan = fcurves.find(dpath, index=0).keyframe_points
        xchan = fcurves.find(dpath, index=1).keyframe_points
        ychan = fcurves.find(dpath, index=2).keyframe_points
        zchan = fcurves.find(dpath, index=3).keyframe_points
        
        #and flip the channels based on armature origin
        index = 0
        while index < len(ychan):
            quaternion_axis_swapped = Quaternion((
            -wchan[index].co[1],
            -ychan[index].co[1],
            xchan[index].co[1],
            zchan[index].co[1]))
            
            wchan[index].co[1] = quaternion_axis_swapped.w
            xchan[index].co[1] = quaternion_axis_swapped.x
            ychan[index].co[1] = quaternion_axis_swapped.y
            zchan[index].co[1] = quaternion_axis_swapped.z
            #print(quaternion_axis_swapped)
            index += 1
    
    flip_animation('Left arm_fk')
    flip_animation('Right arm_fk')

#rename the bones in the imported fbx file to match the Rigify armature's names
def rename_bones(animation_armature):
    retargeting_dict = {
        'cf_j_hips' : 'torso',
        'cf_j_spine01' : 'Spine_fk',
        'cf_j_spine02' : 'Chest_fk',
        'cf_j_spine03' : 'Upper Chest_fk',
        'cf_j_arm00_l' : 'Left arm_fk',
        'cf_j_forearm01_l' : 'Left elbow_fk',
        'cf_j_hand_l' : 'Left wrist_fk',
        'cf_j_index01_l' : 'Indexfinger1_l',
        'cf_j_index02_l' : 'Indexfinger2_l',
        'cf_j_index03_l' : 'Indexfinger3_l',
        'cf_j_little01_l' : 'Littlefinger1_l',
        'cf_j_little02_l' : 'Littlefinger2_l',
        'cf_j_little03_l' : 'Littlefinger3_l',
        'cf_j_middle01_l' : 'middlefinger1_l',
        'cf_j_middle02_l' : 'middlefinger2_l',
        'cf_j_middle03_l' : 'Mmiddlefinger3_l',
        'cf_j_ring01_l' : 'Ringfinger1_l',
        'cf_j_ring02_l' : 'Ringfinger2_l',
        'cf_j_ring03_l' : 'Ringfinger3_l',
        'cf_j_thumb01_l' : 'Thumb0_l',
        'cf_j_thumb02_l' : 'Thumb1_l',
        'cf_j_thumb03_l' : 'Thumb2_l',
        'cf_j_arm00_r' :     'Right arm_fk',
        'cf_j_forearm01_r' : 'Right elbow_fk',
        'cf_j_hand_r' :      'Right wrist_fk',
        'cf_j_index01_r' : 'Indexfinger1_r',
        'cf_j_index02_r' : 'Indexfinger2_r',
        'cf_j_index03_r' : 'Indexfinger3_r',
        'cf_j_little01_r' : 'Littlefinger1_r',
        'cf_j_little02_r' : 'Littlefinger2_r',
        'cf_j_little03_r' : 'Littlefinger3_r',
        'cf_j_middle01_r' : 'Middlefinger1_r',
        'cf_j_middle02_r' : 'Middlefinger2_r',
        'cf_j_middle03_r' : 'Middlefinger3_r',
        'cf_j_ring01_r' : 'Ringfinger1_r',
        'cf_j_ring02_r' : 'Ringfinger2_r',
        'cf_j_ring03_r' : 'Ringfinger3_r',
        'cf_j_thumb01_r' : 'Thumb0_r',
        'cf_j_thumb02_r' : 'Thumb1_r',
        'cf_j_thumb03_r' : 'Thumb2_r',
        'cf_j_neck' : 'Neck',
        'cf_j_head' : 'Head',
        'cf_j_waist01' : 'Hips_fk',
        'cf_j_thigh00_l' : 'Left leg_fk',
        'cf_j_leg01_l' :   'Left knee_fk',
        'cf_j_foot_l' :    'Left ankle_fk',
        'cf_j_toes_l' :    'Left toe_fk',
        'cf_j_thigh00_r' :  'Tight leg_fk',
        'cf_j_leg01_r' :    'Tight knee_fk',
        'cf_j_foot_r' :     'Tight ankle_fk',
        'cf_j_toes_r' :     'Tight toe_fk',
        'cf_j_shoulder_l' : 'Left shoulder',
        'cf_j_waist02' : 'cf_j_waist02',
        'cf_j_shoulder_r' : 'Right shoulder',
        'cf_j_kokan' : 'cf_j_kokan',
        'cf_j_ana' : 'cf_j_ana',
        'cf_d_bust00' : 'Breasts handle',
        'cf_j_bust01_l' : 'Left Breast handle',
        'cf_j_bust02_l' : 'cf_j_bust02_l',
        'cf_j_bust03_l' : 'cf_j_bust03_l',
        'cf_j_bnip02root_l' : 'cf_j_bnip02root_l',
        'cf_j_bnip02_l' : 'cf_j_bnip02_l',
        'cf_j_bust01_r' : 'Right Breast handle',
        'cf_j_bust02_r' : 'cf_j_bust02_r',
        'cf_j_bust03_r' : 'cf_j_bust03_r',
        'cf_j_bnip02root_r' : 'cf_j_bnip02root_r',
        'cf_j_bnip02_r' : 'cf_j_bnip02_r',
        'cf_j_siri_l' : 'Left Buttock handle',
        'cf_j_siri_r' : 'Right Buttock handle',
    }
    for bone in animation_armature.data.bones:
        for key in retargeting_dict:
            if bone.name == key:
                bone.name = retargeting_dict[key]

class import_animation(bpy.types.Operator):
    bl_idname = "kkb.importanimation"
    bl_label = "Import .fbx animation"
    bl_description = "Imports a KK animation (.fbx format) and applies it to your character"
    bl_options = {'REGISTER', 'UNDO'}

    filepath : StringProperty(maxlen=1024, default='', options={'HIDDEN'})
    filter_glob : StringProperty(default='*.fbx', options={'HIDDEN'})
    
    def execute(self, context):
        scene = context.scene.kkbp

        #import the fbx animation from the file dialog
        bpy.ops.import_scene.fbx(filepath=str(self.filepath), use_prepost_rot=False, global_scale=96)
        animation_armature = bpy.context.object
        animation_armature.name = 'Animation Armature'

        rigify_armature = bpy.data.objects['RIG-Armature']
        rename_bones(animation_armature)
        modify_animation_armature(animation_armature)
        print(errororor)
        apply_animation(animation_armature, rigify_armature)
        #correct_animation(rigify_armature)

        #delete the animation armature and clean up orphan data
        bpy.data.objects.remove(bpy.data.objects['Animation Armature'])
        for block in bpy.data.armatures:
            if block.users == 0 and not block.use_fake_user:
                bpy.data.armatures.remove(block)
        
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

if __name__ == "__main__":
    bpy.utils.register_class(import_animation)

    # test call
    print((bpy.ops.kkb.importanimation('INVOKE_DEFAULT')))