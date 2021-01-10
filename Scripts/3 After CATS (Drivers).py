'''
AFTER CATS (DRIVERS) SCRIPT
- Adds IKs to the arms and legs using the "pv" bones
- Moves the Knee and Elbow IKs a little closer to the body
- Adds drivers for twist / joint correction bones for the arms, hands, legs and butt
- Adds an "Eye Controller" bone and UV warp modifiers on the Body object to make the eyes work

Usage:
- Make sure the Fix Model button has already been used in CATS
- Select the armature
- Run the script
'''

import bpy

############## Setup all IKs

#gives the leg an IK modifier, repositions the foot IK controller
def legIK(legbone, IKtarget, IKpole, IKpoleangle, footbone, kneebone, toebone):
    bone = bpy.data.objects['Armature'].pose.bones[legbone]

    #Make IK
    bone.constraints.new("IK")

    #Set target and subtarget
    bone.constraints["IK"].target = bpy.data.objects['Armature']
    bone.constraints["IK"].subtarget = bpy.data.objects['Armature'].data.bones[IKtarget].name

    #Set pole and subpole and pole angle
    bone.constraints["IK"].pole_target = bpy.data.objects['Armature']
    bone.constraints["IK"].pole_subtarget = bpy.data.objects['Armature'].data.bones[IKpole].name
    bone.constraints["IK"].pole_angle = IKpoleangle

    #Set chain length
    bone.constraints["IK"].chain_count=2

    #Move bone backwards and flip bone
    bpy.ops.object.mode_set(mode='EDIT')

    bone = bpy.data.objects['Armature'].data.edit_bones[footbone]

    bone.head.y = bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.y
    bone.tail.y = bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.y
    bone.tail.z = bpy.data.objects['Armature'].data.edit_bones[toebone].tail.z

    #unparent the bone
    bone.parent = None

#Run for each side
legIK('Right knee', 'Cf_Pv_Foot_R', 'Cf_Pv_Knee_R', -1.571, 'Cf_Pv_Foot_R', 'Right knee', 'ToeTipIK_R')
legIK('Left knee',  'Cf_Pv_Foot_L', 'Cf_Pv_Knee_L', -1.571, 'Cf_Pv_Foot_L', 'Left knee', 'ToeTipIK_L')

#adds an IK for the toe bone, moves the knee IKs a little closer to the body
def footIK(footbone, IKtarget, parentTarget, kneebone):

    bone = bpy.data.objects['Armature'].pose.bones[footbone]

    #Make IK
    bone.constraints.new("IK")

    #Set target and subtarget
    bone.constraints["IK"].target=bpy.data.objects['Armature']
    bone.constraints["IK"].subtarget=bpy.data.objects['Armature'].data.bones[IKtarget].name

    #Set chain length
    bone.constraints["IK"].chain_count=1

    #parent the toe tip bone to the foot IK bone
    bpy.data.objects['Armature'].data.edit_bones[IKtarget].parent = bpy.data.objects['Armature'].data.edit_bones[parentTarget]

    # move knee IKs closer to body
    bpy.data.objects['Armature'].data.edit_bones[kneebone].head.y *= (2/3)
    bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.y *= (2/3)

#Run for each side
footIK('Right ankle', 'ToeTipIK_R', 'Cf_Pv_Foot_R', 'Cf_Pv_Knee_R')
footIK('Left ankle',  'ToeTipIK_L', 'Cf_Pv_Foot_L', 'Cf_Pv_Knee_L')

#add an IK to the arm, makes the wrist bone copy the hand IK's rotation, moves elbow IKs a little closer to the body
def armhandIK(elbowbone, handcontroller, elbowcontroller, IKangle, wristbone):
    #Set IK bone
    bone = bpy.data.objects['Armature'].pose.bones[elbowbone]

    #Add IK
    bone.constraints.new("IK")

    #Set target and subtarget
    bone.constraints["IK"].target = bpy.data.objects['Armature']
    bone.constraints["IK"].subtarget = bpy.data.objects['Armature'].data.bones[handcontroller].name

    #Set pole and subpole and pole angle
    bone.constraints["IK"].pole_target = bpy.data.objects['Armature']
    bone.constraints["IK"].pole_subtarget = bpy.data.objects['Armature'].data.bones[elbowcontroller].name
    bone.constraints["IK"].pole_angle= IKangle

    #Set chain length
    bone.constraints["IK"].chain_count=2

    #unparent the bone
    bpy.ops.object.mode_set(mode='EDIT')
    bone = bpy.data.objects['Armature'].data.edit_bones[handcontroller]
    bone.parent = None
    bpy.ops.object.mode_set(mode='POSE')

    # Set hand rotation then hide it
    bone = bpy.data.objects['Armature'].pose.bones[wristbone]

    bone.constraints.new("COPY_ROTATION")
    bone.constraints['Copy Rotation'].target=bpy.data.objects['Armature']
    bone.constraints['Copy Rotation'].subtarget=bpy.data.objects['Armature'].data.bones[handcontroller].name

    bpy.ops.object.mode_set(mode='POSE')
    bpy.data.objects['Armature'].data.bones[wristbone].hide = True
    bpy.ops.object.mode_set(mode='EDIT')

    # move elbow IKs closer to body
    bpy.data.objects['Armature'].data.edit_bones[elbowcontroller].head.y *= (2/3)
    bpy.data.objects['Armature'].data.edit_bones[elbowcontroller].tail.y *= (2/3)

