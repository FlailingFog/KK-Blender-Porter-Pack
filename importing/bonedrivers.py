# most of the joint driver corrections were taken from a blend file by
# johnbbob_la_petite on the koikatsu discord

'''
BONE DRIVERS SCRIPT
- Adds IKs to the arms and legs using the "Pv" bones
- Moves the Knee and Elbow IKs a little closer to the body
- Adds drivers for twist / joint correction bones for the arms, hands, legs, waist and butt
- Adds an "Eye Controller" bone to the top of the head and UV warp modifiers on the Body object to give eye controls
- Scales and repositions some bones
Usage:
- Run the script
'''

import bpy, math
from .cleanarmature import set_armature_layer

#Makes a new bone on the armature
def newbone(newbonepls):
    armature = bpy.data.objects['Armature']
    bpy.ops.armature.bone_primitive_add()
    bo = armature.data.edit_bones['Bone']
    bo.name = newbonepls
    return bo

#reparents some bones on the armature
def reparent_bones():

    #first remove all constraints from all bones
    for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        for bone in armature.pose.bones:
            bonesWithConstraints = [constraint for constraint in bone.constraints if constraint.type == 'IK' or constraint.type == 'COPY_ROTATION']
            for constraint in bonesWithConstraints:
                bone.constraints.remove(constraint)

    #and remove all drivers from all armature bones
    for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        #animation_data is nonetype if no drivers have been created yet
        if armature.animation_data != None:
            drivers_data = armature.animation_data.drivers
            for driver in drivers_data:  
                armature.driver_remove(driver.data_path, -1)

    #Select the armature and make it active
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    armature = bpy.data.objects['Armature']
    armature.select_set(True)
    bpy.context.view_layer.objects.active=armature
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    #separate the PV bones, so the elbow IKs rotate with the spine
    pvrootupper = newbone('cf_pv_root_upper')
    pvrootupper.tail = armature.data.edit_bones['cf_pv_root'].tail
    pvrootupper.head = armature.data.edit_bones['cf_pv_root'].head

    #reparent things
    def reparent(bone,newparent):
        #refresh armature?
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        armature.data.edit_bones[bone].parent = armature.data.edit_bones[newparent]

    reparent('cf_pv_root_upper', 'cf_j_spine01')
    reparent('cf_pv_elbo_R', 'cf_pv_root_upper')
    reparent('cf_pv_elbo_L', 'cf_pv_root_upper')

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')
    
