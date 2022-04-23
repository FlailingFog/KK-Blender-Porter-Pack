import bpy
from bpy.props import StringProperty
from mathutils import Quaternion
from ..importing.bonedrivers import rename_bones_for_clarity

def modify_animation_armature():
    #move armature bones that didn't have animation data up a level
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    animation_armature = bpy.data.objects['Animation Armature']
    animation_armature.select_set(True)
    bpy.context.view_layer.objects.active = animation_armature

    bpy.ops.object.mode_set(mode='EDIT')
    animation_armature.data.edit_bones['Hips'].parent = animation_armature.data.edit_bones['Center']
    animation_armature.data.edit_bones['cf_pv_root'].parent = animation_armature.data.edit_bones['Center']
    animation_armature.data.edit_bones['Center'].parent = None

    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
def apply_animation():
    #stolen from https://blender.stackexchange.com/questions/27136/
    #this script will copy the animation data from the active Object to the selected object:
    armature = bpy.data.objects['Armature']
    animation_armature = bpy.data.objects['Animation Armature']

    properties = [p.identifier for p in animation_armature.animation_data.bl_rna.properties if not p.is_readonly]

    if armature.animation_data == None :
        armature.animation_data_create()
    for prop in properties:
        setattr(armature.animation_data, prop, getattr(animation_armature.animation_data, prop))

def correct_animation():

    #find each bone rotation
    armature = bpy.data.objects['Armature']
    myaction = bpy.context.active_object.animation_data.action
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
    
    flip_animation('Left elbow')
    flip_animation('Right elbow')

class import_animation(bpy.types.Operator):
    bl_idname = "kkb.importanimation"
    bl_label = "Import .fbx animation"
    bl_description = "Imports a KK animation (.fbx format) and applies it to your character"
    bl_options = {'REGISTER', 'UNDO'}

    filepath : StringProperty(maxlen=1024, default='', options={'HIDDEN'})
    filter_glob : StringProperty(default='*.fbx', options={'HIDDEN'})
    
    def execute(self, context):
        scene = context.scene.placeholder
        use_rokoko_plugin = scene.rokoko_bool

        #import the fbx animation from the file dialog
        bpy.ops.import_scene.fbx(filepath=str(self.filepath), use_prepost_rot=False, global_scale=96)
        animation_armature = bpy.data.objects['Armature.001']
        animation_armature.name = 'Animation Armature'

        # if the character armature has renamed bones, the armature is the modified armature type
        armature = bpy.data.objects['Armature']
        if armature.data.bones.get('Left elbow'):
            rename_bones_for_clarity('animation')
            modify_animation_armature()
            apply_animation()
            correct_animation()
        
        #else, the armature is the vanilla armature type
        #apply the animation without modifications
        else:
            #if the user is using the rokoko plugin, use that to apply the animation
            #taken from https://github.com/FlailingFog/KK-Blender-Shader-Pack/issues/29
            if use_rokoko_plugin:
                bpy.data.scenes[0].rsl_retargeting_armature_target = armature
                bpy.data.scenes[0].rsl_retargeting_armature_source = animation_armature
                bpy.ops.rsl.build_bone_list()
                bpy.ops.rsl.retarget_animation()
            else:
                apply_animation()

        #mute all IKs and rotation locks
        armature = bpy.data.objects['Armature']
        for bone in armature.pose.bones:
            bonesWithConstraints = [constraint for constraint in bone.constraints if constraint.type == 'IK' or constraint.type == 'COPY_ROTATION']
            for constraint in bonesWithConstraints:
                constraint.mute = True

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