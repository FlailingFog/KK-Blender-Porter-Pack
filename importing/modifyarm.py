'''
This file performs the following operations

·	Removes body empty, gives outfit id to clothes and parents them to the armature instead of the empties
·	Scales armature bones down by a factor of 12
·	Removes mmd bone constraints and bone drivers, unlocks all bones
·	Reparents leg03 bone and p_cf_body_bone to match koikatsu armature
.   Delete all bones not parented to the cf_n_height bone

·	Move and rotate finger bones to match koikatsu in game armature
·	Set bone roll data to match koikatsu in game armature
·	Slightly bend some bones outward to better support IKs

·	Delete empty vertex groups on the body as long as it's not a bone on the armature
·	Places each bone type (core bones, skirt bones, cf_s_ bones, etc) onto different armature layers
·	Identifies bones that are accessories with weight to them and moves them to a separate armature layer
.   Also sets the outfit ID for each accessory bone (not all accessory bones need to be visible at all times,
        so only the current outfit bones will be shown at the end)

·	Set mmd bone names for each bone

·	(KKBP armature) Visually connects all toe bones
·	(KKBP armature) Scales all skirt / face / eye / BP bones, connects all skirt bones
·	(KKBP armature) shortens kokan bone

·	(KKBP Armature) Creates an Eyesx bone to use as a reference bone for the eyes
·	(KKBP armature) Creates an eye controller bone
·	(KKBP armature) Detects and fixes empty eye L/R vertex groups

·	(KKBP armature) Repurposes pv bones for IK functionality
·	(KKBP armature) Creates a foot IK, hand IK, heel controller

·	(KKBP armature) Sets several bone drivers for several correction bones
·	(KKBP armature) Moves new bones for IK / eyes to correct armature layers

·	(KKBP armature) Adds bones to bone groups to give them colors
·	(KKBP armature) Renames some core bones to be more readable
.   (KKBP armature) Hide armature layers that are not core bones

·	(KKBP armature) Load custom bone widgets from the KK Shader file
·	(KKBP armature) Hide bone widgets collection
'''

import bpy
from .. import common as c

