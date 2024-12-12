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

·	(KKBP armature) Visually connects all toe bones
·	(KKBP armature) Scales all skirt / face / eye / BP bones, connects all skirt bones

·	(KKBP Armature) Creates an Eyesx bone to use as a reference bone for the eyes
·	(KKBP armature) Creates an eye controller bone
·	(KKBP armature) Detects and fixes empty eye L/R vertex groups
·	(KKBP armature) shortens kokan bone
.   (KKBP armature) resizes several skirt and face bones

·	(KKBP armature) Repurposes pv bones for IK functionality
·	(KKBP armature) Creates a foot IK, hand IK, heel controller
·	(KKBP armature) Sets several bone drivers for several correction bones
·	(KKBP armature) Moves new bones for IK / eyes to correct armature layers

·	(KKBP armature) Adds bones to bone groups to give them colors
·	(KKBP armature) Renames some core bones to be more readable
·	Set mmd bone names for each bone

·	(KKBP armature) Load custom bone widgets from the KK Shader file to apply to the armature
·	(KKBP armature) Hide bone widgets collection
.   (KKBP armature) Hide armature layers that are not core bones

Survey code was taken from MediaMoots here https://github.com/FlailingFog/KK-Blender-Shader-Pack/issues/29
Majority of the joint driver corrections were taken from a blend file by johnbbob_la_petite on the koikatsu discord

