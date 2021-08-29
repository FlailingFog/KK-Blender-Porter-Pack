'''
AFTER CATS (BONE DRIVERS) SCRIPT
- Adds IKs to the arms and legs using the "Pv" bones
- Moves the Knee and Elbow IKs a little closer to the body
- Adds drivers for twist / joint correction bones for the arms, hands, legs and butt
- Adds an "Eye Controller" bone to the top of the head and UV warp modifiers on the Body object to make the eyes work
- Scales and repositions some bones
Usage:
- Run the script
'''

import bpy, math

#Makes a new bone on the armature
def newbone(newbonepls):
    armature = bpy.data.objects['Armature']
    bpy.ops.armature.bone_primitive_add()
    bo = armature.data.edit_bones['Bone']
    bo.name = newbonepls
    return bo

#reparents some bones on the armature
def reparent_bones():
    #remove all constraints from all bones
    for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
        for bone in armature.pose.bones:
            bonesWithConstraints = [constraint for constraint in bone.constraints if constraint.type == 'IK' or constraint.type == 'COPY_ROTATION']
            for constraint in bonesWithConstraints:
                bone.constraints.remove(constraint)
    #remove all drivers from all armature bones
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
        #refresh the fucking armature again
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        armature.data.edit_bones[bone].parent = armature.data.edit_bones[newparent]
    reparent('cf_pv_root_upper', 'Spine')
    reparent('cf_pv_elbo_R', 'cf_pv_root_upper')
    reparent('cf_pv_elbo_L', 'cf_pv_root_upper')
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.mode_set(mode='EDIT')
    
