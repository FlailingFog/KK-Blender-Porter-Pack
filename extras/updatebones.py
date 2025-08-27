import bpy
from ..interface.dictionary_en import t
from .. import common as c

class update_bones(bpy.types.Operator):
    bl_idname = "kkbp.updatebones"
    bl_label = "Update bones"
    bl_description = t('bone_visibility_tt')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        arm = c.get_rig() if c.get_rig() else c.get_armature()
        arm = bpy.data.armatures[arm.data.name]

        #check if the outfit linked to accessory bones on the armature is visible or not, then update the bone visibility
        for bone in arm.bones:
            if bone.get('id'):
                hide_this_bone = True
                for outfit_number in bone['id']:
                    matching_outfit = bpy.data.objects.get('Outfit ' + outfit_number + ' ' + c.get_name())
                    if matching_outfit:
                        print(matching_outfit.users_collection[0].name)
                        #also check if the collection this outfit belongs to is enabled in the viewlayer
                        outfit_collection = c.get_layer_collection_state(matching_outfit.users_collection[0].name)
                        if not outfit_collection and not matching_outfit.hide_get():
                                print("Enabling bone {} for outfit {}".format(bone.name, bone['id']))
                                hide_this_bone = False
                                break
                bone.hide = hide_this_bone
            #always hide the rest of the accessory / MCH bones if they don't have an ID
            elif bpy.app.version[0] == 3:
                if bone.layer in [1, 2]:
                    bone.hide = True
            else:
                if bone.collections.get('1') or bone.collections.get('2'):
                    bone.hide = True

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(update_bones)