#Run for each side
armhandIK('Right elbow', 'Cf_Pv_Hand_R', 'Cf_Pv_Elbo_R', 0, 'Right wrist')
armhandIK('Left elbow',  'Cf_Pv_Hand_L', 'Cf_Pv_Elbo_L', 180, 'Left wrist')

############ Setup joint correction drivers

#generic function for creating a driver
def setDriver (bone, drivertype, drivertypeselect, drivertarget, drivertt, driverts, driverrm, driverexpr):
    bpy.ops.object.mode_set(mode='POSE')

    #select bone to add driver to
    bone=bpy.data.objects['Armature'].pose.bones[bone]

    #add driver to first component
    #drivertype can be location/rotation and drivertypeselect (0 is x component, y is 1, z is 2)
    driver = bone.driver_add(drivertype, drivertypeselect)

    #add driver variable
    vari = driver.driver.variables.new()
    vari.name = 'var'
    vari.type = 'TRANSFORMS'

    #set the target and subtarget
    target = vari.targets[0]
    target.id = bpy.data.objects['Armature']
    target.bone_target = bpy.data.objects['Armature'].pose.bones[drivertarget].name

    #set the transforms for the target. this can be rotation or location 
    target.transform_type = drivertt

    #set the transform space. can be world space too
    target.transform_space = driverts

    target.rotation_mode = driverrm

    #driver expression
    driver.driver.expression = vari.name + driverexpr

#Set drivers for KneeB joint correction bones
setDriver('KneeB_R_Twist', 'location', 1, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '*-0.8')
setDriver('KneeB_R_Twist', 'location', 2, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '*-0.4')

setDriver('KneeB_L_Twist', 'location', 1, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '*-0.8')
setDriver('KneeB_L_Twist', 'location', 2, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '*-0.4')

#Set drivers for Elboback and Forearm joint correction  bones
setDriver('Elboback_R_Twist', 'location', 0, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '*-0.4')
setDriver('Elboback_R_Twist', 'location', 2, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '*0.4')
setDriver('Forearm01_R_Twist', 'location', 0, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '*-0.05')

setDriver('Elboback_L_Twist', 'location', 0, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '*-0.4')
setDriver('Elboback_L_Twist', 'location', 2, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '*-0.4')
setDriver('Forearm01_L_Twist', 'location', 0, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '*-0.05')

#Set drivers for wrist joint correction bones
setDriver('Cf_D_Wrist_R_Twist', 'rotation_quaternion', 1, 'Cf_Pv_Hand_R', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '*0.3')
setDriver('Wrist_R_Twist', 'rotation_quaternion', 2, 'Cf_Pv_Hand_R', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '*-0.2')

setDriver('Cf_D_Wrist_L_Twist', 'rotation_quaternion', 1, 'Cf_Pv_Hand_L', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '*0.3')
setDriver('Wrist_L_Twist', 'rotation_quaternion', 2, 'Cf_Pv_Hand_L', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '*0.2')

#Set drivers for butt joint correction bones
setDriver('Cf_D_Siri_R', 'rotation_quaternion', 3, 'Right leg', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '*-0.25')
setDriver('Cf_D_Siri_R', 'rotation_quaternion', 1, 'Right leg', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '*0.25')

setDriver('Cf_D_Siri_L', 'rotation_quaternion', 3, 'Left leg', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '*-0.25')
setDriver('Cf_D_Siri_L', 'rotation_quaternion', 1, 'Left leg', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '*0.25')