def setup_iks(): 
    #gives the leg an IK modifier, repositions the foot IK controller
    armature = bpy.data.objects['Armature']
    center_bone = armature.data.edit_bones['Center']
    
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
    legIK('Right knee', 'cf_pv_foot_R', 'cf_pv_knee_R', math.pi/2, 'cf_pv_foot_R', 'Right knee', 'Right toe', 'Right ankle')
    legIK('Left knee',  'cf_pv_foot_L', 'cf_pv_knee_L', math.pi/2, 'cf_pv_foot_L', 'Left knee', 'Left toe', 'Left ankle')

    #adds an IK for the toe bone, moves the knee IKs a little closer to the body
    def footIK(footbone, toebone, toeIK, footIK, kneebone, legbone):

        bone = bpy.data.objects['Armature'].pose.bones[footbone]

        #Make Copy rotation
        bone.constraints.new("COPY_ROTATION")

        #Set target and subtarget
        bone.constraints[0].target=bpy.data.objects['Armature']
        bone.constraints[0].subtarget=bpy.data.objects['Armature'].data.bones[footIK].name

        #Set the rotation to local space
        bone.constraints[0].target_space = 'LOCAL_WITH_PARENT'
        bone.constraints[0].owner_space = 'LOCAL_WITH_PARENT'
        
        #Lock the footIK's rotation
        #bpy.data.objects['Armature'].pose.bones[footIK].lock_rotation[1] = True
        #bpy.data.objects['Armature'].pose.bones[footIK].lock_rotation[2] = True
        
        #parent the toe tip bone to the foot IK bone
        #bpy.data.objects['Armature'].data.edit_bones[toeIK].parent = bpy.data.objects['Armature'].data.edit_bones[footIK]

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
        
        #hide the toeTipIK bones for now
        #bpy.ops.object.mode_set(mode='POSE')
        #bpy.data.objects['Armature'].data.bones[toeIK].hide = True
        bpy.ops.object.mode_set(mode='EDIT')

    #Run for each side
    footIK('Right ankle', 'Right toe', 'Right toe', 'cf_pv_foot_R', 'cf_pv_knee_R', 'Right knee')
    footIK('Left ankle',  'Left toe',  'Left toe', 'cf_pv_foot_L', 'cf_pv_knee_L', 'Left knee')

    #Add a heel controller to the foot
    def heelController(footbone, footIK, toebone):
        bpy.ops.object.mode_set(mode='EDIT')
        
        #duplicate the foot IK. This is the new master bone
        armatureData = bpy.data.objects['Armature'].data
        masterbone = newbone('MasterFootIK.' + footbone[0])
        masterbone.head = armatureData.edit_bones[footbone].head
        masterbone.tail = armatureData.edit_bones[footbone].tail
        masterbone.matrix = armatureData.edit_bones[footbone].matrix
        masterbone.parent = bpy.data.objects['Armature'].data.edit_bones['Center']
        
        #Create the heel controller
        heelIK = newbone('HeelIK.' + footbone[0])
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
        footPin = newbone('FootPin.' + footbone[0])
        footPin.head = armatureData.edit_bones[toebone].head
        footPin.tail = armatureData.edit_bones[toebone].tail
        footPin.parent = masterbone
        if armature.data.bones.get('Greybone') == None:
            footPin.tail.z*=.8
        else:
            footPin.tail.y*=.8
            
        #make a bone to allow rotation of the toe along an arc
        toeRotator = newbone('ToeRotator.' + footbone[0])
        toeRotator.head = armatureData.edit_bones[toebone].head
        toeRotator.tail = armatureData.edit_bones[toebone].tail
        toeRotator.parent = masterbone
        
        #make a bone to pin the toe
        toePin = newbone('ToePin.' + footbone[0])
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
        bone.constraints["IK"].subtarget = bpy.data.objects['Armature'].data.bones['FootPin.' + footbone[0]].name
        bone.constraints["IK"].chain_count=1
        
        #pin the toe
        bone = bpy.data.objects['Armature'].pose.bones[toebone]
        bone.constraints.new("IK")
        bone.constraints["IK"].target = bpy.data.objects['Armature']
        bone.constraints["IK"].subtarget = bpy.data.objects['Armature'].data.bones['ToePin.' + footbone[0]].name
        bone.constraints["IK"].chain_count=1
        
        #move these bones to armature layer 19
        layer19 =   (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True, False, False, False, False, False, False, False, False, False, False, False, False, False)
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.data.objects['Armature'].data.bones['FootPin.' + footbone[0]].select = True
        bpy.data.objects['Armature'].data.bones['ToePin.' + footbone[0]].select = True
        bpy.data.objects['Armature'].data.bones[toebone].select = True
        bpy.data.objects['Armature'].data.bones[footIK].select = True
        bpy.ops.pose.bone_layers(layers=layer19)
        
    heelController('Left ankle', 'cf_pv_foot_L', 'Left toe')
    heelController('Right ankle', 'cf_pv_foot_R', 'Right toe')
    
    #add an IK to the arm, makes the wrist bone copy the hand IK's rotation, moves elbow IKs a little closer to the body
    def armhandIK(elbowbone, handcontroller, elbowcontroller, IKangle, wristbone, wristtwist):
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
        bone.parent = bpy.data.objects['Armature'].data.edit_bones['Center']
        bpy.ops.object.mode_set(mode='POSE')

        # Set hand rotation then hide it
        bone = bpy.data.objects['Armature'].pose.bones[wristbone]

        bone.constraints.new("COPY_ROTATION")
        bone.constraints[0].target=bpy.data.objects['Armature']
        bone.constraints[0].subtarget=bpy.data.objects['Armature'].data.bones[handcontroller].name

        bone = bpy.data.objects['Armature'].pose.bones[wristtwist]

        bone.constraints.new("COPY_ROTATION")
        bone.constraints[0].target=bpy.data.objects['Armature']
        bone.constraints[0].subtarget=bpy.data.objects['Armature'].data.bones[wristbone].name
        bone.constraints[0].use_x = True
        bone.constraints[0].use_y = False
        bone.constraints[0].use_z = False
        bone.constraints[0].target_space = 'POSE'
        bone.constraints[0].owner_space = 'POSE'
        bone.constraints[0].influence = 0.5
        
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
    armhandIK('Right elbow', 'cf_pv_hand_R', 'cf_pv_elbo_R', 0, 'Right wrist', 'cf_s_wrist_R')
    armhandIK('Left elbow',  'cf_pv_hand_L', 'cf_pv_elbo_L', 180, 'Left wrist', 'cf_s_wrist_L')
    
    # Tilt the bust bone and make it smaller
    if armature.data.bones.get('Greybone'):
        bone = bpy.data.objects['Armature'].data.edit_bones['cf_d_bust00']
        bone.tail.y = bpy.data.objects['Armature'].data.edit_bones['cf_d_bust02_L'].head.y
        bone.tail.z = bpy.data.objects['Armature'].data.edit_bones['cf_d_bust02_L'].head.z * 2
    else:
        bone = bpy.data.objects['Armature'].data.edit_bones['cf_d_bust00']
        bone.tail.y = bpy.data.objects['Armature'].data.edit_bones['cf_d_bust02_L'].head.y * 2
        bone.tail.z = bpy.data.objects['Armature'].data.edit_bones['cf_d_bust02_L'].head.z

