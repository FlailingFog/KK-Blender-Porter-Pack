'''
AFTER CATS (DRIVERS) SCRIPT
- Adds IKs to the arms and legs
- Moves the Knee and Elbow IKs closer to the body
- Adds drivers for twist / joint correction bones for the arms, hands, legs and butt
- Adds an "Eye Controller" bone and UV warp modifiers on the Body object to make the eyes work
'''

import bpy

##################
#Add IK bone constraints
##################

#################
#Right side
#################

################## Right leg IK

bone = bpy.data.objects['Armature'].pose.bones['Right knee']

#Make IK
bone.constraints.new("IK")

#Set target and subtarget
bone.constraints["IK"].target=bpy.data.objects['Armature']
bone.constraints["IK"].subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Foot_R'].name

#Set pole and subpole and pole angle
bone.constraints["IK"].pole_target=bpy.data.objects['Armature']
bone.constraints["IK"].pole_subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Knee_R'].name
bone.constraints["IK"].pole_angle=-1.571

#Set chain length
bone.constraints["IK"].chain_count=2

#Move bone backwards and flip bone
bpy.ops.object.mode_set(mode='EDIT')

bone = bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Foot_R']

bone.head.y = bpy.data.objects['Armature'].data.edit_bones['Right knee'].tail.y
bone.tail.y = bpy.data.objects['Armature'].data.edit_bones['Right knee'].tail.y
bone.tail.z=bpy.data.objects['Armature'].data.edit_bones['ToeTipIK_R'].tail.z

#unparent the bone
bone.parent = None

########################## Right foot IK
bone = bpy.data.objects['Armature'].pose.bones['Right ankle']

#Make IK
bone.constraints.new("IK")

#Set target and subtarget
bone.constraints["IK"].target=bpy.data.objects['Armature']
bone.constraints["IK"].subtarget=bpy.data.objects['Armature'].data.bones['ToeTipIK_R'].name


#Set chain length
bone.constraints["IK"].chain_count=1

#parent the toe tip bone to the foot IK bone
bpy.data.objects['Armature'].data.edit_bones['ToeTipIK_R'].parent = bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Foot_R']

######################## move knee IKs closer to body
bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Knee_R'].head.y /= 2
bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Knee_R'].tail.y /= 2

######################### Right arm IK
#Set IK bone
bone = bpy.data.objects['Armature'].pose.bones['Right elbow']

#Add IK
bone.constraints.new("IK")

#Set target and subtarget
bone.constraints["IK"].target=bpy.data.objects['Armature']
bone.constraints["IK"].subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Hand_R'].name

#Set pole and subpole and pole angle
bone.constraints["IK"].pole_target=bpy.data.objects['Armature']
bone.constraints["IK"].pole_subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Elbo_R'].name
bone.constraints["IK"].pole_angle=-0

#Set chain length
bone.constraints["IK"].chain_count=2

#unparent the bone
bpy.ops.object.mode_set(mode='EDIT')
bone = bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Hand_R']
bone.parent = None
bpy.ops.object.mode_set(mode='POSE')


####################### Set hand rotation then hide it
bone = bpy.data.objects['Armature'].pose.bones['Right wrist']

bone.constraints.new("COPY_ROTATION")
bone.constraints['Copy Rotation'].target=bpy.data.objects['Armature']
bone.constraints['Copy Rotation'].subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Hand_R'].name

bpy.ops.object.mode_set(mode='POSE')
bpy.data.objects['Armature'].data.bones['Right wrist'].hide = True
bpy.ops.object.mode_set(mode='EDIT')

######################## move elbow IKs closer to body

bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Elbo_R'].head.y /= 2
bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Elbo_R'].tail.y /= 2

#######################
#Left side
#######################

################## left leg IK

bone = bpy.data.objects['Armature'].pose.bones['Left knee']

#Make IK
bone.constraints.new("IK")

#Set target and subtarget
bone.constraints["IK"].target=bpy.data.objects['Armature']
bone.constraints["IK"].subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Foot_L'].name

#Set pole and subpole and pole angle
bone.constraints["IK"].pole_target=bpy.data.objects['Armature']
bone.constraints["IK"].pole_subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Knee_L'].name
bone.constraints["IK"].pole_angle=-1.571

#Set chain length
bone.constraints["IK"].chain_count=2

#Move bone backwards and flip bone
bpy.ops.object.mode_set(mode='EDIT')

bone = bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Foot_L']

bone.head.y = bpy.data.objects['Armature'].data.edit_bones['Left knee'].tail.y
bone.tail.y = bpy.data.objects['Armature'].data.edit_bones['Left knee'].tail.y
bone.tail.z=bpy.data.objects['Armature'].data.edit_bones['ToeTipIK_L'].tail.z

#unparent the bone
bone.parent = None

