import bpy

class update_bones(bpy.types.Operator):
    bl_idname = "kkbp.updatebones"
    bl_label = "Update bones"
    bl_description = "Updates visibility of bones based on which outfits are hidden in the outliner"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        rigify_armature = [ob for ob in bpy.data.objects if ob.type == 'ARMATURE' and ob.get('rig_ui')]
        arm = rigify_armature[0] if len(rigify_armature) else bpy.data.objects['Armature']
        arm = bpy.data.armatures[arm.data.name]

        #check if the outfit linked to accessory bones on the armature is visible or not, then update the bone visibility
        for bone in arm.bones:
            if bone.get('KKBP outfit ID'):
                outfit_detected = False
                print("{} for {}".format(bone.name, bone['KKBP outfit ID']))
                for outfit_number in bone['KKBP outfit ID']:
                    matching_outfit = bpy.data.objects.get('Outfit 0' + str(outfit_number))
                    if matching_outfit:
                        print(matching_outfit.hide)
                        outfit_detected += not matching_outfit.hide
                bone.hide = False if outfit_detected else True

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(update_bones)