class modify_material(bpy.types.Operator):
    bl_idname = "kkbp.modifymaterial"
    bl_label = bl_idname
    bl_description = bl_idname
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            self.retreive_stored_tags()
            self.reparent_all_objects()
            self.scale_armature_bones_down()
            self.remove_bone_locks_and_modifiers()
            self.reparent_leg_and_body_bone()
            self.delete_non_height_bones()
            self.set_bone_roll_data()


            return {'FINISHED'}
        except Exception as error:
            c.handle_error(self, error)
            return {"CANCELLED"}

    # %% Main functions
    def retreive_stored_tags(self):
        '''Gets the tag from each object to repopulate the class variables below'''
        self.hairs = []
        self.outfits = []
        self.outfit_alternates = []
        self.hitboxes = []
        for object in [o for o in bpy.data.objects if o.type == 'MESH']:
            if object['KKBP tag'] == 'body':
                self.body = object
            elif object['KKBP tag'] == 'outfit':
                self.outfits.append(object)
            elif object['KKBP tag'] == 'alt':
                self.outfit_alternates.append(object)
            elif object['KKBP tag'] == 'hair':
                self.hairs.append(object)
            elif object['KKBP tag'] == 'hitbox':
                self.hitboxes.append(object)
        
    def reparent_all_objects(self):
        '''Reparents all objects to the main armature'''
        #reparent the body armature
        self.armature = bpy.data.objects['Model_arm'] #Model_arm is always the Body's armature
        empty = bpy.data.objects['Model'] #Model is always the Body's armature's empty
        c.switch(self.armature, 'object')
        self.armature.parent = None
        self.armature.name = 'Armature'
        bpy.data.objects.remove(empty)
        
        #reparent the outfit meshes as well
        for empty in [e for e in bpy.data.objects if ("Model_arm" in e.name and e.type == 'EMPTY')]:
            outfit_id = empty['KKBP outfit ID']
            outfit_arm = empty.children[0]
            outfit_meshes = outfit_arm.children
            bpy.data.objects.remove(empty)
            bpy.data.objects.remove(outfit_arm)
            #preserve outfit ID from empty then reparent
            for outfit in outfit_meshes:
                outfit['KKBP outfit ID'] = outfit_id
                outfit.parent = self.armature
                outfit.modifiers[0].object = self.armature
                outfit.modifiers[0].show_in_editmode = True
                outfit.modifiers[0].show_on_cage = True
                outfit.modifiers[0].show_expanded = False
        #reparent the alts and hairs to the main outfit object
        for alt in self.outfit_alternates:
            alt_parent = [p for p in self.outfits if p['KKBP outfit ID'] == alt['KKBP outfit ID']][0]
            alt.parent = alt_parent
        for hair in self.hairs:
            hair = [p for p in self.outfits if p['KKBP outfit ID'] == hair['KKBP outfit ID']][0]
            hair.parent = alt_parent
        #reparent the tongue, tears and gag eyes if they exist
        for object in ['Tongue (rigged)', 'Tears', 'Gag Eyes']:
            if bpy.data.objects.get(object):
                bpy.data.objects[object].parent = self.body
        #reparent hitboxes if they exist
        for hb in self.hitboxes:
            hb.parent = self.armature
    
    def scale_armature_bones_down(self):
        '''scale all bone sizes down by a factor of 12'''
        c.switch(self.armature, 'edit')
        for bone in self.armature.data.edit_bones:
            bone.tail.z = bone.head.z + (bone.tail.z - bone.head.z)/12

    def remove_bone_locks_and_modifiers(self):
        '''Removes mmd bone constraints and bone drivers, unlocks all bones'''
        #remove all constraints from all bones
        bpy.ops.object.mode_set(mode='POSE')
        for bone in self.armature.pose.bones:
            for constraint in bone.constraints:
                bone.constraints.remove(constraint)
        
        #remove all drivers from all armature bones
        #animation_data is nonetype if no drivers have been created yet
        if self.armature.animation_data:
            drivers_data = self.armature.animation_data.drivers
            for driver in drivers_data:  
                self.armature.driver_remove(driver.data_path, -1)

        #unlock the armature and all bones
        self.armature.lock_location = [False, False, False]
        self.armature.lock_rotation = [False, False, False]
        self.armature.lock_scale = [False, False, False]
        
        for bone in self.armature.pose.bones:
            bone.lock_location = [False, False, False]

    def reparent_leg_and_body_bone(self):
        if bpy.context.scene.kkbp.armature_dropdown != 'D':
            #reparent foot to leg03
            self.armature.data.edit_bones['cf_j_foot_R'].parent = self.armature.data.edit_bones['cf_j_leg03_R']
            self.armature.data.edit_bones['cf_j_foot_L'].parent = self.armature.data.edit_bones['cf_j_leg03_L']
            #unparent body bone to match KK
            self.armature.data.edit_bones['p_cf_body_bone'].parent = None

    def delete_non_height_bones(self):
        '''delete bones not under the cf_n_height bone. Deletes bones not under the BodyTop bone if PMX armature was selected'''
        def select_children(parent):
            try:
                parent.select = True
                parent.select_head = True
                parent.select_tail = True
                for child in parent.children:
                    select_children(child)
            except:
                #This is the last bone in the chain
                return
        if bpy.context.scene.kkbp.armature_dropdown == 'D':
            select_children(self.armature.data.edit_bones['BodyTop'])
        else:
            select_children(self.armature.data.edit_bones['cf_n_height'])
            #make sure these bones aren't deleted
            for preserve_bone in ['cf_j_root', 'p_cf_body_bone', 'cf_n_height']:
                self.armature.data.edit_bones[preserve_bone].select = True
                self.armature.data.edit_bones[preserve_bone].select_head = True
                self.armature.data.edit_bones[preserve_bone].select_tail = True
        bpy.ops.armature.select_all(action='INVERT')
        bpy.ops.armature.delete()

    def set_bone_roll_data(self):













    def remove_unused_material_slots(self):
        '''Remove unused mat slots on all objects'''
        for object in [o for o in bpy.data.objects if o.type == 'MESH']:
            c.switch(object, 'object')
            bpy.ops.object.material_slot_remove_unused()
    
    # %% Supporting functions

if __name__ == "__main__":
    bpy.utils.register_class(modify_material)

    # test call
    print((bpy.ops.kkbp.modifymaterial('INVOKE_DEFAULT')))
