import bpy
from mathutils import Vector
from ..importing.bonedrivers import rename_bones_for_clarity
from ..importing.finalizepmx import modify_pmx_armature
from ..importing.finalizegrey import modify_fbx_armature
from ..importing.importeverything import apply_bone_widgets

class switch_armature(bpy.types.Operator):
    bl_idname = "kkbp.switcharmature"
    bl_label = "Switch koikatsu armature type"
    bl_description = "Click this to switch between the vanilla koikatsu armature structure and the modified KKBP armature. Using this after you have animated a character will ruin the animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = bpy.data.objects['Armature']
        
        #reset to T pose
        for bone in armature.pose.bones:
            bone.rotation_quaternion = (1,0,0,0)
            bone.scale = (1,1,1)
            bone.location = (0,0,0)

        #if the armature has already been modified, and there are drivers active, mute all drivers
        #this means the user wants to switch from modified to the stock armature
        if armature.data.bones.get('Left elbow'):
            print('switching from premodified to stock')
            for driver in armature.animation_data.drivers:
                driver.mute = True
            
            #then mute all constraints
            for bone in armature.pose.bones:
                bonesWithConstraints = [constraint for constraint in bone.constraints if constraint.type == 'IK' or constraint.type == 'COPY_ROTATION']
                for constraint in bonesWithConstraints:
                    constraint.mute = True
            
            #place the pv bones back in their original spot
            def reparent(bone,newparent):
                #refresh armature?
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')
                armature.data.edit_bones[bone].parent = armature.data.edit_bones[newparent]

            reparent('cf_pv_elbo_R', 'cf_pv_root')
            reparent('cf_pv_elbo_L', 'cf_pv_root')
            reparent('cf_pv_foot_R', 'cf_pv_root')
            reparent('cf_pv_foot_L', 'cf_pv_root')
            reparent('cf_pv_hand_R', 'cf_pv_root')
            reparent('cf_pv_hand_L', 'cf_pv_root')
            
            #stow the footIKs in there too
            reparent('MasterFootIK.R', 'cf_pv_root')
            reparent('MasterFootIK.L', 'cf_pv_root')

            #move the root and body bones back to where they're supposed to be
            armature.data.edit_bones['p_cf_body_bone'].parent = None
            reparent('cf_j_root', 'p_cf_body_bone')
            reparent('Center', 'cf_j_root')

            #then rename bones to match the stock armature
            rename_bones_for_clarity('stock')

            # reset the orientation for the leg/arm bones to stock
            #   also move some head/tail positions back to counteract the
            #   results of the finalizepmx relocate tail function
            height_adder = Vector((0,0,0.1))

            def unorient(bone):
                if 'leg' in bone:
                    armature.data.edit_bones[bone].head.y -= -.004
                elif 'hand' in bone:
                    armature.data.edit_bones[bone].tail.z -= .01

                armature.data.edit_bones[bone].tail = armature.data.edit_bones[bone].head + height_adder
                armature.data.edit_bones[bone].roll = 0
            
            unorient_bones = [
                'cf_j_thigh00_R', 'cf_j_thigh00_L',
                'cf_j_leg01_R', 'cf_j_leg01_L',
                'cf_j_foot_R', 'cf_j_foot_L',
                'cf_j_forearm01_R', 'cf_j_forearm01_L',
                'cf_d_bust00',
                'cf_pv_hand_R', 'cf_pv_hand_L']

            for bone in unorient_bones:
                unorient(bone)
        
        elif armature.data.bones.get('MasterFootIK.R'):
            #if the armature has already been modified, and the bones are not renamed, revert changes made above
            # this means the user wants to switch from stock to the premodified armature
            print('switching from stock to premodified')
            for driver in armature.animation_data.drivers:
                driver.mute = False
            
            #then unmute all constraints
            for bone in armature.pose.bones:
                bonesWithConstraints = [constraint for constraint in bone.constraints if constraint.type == 'IK' or constraint.type == 'COPY_ROTATION']
                for constraint in bonesWithConstraints:
                    constraint.mute = False

            #place the pv bones in their modified spots
            def reparent(bone,newparent):
                #refresh armature?
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.mode_set(mode='EDIT')
                armature.data.edit_bones[bone].parent = armature.data.edit_bones[newparent]

            reparent('cf_pv_elbo_R', 'cf_pv_root_upper')
            reparent('cf_pv_elbo_L', 'cf_pv_root_upper')
            reparent('cf_pv_foot_R', 'MasterFootIK.R')
            reparent('cf_pv_foot_L', 'MasterFootIK.L')
            reparent('cf_pv_hand_R', 'cf_n_height')
            reparent('cf_pv_hand_L', 'cf_n_height')
            
            #unstow the foot IKs
            reparent('MasterFootIK.R', 'cf_n_height')
            reparent('MasterFootIK.L', 'cf_n_height')

            #move the root and body bones back to where they're supposed to be
            #armature.data.edit_bones['cf_n_height'].parent = None
            reparent('cf_j_root', 'cf_pv_root')
            reparent('p_cf_body_bone', 'cf_pv_root')

            #then modify the bone names back and set the orientations for IKs
            modify_pmx_armature()
            
            rename_bones_for_clarity('modified')

        else:
            #if the armature has renamed bones, and it was never modified and this is a stock armature
            #this means the user wants to switch to the modified armature
            print('switching from stock to modified for the first time')
            modify_pmx_armature()

            armature.hide = False
            scene = context.scene.kkbp
            scene.armature_edit_bool = True
            bpy.ops.kkbp.bonedrivers('INVOKE_DEFAULT')
            bpy.ops.object.mode_set(mode='OBJECT')
            apply_bone_widgets()
        
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}



