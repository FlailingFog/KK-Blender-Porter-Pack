import bpy

class toggle_ik(bpy.types.Operator):
    bl_idname = "kkb.toggleik"
    bl_label = "Toggle IKs"
    bl_description = "Click this to toggle the hand and arm IKs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        pose_bones = bpy.data.objects['Armature'].pose.bones
        data_bones = bpy.data.objects['Armature'].data.bones

        #if the constaints are active, disable them
        if pose_bones['Left wrist'].constraints[0].mute == False:
            pose_bones['Left wrist'].constraints[0].mute = True
            pose_bones['Right wrist'].constraints[0].mute = True
            pose_bones['Left elbow'].constraints[0].mute = True
            pose_bones['Right elbow'].constraints[0].mute = True
            data_bones['Left wrist'].hide = False
            data_bones['Right wrist'].hide = False
        
        #else enable them
        else:
            pose_bones['Left wrist'].constraints[0].mute = False
            pose_bones['Right wrist'].constraints[0].mute = False
            pose_bones['Left elbow'].constraints[0].mute = False
            pose_bones['Right elbow'].constraints[0].mute = False
            data_bones['Left wrist'].hide = False
            data_bones['Right wrist'].hide = False
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(toggle_ik)