#Hips have a different driver expression
def setDriverHip(hipbone, drivertarget):
    ######### Hip twist drivers
    bone=bpy.data.objects['Armature'].pose.bones[hipbone]

    driver = bone.driver_add('location', 1)
    vari = driver.driver.variables.new()
    vari.name = 'var'
    vari.type = 'TRANSFORMS'
    target = vari.targets[0]
    target.id = bpy.data.objects['Armature']
    target.bone_target = bpy.data.objects['Armature'].pose.bones[drivertarget].name
    target.transform_type = 'ROT_X'
    target.transform_space = 'LOCAL_SPACE'
    driver.driver.expression = 'abs(' + vari.name + '*-.3)'

    # add driver for z movement

    driver = bone.driver_add('location', 2)
    vari = driver.driver.variables.new()
    vari.name = 'var'
    vari.type = 'TRANSFORMS'
    target = vari.targets[0]
    target.id = bpy.data.objects['Armature']
    target.bone_target = bpy.data.objects['Armature'].pose.bones[drivertarget].name
    target.transform_type = 'ROT_X'
    target.transform_space = 'LOCAL_SPACE'
    driver.driver.expression = 'abs(' + vari.name + '*-.3)'

setDriverHip('Leg_R_Twist', 'Right leg')
setDriverHip('Leg_L_Twist', 'Left leg')

# Tilt the bust bone and make it smaller
bpy.ops.object.mode_set(mode='EDIT')
bone = bpy.data.objects['Armature'].data.edit_bones['Cf_D_Bust00']
bone.tail.y = bpy.data.objects['Armature'].data.edit_bones['AH1_R'].head.y * 2
bone.tail.z = bpy.data.objects['Armature'].data.edit_bones['AH1_R'].head.z
bpy.ops.object.mode_set(mode='POSE')

##################### Make an eye controller

#roll the eye bone, create a copy and name it eye controller
bpy.ops.object.mode_set(mode='EDIT')

armatureData = bpy.data.objects['Armature'].data
armatureData.edit_bones['Eyesx'].roll = -1.571

copy = armatureData.edit_bones.new('Eye Controller')

copy.head = armatureData.edit_bones['Eyesx'].head/2
copy.tail = armatureData.edit_bones['Eyesx'].tail/2
copy.matrix = armatureData.edit_bones['Eyesx'].matrix
copy.parent = armatureData.edit_bones['Head']
armatureData.edit_bones['Eye Controller'].roll = -1.571

bpy.ops.object.mode_set(mode='POSE')

#Lock y location at zero
bpy.data.objects['Armature'].pose.bones['Eye Controller'].lock_location[1] = True

#Hide the original Eyesx bone
bpy.data.objects['Armature'].data.bones['Eyesx'].hide = True

bpy.ops.object.mode_set(mode='OBJECT')

#Create a UV warp modifier for the eyes. Controlled by the Eye controller bone
def eyeUV(modifiername, eyevertexgroup):
    mod = bpy.data.objects['Body'].modifiers.new(modifiername, 'UV_WARP')
    mod.axis_u = 'Z'
    mod.axis_v = 'X'
    mod.object_from = bpy.data.objects['Armature']
    mod.bone_from = bpy.data.objects['Armature'].data.bones['Eyesx'].name
    mod.object_to = bpy.data.objects['Armature']
    mod.bone_to = bpy.data.objects['Armature'].data.bones['Eye Controller'].name
    mod.vertex_group = eyevertexgroup
    mod.uv_layer = 'UVMap'
    mod.show_expanded = False

eyeUV("Left Eye UV warp",  'Eyex_L')
eyeUV("Right Eye UV warp", 'Eyex_R')

############### Empty group check
#checks if the Eyex_L vertex group is empty. If it is, assume the Eyex_R vertex group is also empty,
#then find the vertices using the eye material and assign both eyes to Eyex_L

body = bpy.data.objects['Body']

#Deselect all objects
bpy.ops.object.select_all(action='DESELECT')
#Select the Body object
body.select_set(True)
#and make it active
bpy.context.view_layer.objects.active = body

#make the Eyex_L vertex group active
body.vertex_groups.active_index = body.vertex_groups['Eyex_L'].index

#go into edit mode and select the vertices in the Eyex_L vertex group
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.vertex_group_select()

#refresh the selection (this apparently needs to be done for some reason)
bpy.ops.object.mode_set(mode = 'OBJECT')
bpy.ops.object.mode_set(mode = 'EDIT')

#get a list of the selected vertices
vgVerts = [v for v in body.data.vertices if v.select]

#If the list is empty...
if not vgVerts:
    #select the eye materials
    bpy.context.object.active_material_index = body.data.materials.find('cf_m_hitomi_00 (Instance)')
    bpy.ops.object.material_slot_select()
    bpy.context.object.active_material_index = body.data.materials.find('cf_m_hitomi_00 (Instance).001')
    bpy.ops.object.material_slot_select()
    #then assign them to the Eyex_L group
    bpy.ops.object.vertex_group_assign()

#Reselect the armature
bpy.ops.object.mode_set(mode='OBJECT')
armature = bpy.data.objects['Armature']
bpy.ops.object.select_all(action='DESELECT')
armature.select_set(True)
bpy.context.view_layer.objects.active = armature