def setup_iks(): 
    #gives the leg an IK modifier, repositions the foot IK controller
    armature = bpy.data.objects['Armature']
    center_bone = armature.data.edit_bones['cf_n_height']
    
    def legIK(legbone, IKtarget, IKpole, IKpoleangle, footIK, kneebone, toebone, footbone):
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

        #Flip foot IK to match foot bone
        bpy.ops.object.mode_set(mode='EDIT')

        bone = bpy.data.objects['Armature'].data.edit_bones[footIK]
        
        if bpy.data.objects['Armature'].data.edit_bones.get('Greybone') == None:
            head = bone.head.y
            bone.head.y = bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.y
            bone.tail.z = bpy.data.objects['Armature'].data.edit_bones[toebone].head.z
            bone.head.z = bpy.data.objects['Armature'].data.edit_bones[footbone].head.z
            
            bone.head.x = bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.x
            bone.tail.x = bone.head.x
        else:
            head = bone.head.z
            bone.head.z = bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.z
            bone.tail.y = bpy.data.objects['Armature'].data.edit_bones[toebone].head.y
            bone.head.y = bpy.data.objects['Armature'].data.edit_bones[footbone].head.y
            
            bone.head.x = bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.x
            bone.tail.x = bone.head.x

        #unparent the bone
        bone.parent = center_bone

    #Run for each side
    legIK('cf_j_leg01_R', 'cf_pv_foot_R', 'cf_pv_knee_R', math.pi/2, 'cf_pv_foot_R', 'cf_j_leg01_R', 'cf_j_toes_R', 'cf_j_foot_R')
    legIK('cf_j_leg01_L',  'cf_pv_foot_L', 'cf_pv_knee_L', math.pi/2, 'cf_pv_foot_L', 'cf_j_leg01_L', 'cf_j_toes_L', 'cf_j_foot_L')

    #adds an IK for the toe bone, moves the knee IKs a little closer to the body
    def footIK(footbone, toebone, footIK, kneebone, legbone):

        bone = bpy.data.objects['Armature'].pose.bones[footbone]

        #Make Copy rotation
        bone.constraints.new("COPY_ROTATION")

        #Set target and subtarget
        bone.constraints[0].target=bpy.data.objects['Armature']
        bone.constraints[0].subtarget=bpy.data.objects['Armature'].data.bones[footIK].name

        #Set the rotation to local space
        bone.constraints[0].target_space = 'LOCAL_WITH_PARENT'
        bone.constraints[0].owner_space = 'LOCAL_WITH_PARENT'
        
        # move knee IKs closer to body
        #don't run for the fbx armature because it just deletes them
        if armature.data.bones.get('Greybone') == None:
            kneedist = round((bpy.data.objects['Armature'].pose.bones[footbone].head - bpy.data.objects['Armature'].pose.bones[footbone].tail).length,2)
            bpy.data.objects['Armature'].data.edit_bones[kneebone].head.y = kneedist * -5
            bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.y = kneedist * -5

        # make toe bone shorter
        if armature.data.bones.get('Greybone') == None:
            bpy.data.objects['Armature'].data.edit_bones[toebone].tail.z = bpy.data.objects['Armature'].data.edit_bones[legbone].head.z * 0.2
        else:
            bpy.data.objects['Armature'].data.edit_bones[toebone].tail.y = bpy.data.objects['Armature'].data.edit_bones[legbone].head.y * 0.2
        
        bpy.ops.object.mode_set(mode='EDIT')

    #Run for each side
    footIK('cf_j_foot_R', 'cf_j_toes_R', 'cf_pv_foot_R', 'cf_pv_knee_R', 'cf_j_leg01_R')
    footIK('cf_j_foot_L',  'cf_j_toes_L', 'cf_pv_foot_L', 'cf_pv_knee_L', 'cf_j_leg01_L')

    #Add a heel controller to the foot
    def heelController(footbone, footIK, toebone):
        bpy.ops.object.mode_set(mode='EDIT')
        
        #duplicate the foot IK. This is the new master bone
        armatureData = bpy.data.objects['Armature'].data
        masterbone = newbone('MasterFootIK.' + footbone[-1])
        masterbone.head = armatureData.edit_bones[footbone].head
        masterbone.tail = armatureData.edit_bones[footbone].tail
        masterbone.matrix = armatureData.edit_bones[footbone].matrix
        masterbone.parent = bpy.data.objects['Armature'].data.edit_bones['cf_n_height']
        
        #Create the heel controller
        heelIK = newbone('HeelIK.' + footbone[-1])
        heelIK.head = armatureData.edit_bones[footbone].tail
        heelIK.tail = armatureData.edit_bones[footbone].head
        heelIK.parent = masterbone
        if armature.data.bones.get('Greybone') == None:
            heelIK.tail.y *= .5
        else:
            heelIK.tail.z *= .5
        
        #parent footIK to heel controller
        armatureData.edit_bones[footIK].parent = heelIK
        
        #make a bone to pin the foot
        footPin = newbone('FootPin.' + footbone[-1])
        footPin.head = armatureData.edit_bones[toebone].head
        footPin.tail = armatureData.edit_bones[toebone].tail
        footPin.parent = masterbone
        if armature.data.bones.get('Greybone') == None:
            footPin.tail.z*=.8
        else:
            footPin.tail.y*=.8
            
        #make a bone to allow rotation of the toe along an arc
        toeRotator = newbone('ToeRotator.' + footbone[-1])
        toeRotator.head = armatureData.edit_bones[toebone].head
        toeRotator.tail = armatureData.edit_bones[toebone].tail
        toeRotator.parent = masterbone
        
        #make a bone to pin the toe
        toePin = newbone('ToePin.' + footbone[-1])
        toePin.head = armatureData.edit_bones[toebone].tail
        toePin.tail = armatureData.edit_bones[toebone].tail
        toePin.parent = toeRotator
        if armature.data.bones.get('Greybone') == None:
            toePin.tail.z *=1.2
        else:
            toePin.tail.y *=1.2
        
        #pin the foot
        bpy.ops.object.mode_set(mode='POSE')
        bone = bpy.data.objects['Armature'].pose.bones[footbone]
        bone.constraints.new("IK")
        bone.constraints["IK"].target = bpy.data.objects['Armature']
        bone.constraints["IK"].subtarget = bpy.data.objects['Armature'].data.bones['FootPin.' + footbone[-1]].name
        bone.constraints["IK"].chain_count=1
        
        #pin the toe
        bone = bpy.data.objects['Armature'].pose.bones[toebone]
        bone.constraints.new("IK")
        bone.constraints["IK"].target = bpy.data.objects['Armature']
        bone.constraints["IK"].subtarget = bpy.data.objects['Armature'].data.bones['ToePin.' + footbone[-1]].name
        bone.constraints["IK"].chain_count=1
        
        #move these bones to armature layer 2
        layer2 =   (False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.data.objects['Armature'].data.bones['FootPin.' + footbone[-1]].select = True
        bpy.data.objects['Armature'].data.bones['ToePin.' + footbone[-1]].select = True
        bpy.data.objects['Armature'].data.bones[toebone].select = True
        bpy.data.objects['Armature'].data.bones[footIK].select = True
        bpy.ops.pose.bone_layers(layers=layer2)
        
    heelController('cf_j_foot_L', 'cf_pv_foot_L', 'cf_j_toes_L')
    heelController('cf_j_foot_R', 'cf_pv_foot_R', 'cf_j_toes_R')
    
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
        bone.parent = bpy.data.objects['Armature'].data.edit_bones['cf_n_height']
        bpy.ops.object.mode_set(mode='POSE')

        # Set hand rotation then hide it
        bone = bpy.data.objects['Armature'].pose.bones[wristbone]

        bone.constraints.new("COPY_ROTATION")
        bone.constraints[0].target=bpy.data.objects['Armature']
        bone.constraints[0].subtarget=bpy.data.objects['Armature'].data.bones[handcontroller].name
        
        bpy.ops.object.mode_set(mode='POSE')
        bpy.data.objects['Armature'].data.bones[wristbone].hide = True
        bpy.ops.object.mode_set(mode='EDIT')

        # move elbow IKs closer to body
        # if this is run for the fbx the bones will be mysteriously deleted
        if armature.data.bones.get('Greybone') == None:
            elbowdist = round((bpy.data.objects['Armature'].pose.bones[elbowbone].head - bpy.data.objects['Armature'].pose.bones[elbowbone].tail).length,2)
            bpy.data.objects['Armature'].data.edit_bones[elbowcontroller].head.y = elbowdist*2
            bpy.data.objects['Armature'].data.edit_bones[elbowcontroller].tail.y = elbowdist*2

    #Run for each side
    armhandIK('cf_j_forearm01_R', 'cf_pv_hand_R', 'cf_pv_elbo_R', 0, 'cf_j_hand_R')
    armhandIK('cf_j_forearm01_L',  'cf_pv_hand_L', 'cf_pv_elbo_L', 180, 'cf_j_hand_L')

def setup_joints():
    bpy.ops.object.mode_set(mode='EDIT')

    #make the kokan bone shorter or larger depending on the armature
    if bpy.data.objects['Armature'].data.bones.get('Greybone'):
        bpy.data.objects['Armature'].data.edit_bones['cf_j_kokan'].tail.y = bpy.data.objects['Armature'].data.edit_bones['cf_s_waist02'].head.y
    else:
        bpy.data.objects['Armature'].data.edit_bones['cf_j_kokan'].tail.z = bpy.data.objects['Armature'].data.edit_bones['cf_s_waist02'].head.z

    bpy.ops.object.mode_set(mode='POSE')

    #generic function to set a copy rotation modifier
    def set_copy(bone, bonetarget, influence, axis = 'all', mix = 'replace'):
        constraint = bpy.data.objects['Armature'].pose.bones[bone].constraints.new("COPY_ROTATION")
        constraint.target = bpy.data.objects['Armature']
        constraint.subtarget = bonetarget
        constraint.influence = influence
        constraint.target_space = 'LOCAL'
        constraint.owner_space = 'LOCAL'

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
    set_copy('cf_d_shoulder02_R', 'cf_j_arm00_R', 0.5)

    set_copy('cf_d_arm01_L', 'cf_j_arm00_L', 0.75, axis = 'X')
    set_copy('cf_d_arm01_R', 'cf_j_arm00_R', 0.75, axis = 'X')

    set_copy('cf_d_arm02_L', 'cf_j_arm00_L', 0.5, axis = 'X')
    set_copy('cf_d_arm02_R', 'cf_j_arm00_R', 0.5, axis = 'X')

    set_copy('cf_d_arm03_L', 'cf_j_arm00_L', 0.25, axis = 'X')
    set_copy('cf_d_arm03_R', 'cf_j_arm00_R', 0.25, axis = 'X')

    set_copy('cf_d_forearm02_L', 'cf_j_hand_L', 0.33, axis = 'X')
    set_copy('cf_d_forearm02_R', 'cf_j_hand_R', 0.33, axis = 'X')

    set_copy('cf_d_wrist_L', 'cf_j_hand_L', 0.33, axis = 'X', )
    set_copy('cf_d_wrist_R', 'cf_j_hand_R', 0.33, axis = 'X')

    #set_copy('cf_s_leg_L', 'cf_j_thigh00_L', 0.25, axis = 'X', mix = 'add')
    #set_copy('cf_s_leg_R', 'cf_j_thigh00_R', 0.25, axis = 'X', mix = 'add')

    set_copy('cf_d_siri_L', 'cf_j_thigh00_L', 0.33)
    set_copy('cf_d_siri_R', 'cf_j_thigh00_R', 0.33)

    set_copy('cf_d_thigh02_L', 'cf_j_thigh00_L', 0.25, axis='Y')
    set_copy('cf_d_thigh02_R', 'cf_j_thigh00_R', 0.25, axis='Y')

    set_copy('cf_d_thigh03_L', 'cf_j_thigh00_L', 0.25, axis='Y')
    set_copy('cf_d_thigh03_R', 'cf_j_thigh00_R', 0.25, axis='Y')

    set_copy('cf_d_leg02_L', 'cf_j_leg01_L', 0.33, axis='Y')
    set_copy('cf_d_leg02_R', 'cf_j_leg01_R', 0.33, axis='Y')

    set_copy('cf_d_leg03_L', 'cf_j_leg01_L', 0.66, axis='Y')
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
        driver = bpy.data.objects['Armature'].pose.bones[bone].driver_add(drivertype, drivertypeselect)

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
        target.transform_space = 'LOCAL_SPACE'

        target.rotation_mode = 'AUTO' #or QUATERNION

        #use the distance to the target bone's parent to make results consistent for different sized bones
        targetbonelength = str(round((bpy.data.objects['Armature'].pose.bones[drivertarget].head - bpy.data.objects['Armature'].pose.bones[drivertarget].parent.head).length,3))
        
        #driver expression is the rotation value of the target bone multiplied by a percentage of the driver target bone's length
        if expresstype == 'move':
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

    #Set the remaining joint correction drivers
    #bone directions change based on the PMX vs FBX origin because the Y and Z axis for each bone are swapped
    if bpy.data.objects['Armature'].data.bones.get('Greybone') == None:

        #set knee joint corrections. These go in toward the body and down toward the foot at an exponential rate
        setDriver('cf_s_kneeB_R', 'location', 1, 'cf_j_leg01_R', 'ROT_X',  '-0.2', expresstype = 'moveexp')
        setDriver('cf_s_kneeB_R', 'location', 2, 'cf_j_leg01_R', 'ROT_X',  '-0.08')

        setDriver('cf_s_kneeB_L', 'location', 1, 'cf_j_leg01_L', 'ROT_X',  '-0.2', expresstype = 'moveexp')
        setDriver('cf_s_kneeB_L', 'location', 2, 'cf_j_leg01_L', 'ROT_X',  '-0.08')

        #knee tip corrections go up toward the waist and in toward the body
        setDriver('cf_d_kneeF_R', 'location', 1, 'cf_j_leg01_R', 'ROT_X',  '0.02')
        setDriver('cf_d_kneeF_R', 'location', 2, 'cf_j_leg01_R', 'ROT_X',  '-0.02')

        setDriver('cf_d_kneeF_L', 'location', 1, 'cf_j_leg01_L', 'ROT_X',  '0.02')
        setDriver('cf_d_kneeF_L', 'location', 2, 'cf_j_leg01_L', 'ROT_X',  '-0.02')

        #butt corrections go slightly up to the spine and in to the waist 
        setDriver('cf_d_siri_R', 'location', 1, 'cf_j_thigh00_R', 'ROT_X',  '0.02')
        setDriver('cf_d_siri_R', 'location', 2, 'cf_j_thigh00_R',  'ROT_X',  '0.02')

        setDriver('cf_d_siri_L', 'location', 1, 'cf_j_thigh00_L', 'ROT_X',  '0.02')
        setDriver('cf_d_siri_L', 'location', 2, 'cf_j_thigh00_L',  'ROT_X',  '0.02')
        
        #hand corrections go up to the head and in towards the elbow
        setDriver('cf_d_hand_R', 'location', 0, 'cf_j_hand_R', 'ROT_Z',  '-0.4', expresstype = 'movePos')
        setDriver('cf_d_hand_R', 'location', 1, 'cf_j_hand_R', 'ROT_Z', '-0.4', expresstype = 'movePos')

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
'''
    else:
        setDriver('cf_s_kneeB_R', 'location', 2, 'cf_j_leg01_R', 'ROT_X',  '-0.29')
        setDriver('cf_s_kneeB_R', 'location', 1, 'cf_j_leg01_R', 'ROT_X',  '-0.23')

        setDriver('cf_s_kneeB_L', 'location', 2, 'cf_j_leg01_L', 'ROT_X',  '-0.29')
        setDriver('cf_s_kneeB_L', 'location', 1, 'cf_j_leg01_L', 'ROT_X',  '-0.23')

        #set drivers for foot joint correction bones
        setDriver('cf_d_leg03_R', 'location', 1, 'cf_j_leg01_R', 'ROT_X',  '-0.02')
        setDriver('cf_d_leg03_L', 'location', 1, 'cf_j_leg01_L',  'ROT_X',  '-0.02')
        
        #Set drivers for hand joint correction bones
        setDriver('cf_d_hand_R', 'location', 0, 'cf_j_hand_R', 'ROT_Z',  '-1.5')
        setDriver('cf_d_hand_R', 'location', 2, 'cf_j_hand_R', 'ROT_Z',  '-1.5')

        setDriver('cf_d_hand_L', 'location', 0, 'cf_j_hand_L', 'ROT_Z',  '-1.5')
        setDriver('cf_d_hand_L', 'location', 2, 'cf_j_hand_L', 'ROT_Z',  '1.5')
        setDriver('cf_d_hand_L', 'location', 1, 'cf_j_hand_L', 'ROT_Z',  '-1.5')

        #Set drivers for Elbow joint correction  bones
        setDriver('cf_s_elboback_R', 'location', 0, 'cf_j_forearm01_R', 'ROT_Z',  '0.7')
        setDriver('cf_s_elboback_R', 'location', 2, 'cf_j_forearm01_R', 'ROT_Z',  '-0.6')

        setDriver('cf_s_elbo_R', 'location', 0, 'cf_j_forearm01_R', 'ROT_Z',  '-0.025')
        setDriver('cf_s_elbo_R', 'location', 2, 'cf_j_forearm01_R', 'ROT_Z',  '-0.025')

        setDriver('cf_s_elboback_L', 'location', 0, 'cf_j_forearm01_L', 'ROT_Z',  '-0.7')
        setDriver('cf_s_elboback_L', 'location', 2, 'cf_j_forearm01_L', 'ROT_Z',  '-0.6')

        setDriver('cf_s_elbo_L', 'location', 0, 'cf_j_forearm01_L', 'ROT_Z',  '0.025')
        setDriver('cf_s_elbo_L', 'location', 2, 'cf_j_forearm01_L', 'ROT_Z',  '-0.025')

        #Set drivers for Shoulder joint correction bones
        setDriver('cf_d_shoulder02_R', 'rotation_quaternion', 3, 'cf_j_arm00_R', 'ROT_Z',  '0.5', 'rotateNeg')
        setDriver('cf_d_shoulder02_R', 'location', 1, 'cf_j_arm00_R', 'ROT_Z',  '-0.1', 'moveNeg')

        setDriver('cf_d_shoulder02_R', 'location', 0, 'cf_j_arm00_R', 'ROT_Y',  '0.1', 'moveABSNeg')
        setDriver('cf_d_shoulder02_R', 'location', 2, 'cf_j_arm00_R', 'ROT_Y',  '-0.1')

        setDriver('cf_d_arm01_R', 'rotation_quaternion', 1, 'cf_j_arm00_R', 'ROT_X',  '0.7')

        setDriver('cf_d_shoulder02_L', 'rotation_quaternion', 3, 'cf_j_arm00_L', 'ROT_Z',  '0.5', 'rotatePos')
        setDriver('cf_d_shoulder02_L', 'location', 1, 'cf_j_arm00_L', 'ROT_Z',  '0.1', 'movePos')

        setDriver('cf_d_shoulder02_L', 'location', 0, 'cf_j_arm00_L', 'ROT_Y',  '-0.1', 'moveABS')
        setDriver('cf_d_shoulder02_L', 'location', 2, 'cf_j_arm00_L', 'ROT_Y',  '0.1')

        setDriver('cf_d_arm01_L', 'rotation_quaternion', 1, 'cf_j_arm00_L', 'ROT_X',  '-0.7')
'''

def make_eye_controller():
    armature = bpy.data.objects['Armature']
    
    #roll the eye bone based on armature, create a copy and name it eye controller
    bpy.ops.object.mode_set(mode='EDIT')

    armatureData = bpy.data.objects['Armature'].data
    if bpy.data.objects['Armature'].data.bones.get('Greybone'):
        armatureData.edit_bones['Eyesx'].roll = math.pi/2
    else:
        armatureData.edit_bones['Eyesx'].roll = -math.pi/2

    copy = newbone('Eye Controller')

    copy.head = armatureData.edit_bones['Eyesx'].head/2
    copy.tail = armatureData.edit_bones['Eyesx'].tail/2
    copy.matrix = armatureData.edit_bones['Eyesx'].matrix
    copy.parent = armatureData.edit_bones['cf_j_head']
        
    if bpy.data.objects['Armature'].data.bones.get('Greybone'):
        armatureData.edit_bones['Eye Controller'].roll = math.pi/2
    else:
        armatureData.edit_bones['Eye Controller'].roll = -math.pi/2

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

    eyeUV("Left Eye UV warp",  'Left Eye')
    eyeUV("Right Eye UV warp", 'Right Eye')

    ################### Empty group check for pmx files

    #checks if the Eyex_L vertex group is empty. If it is, assume the Eyex_R vertex group is also empty,
    #then find the vertices using the eye material and assign both eyes to Eyex_L
    if armature.pose.bones.get('Greybone') == None:
        body = bpy.data.objects['Body']

        #Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        #Select the Body object
        body.select_set(True)
        #and make it active
        bpy.context.view_layer.objects.active = body

        #make the cf_J_hitomi_tx_L vertex group active
        body.vertex_groups.active_index = body.vertex_groups['cf_J_hitomi_tx_L'].index

        #go into edit mode and select the vertices in the cf_J_hitomi_tx_L vertex group
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.vertex_group_select()

        #refresh the selection (this needs to be done for some reason)
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.mode_set(mode = 'EDIT')

        #get a list of the selected vertices
        vgVerts = [v for v in body.data.vertices if v.select]

        #If the list is empty...
        if not vgVerts:
            #select the eye materials
            bpy.context.object.active_material_index = body.data.materials.find('cf_m_hitomi_00 (Instance)')
            bpy.ops.object.material_slot_select()
            #Try to select the other eye if it wasn't merged
            try:
                bpy.context.object.active_material_index = body.data.materials.find('cf_m_hitomi_00 (Instance).001')
                bpy.ops.object.material_slot_select()
            except:
                #the eye was already merged, skip
                pass
            #then assign them to the Eyex_L group
            bpy.ops.object.vertex_group_assign()

    #Reselect the armature
    bpy.ops.object.mode_set(mode='OBJECT')
    armature = bpy.data.objects['Armature']
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
def scale_final_bones():
    
    #scale all skirt bones
    armature = bpy.data.objects['Armature']
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='POSE')

    def resizeBone(bone, scale, type='MIDPOINT'):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        bpy.context.object.data.edit_bones[bone].select_head = True
        bpy.context.object.data.edit_bones[bone].select_tail = True
        previous_roll = bpy.context.object.data.edit_bones[bone].roll + 1
        if type == 'MIDPOINT':
            bpy.ops.transform.resize(value=(scale, scale, scale), orient_type='GLOBAL',
            orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL',
            mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH',
            proportional_size=0.683013, use_proportional_connected=False, use_proportional_projected=False)
        else:
            bpy.context.object.data.edit_bones[bone].tail = (bpy.context.object.data.edit_bones[bone].tail+bpy.context.object.data.edit_bones[bone].head)/2
            bpy.context.object.data.edit_bones[bone].tail = (bpy.context.object.data.edit_bones[bone].tail+bpy.context.object.data.edit_bones[bone].head)/2
            bpy.context.object.data.edit_bones[bone].tail = (bpy.context.object.data.edit_bones[bone].tail+bpy.context.object.data.edit_bones[bone].head)/2
        bpy.context.object.data.edit_bones[bone].select_head = False
        bpy.context.object.data.edit_bones[bone].select_tail = False
        bpy.context.object.data.edit_bones[bone].roll = previous_roll - 1
        bpy.ops.object.mode_set(mode='POSE')
    
    skirtbones = [0,1,2,3,4,5,6,7]
    skirtlength = [0,1,2,3,4]

    for root in skirtbones:
        for chain in skirtlength:
            resizeBone('cf_j_sk_0'+str(root)+'_0'+str(chain), 0.25)
    
    #scale eye bones, mouth bones, eyebrow bones
    bpy.ops.object.mode_set(mode='POSE')
    
    eyebones = [1,2,3,4,5,6,7,8]
    
    for piece in eyebones:
        bpy.ops.pose.select_all(action='DESELECT')
        left = 'cf_J_Eye0'+str(piece)+'_s_L'
        right = 'cf_J_Eye0'+str(piece)+'_s_R'
        
        resizeBone(left, 0.1, 'face')
        resizeBone(right, 0.1, 'face')
        
    restOfFace = [
    'cf_J_Mayu_R', 'cf_J_MayuMid_s_R', 'cf_J_MayuTip_s_R',
    'cf_J_Mayu_L', 'cf_J_MayuMid_s_L', 'cf_J_MayuTip_s_L',
    'cf_J_Mouth_R', 'cf_J_Mouth_L',
    'cf_J_Mouthup', 'cf_J_MouthLow', 'cf_J_MouthMove', 'cf_J_MouthCavity']
    
    for bone in restOfFace:
        bpy.ops.pose.select_all(action='DESELECT')
        resizeBone(bone, 0.1, 'face')
    
    #move eye bone location
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.armature.select_all(action='DESELECT')

    for eyebone in ['Eyesx', 'Eye Controller']:
        if armature.data.edit_bones.get('Greybone') == None:
            bpy.context.object.data.edit_bones[eyebone].head.y = bpy.context.object.data.edit_bones['cf_d_bust02_R'].tail.y
            bpy.context.object.data.edit_bones[eyebone].tail.y = bpy.context.object.data.edit_bones['cf_d_bust02_R'].tail.y*1.5
            bpy.context.object.data.edit_bones[eyebone].tail.z = bpy.context.object.data.edit_bones['cf_J_Nose_tip'].tail.z
            bpy.context.object.data.edit_bones[eyebone].head.z = bpy.context.object.data.edit_bones['cf_J_Nose_tip'].tail.z
        else:
            bpy.context.object.data.edit_bones[eyebone].head.z = bpy.context.object.data.edit_bones['cf_d_bust02_R'].tail.z
            bpy.context.object.data.edit_bones[eyebone].tail.z = bpy.context.object.data.edit_bones['cf_d_bust02_R'].tail.z*1.5
            bpy.context.object.data.edit_bones[eyebone].tail.y = bpy.context.object.data.edit_bones['cf_J_Nose_tip'].tail.y
            bpy.context.object.data.edit_bones[eyebone].head.y = bpy.context.object.data.edit_bones['cf_J_Nose_tip'].tail.y
    
    #scale BP bones if they exist
    try:
        BPList = ['cf_j_kokan', 'cf_j_ana', 'Vagina_Root', 'Vagina_B', 'Vagina_F', 'Vagina_001_L', 'Vagina_002_L', 'Vagina_003_L', 'Vagina_004_L', 'Vagina_005_L',  'Vagina_001_R', 'Vagina_002_R', 'Vagina_003_R', 'Vagina_004_R', 'Vagina_005_R']
    
        for bone in BPList:
            armature.data.edit_bones[bone].tail.z = armature.data.edit_bones[bone].tail.z*.95
    except:
        #this isn't a BP armature
        pass

