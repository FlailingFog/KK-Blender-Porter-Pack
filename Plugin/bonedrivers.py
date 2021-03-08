'''
AFTER CATS (BONE DRIVERS) SCRIPT
- Adds IKs to the arms and legs using the "Pv" bones
- Moves the Knee and Elbow IKs a little closer to the body
- Adds drivers for twist / joint correction bones for the arms, hands, legs and butt
- Adds an "Eye Controller" bone to the top of the head and UV warp modifiers on the Body object to make the eyes work
Usage:
- Make sure the Fix Model button has already been used in CATS
- Make sure the After CATS (Clean Armature) script has been run
- Run the script
'''

import bpy

class bone_drivers(bpy.types.Operator):
    bl_idname = "kkb.bonedrivers"
    bl_label = "Bone Driver script"
    bl_description = "Add IKs, joint drivers and an eye bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):

        #The hip joint corrections aren't finished yet.
        #Set the useHips variable to True to use them in their current state. 
        useHips = False

        ################### Start script

        import bpy

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
        bpy.data.objects['Armature'].select_set(True)
        bpy.context.view_layer.objects.active=bpy.data.objects['Armature']

        ################### Setup all IKs

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
            
            bone.head.x = bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.x
            bone.tail.x = bone.head.x

            #unparent the bone
            bone.parent = None

        #Run for each side
        legIK('Right knee', 'Cf_Pv_Foot_R', 'Cf_Pv_Knee_R', -1.571, 'Cf_Pv_Foot_R', 'Right knee', 'ToeTipIK_R')
        legIK('Left knee',  'Cf_Pv_Foot_L', 'Cf_Pv_Knee_L', -1.571, 'Cf_Pv_Foot_L', 'Left knee', 'ToeTipIK_L')

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
            bpy.data.objects['Armature'].pose.bones[footIK].lock_rotation[1] = True
            bpy.data.objects['Armature'].pose.bones[footIK].lock_rotation[2] = True

            #parent the toe tip bone to the foot IK bone
            bpy.data.objects['Armature'].data.edit_bones[toeIK].parent = bpy.data.objects['Armature'].data.edit_bones[footIK]

            # move knee IKs closer to body
            kneedist = round((bpy.data.objects['Armature'].pose.bones[footbone].head - bpy.data.objects['Armature'].pose.bones[footbone].tail).length,2)
            bpy.data.objects['Armature'].data.edit_bones[kneebone].head.y = kneedist * -5
            bpy.data.objects['Armature'].data.edit_bones[kneebone].tail.y = kneedist * -5

            # make toe bone shorter
            bpy.data.objects['Armature'].data.edit_bones[toebone].tail.z = bpy.data.objects['Armature'].data.edit_bones[legbone].head.z * 0.2   
            
            #hide the toeTipIK bones for now
            bpy.ops.object.mode_set(mode='POSE')
            bpy.data.objects['Armature'].data.bones[toeIK].hide = True
            bpy.ops.object.mode_set(mode='EDIT')

        #Run for each side
        footIK('Right ankle', 'Right toe', 'ToeTipIK_R', 'Cf_Pv_Foot_R', 'Cf_Pv_Knee_R', 'Right knee')
        footIK('Left ankle',  'Left toe',  'ToeTipIK_L', 'Cf_Pv_Foot_L', 'Cf_Pv_Knee_L', 'Left knee')

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
            bone.constraints[0].target=bpy.data.objects['Armature']
            bone.constraints[0].subtarget=bpy.data.objects['Armature'].data.bones[handcontroller].name

            bpy.ops.object.mode_set(mode='POSE')
            bpy.data.objects['Armature'].data.bones[wristbone].hide = True
            bpy.ops.object.mode_set(mode='EDIT')

            # move elbow IKs closer to body
            elbowdist = round((bpy.data.objects['Armature'].pose.bones[elbowbone].head - bpy.data.objects['Armature'].pose.bones[elbowbone].tail).length,2)
            bpy.data.objects['Armature'].data.edit_bones[elbowcontroller].head.y = elbowdist*2
            bpy.data.objects['Armature'].data.edit_bones[elbowcontroller].tail.y = elbowdist*2

        #Run for each side
        armhandIK('Right elbow', 'Cf_Pv_Hand_R', 'Cf_Pv_Elbo_R', 0, 'Right wrist')
        armhandIK('Left elbow',  'Cf_Pv_Hand_L', 'Cf_Pv_Elbo_L', 180, 'Left wrist')

        ################### Setup joint correction drivers

        #make the kokan bone shorter
        bpy.data.objects['Armature'].data.edit_bones['Kokan'].tail.z = bpy.data.objects['Armature'].data.edit_bones['Waist02_Twist'].head.z

        #generic function for creating a driver
        def setDriver (bonetarget, drivertype, drivertypeselect, drivertarget, drivertt, driverts, driverrm, drivermult, expresstype = 'move'):
            bpy.ops.object.mode_set(mode='POSE')

            #select bone to add driver to
            bone=bpy.data.objects['Armature'].pose.bones[bonetarget]

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
        setDriver('KneeB_R_Twist', 'location', 1, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.45')
        setDriver('KneeB_R_Twist', 'location', 2, 'Right knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.23')

        setDriver('KneeB_L_Twist', 'location', 1, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.45')
        setDriver('KneeB_L_Twist', 'location', 2, 'Left knee', 'ROT_X', 'LOCAL_SPACE', 'AUTO', '-0.23')

        #Set drivers for hand joint correction bones
        setDriver('Cf_D_Hand_R_Twist', 'location', 0, 'Right wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-2')
        setDriver('Cf_D_Hand_R_Twist', 'location', 1, 'Right wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-2')
        setDriver('Cf_D_Hand_R_Twist', 'location', 2, 'Right wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '1')

        setDriver('Cf_D_Hand_L_Twist', 'location', 0, 'Left wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-2')
        setDriver('Cf_D_Hand_L_Twist', 'location', 1, 'Left wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '2')
        setDriver('Cf_D_Hand_L_Twist', 'location', 2, 'Left wrist', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-1')

        #Set drivers for Elbow joint correction  bones
        setDriver('Elboback_R_Twist', 'location', 0, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.7')
        setDriver('Elboback_R_Twist', 'location', 2, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '0.6')

        setDriver('Elbo_R_Twist', 'location', 0, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '0.05')
        setDriver('Elbo_R_Twist', 'location', 2, 'Right elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '0.05')

        setDriver('Elboback_L_Twist', 'location', 0, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.7')
        setDriver('Elboback_L_Twist', 'location', 2, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.6')

        setDriver('Elbo_L_Twist', 'location', 0, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '0.05')
        setDriver('Elbo_L_Twist', 'location', 2, 'Left elbow', 'ROT_Z', 'LOCAL_SPACE', 'AUTO', '-0.05')

        #Set drivers for Shoulder joint correction bones
        setDriver('Shoulder02_R_Twist', 'rotation_quaternion', 3, 'Right arm', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '-0.5', 'rotatePos')
        setDriver('Shoulder02_R_Twist', 'location', 1, 'Right arm', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '0.1', 'movePos')

        setDriver('Shoulder02_R_Twist', 'location', 0, 'Right arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '0.1', 'moveABSNeg')
        setDriver('Shoulder02_R_Twist', 'location', 2, 'Right arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-0.1')

        setDriver('Arm01_R_Twist', 'rotation_quaternion', 1, 'Right arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '0.7')

        setDriver('Shoulder02_L_Twist', 'rotation_quaternion', 3, 'Left arm', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '0.5', 'rotatePos')
        setDriver('Shoulder02_L_Twist', 'location', 1, 'Left arm', 'ROT_X', 'LOCAL_SPACE', 'QUATERNION', '0.1', 'movePos')

        setDriver('Shoulder02_L_Twist', 'location', 0, 'Left arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-0.1', 'moveABS')
        setDriver('Shoulder02_L_Twist', 'location', 2, 'Left arm', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '0.1')

        setDriver('Arm01_L_Twist', 'rotation_quaternion', 1, 'Left arm', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '-0.7')

        ################### Setup the hip drivers

        if useHips:
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
                rotatedriverx = bone.driver_add('rotation_quaternion', 1)
                rotatedriverw = bone.driver_add('rotation_quaternion', 0)
                
                makeHipXYZ(driverx, drivertarget)
                makeHipXYZ(drivery, drivertarget)
                makeHipXYZ(driverz, drivertarget)
                makeHipXYZ(rotatedriverx, drivertarget)
                makeHipXYZ(rotatedriverw, bone.name)
                
                if 'Right' in drivertarget:
                    driverx.driver.expression = 'zcomponent*' + targetbonelength + '*' + xmult + '+ycomponent*2*' + xmult + ' if zcomponent > 0 else 0'
                    
                    drivery.driver.expression = '(1-ycomponent)*(1-wcomponent)*(3 - xcomponent*' + targetbonelength + '*' + ymult1 + '*ycomponent if xcomponent < 0 else 0) if ycomponent >= 0 else (1-ycomponent)*(1-wcomponent)*(3 - zcomponent*' + targetbonelength + '*-ycomponent*' + ymult2 + ')'
                    
                    driverz.driver.expression = '(1-ycomponent)*(1-wcomponent)*(3 - xcomponent*' + targetbonelength + '*' + zmult + '*ycomponent if xcomponent < 0 else 0) if ycomponent >= 0 else (1-ycomponent)*(1-wcomponent)*(3 - xcomponent*' + targetbonelength + '*ycomponent*' + zmult + ')'
                    
                    #this rotates but skips around
                    rotatedriverx.driver.expression = '(xcomponent*' + targetbonelength + '*' + rotatexmult1 + ' if xcomponent < 0 else 0)' + 'if abs(xcomponent)' + '>' +  'abs(ycomponent) else ycomponent*' + targetbonelength + '*' + rotatexmult2
                
                    #Quaternion rotation needs to be "balanced", but blender doesn't appear to do this automatically when drivers are used
                    #Sets W to square root of 1 - (x^2 + y^2 + z^2) using approximations (sort of similar to the quake 3 method)
                    #it's done this way to keep Blender's python security checker happy
                    rotatedriverw.driver.expression = 'log(2 - xcomponent*xcomponent - ycomponent*ycomponent - zcomponent*zcomponent,2)'
                    
                #Left leg has different expressions
                else:
                    driverx.driver.expression = '-zcomponent*' + targetbonelength + '*' + xmult + '+ycomponent*2*' + xmult + ' if zcomponent > 0 else 0'
                    
                    drivery.driver.expression = '(xcomponent*' + targetbonelength + '*' + ymult1 + '-ycomponent*' + ymult2 + ' if xcomponent < 0 else 0)' + 'if abs(xcomponent)' + '>' +  'abs(zcomponent) else -zcomponent*' + targetbonelength + '*' + ymult2
                    
                    driverz.driver.expression = 'xcomponent*' + targetbonelength + '*' + zmult + ' if xcomponent < 0 and ycomponent < 0 else 0'

                    rotatedriverx.driver.expression = '(xcomponent*' + targetbonelength + '*' + rotatexmult1 + ' if xcomponent < 0 else 0)' + 'if abs(xcomponent)' + '>' +  'abs(ycomponent) else ycomponent*' + targetbonelength + '*' + rotatexmult2
                    
                    #Sets W to square root of 1 - (x^2 + y^2 + z^2) using approximations
                    #it's done this way to keep Blender's python security checker happy
                    rotatedriverw.driver.expression = 'log(2 - xcomponent*xcomponent - ycomponent*ycomponent - zcomponent*zcomponent,2)'
                
            setLegDriver('Leg_R_Twist', 'Right leg', '-0.3',    '1', '1',    '0.6',    '0.5', '1')
            setDriver('Leg_R_Twist', 'rotation_quaternion', 3, 'Right leg', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-0.6', 'rotate')
            setDriver('Leg_R_Twist', 'rotation_quaternion', 2, 'Right leg', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '-0.6', 'rotatePos')

            setLegDriver('Leg_L_Twist', 'Left leg', '-0.3',    '1', '1',    '0.6',    '0.5', '1')
            setDriver('Leg_L_Twist', 'rotation_quaternion', 3, 'Left leg', 'ROT_Z', 'LOCAL_SPACE', 'QUATERNION', '-0.6', 'rotate')
            setDriver('Leg_L_Twist', 'rotation_quaternion', 2, 'Left leg', 'ROT_Y', 'LOCAL_SPACE', 'QUATERNION', '-0.6', 'rotateNeg')

            #Cf_D_Siri_L/R_Twist also has a unique driver expression for movement/rotation
            def setButtDriver (bonetarget, drivertarget, ymult1, ymult2, ymult3, zmult1, zmult2, xrotatemult1, xrotatemult2, zrotatemult1, zrotatemult2):
                
                bpy.ops.object.mode_set(mode='POSE')
                bone = bpy.data.objects['Armature'].pose.bones[bonetarget]
                targetbonelength = str(round((bpy.data.objects['Armature'].pose.bones[drivertarget].head - bpy.data.objects['Armature'].pose.bones[drivertarget].tail).length,2))
                
                drivery = bone.driver_add('location', 1)
                driverz = bone.driver_add('location', 2)
                
                makeHipXYZ(drivery, drivertarget)
                makeHipXYZ(driverz, drivertarget)

                drivery.driver.expression = '(xcomponent*' + targetbonelength + '*' + ymult1 + '+ycomponent*' + ymult3 + ' if xcomponent < 0 else 0)' + 'if abs(xcomponent)' + '>' +  'abs(zcomponent) else zcomponent*' + targetbonelength + '*' + ymult2
                
                driverz.driver.expression = '(xcomponent*' + targetbonelength + '*' + zmult1 + ' if xcomponent < 0 else 0)' + 'if abs(xcomponent)' + '>' +  'abs(zcomponent) else zcomponent*' + targetbonelength + '*' + zmult2
                
                rotatedriverx = bone.driver_add('rotation_quaternion', 1)
                rotatedriverz = bone.driver_add('rotation_quaternion', 3)
                rotatedriverw = bone.driver_add('rotation_quaternion', 0)
                makeHipXYZ(rotatedriverx, drivertarget)
                makeHipXYZ(rotatedriverz, drivertarget)
                makeHipXYZ(rotatedriverw, bonetarget)
                
                rotatedriverx.driver.expression = 'xcomponent*' + targetbonelength + '*' + xrotatemult1 + ' if xcomponent < 0 else xcomponent*' + targetbonelength + '*' + xrotatemult2
                
                rotatedriverz.driver.expression = '(xcomponent*' + targetbonelength + '*' + zrotatemult1 + ' if xcomponent < 0 else 0)' + 'if abs(xcomponent)' + '>' +  'abs(zcomponent) else zcomponent*' + targetbonelength + '*' + zrotatemult2
                
                rotatedriverw.driver.expression = 'log(2 - xcomponent*xcomponent - ycomponent*ycomponent - zcomponent*zcomponent,2)'

            #these rotate but they skip around
            setButtDriver('Cf_D_Siri_R_Twist', 'Right leg', '-0.05', '-0.06', '0.05',    '0.05', '-0.06',    '0.1', '0.5',    '0.2', '-0.2')
            setButtDriver('Cf_D_Siri_L_Twist', 'Left leg',  '0.05', '0.06', '-0.05',    '0.05', '-0.06',    '0.1', '0.5',    '-0.2', '0.2')

        # Tilt the bust bone and make it smaller
        bpy.ops.object.mode_set(mode='EDIT')
        bone = bpy.data.objects['Armature'].data.edit_bones['Cf_D_Bust00']
        bone.tail.y = bpy.data.objects['Armature'].data.edit_bones['AH1_R'].head.y * 2
        bone.tail.z = bpy.data.objects['Armature'].data.edit_bones['AH1_R'].head.z
        bpy.ops.object.mode_set(mode='POSE')

        ################### Make an eye controller

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

        ################### Empty group check

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
                    
        return {'FINISHED'}