'''

import bpy, math
from .. import common as c
from mathutils import Vector

class modify_armature(bpy.types.Operator):
    bl_idname = "kkbp.modifyarmature"
    bl_label = bl_idname
    bl_description = bl_idname
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            self.retreive_stored_tags()
            self.reparent_all_objects()
            self.remove_bone_locks_and_modifiers()
            self.scale_armature_bones_down()
            self.reparent_leg_and_body_bone()
            self.delete_non_height_bones()

            self.modify_finger_bone_orientations()
            self.set_bone_roll_data()
            self.bend_bones_for_iks()

            self.remove_empty_vertex_groups()
            self.reorganize_armature_layers()
            self.move_accessory_bones_to_layer10()

            self.create_eye_reference_bone()
            self.create_eye_controller_bone()
            #self.fix_empty_eye_vertex_groups()
            self.shorten_kokan_bone()
            self.scale_skirt_and_face_bones()
            
            self.prepare_ik_bones()
            self.create_ik_bones()
            self.create_joint_drivers()
            
            self.categorize_bones()
            self.rename_bones_for_clarity()
            self.rename_mmd_bones()
            
            self.apply_bone_widgets()
            self.hide_widgets()

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
            if object.get('KKBP tag'):
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
        #c.print_timer('retreive_stored_tags')
        
    def reparent_all_objects(self):
        '''Reparents all objects to the main armature'''
        #reparent the body armature
        self.armature = bpy.data.objects['Model_arm'] #Model_arm is always the Body's armature
        empty = bpy.data.objects['Model'] #Model is always the Body's armature's empty
        c.switch(self.armature, 'object')
        self.armature.parent = None
        self.armature.name = 'Armature'
        self.armature['KKBP tag'] = 'armature'
        bpy.data.objects.remove(empty)

        #change armature modifier on body
        self.body.modifiers[0].show_in_editmode = True
        self.body.modifiers[0].show_on_cage = True
        self.body.modifiers[0].show_expanded = False
        
        #reparent the outfit meshes as well
        for empty in [e for e in bpy.data.objects if ("Model" in e.name and e.type == 'EMPTY')]:
            outfit_id = empty['KKBP outfit ID']
            outfit_arm = empty.children[0]
            outfit_meshes = outfit_arm.children
            #preserve outfit ID from empty then reparent
            for outfit in outfit_meshes:
                outfit['KKBP outfit ID'] = outfit_id
                outfit.parent = self.armature
                outfit.modifiers[0].object = self.armature
                outfit.modifiers[0].show_in_editmode = True
                outfit.modifiers[0].show_on_cage = True
                outfit.modifiers[0].show_expanded = False
            bpy.data.objects.remove(empty)
            bpy.data.objects.remove(outfit_arm)
        #fix outfit names
        for outfit in self.outfits:
            outfit.name = 'Outfit ' + str(outfit['KKBP outfit ID'])
        #reparent the alts and hairs to the main outfit object
        for alt in self.outfit_alternates:
            alt_parent = [p for p in self.outfits if p['KKBP outfit ID'] == alt['KKBP outfit ID']][0]
            alt.parent = alt_parent
        for hair in self.hairs:
            hair_parent = [p for p in self.outfits if p['KKBP outfit ID'] == hair['KKBP outfit ID']][0]
            hair.parent = hair_parent if bpy.context.scene.kkbp.categorize_dropdown not in ['D'] else hair.parent #don't reparent hair if Categorize by SMR
            hair.name = 'Hair Outfit ' + str(hair['KKBP outfit ID'])
        #reparent the tongue, tears and gag eyes if they exist
        for object in ['Tongue (rigged)', 'Tears', 'Gag Eyes']:
            if bpy.data.objects.get(object):
                bpy.data.objects[object].parent = self.body
        #reparent hitboxes if they exist
        for hb in self.hitboxes:
            hb.parent = self.armature
        c.print_timer('reparent_all_objects')
    
    def scale_armature_bones_down(self):
        '''scale all bone sizes down by a factor of 12. (all armature bones must be sticking upwards)'''
        c.switch(self.armature, 'edit')
        for bone in self.armature.data.edit_bones:
            bone.tail.z = bone.head.z + (bone.tail.z - bone.head.z)/12
        c.print_timer('scale_armature_bones_down')

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
        c.print_timer('remove_bone_locks_and_modifiers')

    def reparent_leg_and_body_bone(self):
        '''Reparent the leg bone to match the koikatsu armature. Unparent the body_bone bone to match koikatsu armature'''
        if bpy.context.scene.kkbp.armature_dropdown != 'D':
            #reparent foot to leg03
            self.armature.data.edit_bones['cf_j_foot_R'].parent = self.armature.data.edit_bones['cf_j_leg03_R']
            self.armature.data.edit_bones['cf_j_foot_L'].parent = self.armature.data.edit_bones['cf_j_leg03_L']
            #unparent body bone to match KK
            self.armature.data.edit_bones['p_cf_body_bone'].parent = None
        c.print_timer('reparent_leg_and_body_bone')

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
        c.print_timer('delete_non_height_bones')

    def modify_finger_bone_orientations(self):
        '''Reorient the finger bones to match the in game koikatsu armature'''
        c.switch(self.armature, 'edit')
        height_adjust = Vector((0,0,0.1))
        
        #all finger bones need to be rotated a specific direction
        def rotate_thumb(bone):
            bpy.ops.armature.select_all(action='DESELECT')
            self.armature.data.edit_bones[bone].select = True
            self.armature.data.edit_bones[bone].select_head = True
            self.armature.data.edit_bones[bone].select_tail = True
            parent = self.armature.data.edit_bones[bone].parent
            self.armature.data.edit_bones[bone].parent = None

            #right thumbs face towards hand center
            #left thumbs face away from hand center
            angle = -math.pi/2
            s = math.sin(angle)
            c = math.cos(angle)

            # translate point to origin:
            self.armature.data.edit_bones[bone].tail.x -= self.armature.data.edit_bones[bone].head.x
            self.armature.data.edit_bones[bone].tail.y -= self.armature.data.edit_bones[bone].head.y

            # rotate point around origin
            xnew = self.armature.data.edit_bones[bone].tail.x * c - self.armature.data.edit_bones[bone].tail.y * s
            ynew = self.armature.data.edit_bones[bone].tail.x * s + self.armature.data.edit_bones[bone].tail.y * c

            # translate point back to original position:
            self.armature.data.edit_bones[bone].tail.x = xnew + self.armature.data.edit_bones[bone].head.x
            self.armature.data.edit_bones[bone].tail.y = ynew + self.armature.data.edit_bones[bone].head.y
            self.armature.data.edit_bones[bone].roll = 0
            self.armature.data.edit_bones[bone].parent = parent
            
        rotate_thumb('cf_j_thumb03_L')
        rotate_thumb('cf_j_thumb02_L')
        rotate_thumb('cf_j_thumb01_L')
        rotate_thumb('cf_j_thumb03_R')
        rotate_thumb('cf_j_thumb02_R')
        rotate_thumb('cf_j_thumb01_R')
        
        height_adjust = Vector((0,0,0.05))
        def flip_finger(bone):
            parent = self.armature.data.edit_bones[bone].parent
            self.armature.data.edit_bones[bone].parent = None
            self.armature.data.edit_bones[bone].tail = self.armature.data.edit_bones[bone].head - height_adjust
            self.armature.data.edit_bones[bone].parent = parent
        
        finger_list = (
        'cf_j_index03_R', 'cf_j_index02_R', 'cf_j_index01_R',
        'cf_j_middle03_R', 'cf_j_middle02_R', 'cf_j_middle01_R',
        'cf_j_ring03_R', 'cf_j_ring02_R', 'cf_j_ring01_R',
        'cf_j_little03_R', 'cf_j_little02_R', 'cf_j_little01_R'
        )
        
        for finger in finger_list:
            flip_finger(finger)
        
            height_adjust = Vector((0,0,0.05))
        def resize_finger(bone):
            parent = self.armature.data.edit_bones[bone].parent
            self.armature.data.edit_bones[bone].parent = None
            self.armature.data.edit_bones[bone].tail = self.armature.data.edit_bones[bone].head + height_adjust
            self.armature.data.edit_bones[bone].parent = parent
        
        finger_list = (
        'cf_j_index03_L', 'cf_j_index02_L', 'cf_j_index01_L',
        'cf_j_middle03_L', 'cf_j_middle02_L', 'cf_j_middle01_L',
        'cf_j_ring03_L', 'cf_j_ring02_L', 'cf_j_ring01_L',
        'cf_j_little03_L', 'cf_j_little02_L', 'cf_j_little01_L'
        )
        
        for finger in finger_list:
            resize_finger(finger)
        
        #reset the orientation of certain bones
        height_adjust = Vector((0,0,0.1))
        def reorient(bone):
            self.armature.data.edit_bones[bone].tail = self.armature.data.edit_bones[bone].head + height_adjust

        reorient_list = [
            'cf_j_thigh00_R', 'cf_j_thigh00_L',
            'cf_j_leg01_R', 'cf_j_leg01_L',
            'cf_j_leg03_R', 'cf_j_leg03_L',
            'cf_j_foot_R', 'cf_j_foot_L',
            'cf_d_arm01_R', 'cf_d_arm01_L',
            'cf_d_shoulder02_R', 'cf_d_shoulder02_L',]

        for bone in reorient_list:
            reorient(bone)
        c.print_timer('modify_finger_bone_orientations')

    def set_bone_roll_data(self):
        '''Use roll data from a reference armature dump to set the roll for each bone'''
        reroll_data = {
        'BodyTop':0.0,
        'p_cf_body_bone':0.0,
        'cf_j_root':0.0,
        'cf_n_height':0.0,
        'cf_j_hips':0.0,
        'cf_j_spine01':0.0,
        'cf_j_spine02':0.0,
        'cf_j_spine03':0.0,
        'cf_d_backsk_00':0.0,
        'cf_j_backsk_C_01':-1.810556946517264e-23,
        'cf_j_backsk_C_02':-1.1667208633608472e-15,
        'cf_j_backsk_L_01':-0.001851903973147273,
        'cf_j_backsk_L_02':-0.0034122250508517027,
        'cf_j_backsk_R_01':0.0018519698642194271,
        'cf_j_backsk_R_02':0.003412271151319146,
        'cf_d_bust00':0.0,
        'cf_s_bust00_L':0.0,
        'cf_d_bust01_L':0.4159948229789734,
        'cf_j_bust01_L':0.4159948229789734,
        'cf_d_bust02_L':0.4159948229789734,
        'cf_j_bust02_L':0.4151105582714081,
        'cf_d_bust03_L':0.4151104986667633,
        'cf_j_bust03_L':0.4151104986667633,
        'cf_d_bnip01_L':0.4151104986667633,
        'cf_j_bnip02root_L':0.4151104986667633,
        'cf_s_bnip02_L':0.4151104986667633,
        'cf_j_bnip02_L':0.4154767096042633,
        'cf_s_bnip025_L':0.4154742360115051,
        'cf_s_bnip01_L':0.41547420620918274,
        'cf_s_bnip015_L':0.41547420620918274,
        'cf_s_bust03_L':0.4153861403465271,
        'cf_s_bust02_L':0.38631150126457214,
        'cf_s_bust01_L':0.4159947633743286,
        'cf_s_bust00_R':0.0,
        'cf_d_bust01_R':-0.4159948527812958,
        'cf_j_bust01_R':-0.4159948229789734,
        'cf_d_bust02_R':-0.41599488258361816,
        'cf_j_bust02_R':-0.41511064767837524,
        'cf_d_bust03_R':-0.41511061787605286,
        'cf_j_bust03_R':-0.41511064767837524,
        'cf_d_bnip01_R':-0.41511061787605286,
        'cf_j_bnip02root_R':-0.41511061787605286,
        'cf_s_bnip02_R':-0.41511061787605286,
        'cf_j_bnip02_R':-0.41547682881355286,
        'cf_s_bnip025_R':-0.4154742360115051,
        'cf_s_bnip01_R':-0.4154742956161499,
        'cf_s_bnip015_R':-0.4154742956161499,
        'cf_s_bust03_R':-0.41538622975349426,
        'cf_s_bust02_R':-0.38631150126457214,
        'cf_s_bust01_R':-0.4159948229789734,
        'cf_d_shoulder_L':0.0,
        'cf_j_shoulder_L':0.0,
        'cf_d_shoulder02_L':4.2021918488899246e-05,
        'cf_s_shoulder02_L':4.202192212687805e-05,
        'cf_j_arm00_L':0.0,
        'cf_d_arm01_L':-0.0012054670369252563,
        'cf_s_arm01_L':0.009222406893968582,
        'cf_d_arm02_L':-0.0012054670369252563,
        'cf_s_arm02_L':0.004008470103144646,
        'cf_d_arm03_L':-0.0012054670369252563,
        'cf_s_arm03_L':-0.0012097591534256935,
        'cf_j_forearm01_L':0.0,
        'cf_d_forearm02_L':0.0,
        'cf_s_forearm02_L':0.0,
        'cf_d_wrist_L':0.0,
        'cf_s_wrist_L':0.0,
        'cf_d_hand_L':0.0,
        'cf_j_hand_L':-6.776263578034403e-21,
        'cf_s_hand_L':-6.776263578034403e-21,
        'cf_j_index01_L':math.radians(-11),
        'cf_j_index02_L':math.radians(-5),
        'cf_j_index03_L':math.radians(0),
        'cf_j_little01_L':math.radians(30),
        'cf_j_little02_L':math.radians(11),
        'cf_j_little03_L':math.radians(30),
        'cf_j_middle01_L':math.radians(3),
        'cf_j_middle02_L':math.radians(3),
        'cf_j_middle03_L':math.radians(3),
        'cf_j_ring01_L':math.radians(15),
        'cf_j_ring02_L':math.radians(7),
        'cf_j_ring03_L':math.radians(15),
        'cf_j_thumb01_L':math.pi,
        'cf_j_thumb02_L':math.pi,
        'cf_j_thumb03_L':math.pi,
        'cf_s_elbo_L':0.0,
        'cf_s_forearm01_L':0.0,
        'cf_s_elboback_L':0.0,
        'cf_d_shoulder_R':0.0,
        'cf_j_shoulder_R':0.0,
        'cf_d_shoulder02_R':-4.355472628958523e-05,
        'cf_s_shoulder02_R':-4.355472628958523e-05,
        'cf_j_arm00_R':0.0,
        'cf_d_arm01_R':0.0009736516512930393,
        'cf_s_arm01_R':0.0009736517095007002,
        'cf_d_arm02_R':0.0009736516512930393,
        'cf_s_arm02_R':-0.004238337744027376,
        'cf_d_arm03_R':0.0009736516512930393,
        'cf_s_arm03_R':0.0009736517095007002,
        'cf_j_forearm01_R':0.0,
        'cf_d_forearm02_R':2.6637668270268477e-05,
        'cf_s_forearm02_R':2.6637668270268477e-05,
        'cf_d_wrist_R':1.9139706637361087e-05,
        'cf_s_wrist_R':1.9139704818371683e-05,
        'cf_d_hand_R':1.9139704818371683e-05,
        'o_brac':0.0,
        'cf_j_hand_R':-6.776470373187541e-21,
        'cf_s_hand_R':-6.776470373187541e-21,
        'cf_j_index01_R':math.radians(-11),
        'cf_j_index02_R':math.radians(-5),
        'cf_j_index03_R':math.radians(0),
        'cf_j_little01_R':math.radians(30),
        'cf_j_little02_R':math.radians(11),
        'cf_j_little03_R':math.radians(30),
        'cf_j_middle01_R':math.radians(3),
        'cf_j_middle02_R':math.radians(3),
        'cf_j_middle03_R':math.radians(3),
        'cf_j_ring01_R':math.radians(15),
        'cf_j_ring02_R':math.radians(7),
        'cf_j_ring03_R':math.radians(15),
        'cf_j_thumb01_R':math.radians(0),
        'cf_j_thumb02_R':math.radians(0),
        'cf_j_thumb03_R':math.radians(0),
        'cf_s_elbo_R':0.0,
        'cf_s_forearm01_R':0.0,
        'cf_s_elboback_R':4.203895392974451e-44,
        'cf_d_spinesk_00':0.0,
        'cf_j_spinesk_00':5.2774636787104646e-23,
        'cf_j_spinesk_01':-0.01019450556486845,
        'cf_j_spinesk_02':0.0032659571152180433,
        'cf_j_spinesk_03':-0.001969193108379841,
        'cf_j_spinesk_04':-0.001969192875549197,
        'cf_j_spinesk_05':-0.00196919240988791,
        'cf_j_neck':0.0,
        'cf_j_head':0.0,
        'cf_s_head':0.0,
        'p_cf_head_bone':0.0,
        'cf_J_N_FaceRoot':2.1210576051089447e-07,
        'cf_J_FaceRoot':2.1210573208918504e-07,
        'cf_J_FaceBase':2.1210573208918504e-07,
        'cf_J_FaceLow_tz':2.1210573208918504e-07,
        'cf_J_FaceLow_sx':2.1210573208918504e-07,
        'cf_J_CheekUpBase':2.1210573208918504e-07,
        'cf_J_CheekUp_s_L':2.1210573208918504e-07,
        'cf_J_CheekUp_s_R':2.1210573208918504e-07,
        'cf_J_Chin_Base':2.1210574630003975e-07,
        'cf_J_CheekLow_s_L':2.1210573208918504e-07,
        'cf_J_CheekLow_s_R':2.1210573208918504e-07,
        'cf_J_Chin_s':2.1210573208918504e-07,
        'cf_J_ChinTip_Base':2.1210574630003975e-07,
        'cf_J_ChinLow':2.1210573208918504e-07,
        'cf_J_MouthBase_ty':2.1210573208918504e-07,
        'cf_J_MouthBase_rx':2.1210573208918504e-07,
        'cf_J_MouthCavity':2.1210571787833032e-07,
        'cf_J_MouthMove':2.1210571787833032e-07,
        'cf_J_Mouth_L':2.1210573208918504e-07,
        'cf_J_Mouth_R':2.1210573208918504e-07,
        'cf_J_MouthLow':2.1210573208918504e-07,
        'cf_J_Mouthup':2.1210573208918504e-07,
        'cf_J_FaceUp_ty':2.1210573208918504e-07,
        'a_n_headside':2.1210574630003975e-07,
        'cf_J_EarBase_ry_L':-0.1504509449005127,
        'cf_J_EarLow_L':-0.1504509449005127,
        'cf_J_EarUp_L':-0.1504509449005127,
        'cf_J_EarBase_ry_R':0.15762563049793243,
        'cf_J_EarLow_R':0.15762564539909363,
        'cf_J_EarUp_R':0.15762564539909363,
        'cf_J_FaceUp_tz':2.1210574630003975e-07,
        'cf_J_Eye_tz':2.1210574630003975e-07,
        'cf_J_Eye_txdam_L':2.1210574630003975e-07,
        'cf_J_Eye_tx_L':2.1210573208918504e-07,
        'cf_J_Eye_rz_L':0.20466913282871246,
        'cf_J_CheekUp2_L':0.004773593973368406,
        'cf_J_Eye01_s_L':0.20466917753219604,
        'cf_J_Eye02_s_L':0.20466917753219604,
        'cf_J_Eye03_s_L':0.20466917753219604,
        'cf_J_Eye04_s_L':0.20466917753219604,
        'cf_J_Eye05_s_L':0.20466917753219604,
        'cf_J_Eye06_s_L':0.20466917753219604,
        'cf_J_Eye07_s_L':0.20466917753219604,
        'cf_J_Eye08_s_L':0.20466917753219604,
        'cf_J_hitomi_tx_L':0.18981075286865234,
        'cf_J_Eye_txdam_R':2.1210574630003975e-07,
        'cf_J_Eye_tx_R':2.1210576051089447e-07,
        'cf_J_Eye_rz_R':-0.2046687752008438,
        'cf_J_CheekUp2_R':-0.0047732163220644,
        'cf_J_Eye01_s_R':-0.2046687752008438,
        'cf_J_Eye02_s_R':-0.2046687752008438,
        'cf_J_Eye03_s_R':-0.2046687752008438,
        'cf_J_Eye04_s_R':-0.2046687752008438,
        'cf_J_Eye05_s_R':-0.2046687752008438,
        'cf_J_Eye06_s_R':-0.2046687752008438,
        'cf_J_Eye07_s_R':-0.2046687752008438,
        'cf_J_Eye08_s_R':-0.2046687752008438,
        'cf_J_hitomi_tx_R':-0.2046687752008438,
        'cf_J_Mayu_ty':2.1210574630003975e-07,
        'cf_J_Mayumoto_L':0.3458269536495209,
        'cf_J_Mayu_L':0.34616410732269287,
        'cf_J_MayuMid_s_L':0.34626930952072144,
        'cf_J_MayuTip_s_L':0.3462893068790436,
        'cf_J_Mayumoto_R':-0.34582653641700745,
        'cf_J_Mayu_R':-0.34616369009017944,
        'cf_J_MayuMid_s_R':-0.3462689220905304,
        'cf_J_MayuTip_s_R':-0.34628885984420776,
        'cf_J_NoseBase':2.1210573208918504e-07,
        'cf_J_NoseBase_rx':2.1210573208918504e-07,
        'cf_J_Nose_rx':2.1210573208918504e-07,
        'cf_J_Nose_tip':2.1210571787833032e-07,
        'cf_J_NoseBridge_ty':2.1210573208918504e-07,
        'cf_J_NoseBridge_rx':2.1210573208918504e-07,
        'cf_s_neck':0.0,
        'cf_s_spine03':0.0,
        'a_n_back':-3.1415927410125732,
        'cf_s_spine02':0.0,
        'cf_s_spine01':0.0,
        'cf_j_waist01':0.0,
        'cf_d_sk_top':0.0,
        'cf_d_sk_00_00':-3.1415927410125732,
        'cf_j_sk_00_00':-3.1415927410125732,
        'cf_j_sk_00_01':-3.1415927410125732,
        'cf_j_sk_00_02':3.1415293216705322,
        'cf_j_sk_00_03':3.1415293216705322,
        'cf_j_sk_00_04':3.1415293216705322,
        'cf_j_sk_00_05':3.1415293216705322,
        'cf_d_sk_01_00':2.3621666431427,
        'cf_j_sk_01_00':2.3621666431427,
        'cf_j_sk_01_01':2.364142656326294,
        'cf_j_sk_01_02':2.3684122562408447,
        'cf_j_sk_01_03':2.3684122562408447,
        'cf_j_sk_01_04':2.3684122562408447,
        'cf_j_sk_01_05':2.3684122562408447,
        'cf_d_sk_02_00':1.5806118249893188,
        'cf_j_sk_02_00':1.5808137655258179,
        'cf_j_sk_02_01':1.5806832313537598,
        'cf_j_sk_02_02':1.5820348262786865,
        'cf_j_sk_02_03':1.5820348262786865,
        'cf_j_sk_02_04':1.5820348262786865,
        'cf_j_sk_02_05':1.5820348262786865,
        'cf_d_sk_03_00':0.7112568616867065,
        'cf_j_sk_03_00':0.7112571597099304,
        'cf_j_sk_03_01':0.7112568020820618,
        'cf_j_sk_03_02':0.709623396396637,
        'cf_j_sk_03_03':0.7096233367919922,
        'cf_j_sk_03_04':0.7096233367919922,
        'cf_j_sk_03_05':0.7096234560012817,
        'cf_d_sk_04_00':3.4498308600352867e-17,
        'cf_j_sk_04_00':0.00037256989162415266,
        'cf_j_sk_04_01':0.00012998198508284986,
        'cf_j_sk_04_02':0.0001299990399274975,
        'cf_j_sk_04_03':0.0001299990399274975,
        'cf_j_sk_04_04':0.0001299990399274975,
        'cf_j_sk_04_05':0.0001299990399274975,
        'cf_d_sk_05_00':-0.7112577557563782,
        'cf_j_sk_05_00':-0.7112579345703125,
        'cf_j_sk_05_01':-0.7112577557563782,
        'cf_j_sk_05_02':-0.7096185088157654,
        'cf_j_sk_05_03':-0.7096185088157654,
        'cf_j_sk_05_04':-0.7096185088157654,
        'cf_j_sk_05_05':-0.7096185088157654,
        'cf_d_sk_06_00':-1.5806118249893188,
        'cf_j_sk_06_00':-1.5808138847351074,
        'cf_j_sk_06_01':-1.5806833505630493,
        'cf_j_sk_06_02':-1.5820401906967163,
        'cf_j_sk_06_03':-1.5820401906967163,
        'cf_j_sk_06_04':-1.5820401906967163,
        'cf_j_sk_06_05':-1.5820401906967163,
        'cf_d_sk_07_00':-2.3621666431427,
        'cf_j_sk_07_00':-2.3621666431427,
        'cf_j_sk_07_01':-2.3649401664733887,
        'cf_j_sk_07_02':-2.3683762550354004,
        'cf_j_sk_07_03':-2.3683762550354004,
        'cf_j_sk_07_04':-2.3683762550354004,
        'cf_j_sk_07_05':-2.3683762550354004,
        'cf_j_waist02':0.0,
        'cf_d_siri_L':4.435180380824022e-05,
        'cf_d_siri01_L':4.484502278501168e-05,
        'cf_j_siri_L':4.435180744621903e-05,
        'cf_s_siri_L':4.607543087331578e-05,
        'cf_d_ana':4.053832753925235e-07,
        'cf_j_ana':4.053832753925235e-07,
        'cf_s_ana':4.0538333223594236e-07,
        'cf_d_kokan':0.0,
        'cf_j_kokan':7.531064056820469e-07,
        'cf_d_siri_R':-5.766015220842746e-08,
        'cf_d_siri01_R':-5.766015220842746e-08,
        'cf_j_siri_R':-5.766015220842746e-08,
        'cf_s_siri_R':-5.766015576114114e-08,
        'cf_j_thigh00_L':0.0,
        'cf_d_thigh01_L':0.0,
        'cf_s_thigh01_L':0.0,
        'cf_d_thigh02_L':0.0,
        'cf_s_thigh02_L':0.0,
        'cf_d_thigh03_L':0.0,
        'cf_s_thigh03_L':0.0,
        'cf_j_leg01_L':0.0,
        'cf_d_kneeF_L':0.0,
        'cf_d_leg02_L':-8.435114585980674e-12,
        'cf_s_leg02_L':0.0019489085534587502,
        'cf_d_leg03_L':2.6021072699222714e-05,
        'cf_s_leg03_L':2.6021054509328678e-05,
        'cf_j_leg03_L':-1.7005811689396744e-11,
        'cf_j_foot_L':-1.6870217028897017e-11,
        'cf_j_toes_L':-1.6870217028897017e-11,
        'cf_s_leg01_L':1.5783663344534925e-25,
        'cf_s_kneeB_L':1.5783659646749431e-25,
        'cf_j_thigh00_R':0.0,
        'cf_d_thigh01_R':-2.9915531455925155e-27,
        'cf_s_thigh01_R':-2.3654518046693106e-22,
        'cf_d_thigh02_R':0.0,
        'cf_s_thigh02_R':0.0,
        'cf_d_thigh03_R':0.0,
        'cf_s_thigh03_R':0.0,
        'cf_j_leg01_R':0.0,
        'cf_d_kneeF_R':0.0,
        'cf_d_leg02_R':-3.092561655648751e-07,
        'cf_s_leg02_R':-3.092561655648751e-07,
        'cf_d_leg03_R':-4.125216790384911e-08,
        'cf_s_leg03_R':-4.125216790384911e-08,
        'cf_j_leg03_R':-6.69778160045098e-07,
        'cf_j_foot_R':-6.185123311297502e-07,
        'cf_j_toes_R':-6.185122742863314e-07,
        'cf_s_leg01_R':-8.901179133911008e-16,
        'cf_s_kneeB_R':-8.901180192702192e-16,
        'cf_s_waist02':0.0,
        'cf_s_leg_L':-0.004678195342421532,
        'cf_s_leg_R':0.004779986571520567,
        'cf_s_waist01':0.0,
        }
        
        c.switch(self.armature, 'edit')
        for bone in reroll_data:
            if self.armature.data.edit_bones.get(bone):
                self.armature.data.edit_bones[bone].roll = reroll_data[bone]
        c.print_timer('set_bone_roll_data')

    def bend_bones_for_iks(self):
        '''slightly modify the armature to support IKs'''
        if not bpy.context.scene.kkbp.armature_dropdown in ['A', 'B']:
            return
        c.switch(self.armature, 'edit')
        self.armature.data.edit_bones['cf_n_height'].parent = None
        self.armature.data.edit_bones['cf_j_root'].parent = self.armature.data.edit_bones['cf_pv_root']
        self.armature.data.edit_bones['p_cf_body_bone'].parent = self.armature.data.edit_bones['cf_pv_root']
        #relocate the tail of some bones to make IKs easier
        def relocate_tail(bone1, bone2, direction):
            if direction == 'leg':
                self.armature.data.edit_bones[bone1].tail.z = self.armature.data.edit_bones[bone2].head.z
                self.armature.data.edit_bones[bone1].roll = 0
            elif direction == 'arm':
                self.armature.data.edit_bones[bone1].tail.x = self.armature.data.edit_bones[bone2].head.x
                self.armature.data.edit_bones[bone1].tail.z = self.armature.data.edit_bones[bone2].head.z
                self.armature.data.edit_bones[bone1].roll = -math.pi/2
            elif direction == 'hand':
                self.armature.data.edit_bones[bone1].tail = self.armature.data.edit_bones[bone2].tail
                #make hand bone shorter so you can easily click the hand and the pv bone
                self.armature.data.edit_bones[bone1].tail.z += .01 
                self.armature.data.edit_bones[bone1].head = self.armature.data.edit_bones[bone2].head
            else:
                self.armature.data.edit_bones[bone1].tail.y = self.armature.data.edit_bones[bone2].head.y
                self.armature.data.edit_bones[bone1].tail.z = self.armature.data.edit_bones[bone2].head.z
                self.armature.data.edit_bones[bone1].roll = 0
        relocate_tail('cf_j_leg01_R', 'cf_j_foot_R', 'leg')
        relocate_tail('cf_j_leg01_L', 'cf_j_foot_L', 'leg')
        relocate_tail('cf_j_forearm01_R', 'cf_j_hand_R', 'arm')
        relocate_tail('cf_j_forearm01_L', 'cf_j_hand_L', 'arm')
        relocate_tail('cf_pv_hand_R', 'cf_j_hand_R', 'hand')
        relocate_tail('cf_pv_hand_L', 'cf_j_hand_L', 'hand')
        relocate_tail('cf_j_foot_R', 'cf_j_toes_R', 'foot')
        relocate_tail('cf_j_foot_L', 'cf_j_toes_L', 'foot')
        c.print_timer('bend_bones_for_iks')

    def remove_empty_vertex_groups(self):
        '''check body for groups with no vertexes. Delete if the group is not a bone on the armature'''
        vertexWeightMap = self.survey_vertexes(self.body)
        bones_in_armature = [bone.name for bone in self.armature.data.bones]
        for group in vertexWeightMap:
            if group not in bones_in_armature and vertexWeightMap[group] == False and 'cf_J_Vagina' not in group:
                self.body.vertex_groups.remove(self.body.vertex_groups[group])
        c.print_timer('remove_empty_vertex_groups')

    def reorganize_armature_layers(self):
        '''Moves all bones to different armature layers'''
        if bpy.app.version[0] == 3:
            c.switch(self.armature, 'pose')
        else:
            c.switch(self.armature, 'object')
        
        core_list   = self.get_bone_list('core_list')
        non_ik      = self.get_bone_list('non_ik')
        toe_list    = self.get_bone_list('toe_list')
        bp_list     = self.get_bone_list('bp_list')
        eye_list    = self.get_bone_list('eye_list')
        mouth_list  = self.get_bone_list('mouth_list')
        skirt_list  = self.get_bone_list('skirt_list')
        tongue_list = self.get_bone_list('tongue_list')

        #throw all bones to armature layer 11
        for bone in bpy.data.armatures[0].bones:
            self.set_armature_layer(bone.name, show_layer = 10)
        #reshow cf_hit_ bones on layer 12
        for bone in [bones for bones in bpy.data.armatures[0].bones if 'cf_hit_' in bones.name]:
            self.set_armature_layer(bone.name, show_layer = 11)
        #reshow k_f_ bones on layer 13
        for bone in [bones for bones in bpy.data.armatures[0].bones if 'k_f_' in bones.name]:
            self.set_armature_layer(bone.name, show_layer = 12)
        #reshow core bones on layer 1
        for bone in core_list:
            self.set_armature_layer(bone, show_layer = 0)
        #reshow non_ik bones on layer 2
        for bone in non_ik:
            self.set_armature_layer(bone, show_layer = 1)
        #Put the charamaker bones on layer 3
        for bone in [bones for bones in bpy.data.armatures[0].bones if 'cf_s_' in bones.name]:
            self.set_armature_layer(bone.name, show_layer = 2)
        #Put the deform bones on layer 4
        for bone in [bones for bones in bpy.data.armatures[0].bones if 'cf_d_' in bones.name]:
            self.set_armature_layer(bone.name, show_layer = 3)
        try:
            #Put the better penetration bones on layer 5
            for bone in bp_list:
                self.set_armature_layer(bone, show_layer = 4)
                #rename the bones so you can mirror them over the x axis in pose mode
                if 'Vagina_L_' in bone or 'Vagina_R_' in bone:
                    bpy.data.armatures[0].bones[bone].name = 'Vagina' + bone[8:] + '_' + bone[7]
            #Put the toe bones on layer 5
            for bone in toe_list:
                self.set_armature_layer(bone, show_layer = 4)
        except:
            #this armature isn't a BP armature
            pass
        #Put the upper eye bones on layer 17
        for bone in eye_list:
            self.set_armature_layer(bone, show_layer = 16)
        #Put the lower mouth bones on layer 18
        for bone in mouth_list:
            self.set_armature_layer(bone, show_layer = 17)
        #Put the tongue rig bones on layer 19
        for bone in tongue_list:
            self.set_armature_layer(bone, show_layer = 18)
        #Put the skirt bones on layer 9
        for bone in skirt_list:
            self.set_armature_layer(bone, show_layer = 8)
        #put accessory bones on layer 10 during reshow_accessory_bones() later on        
        #Make all bone layers visible for now
        all_layers = [
        True, True, True, True, True, False, False, False, #body
        True, True, True, False, False, False, False, False, #clothes
        True, True, False, False, False, False, False, False, #face
        False, False, False, False, False, False, False, False]
        if bpy.app.version[0] == 3:
            bpy.ops.armature.armature_layers(layers=all_layers)
        else:
            for index, show_layer in enumerate(all_layers):
                if self.armature.data.collections.get(str(index)):
                    self.armature.data.collections.get(str(index)).is_visible = show_layer
        self.armature.data.display_type = 'STICK'
        c.switch(self.armature, 'object')
        c.print_timer('reorganize_armature_layers')

    def move_accessory_bones_to_layer10(self):
        '''Moves the accessory bones that have weight to them to armature layer 10'''
        c.switch(self.armature, 'object')
        #go through each outfit and move ALL accessory bones to layer 10
        dont_move_these = [
                'cf_pv', 'Eyesx',
                'cf_J_hitomi_tx_', 'cf_J_FaceRoot', 'cf_J_FaceUp_t',
                'n_cam', 'EyesLookTar', 'N_move', 'a_n_', 'cf_hit',
                'cf_j_bnip02', 'cf_j_kokan', 'cf_j_ana']
        for outfit_or_hair in [obj for obj in bpy.data.objects if 'Outfit ' in obj.name]:
            # Find empty vertex groups
            vertexWeightMap = self.survey_vertexes(outfit_or_hair)
            #add outfit id to all accessory bones used by that outfit in an array
            number_of_outfits = len([outfit for outfit in bpy.data.objects if 'Outfit ' in outfit.name and 'Hair' not in outfit.name and 'alt ' not in outfit.name and 'Indoor' not in outfit.name])
            if bpy.app.version[0] == 3:
                for bone in [bone for bone in self.armature.data.bones if bone.layers[10]]:
                    no_move_bone = False
                    for this_prefix in dont_move_these:
                        if this_prefix in bone.name:
                            no_move_bone = True
                    if not no_move_bone and vertexWeightMap.get(bone.name):
                        try:
                            outfit_id_array = bone['KKBP outfit ID'].to_list()
                            outfit_id_array.append(outfit_or_hair['KKBP outfit ID'])
                            bone['KKBP outfit ID'] = outfit_id_array
                        except:
                            bone['KKBP outfit ID'] = [outfit_or_hair['KKBP outfit ID']]
            else:
                for bone in [bone for bone in self.armature.data.bones if bone.collections.get('10')]:
                    no_move_bone = False
                    for this_prefix in dont_move_these:
                        if this_prefix in bone.name:
                            no_move_bone = True
                    if not no_move_bone and vertexWeightMap.get(bone.name):
                        try:
                            outfit_id_array = bone['KKBP outfit ID'].to_list()
                            outfit_id_array.append(outfit_or_hair['KKBP outfit ID'])
                            bone['KKBP outfit ID'] = outfit_id_array
                        except:
                            bone['KKBP outfit ID'] = [outfit_or_hair['KKBP outfit ID']]
        #move accessory bones to armature layer 10
        for bone in [bone for bone in self.armature.data.bones if bone.get('KKBP outfit ID')]:
            self.set_armature_layer(bone.name, show_layer = 9)
        c.print_timer('move_accessory_bones_to_layer10')

    def rename_mmd_bones(self):
        '''renames japanese name field for importing vmds via mmd tools
        these names are separate from Blender's bone names'''
        pmx_rename_dict = {
        '全ての親':'p_cf_body_bone',
        'センター':'cf_j_hips',
        '上半身':'cf_j_spine01',
        '上半身2':'cf_j_spine02',
        '首':'cf_j_neck',
        '頭':'cf_j_head',
        '両目':'Eyesx',
        '左目':'cf_J_hitomi_tx_L',
        '右目':'cf_J_hitomi_tx_R',
        '左腕':'cf_j_arm00_L',
        '右腕':'cf_j_arm00_R',
        '左ひじ':'cf_j_forearm01_L',
        '右ひじ':'cf_j_forearm01_R',
        '左肩':'cf_j_shoulder_L',
        '右肩':'cf_j_shoulder_R',
        '左手首':'cf_j_hand_L',
        '右手首':'cf_j_hand_R',
        '左親指０':'cf_j_thumb01_L',
        '左親指１':'cf_j_thumb02_L',
        '左親指２':'cf_j_thumb03_L',
        '左薬指１':'cf_j_ring01_L',
        '左薬指２':'cf_j_ring02_L',
        '左薬指３':'cf_j_ring03_L',
        '左中指１':'cf_j_middle01_L',
        '左中指２':'cf_j_middle02_L',
        '左中指３':'cf_j_middle03_L',
        '左小指１':'cf_j_little01_L',
        '左小指２':'cf_j_little02_L',
        '左小指３':'cf_j_little03_L',
        '左人指１':'cf_j_index01_L',
        '左人指２':'cf_j_index02_L',
        '左人指３':'cf_j_index03_L',
        '右親指０':'cf_j_thumb01_R',
        '右親指１':'cf_j_thumb02_R',
        '右親指２':'cf_j_thumb03_R',
        '右薬指１':'cf_j_ring01_R',
        '右薬指２':'cf_j_ring02_R',
        '右薬指３':'cf_j_ring03_R',
        '右中指１':'cf_j_middle01_R',
        '右中指２':'cf_j_middle02_R',
        '右中指３':'cf_j_middle03_R',
        '右小指１':'cf_j_little01_R',
        '右小指２':'cf_j_little02_R',
        '右小指３':'cf_j_little03_R',
        '右人指１':'cf_j_index01_R',
        '右人指２':'cf_j_index02_R',
        '右人指３':'cf_j_index03_R',
        '下半身':'cf_j_waist01',
        '左足':'cf_j_thigh00_L',
        '右足':'cf_j_thigh00_R',
        '左ひざ':'cf_j_leg01_L',
        '右ひざ':'cf_j_leg01_R',
        '左足首':'cf_j_leg03_L',
        '右足首':'cf_j_leg03_R',
        }
        for bone in pmx_rename_dict:
            if self.armature.pose.bones.get(pmx_rename_dict[bone]):
                self.armature.pose.bones[pmx_rename_dict[bone]].mmd_bone.name_j = bone
        c.print_timer('rename_mmd_bones')

    def visually_connect_bones(self):
        '''make sure certain bones are visually connected'''
        if not bpy.context.scene.kkbp.armature_dropdown in ['A', 'B']:
            return
        c.switch(self.armature, 'edit')
        # Make sure all toe bones are visually correct if using the better penetration armature 
        try:
            self.armature.data.edit_bones['Toes4_L'].tail.y = self.armature.data.edit_bones['Toes30_L'].head.y
            self.armature.data.edit_bones['Toes4_L'].tail.z = self.armature.data.edit_bones['Toes30_L'].head.z*.8
            self.armature.data.edit_bones['Toes0_L'].tail.y = self.armature.data.edit_bones['Toes10_L'].head.y
            self.armature.data.edit_bones['Toes0_L'].tail.z = self.armature.data.edit_bones['Toes30_L'].head.z*.9
            
            self.armature.data.edit_bones['Toes30_L'].tail.z = self.armature.data.edit_bones['Toes30_L'].head.z*0.8
            self.armature.data.edit_bones['Toes30_L'].tail.y = self.armature.data.edit_bones['Toes30_L'].head.y*1.2
            self.armature.data.edit_bones['Toes20_L'].tail.z = self.armature.data.edit_bones['Toes20_L'].head.z*0.8
            self.armature.data.edit_bones['Toes20_L'].tail.y = self.armature.data.edit_bones['Toes20_L'].head.y*1.2
            self.armature.data.edit_bones['Toes10_L'].tail.z = self.armature.data.edit_bones['Toes10_L'].head.z*0.8
            self.armature.data.edit_bones['Toes10_L'].tail.y = self.armature.data.edit_bones['Toes10_L'].head.y*1.2
            
            self.armature.data.edit_bones['Toes4_R'].tail.y = self.armature.data.edit_bones['Toes30_R'].head.y
            self.armature.data.edit_bones['Toes4_R'].tail.z = self.armature.data.edit_bones['Toes30_R'].head.z*.8
            self.armature.data.edit_bones['Toes0_R'].tail.y = self.armature.data.edit_bones['Toes10_R'].head.y
            self.armature.data.edit_bones['Toes0_R'].tail.z = self.armature.data.edit_bones['Toes30_R'].head.z*.9
            
            self.armature.data.edit_bones['Toes30_R'].tail.z = self.armature.data.edit_bones['Toes30_R'].head.z*0.8
            self.armature.data.edit_bones['Toes30_R'].tail.y = self.armature.data.edit_bones['Toes30_R'].head.y*1.2
            self.armature.data.edit_bones['Toes20_R'].tail.z = self.armature.data.edit_bones['Toes20_R'].head.z*0.8
            self.armature.data.edit_bones['Toes20_R'].tail.y = self.armature.data.edit_bones['Toes20_R'].head.y*1.2
            self.armature.data.edit_bones['Toes10_R'].tail.z = self.armature.data.edit_bones['Toes10_R'].head.z*0.8
            self.armature.data.edit_bones['Toes10_R'].tail.y = self.armature.data.edit_bones['Toes10_R'].head.y*1.2
        except:
            #this character isn't using the BP/toe control armature
            pass
        c.switch(self.armature, 'object')
        c.print_timer('visually_connect_bones')

    def shorten_kokan_bone(self):
        '''make the kokan bone shorter if it's on the armature'''
        if not bpy.context.scene.kkbp.armature_dropdown in ['A', 'B']:
            return
        c.switch(self.armature, 'edit')
        if self.armature.data.edit_bones.get('cf_j_kokan'):
            self.armature.data.edit_bones['cf_j_kokan'].tail.z = self.armature.data.edit_bones['cf_s_waist02'].head.z
        c.print_timer('shorten_kokan_bone')

    def scale_skirt_and_face_bones(self):
        '''scales skirt bones and face bones down. Scales BP bones down if exists'''

        #skip this operation if this is the pmx or koikatsu armature
        if not bpy.context.scene.kkbp.armature_dropdown in ['A', 'B']:
            return

        c.switch(self.armature, 'pose')

        def shorten_bone(bone, scale):
            c.switch(self.armature, 'edit')
            self.armature.data.edit_bones[bone].select_head = True
            self.armature.data.edit_bones[bone].select_tail = True
            previous_roll = self.armature.data.edit_bones[bone].roll + 1 #roll doesn't save if you don't add a number at the end
            self.armature.data.edit_bones[bone].tail = (self.armature.data.edit_bones[bone].tail+self.armature.data.edit_bones[bone].head)/2
            self.armature.data.edit_bones[bone].tail = (self.armature.data.edit_bones[bone].tail+self.armature.data.edit_bones[bone].head)/2
            self.armature.data.edit_bones[bone].tail = (self.armature.data.edit_bones[bone].tail+self.armature.data.edit_bones[bone].head)/2
            self.armature.data.edit_bones[bone].select_head = False
            self.armature.data.edit_bones[bone].select_tail = False
            self.armature.data.edit_bones[bone].roll = previous_roll - 1 #subtract the number at the end to save roll
            c.switch(self.armature, 'pose')
        
        def connect_bone(root, chain):
            bone = 'cf_j_sk_0'+str(root)+'_0'+str(chain)
            child_bone = 'cf_j_sk_0'+str(root)+'_0'+str(chain+1)
            #first connect tail to child bone to keep head in place during connection
            c.switch(self.armature, 'edit')
            if self.armature.data.edit_bones.get(bone) and self.armature.data.edit_bones.get(child_bone) and chain <= 4:
                self.armature.data.edit_bones[bone].tail = self.armature.data.edit_bones[child_bone].head
                #then connect child head to parent tail (both are at the same position, so head doesn't move)
                self.armature.data.edit_bones[child_bone].use_connect = True

        skirtchain = [0,1,2,3,4,5,6,7]
        skirtchild = [0,1,2,3,4]
        try:
            for root in skirtchain:
                for chain in skirtchild:
                    connect_bone(root, chain)
        except:
            c.kklog('No skirt bones detected. Skipping...', type = 'warn')
        
        #scale eye bones, mouth bones, eyebrow bones
        c.switch(self.armature, 'pose')
        
        eyebones = [1,2,3,4,5,6,7,8]
        
        for piece in eyebones:
            bpy.ops.pose.select_all(action='DESELECT')
            left = 'cf_J_Eye0'+str(piece)+'_s_L'
            right = 'cf_J_Eye0'+str(piece)+'_s_R'
            
            shorten_bone(left, 0.1)
            shorten_bone(right, 0.1)
            
        restOfFace = [
        'cf_J_Mayu_R', 'cf_J_MayuMid_s_R', 'cf_J_MayuTip_s_R',
        'cf_J_Mayu_L', 'cf_J_MayuMid_s_L', 'cf_J_MayuTip_s_L',
        'cf_J_Mouth_R', 'cf_J_Mouth_L',
        'cf_J_Mouthup', 'cf_J_MouthLow', 'cf_J_MouthMove', 'cf_J_MouthCavity']
        
        for bone in restOfFace:
            bpy.ops.pose.select_all(action='DESELECT')
            shorten_bone(bone, 0.1)
        
        #move eye bone location
        c.switch(self.armature, 'edit')

        for eyebone in ['Eyesx', 'Eye Controller']:
            self.armature.data.edit_bones[eyebone].head.y = self.armature.data.edit_bones['cf_d_bust02_R'].tail.y
            self.armature.data.edit_bones[eyebone].tail.y = self.armature.data.edit_bones['cf_d_bust02_R'].tail.y*1.5
            self.armature.data.edit_bones[eyebone].tail.z = self.armature.data.edit_bones['cf_J_Nose_tip'].tail.z
            self.armature.data.edit_bones[eyebone].head.z = self.armature.data.edit_bones['cf_J_Nose_tip'].tail.z

        #scale BP bones if they exist
        BPList = ['cf_j_kokan', 'cf_j_ana', 'Vagina_Root', 'Vagina_B', 'Vagina_F', 'Vagina_001_L', 'Vagina_002_L', 'Vagina_003_L', 'Vagina_004_L', 'Vagina_005_L',  'Vagina_001_R', 'Vagina_002_R', 'Vagina_003_R', 'Vagina_004_R', 'Vagina_005_R']
        for bone in BPList:
            if self.armature.data.edit_bones.get(bone):
                self.armature.data.edit_bones[bone].tail.z = self.armature.data.edit_bones[bone].tail.z*.95
        c.print_timer('scale_skirt_and_face_bones')

    def create_eye_reference_bone(self):
        '''Create a bone called "Eyesx that will act as a fixed reference bone for the Eye controller" '''
        if not bpy.context.scene.kkbp.armature_dropdown in ['A', 'B']:
            return
        c.switch(self.armature, 'edit')       
        new_bone = self.armature.data.edit_bones.new('Eyesx')
        new_bone.head = self.armature.data.edit_bones['cf_hit_head'].tail
        new_bone.head.y = new_bone.head.y + 0.05
        new_bone.tail = self.armature.data.edit_bones['cf_J_Mayu_R'].tail
        new_bone.tail.x = new_bone.head.x
        new_bone.tail.y = new_bone.head.y
        new_bone.parent = self.armature.data.edit_bones['cf_j_head']
        c.print_timer('create_eye_reference_bone')

    def create_eye_controller_bone(self):
        if not bpy.context.scene.kkbp.armature_dropdown in ['A', 'B']:
            return
        c.switch(self.armature, 'edit')
    
        #roll the eye bone based on armature, create a copy and name it eye controller
        armature_data = self.armature.data
        armature_data.edit_bones['Eyesx'].roll = -math.pi/2
        copy = self.new_bone('Eye Controller')
        copy.head = armature_data.edit_bones['Eyesx'].head/2
        copy.tail = armature_data.edit_bones['Eyesx'].tail/2
        copy.matrix = armature_data.edit_bones['Eyesx'].matrix
        copy.parent = armature_data.edit_bones['cf_j_head']
        armature_data.edit_bones['Eye Controller'].roll = -math.pi/2

        c.switch(self.armature, 'pose')
        #Lock y location at zero
        self.armature.pose.bones['Eye Controller'].lock_location[1] = True
        #Hide the original Eyesx bone
        self.armature.data.bones['Eyesx'].hide = True
        self.set_armature_layer('Eye Controller', 0)
        c.switch(self.armature, 'object')

        #Create a UV warp modifier for the eyes. Controlled by the Eye controller bone
        def eyeUV(modifiername, eyevertexgroup):
            mod = bpy.data.objects['Body'].modifiers.new(modifiername, 'UV_WARP')
            mod.axis_u = 'Z'
            mod.axis_v = 'X'
            mod.object_from = self.armature
            mod.bone_from = self.armature.data.bones['Eyesx'].name
            mod.object_to = self.armature
            mod.bone_to = self.armature.data.bones['Eye Controller'].name
            mod.vertex_group = eyevertexgroup
            mod.uv_layer = 'UVMap'
            mod.show_expanded = False

        eyeUV("Left Eye UV warp",  'Left Eye')
        eyeUV("Right Eye UV warp", 'Right Eye')
        c.print_timer('create_eye_controller_bone')

    def fix_empty_eye_vertex_groups(self):
        '''checks if the Eyex_L vertex group is empty. If it is, assume the Eyex_R vertex group is also empty,
        then fix it by finding the vertices using the eye material and assign both eyes to Eyex_L'''
        if not bpy.context.scene.kkbp.armature_dropdown in ['A', 'B']:
            return
        c.switch(self.body, 'object')
        #make the cf_J_hitomi_tx_L vertex group active
        self.body.vertex_groups.active_index = self.body.vertex_groups['cf_J_hitomi_tx_L'].index
        #go into edit mode and select the vertices in the cf_J_hitomi_tx_L vertex group
        c.switch(self.body, 'edit')
        bpy.ops.object.vertex_group_select()
        #refresh the selection (this needs to be done for some reason)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        #get a list of the selected vertices
        vgVerts = True if [v for v in self.body.data.vertices if v.select] else False
        #If the list is empty...
        if not vgVerts:
            #select the eye materials
            self.body.active_material_index = self.body.data.materials.find(self.body['SMR materials']['cf_Ohitomi_L02'])
            bpy.ops.object.material_slot_select()
            #Try to select the other eye if it wasn't merged
            try:
                self.body.active_material_index = self.body.data.materials.find(self.body['SMR materials']['cf_Ohitomi_R02'])
                bpy.ops.object.material_slot_select()
            except:
                #the eye was already merged, skip
                pass
            #then assign them to the Eyex_L group
            bpy.ops.object.vertex_group_assign()
            bpy.ops.mesh.select_all(action = 'DESELECT')
        c.print_timer('fix_empty_eye_vertex_groups')

    def prepare_ik_bones(self):
        '''reparents some bones to work for IK'''
        if not bpy.context.scene.kkbp.armature_dropdown in ['A','B']:
            return
        #Select the armature and make it active
        c.switch(self.armature, 'edit')
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
        #separate the PV bones, so the elbow IKs rotate with the spine
        pvrootupper = self.new_bone('cf_pv_root_upper')
        pvrootupper.tail = self.armature.data.edit_bones['cf_pv_root'].tail
        pvrootupper.head = self.armature.data.edit_bones['cf_pv_root'].head
        #reparent things
        def reparent(bone,newparent):
            #refresh armature by going to object mode then back to edit mode?
            c.switch(self.armature, 'edit')
            self.armature.data.edit_bones[bone].parent = self.armature.data.edit_bones[newparent]
        reparent('cf_pv_root_upper', 'cf_j_spine01')
        reparent('cf_pv_elbo_R', 'cf_pv_root_upper')
        reparent('cf_pv_elbo_L', 'cf_pv_root_upper')
        c.print_timer('prepare_ik_bones')

    def create_ik_bones(self):
        '''give the leg a foot IK, the foot a heel controller, and the arm a hand IK'''
        if not bpy.context.scene.kkbp.armature_dropdown in ['A','B']:
            return
        center_bone = self.armature.data.edit_bones['cf_n_height']
        c.switch(self.armature, 'edit')
        self.retreive_stored_tags()
        
        def legIK(legbone, IKtarget, IKpole, IKpoleangle, footIK, kneebone, toebone, footbone):
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[legbone]

            #Make IK
            self.retreive_stored_tags()
            bone.constraints.new("IK")

            #Set target and subtarget
            self.retreive_stored_tags()
            bone.constraints["IK"].target = self.armature
            self.retreive_stored_tags()
            bone.constraints["IK"].subtarget = self.armature.data.bones[IKtarget].name

            #Set pole and subpole and pole angle
            self.retreive_stored_tags()
            bone.constraints["IK"].pole_target = self.armature
            self.retreive_stored_tags()
            bone.constraints["IK"].pole_subtarget = self.armature.data.bones[IKpole].name
            self.retreive_stored_tags()
            bone.constraints["IK"].pole_angle = IKpoleangle

            #Set chain length
            self.retreive_stored_tags()
            bone.constraints["IK"].chain_count=2

            #Flip foot IK to match foot bone
            self.retreive_stored_tags()
            bone = self.armature.data.edit_bones[footIK]
            self.retreive_stored_tags()

            bone = self.armature.data.edit_bones[footIK]
            bone.head.y = self.armature.data.edit_bones[kneebone].tail.y
            self.retreive_stored_tags()
            bone = self.armature.data.edit_bones[footIK]
            bone.tail.z = self.armature.data.edit_bones[toebone].head.z
            self.retreive_stored_tags()
            bone = self.armature.data.edit_bones[footIK]
            bone.head.z = self.armature.data.edit_bones[footbone].head.z
            self.retreive_stored_tags()

            bone = self.armature.data.edit_bones[footIK]
            bone.head.x = self.armature.data.edit_bones[kneebone].tail.x
            self.retreive_stored_tags()
            bone = self.armature.data.edit_bones[footIK]
            bone.tail.x = bone.head.x

            #unparent the bone
            self.retreive_stored_tags()
            center_bone = self.armature.data.edit_bones['cf_n_height']
            bone = self.armature.data.edit_bones[footIK]
            bone.parent = center_bone

            #set rotation constraints
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[legbone]
            bone.constraints.new("LIMIT_ROTATION")
            bone.constraints[1].use_limit_x = True
            bone.constraints[1].max_x = 3.13287

        #Run for each side
        legIK('cf_j_leg01_R', 'cf_pv_foot_R', 'cf_pv_knee_R', math.pi/2, 'cf_pv_foot_R', 'cf_j_leg01_R', 'cf_j_toes_R', 'cf_j_foot_R')
        legIK('cf_j_leg01_L',  'cf_pv_foot_L', 'cf_pv_knee_L', math.pi/2, 'cf_pv_foot_L', 'cf_j_leg01_L', 'cf_j_toes_L', 'cf_j_foot_L')
        #adds an IK for the toe bone, moves the knee IKs a little closer to the body
        def footIK(footbone, toebone, footIK, kneebone, legbone):
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[footbone]

            #Make Copy rotation
            self.retreive_stored_tags()
            bone.constraints.new("COPY_ROTATION")

            #Set target and subtarget
            self.retreive_stored_tags()
            bone.constraints[0].target=self.armature
            self.retreive_stored_tags()
            bone.constraints[0].subtarget=self.armature.data.bones[footIK].name

            #Set the rotation to local space
            self.retreive_stored_tags()
            bone.constraints[0].target_space = 'LOCAL_WITH_PARENT'
            self.retreive_stored_tags()
            bone.constraints[0].owner_space = 'LOCAL_WITH_PARENT'
            
            # move knee IKs closer to body
            self.retreive_stored_tags()
            kneedist = round((self.armature.pose.bones[footbone].head - self.armature.pose.bones[footbone].tail).length,2)
            self.retreive_stored_tags()
            self.armature.data.edit_bones[kneebone].head.y = kneedist * -5
            self.retreive_stored_tags()
            self.armature.data.edit_bones[kneebone].tail.y = kneedist * -5

            # make toe bone shorter
            self.retreive_stored_tags()
            self.armature.data.edit_bones[toebone].tail.z = self.armature.data.edit_bones[legbone].head.z * 0.2

        #Run for each side
        footIK('cf_j_foot_R', 'cf_j_toes_R', 'cf_pv_foot_R', 'cf_pv_knee_R', 'cf_j_leg01_R')
        footIK('cf_j_foot_L',  'cf_j_toes_L', 'cf_pv_foot_L', 'cf_pv_knee_L', 'cf_j_leg01_L')

        #Add a heel controller to the foot
        #this fucking thing keeps crashing so retreive_stored_tags is called after most operations
        def heelController(footbone, footIK, toebone):
            self.retreive_stored_tags()
            #duplicate the foot IK. This is the new master bone
            c.switch(self.armature, 'edit')
            self.retreive_stored_tags()
            masterbone = self.new_bone('MasterFootIK.' + footbone[-1])
            self.retreive_stored_tags()
            masterbone = self.armature.data.edit_bones['MasterFootIK.' + footbone[-1]]
            self.retreive_stored_tags()
            masterbone.head = self.armature.data.edit_bones[footbone].head
            self.retreive_stored_tags()
            masterbone = self.armature.data.edit_bones['MasterFootIK.' + footbone[-1]]
            self.retreive_stored_tags()
            masterbone.tail = self.armature.data.edit_bones[footbone].tail
            self.retreive_stored_tags()
            masterbone = self.armature.data.edit_bones['MasterFootIK.' + footbone[-1]]
            self.retreive_stored_tags()
            masterbone.matrix = self.armature.data.edit_bones[footbone].matrix
            self.retreive_stored_tags()
            masterbone = self.armature.data.edit_bones['MasterFootIK.' + footbone[-1]]
            self.retreive_stored_tags()
            masterbone.parent = self.armature.data.edit_bones['cf_n_height']
            
            #Create the heel controller
            heelIK = self.new_bone('HeelIK.' + footbone[-1])
            self.retreive_stored_tags()
            heelIK = self.armature.data.edit_bones['HeelIK.' + footbone[-1]]
            self.retreive_stored_tags()
            heelIK.head = self.armature.data.edit_bones[footbone].tail
            self.retreive_stored_tags()
            heelIK = self.armature.data.edit_bones['HeelIK.' + footbone[-1]]
            self.retreive_stored_tags()
            heelIK.tail = self.armature.data.edit_bones[footbone].head
            self.retreive_stored_tags()
            heelIK = self.armature.data.edit_bones['HeelIK.' + footbone[-1]]
            self.retreive_stored_tags()
            heelIK.parent = masterbone
            self.retreive_stored_tags()
            heelIK = self.armature.data.edit_bones['HeelIK.' + footbone[-1]]
            self.retreive_stored_tags()
            heelIK = self.armature.data.edit_bones['HeelIK.' + footbone[-1]]
            self.retreive_stored_tags()
            heelIK.tail.y *= .5
            self.retreive_stored_tags()

            #parent footIK to heel controller
            self.armature.data.edit_bones[footIK].parent = heelIK
            
            #make a bone to pin the foot
            self.retreive_stored_tags()
            footPin = self.new_bone('FootPin.' + footbone[-1])
            self.retreive_stored_tags()
            footPin = self.armature.data.edit_bones['FootPin.' + footbone[-1]]
            self.retreive_stored_tags()
            footPin.head = self.armature.data.edit_bones[toebone].head
            self.retreive_stored_tags()
            footPin = self.armature.data.edit_bones['FootPin.' + footbone[-1]]
            self.retreive_stored_tags()
            footPin.tail = self.armature.data.edit_bones[toebone].tail
            self.retreive_stored_tags()
            footPin = self.armature.data.edit_bones['FootPin.' + footbone[-1]]
            self.retreive_stored_tags()
            footPin.parent = masterbone
            self.retreive_stored_tags()
            footPin = self.armature.data.edit_bones['FootPin.' + footbone[-1]]
            self.retreive_stored_tags()
            footPin.tail.z*=.8
            self.retreive_stored_tags()
            #make a bone to allow rotation of the toe along an arc
            self.retreive_stored_tags()
            toeRotator = self.new_bone('ToeRotator.' + footbone[-1])
            self.retreive_stored_tags()
            toeRotator = self.armature.data.edit_bones['ToeRotator.' + footbone[-1]]
            self.retreive_stored_tags()
            toeRotator.head = self.armature.data.edit_bones[toebone].head
            self.retreive_stored_tags()
            toeRotator = self.armature.data.edit_bones['ToeRotator.' + footbone[-1]]
            self.retreive_stored_tags()
            toeRotator.tail = self.armature.data.edit_bones[toebone].tail
            self.retreive_stored_tags()
            toeRotator = self.armature.data.edit_bones['ToeRotator.' + footbone[-1]]
            self.retreive_stored_tags()
            toeRotator.parent = masterbone
            self.retreive_stored_tags()
            #make a bone to pin the toe
            self.retreive_stored_tags()
            toePin = self.new_bone('ToePin.' + footbone[-1])
            self.retreive_stored_tags()
            toePin = self.armature.data.edit_bones['ToePin.' + footbone[-1]]
            self.retreive_stored_tags()
            toePin.head = self.armature.data.edit_bones[toebone].tail
            self.retreive_stored_tags()
            toePin = self.armature.data.edit_bones['ToePin.' + footbone[-1]]
            self.retreive_stored_tags()
            toePin.tail = self.armature.data.edit_bones[toebone].tail
            self.retreive_stored_tags()
            toePin = self.armature.data.edit_bones['ToePin.' + footbone[-1]]
            self.retreive_stored_tags()
            toePin.parent = toeRotator
            self.retreive_stored_tags()
            toePin = self.armature.data.edit_bones['ToePin.' + footbone[-1]]
            toePin.tail.z *=1.2
            self.retreive_stored_tags()
            #pin the foot
            self.retreive_stored_tags()
            c.switch(self.armature, 'pose')
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[footbone]
            self.retreive_stored_tags()
            bone.constraints.new("IK")
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[footbone]
            self.retreive_stored_tags()
            bone.constraints["IK"].target = self.armature
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[footbone]
            self.retreive_stored_tags()
            bone.constraints["IK"].subtarget = self.armature.data.bones['FootPin.' + footbone[-1]].name
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[footbone]
            self.retreive_stored_tags()
            bone.constraints["IK"].chain_count=1
            self.retreive_stored_tags()
            #pin the toe
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[toebone]
            self.retreive_stored_tags()
            bone.constraints.new("IK")
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[toebone]
            self.retreive_stored_tags()
            bone.constraints["IK"].target = self.armature
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[toebone]
            self.retreive_stored_tags()
            bone.constraints["IK"].subtarget = self.armature.data.bones['ToePin.' + footbone[-1]].name
            self.retreive_stored_tags()
            bone = self.armature.pose.bones[toebone]
            self.retreive_stored_tags()
            bone.constraints["IK"].chain_count=1
            self.retreive_stored_tags()
            #move these bones to armature layer 2
            self.retreive_stored_tags()
            bpy.ops.object.mode_set(mode='POSE') #use this instead of c.switch to prevent crashing
            self.retreive_stored_tags()
            layer2 =   (False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
            self.retreive_stored_tags()
            bpy.ops.pose.select_all(action='DESELECT')
            self.retreive_stored_tags()
            if bpy.app.version[0] == 3:
                self.armature.data.bones['FootPin.' + footbone[-1]].select = True
                self.retreive_stored_tags()
                self.armature.data.bones['ToePin.' + footbone[-1]].select = True
                self.retreive_stored_tags()
                self.armature.data.bones[toebone].select = True
                self.retreive_stored_tags()
                bpy.ops.pose.bone_layers(layers=layer2)
                self.retreive_stored_tags()
                self.armature.data.bones[footIK].select = True
            else:
                self.armature.data.bones['FootPin.' + footbone[-1]].collections.clear()
                self.retreive_stored_tags()
                self.set_armature_layer('FootPin.' + footbone[-1], 2)
                self.retreive_stored_tags()
                self.armature.data.bones['ToePin.' + footbone[-1]].collections.clear()
                self.retreive_stored_tags()
                self.set_armature_layer('ToePin.' + footbone[-1], 2)
                self.retreive_stored_tags()
                self.armature.data.bones[toebone].collections.clear()
                self.retreive_stored_tags()
                self.set_armature_layer(toebone, 2)
                self.retreive_stored_tags()
                self.armature.data.bones[footIK].collections.clear()
                self.retreive_stored_tags()
                self.set_armature_layer(footIK, 2)
        self.retreive_stored_tags()
        heelController('cf_j_foot_L', 'cf_pv_foot_L', 'cf_j_toes_L')
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        heelController('cf_j_foot_R', 'cf_pv_foot_R', 'cf_j_toes_R')
        self.retreive_stored_tags()
        #Give the new foot IKs an mmd bone name
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        self.retreive_stored_tags()
        self.armature.pose.bones['MasterFootIK.L'].mmd_bone.name_j = '左足ＩＫ'
        self.retreive_stored_tags()
        self.armature.pose.bones['MasterFootIK.R'].mmd_bone.name_j = '右足ＩＫ'
        self.retreive_stored_tags()
        #add an IK to the arm, makes the wrist bone copy the hand IK's rotation, moves elbow IKs a little closer to the body
        def armhandIK(elbowbone, handcontroller, elbowcontroller, IKangle, wristbone):
            #Set IK bone
            bone = self.armature.pose.bones[elbowbone]

            #Add IK
            bone.constraints.new("IK")

            #Set target and subtarget
            bone.constraints["IK"].target = self.armature
            bone.constraints["IK"].subtarget = self.armature.data.bones[handcontroller].name

            #Set pole and subpole and pole angle
            bone.constraints["IK"].pole_target = self.armature
            bone.constraints["IK"].pole_subtarget = self.armature.data.bones[elbowcontroller].name
            bone.constraints["IK"].pole_angle= IKangle

            #Set chain length
            bone.constraints["IK"].chain_count=2

            #unparent the bone
            c.switch(self.armature, 'edit')
            self.retreive_stored_tags()
            bone = self.armature.data.edit_bones[handcontroller]
            bone.parent = self.armature.data.edit_bones['cf_n_height']
            self.armature.data.bones[wristbone].hide = True
            
            # move elbow IKs closer to body
            elbowdist = round((self.armature.data.edit_bones[elbowbone].head - self.armature.data.edit_bones[elbowbone].tail).length,2)
            self.armature.data.edit_bones[elbowcontroller].head.y = elbowdist*2
            self.armature.data.edit_bones[elbowcontroller].tail.y = elbowdist*2
            c.switch(self.armature, 'pose')

            # Set hand rotation then hide it
            bone = self.armature.pose.bones[wristbone]
            bone.constraints.new("COPY_ROTATION")
            bone.constraints[0].target=self.armature
            bone.constraints[0].subtarget=self.armature.data.bones[handcontroller].name

            #set arm limit constraint
            bone = self.armature.pose.bones[elbowbone]
            bone.constraints.new("LIMIT_ROTATION")
            bone.constraints[1].use_limit_z = True
            bone.constraints[1].max_z = 6.26573

        #Run for each side
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        armhandIK('cf_j_forearm01_R', 'cf_pv_hand_R', 'cf_pv_elbo_R', 0, 'cf_j_hand_R')
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        armhandIK('cf_j_forearm01_L',  'cf_pv_hand_L', 'cf_pv_elbo_L', 180, 'cf_j_hand_L')

        #move newly created bones to correct armature layers
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        self.set_armature_layer('MasterFootIK.L', 0)
        self.set_armature_layer('MasterFootIK.R', 0)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        self.set_armature_layer('HeelIK.L', 0)
        self.set_armature_layer('HeelIK.R', 0)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        self.set_armature_layer('ToeRotator.L', 0)
        self.set_armature_layer('ToeRotator.R', 0)
        self.set_armature_layer('cf_d_bust00', 0)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        self.armature.data.bones['cf_pv_root_upper'].hide = True
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        c.switch(self.armature, 'object')
        self.retreive_stored_tags()

    def create_joint_drivers(self):
        '''There are several joint corrections that use the cf_d_ and cf_s_ bones on the armature. This function attempts to replicate them using blender drivers and bone constraints'''
        if not bpy.context.scene.kkbp.armature_dropdown in ['A','B']:
            return
        c.switch(self.armature, 'pose')
        #generic function to set a copy rotation modifier
        def set_copy(bone, bonetarget, influence, axis = 'all', mix = 'replace', space = 'LOCAL'):
            constraint = self.armature.pose.bones[bone].constraints.new("COPY_ROTATION")
            constraint.target = self.armature
            constraint.subtarget = bonetarget
            constraint.influence = influence
            constraint.target_space = space
            constraint.owner_space = space

            if axis == 'X':
                constraint.use_y = False
                constraint.use_z = False
            
            elif axis == 'Y':
                constraint.use_x = False
                constraint.use_z = False
            
            elif axis == 'antiX':
                constraint.use_y = False
                constraint.use_z = False
                constraint.invert_x = True
            
            elif axis == 'Z':
                constraint.use_x = False
                constraint.use_y = False

            if mix == 'add':
                constraint.mix_mode = 'ADD'

        #setup most of the drivers with this
        set_copy('cf_d_shoulder02_L', 'cf_j_arm00_L', 0.5)
        set_copy('cf_d_arm01_L', 'cf_j_arm00_L', 0.75, axis = 'X')
        set_copy('cf_d_arm02_L', 'cf_j_arm00_L', 0.5, axis = 'X')
        set_copy('cf_d_arm03_L', 'cf_j_arm00_L', 0.25, axis = 'X')
        set_copy('cf_d_forearm02_L', 'cf_j_hand_L', 0.33, axis = 'X')
        set_copy('cf_d_wrist_L', 'cf_j_hand_L', 0.33, axis = 'X', )
        set_copy('cf_d_kneeF_L', 'cf_j_leg01_L', 0.5, axis = 'antiX', mix = 'add')
        set_copy('cf_d_siri_L', 'cf_j_thigh00_L', 0.33)
        set_copy('cf_d_thigh02_L', 'cf_j_thigh00_L', 0.25, axis='Y')
        set_copy('cf_d_thigh03_L', 'cf_j_thigh00_L', 0.25, axis='Y')
        set_copy('cf_d_leg02_L', 'cf_j_leg01_L', 0.33, axis='Y')
        set_copy('cf_d_leg03_L', 'cf_j_leg01_L', 0.66, axis='Y')

        set_copy('cf_d_shoulder02_R', 'cf_j_arm00_R', 0.5)
        set_copy('cf_d_arm01_R', 'cf_j_arm00_R', 0.75, axis = 'X')
        set_copy('cf_d_arm02_R', 'cf_j_arm00_R', 0.5, axis = 'X')
        set_copy('cf_d_arm03_R', 'cf_j_arm00_R', 0.25, axis = 'X')
        set_copy('cf_d_forearm02_R', 'cf_j_hand_R', 0.33, axis = 'X')
        set_copy('cf_d_wrist_R', 'cf_j_hand_R', 0.33, axis = 'X')
        set_copy('cf_d_kneeF_R', 'cf_j_leg01_R', 0.5, axis = 'antiX', mix = 'add')
        set_copy('cf_d_siri_R', 'cf_j_thigh00_R', 0.33)
        set_copy('cf_d_thigh02_R', 'cf_j_thigh00_R', 0.25, axis='Y')
        set_copy('cf_d_thigh03_R', 'cf_j_thigh00_R', 0.25, axis='Y')
        set_copy('cf_d_leg02_R', 'cf_j_leg01_R', 0.33, axis='Y')
        set_copy('cf_d_leg03_R', 'cf_j_leg01_R', 0.66, axis='Y')

        #move the waist some if only one leg is rotated
        set_copy('cf_s_waist02', 'cf_j_thigh00_L', 0.1, mix = 'add')
        set_copy('cf_s_waist02', 'cf_j_thigh00_R', 0.1, mix = 'add')
        #set_copy('cf_s_waist02', 'cf_j_thigh00_R', 0.1, mix = 'add')
        #set_copy('cf_s_waist02', 'cf_j_thigh00_L', 0.1, mix = 'add')

        set_copy('cf_s_waist02', 'cf_j_waist02', 0.5, axis = 'antiX')

        #this rotation helps when doing a split
        set_copy('cf_s_leg_L', 'cf_j_thigh00_L', .9, axis = 'Z', mix = 'add')
        set_copy('cf_s_leg_R', 'cf_j_thigh00_R', .9, axis = 'Z', mix = 'add')

        #generic function for creating a driver
        def setDriver (bone, drivertype, drivertypeselect, drivertarget, drivertt, drivermult, expresstype = 'move'):

            #add driver to first component
            #drivertype is the kind of driver you want to be applied to the bone and can be location/rotation
            #drivertypeselect is the component of the bone you want the driver to be applied to
            # for location it's (0 is x component, y is 1, z is 2)
            # for rotation it's (0 is w, 1 is x, etc)
            # for scale it's (0 is x, 1 is y, 2 is z)
            driver = self.armature.pose.bones[bone].driver_add(drivertype, drivertypeselect)

            #add driver variable
            vari = driver.driver.variables.new()
            vari.name = 'var'
            vari.type = 'TRANSFORMS'

            #set the target and subtarget
            target = vari.targets[0]
            target.id = self.armature
            target.bone_target = self.armature.pose.bones[drivertarget].name

            #set the transforms for the target. this can be rotation or location 
            target.transform_type = drivertt

            #set the transform space. can be world space too
            target.transform_space = 'LOCAL_SPACE'
            target.rotation_mode = 'QUATERNION' if expresstype in ['scale', 'quat'] else 'AUTO'

            #use the distance to the target bone's parent to make results consistent for different sized bones
            targetbonelength = str(round((self.armature.pose.bones[drivertarget].head - self.armature.pose.bones[drivertarget].parent.head).length,3))
            
            #driver expression is the rotation value of the target bone multiplied by a percentage of the driver target bone's length
            if expresstype in ['move', 'quat']:
                driver.driver.expression = vari.name + '*' + targetbonelength + '*' + drivermult 
            
            #move but only during positive rotations
            elif expresstype == 'movePos':
                driver.driver.expression = vari.name + '*' + targetbonelength + '*' + drivermult + ' if ' + vari.name + ' > 0 else 0'
            
            #move but only during negative rotations
            elif expresstype == 'moveNeg':
                driver.driver.expression = vari.name + '*' + targetbonelength + '*' + drivermult + ' if ' + vari.name + ' < 0 else 0'
            
            #move but the ABS value
            elif expresstype == 'moveABS':    
                driver.driver.expression = 'abs(' + vari.name + '*' + targetbonelength + '*' + drivermult +')'

            #move but the negative ABS value
            elif expresstype == 'moveABSNeg':
                driver.driver.expression = '-abs(' + vari.name + '*' + targetbonelength + '*' + drivermult +')'
            
            #move but exponentially
            elif expresstype == 'moveexp':
                driver.driver.expression = vari.name + '*' + vari.name + '*' + targetbonelength + '*' + drivermult
            
            elif expresstype == 'scale':
                driver.driver.expression = '1 + ' + vari.name + '*' + targetbonelength + '*' + drivermult
            
            elif expresstype == 'rotation':
                driver.driver.expression = vari.name + '*' + targetbonelength + '*' + drivermult

        #Set the remaining joint correction drivers
        #set knee joint corrections. These go in toward the body and down toward the foot at an exponential rate
        setDriver('cf_s_kneeB_R', 'location', 1, 'cf_j_leg01_R', 'ROT_X',  '-0.2', expresstype = 'moveexp')
        setDriver('cf_s_kneeB_R', 'location', 2, 'cf_j_leg01_R', 'ROT_X',  '-0.08')

        setDriver('cf_s_kneeB_L', 'location', 1, 'cf_j_leg01_L', 'ROT_X',  '-0.2', expresstype = 'moveexp')
        setDriver('cf_s_kneeB_L', 'location', 2, 'cf_j_leg01_L', 'ROT_X',  '-0.08')

        #knee correction to thicken the knee in a kneeling pose if the rigify armature is being used
        # if bpy.context.scene.kkbp.armature_dropdown == 'B' and bpy.context.scene.kkbp.categorize_dropdown in ['A', 'B', 'C']:
        #     setDriver('cf_s_leg01_R', 'scale', 2, 'cf_j_leg01_R', 'ROT_X',  '1',  expresstype = 'scale')
        #     setDriver('cf_s_leg01_R', 'scale', 0, 'cf_j_leg01_R', 'ROT_X',  '-2', expresstype = 'scale')
        #     setDriver('cf_s_leg01_R', 'location', 2, 'cf_j_leg01_R', 'ROT_X',  '0.05', expresstype='quat')
        #     setDriver('cf_d_thigh03_R', 'location', 2, 'cf_j_leg01_R', 'ROT_X',   '.015')

        #     setDriver('cf_s_leg01_L', 'scale', 2, 'cf_j_leg01_L', 'ROT_X',  '1', expresstype = 'scale')
        #     setDriver('cf_s_leg01_L', 'scale', 0, 'cf_j_leg01_L', 'ROT_X',  '-2', expresstype = 'scale')
        #     setDriver('cf_s_leg01_L', 'location', 2, 'cf_j_leg01_L', 'ROT_X',  '0.05', expresstype='quat')
        #     setDriver('cf_d_thigh03_L', 'location', 2, 'cf_j_leg01_L', 'ROT_X',  '-.015')

        #knee tip corrections go up toward the waist and in toward the body, also rotate a bit
        setDriver('cf_d_kneeF_R', 'location', 1, 'cf_j_leg01_R', 'ROT_X',  '0.02')
        setDriver('cf_d_kneeF_R', 'location', 2, 'cf_j_leg01_R', 'ROT_X',  '-0.04')

        setDriver('cf_d_kneeF_L', 'location', 1, 'cf_j_leg01_L', 'ROT_X',  '0.02')
        setDriver('cf_d_kneeF_L', 'location', 2, 'cf_j_leg01_L', 'ROT_X',  '-0.04')

        #butt corrections go slightly up to the spine and in to the waist 
        setDriver('cf_d_siri_R', 'location', 1, 'cf_j_thigh00_R', 'ROT_X',  '0.02')
        setDriver('cf_d_siri_R', 'location', 2, 'cf_j_thigh00_R',  'ROT_X',  '0.02')

        setDriver('cf_d_siri_L', 'location', 1, 'cf_j_thigh00_L', 'ROT_X',  '0.02')
        setDriver('cf_d_siri_L', 'location', 2, 'cf_j_thigh00_L',  'ROT_X',  '0.02')
        
        #hand corrections go up to the head and in towards the elbow
        setDriver('cf_d_hand_R', 'location', 0, 'cf_j_hand_R', 'ROT_Z',  '-0.4', expresstype = 'moveNeg')
        setDriver('cf_d_hand_R', 'location', 1, 'cf_j_hand_R', 'ROT_Z', '-0.4', expresstype = 'moveNeg')

        setDriver('cf_d_hand_L', 'location', 0, 'cf_j_hand_L', 'ROT_Z', '-0.4', expresstype = 'movePos')
        setDriver('cf_d_hand_L', 'location', 1, 'cf_j_hand_L', 'ROT_Z', '0.4', expresstype = 'movePos')

        #elboback goes out to the chest and into the shoulder
        #elbo goes does the opposite
        setDriver('cf_s_elboback_R', 'location', 0, 'cf_j_forearm01_R', 'ROT_X',  '-0.7')
        setDriver('cf_s_elboback_R', 'location', 2, 'cf_j_forearm01_R', 'ROT_X',  '0.6')
        setDriver('cf_s_elbo_R', 'location', 0, 'cf_j_forearm01_R', 'ROT_X',  '0.025')
        setDriver('cf_s_elbo_R', 'location', 2, 'cf_j_forearm01_R', 'ROT_X',  '0.025')

        setDriver('cf_s_elboback_L', 'location', 0, 'cf_j_forearm01_L', 'ROT_X',  '-0.7')
        setDriver('cf_s_elboback_L', 'location', 2, 'cf_j_forearm01_L', 'ROT_X',  '-0.6')
        setDriver('cf_s_elbo_L', 'location', 0, 'cf_j_forearm01_L', 'ROT_X',  '0.025')
        setDriver('cf_s_elbo_L', 'location', 2, 'cf_j_forearm01_L', 'ROT_X',  '-0.025')

        #shoulder bones have a few corrections as well
        setDriver('cf_d_shoulder02_R', 'location', 1, 'cf_j_arm00_R', 'ROT_Z',  '-0.1', expresstype = 'moveNeg')
        setDriver('cf_d_shoulder02_R', 'location', 0, 'cf_j_arm00_R', 'ROT_Y',  '0.1', expresstype = 'moveABSNeg')
        setDriver('cf_d_shoulder02_R', 'location', 2, 'cf_j_arm00_R', 'ROT_Y',  '-0.1')

        setDriver('cf_d_shoulder02_L', 'location', 1, 'cf_j_arm00_L', 'ROT_Z',  '0.1', expresstype = 'movePos')
        setDriver('cf_d_shoulder02_L', 'location', 0, 'cf_j_arm00_L', 'ROT_Y',  '-0.1', expresstype = 'moveABS')
        setDriver('cf_d_shoulder02_L', 'location', 2, 'cf_j_arm00_L', 'ROT_Y',  '0.1')

        #leg corrections go up to the head and slightly forwards/backwards
        setDriver('cf_s_leg_R', 'location', 1, 'cf_j_thigh00_R', 'ROT_X',  '1', expresstype = 'moveexp')
        setDriver('cf_s_leg_R', 'location', 2, 'cf_j_thigh00_R', 'ROT_X',  '-1.5')

        setDriver('cf_s_leg_L', 'location', 1, 'cf_j_thigh00_L', 'ROT_X',  '1', expresstype = 'moveexp')
        setDriver('cf_s_leg_L', 'location', 2, 'cf_j_thigh00_L', 'ROT_X',  '-1.5')

        #waist correction slightly moves out to chest when lower waist rotates
        setDriver('cf_s_waist02', 'location', 2, 'cf_j_waist02', 'ROT_X',  '0.2', expresstype='moveABS')

    def categorize_bones(self):
        '''Add some bones to bone groups to give them colors'''
        if bpy.context.scene.kkbp.armature_dropdown in ['A','B']:
            c.switch(self.armature, 'pose')
            if bpy.app.version[0] == 3:
                bpy.ops.pose.group_add()
                group_index = len(self.armature.pose.bone_groups)-1
                group = self.armature.pose.bone_groups[group_index]
                group.name = 'IK controllers'
                self.armature.data.bones['cf_pv_hand_L'].select = True
                self.armature.data.bones['cf_pv_hand_R'].select = True
                self.armature.data.bones['MasterFootIK.L'].select = True
                self.armature.data.bones['MasterFootIK.R'].select = True
                bpy.ops.pose.group_assign(type=group_index+1)
                group.color_set = 'THEME01'

                c.switch(self.armature, 'pose')
                bpy.ops.pose.group_add()
                group_index = len(self.armature.pose.bone_groups)-1
                group = self.armature.pose.bone_groups[group_index]
                group.name = 'IK poles'
                self.armature.pose.bone_groups.active_index = 1
                self.armature.data.bones['cf_pv_elbo_R'].select = True
                self.armature.data.bones['cf_pv_elbo_L'].select = True
                self.armature.data.bones['cf_pv_knee_R'].select = True
                self.armature.data.bones['cf_pv_knee_L'].select = True
                bpy.ops.pose.group_assign(type=group_index+1)
                group.color_set = 'THEME09'
            else:
                group_name = 'IK controllers'
                for bone in ['cf_pv_hand_L', 'cf_pv_hand_R', 'MasterFootIK.L', 'MasterFootIK.R']:
                    self.set_armature_layer(bone, group_name)
                    self.armature.data.bones[bone].color.palette = 'THEME01'
                
                group_name = 'IK poles'
                for bone in ['cf_pv_elbo_R', 'cf_pv_elbo_L', 'cf_pv_knee_R', 'cf_pv_knee_L']:
                    self.set_armature_layer(bone, group_name)
                    self.armature.data.bones[bone].color.palette = 'THEME09'

    def rename_bones_for_clarity(self):
        '''rename core bones for easier identification. Also allows Unity to automatically detect each bone in a humanoid armature'''
        if bpy.context.scene.kkbp.armature_dropdown in ['A','B']:
            unity_rename_dict = {
            'cf_n_height':'Center',
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
            'cf_J_hitomi_tx_L':'Left Eye',
            'cf_J_hitomi_tx_R':'Right Eye',

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
            for bone in unity_rename_dict:
                if self.armature.data.bones.get(bone):
                    self.armature.data.bones[bone].name = unity_rename_dict[bone]
            
            #reset the eye vertex groups after renaming the bones
            mod = bpy.data.objects['Body'].modifiers[2]
            mod.vertex_group = 'Left Eye'
            mod = bpy.data.objects['Body'].modifiers[3]
            mod.vertex_group = 'Right Eye'

            #rename the name of the armature modifier
            bpy.data.objects['Body'].modifiers[0].name = 'Armature'

    def apply_bone_widgets(self):
        '''apply custom bone shapes from library file'''
        if bpy.context.scene.kkbp.armature_dropdown in ['A','B']:
            #Import custom bone shapes
            c.import_from_library_file('Collection', ['Bone Widgets'], use_fake_user=False)
        
            #Add custom shapes to the armature        
            self.armature.data.show_bone_custom_shapes = True
            c.switch(self.armature, 'pose')
            
            self.armature.pose.bones["Spine"].custom_shape = bpy.data.objects["WidgetChest"]
            self.armature.pose.bones["Chest"].custom_shape = bpy.data.objects["WidgetChest"]
            self.armature.pose.bones["Upper Chest"].custom_shape = bpy.data.objects["WidgetChest"]

            self.armature.pose.bones["cf_d_bust00"].custom_shape = bpy.data.objects["WidgetBust"]
            self.armature.pose.bones["cf_d_bust00"].use_custom_shape_bone_size = False
            self.armature.pose.bones["cf_j_bust01_L"].custom_shape = bpy.data.objects["WidgetBreastL"]
            self.armature.pose.bones["cf_j_bust01_L"].use_custom_shape_bone_size = False
            self.armature.pose.bones["cf_j_bust01_R"].custom_shape = bpy.data.objects["WidgetBreastR"]
            self.armature.pose.bones["cf_j_bust01_R"].use_custom_shape_bone_size = False

            self.armature.pose.bones["Left shoulder"].custom_shape = bpy.data.objects["WidgetShoulderL"]
            self.armature.pose.bones["Right shoulder"].custom_shape = bpy.data.objects["WidgetShoulderR"]
            self.armature.pose.bones["cf_pv_hand_R"].custom_shape = bpy.data.objects["WidgetHandR"]
            self.armature.pose.bones["cf_pv_hand_L"].custom_shape = bpy.data.objects["WidgetHandL"]

            self.armature.pose.bones["Head"].custom_shape = bpy.data.objects["WidgetHead"]
            self.armature.pose.bones["Eye Controller"].custom_shape = bpy.data.objects["WidgetEye"]
            self.armature.pose.bones["Neck"].custom_shape = bpy.data.objects["WidgetNeck"]

            self.armature.pose.bones["Hips"].custom_shape = bpy.data.objects["WidgetHips"]
            self.armature.pose.bones["Pelvis"].custom_shape = bpy.data.objects["WidgetPelvis"]

            self.armature.pose.bones["MasterFootIK.R"].custom_shape = bpy.data.objects["WidgetFoot"]
            self.armature.pose.bones["MasterFootIK.L"].custom_shape = bpy.data.objects["WidgetFoot"]
            self.armature.pose.bones["ToeRotator.R"].custom_shape = bpy.data.objects["WidgetToe"]
            self.armature.pose.bones["ToeRotator.L"].custom_shape = bpy.data.objects["WidgetToe"]
            self.armature.pose.bones["HeelIK.R"].custom_shape = bpy.data.objects["WidgetHeel"]
            self.armature.pose.bones["HeelIK.L"].custom_shape = bpy.data.objects["WidgetHeel"]

            self.armature.pose.bones["cf_pv_knee_R"].custom_shape = bpy.data.objects["WidgetKnee"]
            self.armature.pose.bones["cf_pv_knee_L"].custom_shape = bpy.data.objects["WidgetKnee"]
            self.armature.pose.bones["cf_pv_elbo_R"].custom_shape = bpy.data.objects["WidgetKnee"]
            self.armature.pose.bones["cf_pv_elbo_L"].custom_shape = bpy.data.objects["WidgetKnee"]
            
            self.armature.pose.bones["Center"].custom_shape = bpy.data.objects["WidgetRoot"]
            
            try:
                bpy.context.space_data.overlay.show_relationship_lines = False
            except:
                #the script was run in the text editor or console, so this won't work
                pass
            
            # apply eye bones, mouth bones, eyebrow bones
            eyebones = [1,2,3,4,5,6,7,8]
            for piece in eyebones:
                left = 'cf_J_Eye0'+str(piece)+'_s_L'
                right = 'cf_J_Eye0'+str(piece)+'_s_R'
                self.armature.pose.bones[left].custom_shape  = bpy.data.objects['WidgetFace']
                self.armature.pose.bones[right].custom_shape = bpy.data.objects['WidgetFace']
            
            restOfFace = [
            'cf_J_Mayu_R', 'cf_J_MayuMid_s_R', 'cf_J_MayuTip_s_R',
            'cf_J_Mayu_L', 'cf_J_MayuMid_s_L', 'cf_J_MayuTip_s_L',
            'cf_J_Mouth_R', 'cf_J_Mouth_L',
            'cf_J_Mouthup', 'cf_J_MouthLow', 'cf_J_MouthMove', 'cf_J_MouthCavity']
            for bone in restOfFace:
                self.armature.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetFace']
            
            evenMoreOfFace = [
            'cf_J_EarUp_L', 'cf_J_EarBase_ry_L', 'cf_J_EarLow_L',
            'cf_J_CheekUp2_L', 'cf_J_Eye_rz_L', 'cf_J_Eye_rz_L', 
            'cf_J_CheekUp_s_L', 'cf_J_CheekLow_s_L', 

            'cf_J_EarUp_R', 'cf_J_EarBase_ry_R', 'cf_J_EarLow_R',
            'cf_J_CheekUp2_R', 'cf_J_Eye_rz_R', 'cf_J_Eye_rz_R', 
            'cf_J_CheekUp_s_R', 'cf_J_CheekLow_s_R',

            'cf_J_ChinLow', 'cf_J_Chin_s', 'cf_J_ChinTip_Base', 
            'cf_J_NoseBase', 'cf_J_NoseBridge_rx', 'cf_J_Nose_tip']
            
            for bone in evenMoreOfFace:
                self.armature.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetSpine']
                
            fingerList = [
            'IndexFinger1_L', 'IndexFinger2_L', 'IndexFinger3_L',
            'MiddleFinger1_L', 'MiddleFinger2_L', 'MiddleFinger3_L',
            'RingFinger1_L', 'RingFinger2_L', 'RingFinger3_L',
            'LittleFinger1_L', 'LittleFinger2_L', 'LittleFinger3_L',
            'Thumb0_L', 'Thumb1_L', 'Thumb2_L',
            
            'IndexFinger1_R', 'IndexFinger2_R', 'IndexFinger3_R',
            'MiddleFinger1_R', 'MiddleFinger2_R', 'MiddleFinger3_R',
            'RingFinger1_R', 'RingFinger2_R', 'RingFinger3_R',
            'LittleFinger1_R', 'LittleFinger2_R', 'LittleFinger3_R',
            'Thumb0_R', 'Thumb1_R', 'Thumb2_R']
            
            for finger in fingerList:
                if 'Thumb' in finger:
                    self.armature.pose.bones[finger].custom_shape  = bpy.data.objects['WidgetFingerThumb']
                else:
                    self.armature.pose.bones[finger].custom_shape  = bpy.data.objects['WidgetFinger']
                
            bp_list = self.get_bone_list('bp_list')
            toe_list = self.get_bone_list('toe_list')
            for bone in bp_list:
                if self.armature.pose.bones.get(bone):
                    self.armature.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetSpine']
                    self.armature.pose.bones[bone].custom_shape_scale_xyz = Vector((1.8, 1.8, 1.8))
            for bone in toe_list:
                if self.armature.pose.bones.get(bone):
                    self.armature.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetSpine']
            
            #Make the body and clothes layers visible
            all_layers = [
            False, False, False, False, False, False, False, False,
            False, False, False, False, False, False, False, False,
            False, False, False, False, False, False, False, False,
            False, False, False, False, False, False, False, False]
            all_layers[0] = True
            all_layers[8] = True
            all_layers[9] = True

            if bpy.app.version[0] == 3:
                bpy.ops.armature.armature_layers(layers=all_layers)
            else:
                for index, show_layer in enumerate(all_layers):
                    if self.armature.data.collections.get(str(index)):
                        self.armature.data.collections.get(str(index)).is_visible = show_layer
                self.armature.data.display_type = 'STICK'

    def hide_widgets(self):
        '''automatically hide bone widgets collection if it's visible'''
        if bpy.context.scene.kkbp.armature_dropdown in ['A','B']:
            for widget_col in ['Bone Widgets']:
                try:
                    bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children[widget_col]
                    bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
                except:
                    try:
                        #maybe the collection is in the Collection collection
                        bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children['Collection'].children[widget_col]
                        bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
                    except:
                        #maybe the collection is already hidden
                        pass

    def only_show_core_armature_bones(self):
        #Make only core, skirt and accessory bones visible
        c.switch(self.armature, 'object')
        core_layers = [
        True,  False, False, False, False, False, False, False, #body
        True,  True,  False, False, False, False, False, False, #clothes
        False, False, False, False, False, False, False, False, #face
        False, False, False, False, False, False, False, False]
        if bpy.app.version[0] == 3:
            bpy.ops.armature.armature_layers(layers=core_layers)
        else:
            for index, show_layer in enumerate(core_layers):
                if self.armature.data.collections.get(str(index)):
                    self.armature.data.collections.get(str(index)).is_visible = show_layer
        self.armature.data.display_type = 'STICK'
        c.switch(self.armature, 'object')

    # %% Supporting functions
    @staticmethod
    def survey(obj):
        '''Function to check for empty vertex groups of an object
        returns a dictionary in the form {vertex_group1: maxweight1, vertex_group2: maxweight2, etc}'''
        maxWeight = {}
        #prefill vertex group list with zeroes
        for i in obj.vertex_groups:
            maxWeight[i.name] = 0
        #preserve the indexes
        keylist = list(maxWeight)
        #then fill in the real value using the indexes
        for v in obj.data.vertices:
            for g in v.groups:
                gn = g.group
                w = obj.vertex_groups[g.group].weight(v.index)
                if (maxWeight.get(keylist[gn]) is None or w>maxWeight[keylist[gn]]):
                    maxWeight[keylist[gn]] = w
        return maxWeight

    @staticmethod
    def survey_vertexes(obj):
        has_vertexes = {}
        for i in obj.vertex_groups:
            has_vertexes[i.name] = False
        #preserve the indexes
        keylist = list(has_vertexes)
        #then fill in the real value using the indexes
        for v in obj.data.vertices:
            for g in v.groups:
                gn = g.group
                w = obj.vertex_groups[g.group].weight(v.index)
                if (has_vertexes.get(keylist[gn]) is None or w>has_vertexes[keylist[gn]]):
                    has_vertexes[keylist[gn]] = True
        return has_vertexes

    def set_armature_layer(self, bone_name, show_layer, hidden = False):
        '''Assigns a bone to a bone collection.'''
        bone = self.armature.data.bones.get(bone_name)
        if bone:
            if bpy.app.version[0] == 3:
                if self.armature.data.bones.get(bone_name):
                    self.armature.data.bones[bone_name].layers = (
                        True, False, False, False, False, False, False, False,
                        False, False, False, False, False, False, False, False, 
                        False, False, False, False, False, False, False, False, 
                        False, False, False, False, False, False, False, False
                    )
                    #have to show the bone on both layer 1 and chosen layer before setting it to just chosen layer
                    self.armature.data.bones[bone_name].layers[show_layer] = True 
                    self.armature.data.bones[bone_name].layers[0] = False
                    self.armature.data.bones[bone_name].hide = hidden
            else:
                original_mode = bpy.context.object.mode
                bpy.ops.object.mode_set(mode = 'OBJECT')
                show_layer = str(show_layer)
                bone.collections.clear()
                if self.armature.data.bones.get(bone_name):
                    if self.armature.data.collections.get(show_layer):
                        self.armature.data.collections[show_layer].assign(self.armature.data.bones.get(bone_name))
                    else:
                        self.armature.data.collections.new(show_layer)
                        self.armature.data.collections[show_layer].assign(self.armature.data.bones.get(bone_name))
                    self.armature.data.bones[bone_name].hide = hidden
                bpy.ops.object.mode_set(mode = original_mode)

    @staticmethod
    def get_bone_list(kind):
        '''returns a list of a certain category of bones'''
        if kind == 'core_list':
            #main bone list
            return [
            'cf_n_height', 'cf_j_hips', 'cf_j_waist01', 'cf_j_waist02',
            'cf_j_spine01', 'cf_j_spine02', 'cf_j_spine03',
            'cf_j_neck', 'cf_j_head',
            'cf_d_bust00', 'cf_j_bust01_L', 'cf_j_bust01_R', 'Eyesx',

            'cf_j_shoulder_L', 'cf_j_shoulder_R', 'cf_j_arm00_L', 'cf_j_arm00_R',
            'cf_j_forearm01_L', 'cf_j_forearm01_R', 'cf_j_hand_R', 'cf_j_hand_L',

            'cf_j_thumb01_L','cf_j_thumb02_L', 'cf_j_thumb03_L',
            'cf_j_ring01_L', 'cf_j_ring02_L', 'cf_j_ring03_L', 
            'cf_j_middle01_L','cf_j_middle02_L', 'cf_j_middle03_L', 
            'cf_j_little01_L','cf_j_little02_L', 'cf_j_little03_L', 
            'cf_j_index01_L','cf_j_index02_L', 'cf_j_index03_L', 

            'cf_j_thumb01_R','cf_j_thumb02_R',  'cf_j_thumb03_R',
            'cf_j_ring01_R','cf_j_ring02_R', 'cf_j_ring03_R', 
            'cf_j_middle01_R','cf_j_middle02_R', 'cf_j_middle03_R', 
            'cf_j_little01_R','cf_j_little02_R', 'cf_j_little03_R', 
            'cf_j_index01_R', 'cf_j_index02_R', 'cf_j_index03_R',

            'cf_j_thigh00_L', 'cf_j_thigh00_R', 'cf_j_leg01_L', 'cf_j_leg01_R',
            'cf_j_foot_L', 'cf_j_foot_R', 'cf_j_toes_L', 'cf_j_toes_R',

            'cf_j_siri_L', 'cf_j_siri_R',

            'cf_pv_knee_L', 'cf_pv_knee_R',
            'cf_pv_elbo_L', 'cf_pv_elbo_R',
            'cf_pv_hand_L', 'cf_pv_hand_R',
            'cf_pv_foot_L', 'cf_pv_foot_R'
            ]
            
        elif kind == 'non_ik':
            #IK bone list
            return [
            'cf_j_forearm01_L', 'cf_j_forearm01_R',
            'cf_j_arm00_L', 'cf_j_arm00_R',
            'cf_j_thigh00_L', 'cf_j_thigh00_R',
            'cf_j_leg01_L', 'cf_j_leg01_R',
            'cf_j_leg03_L', 'cf_j_leg03_R',
            'cf_j_foot_L', 'cf_j_foot_R',
            'cf_j_hand_L', 'cf_j_hand_R',
            'cf_j_bust03_L', 'cf_j_bnip02root_L', 'cf_j_bnip02_L',
            'cf_j_bust03_R', 'cf_j_bnip02root_R', 'cf_j_bnip02_R']
            
        elif kind == 'eye_list':
            return [
            'cf_J_Eye01_s_L', 'cf_J_Eye01_s_R',
            'cf_J_Eye02_s_L', 'cf_J_Eye02_s_R',
            'cf_J_Eye03_s_L', 'cf_J_Eye03_s_R',
            'cf_J_Eye04_s_L', 'cf_J_Eye04_s_R',
            'cf_J_Eye05_s_L', 'cf_J_Eye05_s_R',
            'cf_J_Eye06_s_L', 'cf_J_Eye06_s_R',
            'cf_J_Eye07_s_L', 'cf_J_Eye07_s_R',
            'cf_J_Eye08_s_L', 'cf_J_Eye08_s_R',
            
            'cf_J_Mayu_R', 'cf_J_MayuMid_s_R', 'cf_J_MayuTip_s_R',
            'cf_J_Mayu_L', 'cf_J_MayuMid_s_L', 'cf_J_MayuTip_s_L']

        elif kind == 'mouth_list':
            return [
            'cf_J_Mouth_R', 'cf_J_Mouth_L',
            'cf_J_Mouthup', 'cf_J_MouthLow', 'cf_J_MouthMove', 'cf_J_MouthCavity',
            
            'cf_J_EarUp_L', 'cf_J_EarBase_ry_L', 'cf_J_EarLow_L',
            'cf_J_CheekUp2_L', 'cf_J_Eye_rz_L', 'cf_J_Eye_rz_L', 
            'cf_J_CheekUp_s_L', 'cf_J_CheekLow_s_L', 

            'cf_J_EarUp_R', 'cf_J_EarBase_ry_R', 'cf_J_EarLow_R',
            'cf_J_CheekUp2_R', 'cf_J_Eye_rz_R', 'cf_J_Eye_rz_R', 
            'cf_J_CheekUp_s_R', 'cf_J_CheekLow_s_R',

            'cf_J_ChinLow', 'cf_J_Chin_s', 'cf_J_ChinTip_Base', 
            'cf_J_NoseBase', 'cf_J_NoseBridge_rx', 'cf_J_Nose_tip']
            
        elif kind == 'toe_list':
            #bones that appear on the Better Penetration armature
            return [
            'cf_j_toes0_L', 'cf_j_toes1_L', 'cf_j_toes10_L',
            'cf_j_toes2_L', 'cf_j_toes20_L',
            'cf_j_toes3_L', 'cf_j_toes30_L', 'cf_j_toes4_L',
            
            'cf_j_toes0_R', 'cf_j_toes1_R', 'cf_j_toes10_R',
            'cf_j_toes2_R', 'cf_j_toes20_R',
            'cf_j_toes3_R', 'cf_j_toes30_R', 'cf_j_toes4_R']
            
        elif kind == 'bp_list':
            #more bones that appear on the Better Penetration armature
            return [
            'cf_j_kokan', 'cf_j_ana', 'cf_J_Vagina_root', 'cf_J_Vagina_B', 'cf_J_Vagina_F',
            'cf_J_Vagina_L.001', 'cf_J_Vagina_L.002', 'cf_J_Vagina_L.003', 'cf_J_Vagina_L.004', 'cf_J_Vagina_L.005', 
            'cf_J_Vagina_R.001', 'cf_J_Vagina_R.002', 'cf_J_Vagina_R.003', 'cf_J_Vagina_R.004', 'cf_J_Vagina_R.005']

        elif kind == 'skirt_list':
            return [
            'cf_j_sk_00_00', 'cf_j_sk_00_01', 'cf_j_sk_00_02', 'cf_j_sk_00_03', 'cf_j_sk_00_04',
            'cf_j_sk_01_00', 'cf_j_sk_01_01', 'cf_j_sk_01_02', 'cf_j_sk_01_03', 'cf_j_sk_01_04',
            'cf_j_sk_02_00', 'cf_j_sk_02_01', 'cf_j_sk_02_02', 'cf_j_sk_02_03', 'cf_j_sk_02_04',
            'cf_j_sk_03_00', 'cf_j_sk_03_01', 'cf_j_sk_03_02', 'cf_j_sk_03_03', 'cf_j_sk_03_04',
            'cf_j_sk_04_00', 'cf_j_sk_04_01', 'cf_j_sk_04_02', 'cf_j_sk_04_03', 'cf_j_sk_04_04',
            'cf_j_sk_05_00', 'cf_j_sk_05_01', 'cf_j_sk_05_02', 'cf_j_sk_05_03', 'cf_j_sk_05_04',
            'cf_j_sk_06_00', 'cf_j_sk_06_01', 'cf_j_sk_06_02', 'cf_j_sk_06_03', 'cf_j_sk_06_04',
            'cf_j_sk_07_00', 'cf_j_sk_07_01', 'cf_j_sk_07_02', 'cf_j_sk_07_03', 'cf_j_sk_07_04']
        
        elif kind == 'tongue_list':
            return [
                'cf_j_tang_01', 'cf_j_tang_02', 'cf_j_tang_03', 'cf_j_tang_04', 'cf_j_tang_05', 
                'cf_j_tang_L_03', 'cf_j_tang_L_04', 'cf_j_tang_L_05', 
                'cf_j_tang_R_03', 'cf_j_tang_R_04', 'cf_j_tang_R_05', 
                ]

    def new_bone(self, new_bone_name):
        '''Creates a new bone on the armature with the specified name and returns the blender bone'''
        if bpy.app.version[0] == 3:
            bpy.ops.armature.bone_primitive_add()
            bone = self.armature.data.edit_bones['Bone']
            bone.name = new_bone_name
        else:
            bone = self.armature.data.edit_bones.new(new_bone_name)
        return bone

if __name__ == "__main__":
    bpy.utils.register_class(modify_armature)

    # test call
    print((bpy.ops.kkbp.modifyarmature('INVOKE_DEFAULT')))