def setup_joints():
    #make the kokan bone shorter or larger depending on the armature
    if bpy.data.objects['Armature'].data.bones.get('Greybone'):
        bpy.data.objects['Armature'].data.edit_bones['cf_j_kokan'].tail.y = bpy.data.objects['Armature'].data.edit_bones['cf_s_waist02'].head.y
    else:
        bpy.data.objects['Armature'].data.edit_bones['cf_j_kokan'].tail.z = bpy.data.objects['Armature'].data.edit_bones['cf_s_waist02'].head.z

    #generic function for creating a driver
    def setDriver (bonetarget, drivertype, drivertypeselect, drivertarget, drivertt, driverts, driverrm, drivermult, expresstype = 'move'):
        bpy.ops.object.mode_set(mode='POSE')

        #select bone to add driver to
        bone=bpy.data.objects['Armature'].pose.bones[bonetarget]

        #add driver to first component
        #drivertype is the kind of driver you want to be applied to the bonetarget and can be location/rotation
        #drivertypeselect is the component you want the driver to be applied to (0 is x component, y is 1, z is 2)
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

        #get the length of the driver target bone
        targetbonelength = str((bpy.data.objects['Armature'].pose.bones[drivertarget].head - bpy.data.objects['Armature'].pose.bones[drivertarget].tail).length)
        #print(targetbonelength)

        if expresstype == 'move':
            #driver expression is the rotation value of the target bone multiplied by a percentage of the driver target bone's length
            driver.driver.expression = vari.name + '*' + targetbonelength + '*' + drivermult 
        elif expresstype == 'rotate':
            #driver expression is a percentage of the rotation value of the target bone
            driver.driver.expression = vari.name + '*' + drivermult
        elif expresstype == 'movePos':
            #move but only during positive rotations
            driver.driver.expression = vari.name + '*' + targetbonelength + '*' + drivermult + ' if ' + vari.name + ' > 0 else 0'
        elif expresstype == 'moveNeg':
            #move but only during negative rotations
            driver.driver.expression = vari.name + '*' + targetbonelength + '*' + drivermult + ' if ' + vari.name + ' < 0 else 0'
        elif expresstype == 'rotatePos':
            #rotate but only during positive rotations
            driver.driver.expression = vari.name + '*' + drivermult + ' if ' + vari.name + ' > 0 else 0'
        elif expresstype == 'rotateNeg':
            #rotate but only during negative rotations
            driver.driver.expression = vari.name + '*' + drivermult + ' if ' + vari.name + ' < 0 else 0'
        elif expresstype == 'moveABS':
            #move but the ABS value
            driver.driver.expression = 'abs(' + vari.name + '*' + targetbonelength + '*' + drivermult +')'
        elif expresstype == 'moveABSNeg':
            #move but the negative ABS value
            driver.driver.expression = '-abs(' + vari.name + '*' + targetbonelength + '*' + drivermult +')'

    #Set drivers for Knee joint correction bones
    #bone directions change based on the armature because the Y and Z axis for each bone are swapped
    if bpy.data.objects['Armature'].data.bones.get('Greybone') == None:
        setDriver('cf_s_kneeB_R', 'location', 1, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.29')
        setDriver('cf_s_kneeB_R', 'location', 2, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.23')
        #setDriver('cf_s_kneeB_L', 'rotation_quaternion', 1, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '0.33')

        setDriver('cf_s_kneeB_L', 'location', 1, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.29')
        setDriver('cf_s_kneeB_L', 'location', 2, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.23')
        #setDriver('cf_s_kneeB_L', 'rotation_quaternion', 1, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '-0.33')

        #set drivers for foot joint correction bones
        setDriver('cf_d_leg03_R', 'location', 2, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.02')
        setDriver('cf_d_leg03_L', 'location', 2, 'Left knee',  'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.02')
        
        #Set drivers for hand joint correction bones
        setDriver('cf_d_hand_R', 'location', 0, 'Right wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-1.5')
        setDriver('cf_d_hand_R', 'location', 1, 'Right wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-1.5')
        setDriver('cf_d_hand_R', 'location', 2, 'Right wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '1.5')

        setDriver('cf_d_hand_L', 'location', 0, 'Left wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-1.5')
        setDriver('cf_d_hand_L', 'location', 1, 'Left wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '1.5')
        setDriver('cf_d_hand_L', 'location', 2, 'Left wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-1.5')

        #Set drivers for Elbow joint correction  bones
        setDriver('cf_s_elboback_R', 'location', 0, 'Right elbow', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.7')
        setDriver('cf_s_elboback_R', 'location', 2, 'Right elbow', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '0.6')

        setDriver('cf_s_elbo_R', 'location', 0, 'Right elbow', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '0.025')
        setDriver('cf_s_elbo_R', 'location', 2, 'Right elbow', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '0.025')

        setDriver('cf_s_elboback_L', 'location', 0, 'Left elbow', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.7')
        setDriver('cf_s_elboback_L', 'location', 2, 'Left elbow', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.6')

        setDriver('cf_s_elbo_L', 'location', 0, 'Left elbow', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '0.025')
        setDriver('cf_s_elbo_L', 'location', 2, 'Left elbow', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.025')

        #Set drivers for Shoulder joint correction bones
        setDriver('cf_d_shoulder02_R', 'rotation_quaternion', 3, 'Right arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '0.5', 'rotateNeg')
        setDriver('cf_d_shoulder02_R', 'location', 1, 'Right arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-0.1', 'moveNeg')

        setDriver('cf_d_shoulder02_R', 'location', 0, 'Right arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '0.1', 'moveABSNeg')
        setDriver('cf_d_shoulder02_R', 'location', 2, 'Right arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '-0.1')

        setDriver('cf_d_arm01_R', 'rotation_quaternion', 1, 'Right arm', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '0.7')

        setDriver('cf_d_shoulder02_L', 'rotation_quaternion', 3, 'Left arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '0.5', 'rotatePos')
        setDriver('cf_d_shoulder02_L', 'location', 1, 'Left arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '0.1', 'movePos')

        setDriver('cf_d_shoulder02_L', 'location', 0, 'Left arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '-0.1', 'moveABS')
        setDriver('cf_d_shoulder02_L', 'location', 2, 'Left arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '0.1')

        setDriver('cf_d_arm01_L', 'rotation_quaternion', 1, 'Left arm', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '-0.7')
        
    else:
        setDriver('cf_s_kneeB_R', 'location', 2, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.29')
        setDriver('cf_s_kneeB_R', 'location', 1, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.23')
        #setDriver('cf_s_kneeB_L', 'rotation_quaternion', 1, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '0.33')

        setDriver('cf_s_kneeB_L', 'location', 2, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.29')
        setDriver('cf_s_kneeB_L', 'location', 1, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.23')
        #setDriver('cf_s_kneeB_L', 'rotation_quaternion', 1, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '-0.33')

        #set drivers for foot joint correction bones
        setDriver('cf_d_leg03_R', 'location', 1, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.02')
        setDriver('cf_d_leg03_L', 'location', 1, 'Left knee',  'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.02')
        
        #Set drivers for hand joint correction bones
        setDriver('cf_d_hand_R', 'location', 0, 'Right wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-1.5')
        setDriver('cf_d_hand_R', 'location', 2, 'Right wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-1.5')
        setDriver('cf_d_hand_R', 'location', 1, 'Right wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '1.5')

        setDriver('cf_d_hand_L', 'location', 0, 'Left wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-1.5')
        setDriver('cf_d_hand_L', 'location', 2, 'Left wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '1.5')
        setDriver('cf_d_hand_L', 'location', 1, 'Left wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-1.5')

        #Set drivers for Elbow joint correction  bones
        setDriver('cf_s_elboback_R', 'location', 0, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '0.7')
        setDriver('cf_s_elboback_R', 'location', 2, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.6')

        setDriver('cf_s_elbo_R', 'location', 0, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.025')
        setDriver('cf_s_elbo_R', 'location', 2, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.025')

        setDriver('cf_s_elboback_L', 'location', 0, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.7')
        setDriver('cf_s_elboback_L', 'location', 2, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.6')

        setDriver('cf_s_elbo_L', 'location', 0, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '0.025')
        setDriver('cf_s_elbo_L', 'location', 2, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.025')

        #Set drivers for Shoulder joint correction bones
        setDriver('cf_d_shoulder02_R', 'rotation_quaternion', 3, 'Right arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '0.5', 'rotateNeg')
        setDriver('cf_d_shoulder02_R', 'location', 1, 'Right arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-0.1', 'moveNeg')

        setDriver('cf_d_shoulder02_R', 'location', 0, 'Right arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '0.1', 'moveABSNeg')
        setDriver('cf_d_shoulder02_R', 'location', 2, 'Right arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '-0.1')

        setDriver('cf_d_arm01_R', 'rotation_quaternion', 1, 'Right arm', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '0.7')

        setDriver('cf_d_shoulder02_L', 'rotation_quaternion', 3, 'Left arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '0.5', 'rotatePos')
        setDriver('cf_d_shoulder02_L', 'location', 1, 'Left arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '0.1', 'movePos')

        setDriver('cf_d_shoulder02_L', 'location', 0, 'Left arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '-0.1', 'moveABS')
        setDriver('cf_d_shoulder02_L', 'location', 2, 'Left arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '0.1')

        setDriver('cf_d_arm01_L', 'rotation_quaternion', 1, 'Left arm', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '-0.7')
        
    ################### Setup the hip drivers
def setup_hips():
    def makeHipXYZ (passedDriver, drivertarget):
        nameROT = [['xcomponent', 'ROT_X'] ,['ycomponent', 'ROT_Y'] , ['zcomponent', 'ROT_Z'], ['wcomponent', 'ROT_W']]
        index = [0, 1, 2, 3]    
        
        for i in index:
            var = passedDriver.driver.variables.new()
            var.name = nameROT[i][0]
            var.type = 'TRANSFORMS'
            target = var.targets[0]
            target.id = bpy.data.objects['Armature']
            target.bone_target = bpy.data.objects['Armature'].pose.bones[drivertarget].name
            target.transform_type = nameROT[i][1]
            target.transform_space = 'LOCAL_SPACE'
            target.rotation_mode = 'QUATERNION'

    def setLegDriver (bonetarget, drivertarget, xmult, ymult1, ymult2, zmult, rotatexmult1, rotatexmult2):
        bpy.ops.object.mode_set(mode='POSE')
        bone = bpy.data.objects['Armature'].pose.bones[bonetarget]
        targetbonelength = str(round((bpy.data.objects['Armature'].pose.bones[drivertarget].head - bpy.data.objects['Armature'].pose.bones[drivertarget].tail).length,2))
        
        driverx = bone.driver_add('location', 0)
        drivery = bone.driver_add('location', 1)
        driverz = bone.driver_add('location', 2)
        #rotatedriverx = bone.driver_add('rotation_quaternion', 1)
        #rotatedriverw = bone.driver_add('rotation_quaternion', 0)
        
        makeHipXYZ(driverx, drivertarget)
        makeHipXYZ(drivery, drivertarget)
        makeHipXYZ(driverz, drivertarget)
        #makeHipXYZ(rotatedriverx, drivertarget)
        #makeHipXYZ(rotatedriverw, bone.name)
        
        #define four states for leg rotation:
        #1) leg rotates up on x axis 90deg
        #2) leg rotates out to hand on y axis 90deg
        #3) leg rotates up on x axis 90deg, //and then// out on z axis 90deg
        #4) leg rotates out on y axis 90deg, //and then// forward on z axis 90deg
        
        if 'Right' in drivertarget:
            #only moves right/left in states 3 and 4
            #these are the only states where y and z are nonzero
            driverx.driver.expression = '-ycomponent*zcomponent*2.92'
            
            #moves upward in all four states
            #it comes out to roughly the same height for each state
            #disabled when leg is rotated backwards on the x axis
            drivery.driver.expression = '(1-wcomponent)*3 if xcomponent < 0 else 0'
            
            #only moves outward in state 1 or state 4
            #state 1 is the only state with a negative x component and zero z component
            #it should move more outward in state 1 vs state 4
            driverz.driver.expression = '1.15*((wcomponent*-ycomponent) + (wcomponent*-ycomponent)*(0.707-zcomponent)) + 1.414*(0.707-zcomponent)*(-xcomponent) if xcomponent<=0 else 0'#1.15*((wcomponent*-ycomponent) + (wcomponent*-ycomponent)*(0.707-zcomponent))'
  
            #only rotates in state 1
            #state 1 is the only state with a negative x component and zero z component
            #rotatedriverx.driver.expression = '-0.5*(0.707-zcomponent)*(-xcomponent) if xcomponent<=0 else 0'
            
            #Quaternion rotation needs to be "balanced", but blender doesn't appear to do this automatically when drivers are used
            #Sets W to square root of 1 - (x^2 + y^2 + z^2) using approximations
            #it's done this way to keep Blender's python security checker happy
            #rotatedriverw.driver.expression = 'log(2 - xcomponent*xcomponent - ycomponent*ycomponent - zcomponent*zcomponent,2)'
            
            #give the twist bone a copy rotation instead of that
            #this works well enough
            bone = bpy.data.objects['Armature'].pose.bones[bonetarget]
            bone.constraints.new("COPY_ROTATION")
            bone.constraints[0].target=bpy.data.objects['Armature']
            bone.constraints[0].subtarget=bpy.data.objects['Armature'].data.bones[drivertarget].name
            bone.constraints[0].influence=0.558
            bone.constraints[0].invert_z=True
            bone.constraints[0].target_space = 'LOCAL_WITH_PARENT'
            bone.constraints[0].owner_space = 'LOCAL_WITH_PARENT'
            
        #Left leg has different expressions
        else:
            driverx.driver.expression = 'ycomponent*zcomponent*2.92'
            drivery.driver.expression = '(1-wcomponent)*3 if xcomponent < 0 else 0'
            driverz.driver.expression = '1.15*((wcomponent*-ycomponent) + (wcomponent*-ycomponent)*(-0.707+zcomponent)) + 1.414*(0.707+zcomponent)*(-xcomponent) if xcomponent<=0 else 0'
            
            bone = bpy.data.objects['Armature'].pose.bones[bonetarget]
            bone.constraints.new("COPY_ROTATION")
            bone.constraints[0].target=bpy.data.objects['Armature']
            bone.constraints[0].subtarget=bpy.data.objects['Armature'].data.bones[drivertarget].name
            bone.constraints[0].influence=0.558
            bone.constraints[0].invert_z=True
            bone.constraints[0].target_space = 'LOCAL_WITH_PARENT'
            bone.constraints[0].owner_space = 'LOCAL_WITH_PARENT'
        
    setLegDriver('cf_d_thigh01_R', 'Right leg', '0.66',    '1', '1',    '0.6',    '0.5', '1')
    setLegDriver('cf_d_thigh01_L', 'Left leg', '-0.6',    '1', '1',    '0.6',    '0.5', '1')

    #Cf_D_Siri_L/R_Twist also has a unique driver expression for movement/rotation
    def setButtDriver (bonetarget, drivertarget, ymult1, ymult2, ymult3, zmult1, zmult2, xrotatemult1, xrotatemult2, zrotatemult1, zrotatemult2):
        
        bpy.ops.object.mode_set(mode='POSE')
        bone = bpy.data.objects['Armature'].pose.bones[bonetarget]
        targetbonelength = str(round((bpy.data.objects['Armature'].pose.bones[drivertarget].head - bpy.data.objects['Armature'].pose.bones[drivertarget].tail).length,2))
        
        drivery = bone.driver_add('location', 1)
        makeHipXYZ(drivery, drivertarget)

        drivery.driver.expression = '(1-wcomponent)*.5 if xcomponent < 0 else 0'
        
        bone = bpy.data.objects['Armature'].pose.bones[bonetarget]
        bone.constraints.new("COPY_ROTATION")
        bone.constraints[0].target=bpy.data.objects['Armature']
        bone.constraints[0].subtarget=bpy.data.objects['Armature'].data.bones[drivertarget].name
        bone.constraints[0].influence=0.4
        bone.constraints[0].use_y=False
        bone.constraints[0].invert_z=True
        bone.constraints[0].target_space = 'LOCAL_WITH_PARENT'
        bone.constraints[0].owner_space = 'LOCAL_WITH_PARENT'

    setButtDriver('cf_d_siri01_R', 'Right leg', '-0.05', '-0.06', '0.05',    '0.05', '-0.06',    '0.1', '0.5',    '0.2', '-0.2')
    setButtDriver('cf_d_siri01_L', 'Left leg',  '0.05', '0.06', '-0.05',    '0.05', '-0.06',    '0.1', '0.5',    '-0.2', '0.2')

    #give the waist a copy rotation as well
    def setWaistDriver(bonetarget, drivertarget):
        bone = bpy.data.objects['Armature'].pose.bones[bonetarget]
        const = bone.constraints.new("COPY_ROTATION")
        const.target=bpy.data.objects['Armature']
        const.subtarget=bpy.data.objects['Armature'].data.bones[drivertarget].name
        const.influence=0.1
        const.use_y=False
        const.use_z=False
        const.target_space = 'LOCAL_WITH_PARENT'
        const.owner_space = 'LOCAL_WITH_PARENT'
        
    setWaistDriver('cf_s_waist02', 'Left leg')
    setWaistDriver('cf_s_waist02', 'Right leg')

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
    copy.parent = armatureData.edit_bones['Head']
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

    if armature.pose.bones.get('Greybone'):
        eyeUV("Left Eye UV warp",  'cf_J_hitomi_tx_L') # this is Eyex for pmx
        eyeUV("Right Eye UV warp", 'cf_J_hitomi_tx_R')
    else:
        eyeUV("Left Eye UV warp",  'Eyex_L') # this is cf_J_hitomi_tx_L for grey
        eyeUV("Right Eye UV warp", 'Eyex_R')

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

        #make the Eyex_L vertex group active
        body.vertex_groups.active_index = body.vertex_groups['Eyex_L'].index #this is cf_J_hitomi_tx_L for grey

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
            bpy.ops.transform.resize(value=(scale, scale, scale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.683013, use_proportional_connected=False, use_proportional_projected=False)
        else:
            bpy.context.object.data.edit_bones[bone].tail=(bpy.context.object.data.edit_bones[bone].tail+bpy.context.object.data.edit_bones[bone].head)/2
            bpy.context.object.data.edit_bones[bone].tail=(bpy.context.object.data.edit_bones[bone].tail+bpy.context.object.data.edit_bones[bone].head)/2
            bpy.context.object.data.edit_bones[bone].tail=(bpy.context.object.data.edit_bones[bone].tail+bpy.context.object.data.edit_bones[bone].head)/2
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
    #move new bones to correct armature layers
    layer1 =    (True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
    layer2 =    (False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
    oneList = [
    'ToeRotator.L', 'HeelIK.L', 'MasterFootIK.L',
    'ToeRotator.R', 'HeelIK.R', 'MasterFootIK.R', 'Hips']
    
    for bone in oneList:
        bpy.ops.pose.select_all(action='DESELECT')
        armature.data.bones[bone].select = True
        bpy.ops.pose.bone_layers(layers=layer1)
    
    bpy.ops.pose.select_all(action='DESELECT')
    armature.data.bones['Eye Controller'].select = True
    armature.data.bones['cf_j_waist02'].select = True
    bpy.ops.pose.bone_layers(layers=layer2)
    
    armature.data.bones['cf_pv_root_upper'].hide = True
    armature.data.bones['cf_j_waist02'].hide = True
    
    #Add some bones to bone groups
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.ops.pose.group_add()
    group = armature.pose.bone_groups[len(armature.pose.bone_groups)-1]
    group.name = 'IK controllers'
    armature.data.bones['cf_pv_hand_L'].select = True
    armature.data.bones['cf_pv_hand_R'].select = True
    armature.data.bones['cf_pv_foot_R'].select = True
    armature.data.bones['cf_pv_foot_L'].select = True
    bpy.ops.pose.group_assign(type=1)
    group.color_set = 'THEME01'
    
    bpy.ops.pose.select_all(action='DESELECT')
    bpy.ops.pose.group_add()
    group = armature.pose.bone_groups[len(armature.pose.bone_groups)-1]
    group.name = 'IK poles'
    armature.pose.bone_groups.active_index = 1
    armature.data.bones['cf_pv_elbo_R'].select = True
    armature.data.bones['cf_pv_elbo_L'].select = True
    armature.data.bones['cf_pv_knee_R'].select = True
    armature.data.bones['cf_pv_knee_L'].select = True
    bpy.ops.pose.group_assign(type=1)
    group.color_set = 'THEME09'
 
    bpy.ops.object.mode_set(mode='OBJECT')

class bone_drivers(bpy.types.Operator):
    bl_idname = "kkb.bonedrivers"
    bl_label = "Bone Driver script"
    bl_description = "Add IKs, joint drivers and an eye bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        #The hip joint corrections aren't finished yet.
        #Enable debug mode to use them in their current state.
        scene = context.scene.placeholder
        use_hips = scene.driver_bool
        
        reparent_bones()
        setup_iks()
        setup_joints()
        #if use_hips:
        #    setup_hips()
        make_eye_controller()
        scale_final_bones()
        categorize_bones()
        
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(bone_drivers)

    # test call
    print((bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT')))