def categorize_bones():
    armature = bpy.data.objects['Armature']
    bpy.ops.object.mode_set(mode='POSE')
    #move newly created bones to correct armature layers

    set_armature_layer('MasterFootIK.L', 0)
    set_armature_layer('MasterFootIK.R', 0)
    set_armature_layer('Eye Controller', 0)
    
    armature.data.bones['cf_pv_root_upper'].hide = True
    
    #Add some bones to bone groups
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.ops.pose.group_add()
    group_index = len(armature.pose.bone_groups)-1
    group = armature.pose.bone_groups[group_index]
    group.name = 'IK controllers'
    armature.data.bones['cf_pv_hand_L'].select = True
    armature.data.bones['cf_pv_hand_R'].select = True
    armature.data.bones['MasterFootIK.L'].select = True
    armature.data.bones['MasterFootIK.R'].select = True
    bpy.ops.pose.group_assign(type=group_index+1)
    group.color_set = 'THEME01'
    
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.ops.pose.group_add()
    group_index = len(armature.pose.bone_groups)-1
    group = armature.pose.bone_groups[group_index]
    group.name = 'IK poles'
    armature.pose.bone_groups.active_index = 1
    armature.data.bones['cf_pv_elbo_R'].select = True
    armature.data.bones['cf_pv_elbo_L'].select = True
    armature.data.bones['cf_pv_knee_R'].select = True
    armature.data.bones['cf_pv_knee_L'].select = True
    bpy.ops.pose.group_assign(type=group_index+1)
    group.color_set = 'THEME09'
 
    bpy.ops.object.mode_set(mode='OBJECT')