########################## left foot IK
bone = bpy.data.objects['Armature'].pose.bones['Left ankle']

#Make IK
bone.constraints.new("IK")

#Set target and subtarget
bone.constraints["IK"].target=bpy.data.objects['Armature']
bone.constraints["IK"].subtarget=bpy.data.objects['Armature'].data.bones['ToeTipIK_L'].name


#Set chain length
bone.constraints["IK"].chain_count=1

#parent the toe tip bone to the foot IK bone
bpy.data.objects['Armature'].data.edit_bones['ToeTipIK_L'].parent = bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Foot_L']

######################## move knee IKs closer to body
bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Knee_L'].head.y /= 2
bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Knee_L'].tail.y /= 2

######################### left arm IK
#Set IK bone
bone = bpy.data.objects['Armature'].pose.bones['Left elbow']

#Add IK
bone.constraints.new("IK")

#Set target and subtarget
bone.constraints["IK"].target=bpy.data.objects['Armature']
bone.constraints["IK"].subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Hand_L'].name

#Set pole and subpole and pole angle
bone.constraints["IK"].pole_target=bpy.data.objects['Armature']
bone.constraints["IK"].pole_subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Elbo_L'].name
bone.constraints["IK"].pole_angle=180

#Set chain length
bone.constraints["IK"].chain_count=2

#unparent the bone
bpy.ops.object.mode_set(mode='EDIT')
bone = bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Hand_L']
bone.parent = None
bpy.ops.object.mode_set(mode='POSE')

####################### Set hand rotation then hide it
bone = bpy.data.objects['Armature'].pose.bones['Left wrist']

bone.constraints.new("COPY_ROTATION")
bone.constraints['Copy Rotation'].target=bpy.data.objects['Armature']
bone.constraints['Copy Rotation'].subtarget=bpy.data.objects['Armature'].data.bones['Cf_Pv_Hand_L'].name

bpy.ops.object.mode_set(mode='POSE')
bpy.data.objects['Armature'].data.bones['Left wrist'].hide = True
bpy.ops.object.mode_set(mode='EDIT')

######################## move elbow IKs closer to body

bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Elbo_L'].head.y /= 2
bpy.data.objects['Armature'].data.edit_bones['Cf_Pv_Elbo_L'].tail.y /= 2

######################
#Add right twist bone drivers
#######################

bpy.ops.object.mode_set(mode='POSE')

############ Knee twist drivers

#Add driver for y component
bone=bpy.data.objects['Armature'].pose.bones['KneeB_R_Twist']

#add driver for the y location (0 is z, y is 1, z is 2)
driver = bone.driver_add('location', 1)
#add driver variable
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
#set the target and subtarget
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Right knee'].name
#set the transforms for the target. this can be rotation or location 
target.transform_type = 'ROT_X'
#can be world space too
target.transform_space = 'LOCAL_SPACE'
#driver expression
driver.driver.expression = vari.name + '*-0.8'

# add driver for z component

driver = bone.driver_add('location', 2)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Right knee'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*-0.4'



################### Arm twist drivers

bone=bpy.data.objects['Armature'].pose.bones['Elboback_R_Twist']

driver = bone.driver_add('location', 0)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Right elbow'].name
target.transform_type = 'ROT_Z'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*-0.4'

# add driver for z component

driver = bone.driver_add('location', 2)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Right elbow'].name
target.transform_type = 'ROT_Z'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*0.4'

# and for the forearm bone
bone=bpy.data.objects['Armature'].pose.bones['Forearm01_R_Twist']

driver = bone.driver_add('location', 0)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Right elbow'].name
target.transform_type = 'ROT_Z'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*-0.05'

#################### Hand twist drivers

bone=bpy.data.objects['Armature'].pose.bones['Cf_D_Wrist_R_Twist']

driver = bone.driver_add('rotation_quaternion', 1)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Cf_Pv_Hand_R'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
target.rotation_mode = 'QUATERNION'
driver.driver.expression = vari.name + '*0.3'

# for the other twist bone too
bone=bpy.data.objects['Armature'].pose.bones['Wrist_R_Twist']

driver = bone.driver_add('rotation_quaternion', 2)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Cf_Pv_Hand_R'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
target.rotation_mode = 'QUATERNION'
driver.driver.expression = vari.name + '*-0.2'

######### Hip twist drivers
bone=bpy.data.objects['Armature'].pose.bones['Leg_R_Twist']