def rename_bones_for_clarity(action):
    armature = bpy.data.objects['Armature']
    
    #rename core bones to match unity bone names (?)
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

    if action == 'modified':
        for bone in armature.data.bones:
            if bone.name in unity_rename_dict:
                bone.name = unity_rename_dict[bone.name]
    
    elif action == 'stock':
        for bone in unity_rename_dict:
            if armature.data.bones.get(unity_rename_dict[bone]):
                armature.data.bones[unity_rename_dict[bone]].name = bone

    elif action == 'animation':
        animation_armature = bpy.data.objects['Animation Armature']
        for bone in unity_rename_dict:
            if animation_armature.data.bones.get(bone):
                animation_armature.data.bones[bone].name = unity_rename_dict[bone]
    
#selects all materials that have "_hair" or "_ahoge" in their name to give the user a head start with separating the hair
def begin_hair_selections():
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    clothes = bpy.data.objects['Clothes']
    clothes.select_set(True)
    bpy.context.view_layer.objects.active=clothes
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')

    for index in range(len(clothes.data.materials)):
        mat_name = clothes.data.materials[index].name
        if ('_hair' in mat_name or '_ahoge' in mat_name) and ('_ribon_' not in mat_name and '_hair_sakura_' not in mat_name):
            clothes.active_material_index = index
            bpy.ops.object.material_slot_select()
    
    bpy.data.objects['Armature'].hide = True

class bone_drivers(bpy.types.Operator):
    bl_idname = "kkb.bonedrivers"
    bl_label = "Bone Driver script"
    bl_description = "Add IKs, joint drivers and an eye bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        scene = context.scene.placeholder
        modify_armature = scene.armature_edit_bool
        armature_not_modified = bpy.data.objects['Armature'].data.bones.get('MasterFootIK.L') == None
        
        if modify_armature and armature_not_modified:
            reparent_bones()
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            setup_iks()
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        setup_joints()
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        
        if modify_armature and armature_not_modified:
            make_eye_controller()
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            scale_final_bones()
            categorize_bones()
            rename_bones_for_clarity('modified')
        
        begin_hair_selections()

        #set the viewport shading
        my_areas = bpy.context.workspace.screens[0].areas
        my_shading = 'MATERIAL'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'

        for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = my_shading 
        
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(bone_drivers)

    # test call
    print((bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT')))