driver = bone.driver_add('location', 1)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Right leg'].name
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
target.bone_target = bpy.data.objects['Armature'].pose.bones['Right leg'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = 'abs(' + vari.name + '*-.3)'

################### butt twist drivers

bone=bpy.data.objects['Armature'].pose.bones['Cf_D_Siri_R']

driver = bone.driver_add('rotation_quaternion', 3)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Right leg'].name
target.transform_type = 'ROT_Z'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*-.25'

driver = bone.driver_add('rotation_quaternion', 1)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Right leg'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*.25'


######################
#Add left twist bone drivers
#######################

bpy.ops.object.mode_set(mode='POSE')

############ Knee twist drivers

#Add driver for y component
bone=bpy.data.objects['Armature'].pose.bones['KneeB_L_Twist']

#add driver for the y location (0 is z, y is 1, z is 2)
driver = bone.driver_add('location', 1)
#add driver variable
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
#set the target and subtarget
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Left knee'].name
#set the transforms for the target. this can be rotation or location 
target.transform_type = 'ROT_X'
#can be world space too
target.transform_space = 'LOCAL_SPACE'
#driver expression
driver.driver.expression = vari.name + '*-0.8'

# add driver for z component

driver = bone.driver_add('location', 2)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Left knee'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*-0.4'



################### Arm twist drivers

bone=bpy.data.objects['Armature'].pose.bones['Elboback_L_Twist']

driver = bone.driver_add('location', 0)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Left elbow'].name
target.transform_type = 'ROT_Z'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*-0.4'

# add driver for z component

driver = bone.driver_add('location', 2)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Left elbow'].name
target.transform_type = 'ROT_Z'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*-0.4'

# and for the forearm bone
bone=bpy.data.objects['Armature'].pose.bones['Forearm01_L_Twist']

driver = bone.driver_add('location', 0)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Left elbow'].name
target.transform_type = 'ROT_Z'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*-0.05'

#################### Hand twist drivers

bone=bpy.data.objects['Armature'].pose.bones['Cf_D_Wrist_L_Twist']

driver = bone.driver_add('rotation_quaternion', 1)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Cf_Pv_Hand_L'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
target.rotation_mode = 'QUATERNION'
driver.driver.expression = vari.name + '*0.3'

# for the other twist bone too
bone=bpy.data.objects['Armature'].pose.bones['Wrist_L_Twist']

driver = bone.driver_add('rotation_quaternion', 2)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Cf_Pv_Hand_L'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
target.rotation_mode = 'QUATERNION'
driver.driver.expression = vari.name + '*0.2'

######### Hip twist drivers
bone=bpy.data.objects['Armature'].pose.bones['Leg_L_Twist']

driver = bone.driver_add('location', 1)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Left leg'].name
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
target.bone_target = bpy.data.objects['Armature'].pose.bones['Left leg'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = 'abs(' + vari.name + '*-.3)'

################### butt twist drivers

bone=bpy.data.objects['Armature'].pose.bones['Cf_D_Siri_L']

driver = bone.driver_add('rotation_quaternion', 3)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Left leg'].name
target.transform_type = 'ROT_Z'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*-.25'

driver = bone.driver_add('rotation_quaternion', 1)
vari = driver.driver.variables.new()
vari.name = 'var'
vari.type = 'TRANSFORMS'
target = vari.targets[0]
target.id = bpy.data.objects['Armature']
target.bone_target = bpy.data.objects['Armature'].pose.bones['Left leg'].name
target.transform_type = 'ROT_X'
target.transform_space = 'LOCAL_SPACE'
driver.driver.expression = vari.name + '*.25'

###################### Tilt the bust bone and make it smaller
bpy.ops.object.mode_set(mode='EDIT')

bone = bpy.data.objects['Armature'].data.edit_bones['Cf_D_Bust00']
bone.tail.y = bpy.data.objects['Armature'].data.edit_bones['AH1_R'].head.y * 2
bone.tail.z = bpy.data.objects['Armature'].data.edit_bones['AH1_R'].head.z

bpy.ops.object.mode_set(mode='POSE')



##################### Make an eye controller

#roll the eye bone, reate a copy and name it eye controller
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

mod = bpy.data.objects['Body'].modifiers.new("Left Eye warp", 'UV_WARP')
mod.axis_u = 'Z'
mod.axis_v = 'X'
mod.object_from = bpy.data.objects['Armature']
mod.bone_from = bpy.data.objects['Armature'].data.bones['Eyesx'].name
mod.object_to = bpy.data.objects['Armature']
mod.bone_to = bpy.data.objects['Armature'].data.bones['Eye Controller'].name
mod.vertex_group = 'Eyex_L'
mod.uv_layer = 'UVMap'
mod.show_expanded = False

mod = bpy.data.objects['Body'].modifiers.new("Right Eye warp", 'UV_WARP')
mod.axis_u = 'Z'
mod.axis_v = 'X'
mod.object_from = bpy.data.objects['Armature']
mod.bone_from = bpy.data.objects['Armature'].data.bones['Eyesx'].name
mod.object_to = bpy.data.objects['Armature']
mod.bone_to = bpy.data.objects['Armature'].data.bones['Eye Controller'].name
mod.vertex_group = 'Eyex_R'
mod.uv_layer = 'UVMap'
mod.show_expanded = False

