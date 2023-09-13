
#Switch to Object Mode and select Generated Rig

import bpy
import traceback
import sys
import math
from math import radians
from . import commons as koikatsuCommons
    
def main():		   
    generatedRig = bpy.context.active_object

    assert generatedRig.mode == "OBJECT", 'assert generated_rig.mode == "OBJECT"'
    assert generatedRig.type == "ARMATURE", 'assert generatedRig.type == "ARMATURE"'
    
    generatedRig.show_in_front = True
    generatedRig.display_type = 'TEXTURED'

    """
    for i in range(32):
        if i == 0 or i == 1:
            generatedRig.data.layers[i] = True
        else:
            generatedRig.data.layers[i] = False
    """
    
    hasRiggedTongue = generatedRig.pose.bones.get(koikatsuCommons.riggedTongueBone1Name)
    hasBetterPenetrationMod = generatedRig.pose.bones.get(koikatsuCommons.betterPenetrationRootCrotchBoneName)
    
    metarig = None
    for bone in generatedRig.pose.bones:
        if bone.name.startswith(koikatsuCommons.metarigIdBonePrefix):
            generatedRigIdBoneName = bone.name
            for object in bpy.data.objects:
                if object != generatedRig and object.type == "ARMATURE":
                    for objectBone in object.pose.bones:
                        if objectBone.name == generatedRigIdBoneName:
                            metarig = object
                            break
            break
                        
    if metarig:
        metarig.hide_set(True)
        for object in bpy.data.objects:
            if object.type == "MESH":
                if object.parent == metarig:
                    object.parent = generatedRig
                for modifier in object.modifiers:
                    if modifier.type == "ARMATURE" and modifier.object == metarig:
                        modifier.object = generatedRig
                    if modifier.type == "UV_WARP" and modifier.object_from == metarig:
                        if modifier.name == "Left Eye UV warp":
                            modifier.object_from = generatedRig
                            modifier.bone_from = koikatsuCommons.eyesXBoneName
                            modifier.object_to = generatedRig
                            modifier.bone_to = koikatsuCommons.leftEyeBoneName
                        elif modifier.name == "Right Eye UV warp":
                            modifier.object_from = generatedRig
                            modifier.bone_from = koikatsuCommons.eyesXBoneName
                            modifier.object_to = generatedRig
                            modifier.bone_to = koikatsuCommons.rightEyeBoneName

    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.eyesTrackTargetBoneName, 1.5)
    if hasRiggedTongue:
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.riggedTongueLeftBone3Name, 0.25)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.riggedTongueRightBone3Name, 0.25)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.riggedTongueLeftBone4Name, 0.25)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.riggedTongueRightBone4Name, 0.25)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.riggedTongueLeftBone5Name, 0.25)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.riggedTongueRightBone5Name, 0.25)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.headTweakBoneName, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.crotchBoneName, 2)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.anusBoneName, 0.25)
    if hasBetterPenetrationMod:
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationRootCrotchBoneName, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationFrontCrotchBoneName, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationLeftCrotchBone1Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationRightCrotchBone1Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationLeftCrotchBone2Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationRightCrotchBone2Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationLeftCrotchBone3Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationRightCrotchBone3Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationLeftCrotchBone4Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationRightCrotchBone4Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationLeftCrotchBone5Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationRightCrotchBone5Name, 0.09)
        koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.betterPenetrationBackCrotchBoneName, 0.09)    
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftBreastDeformBone1Name, 0.4)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightBreastDeformBone1Name, 0.4)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftBreastBone2Name, 3)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightBreastBone2Name, 3)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftBreastDeformBone2Name, 0.3)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightBreastDeformBone2Name, 0.3)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftBreastBone3Name, 2)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightBreastBone3Name, 2)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftBreastDeformBone3Name, 0.2)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightBreastDeformBone3Name, 0.2)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftNippleBone1Name, 1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightNippleBone1Name, 1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftNippleDeformBone1Name, 0.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightNippleDeformBone1Name, 0.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftNippleBone2Name, 0.5)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightNippleBone2Name, 0.5)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftNippleDeformBone2Name, 0.05)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightNippleDeformBone2Name, 0.05)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftShoulderBoneName, 1.25)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightShoulderBoneName, 1.25)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftThumbBone1Name, 1.3)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightThumbBone1Name, 1.3)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftThumbBone2Name, 1.3)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightThumbBone2Name, 1.3)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftThumbBone3Name, 1.2)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightThumbBone3Name, 1.2)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftIndexFingerBone2Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightIndexFingerBone2Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftIndexFingerBone3Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightIndexFingerBone3Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftMiddleFingerBone2Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightMiddleFingerBone2Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftMiddleFingerBone3Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightMiddleFingerBone3Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftRingFingerBone2Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightRingFingerBone2Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftRingFingerBone3Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightRingFingerBone3Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftLittleFingerPalmBoneName, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightLittleFingerPalmBoneName, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftLittleFingerPalmFkBoneName, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightLittleFingerPalmFkBoneName, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftLittleFingerBone2Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightLittleFingerBone2Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.leftLittleFingerBone3Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rightLittleFingerBone3Name, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.rootBoneName, 0.35)
    
    for bone in generatedRig.pose.bones:
        if generatedRig.data.bones[bone.name].layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.faceLayerName + koikatsuCommons.mchLayerSuffix)] == True:
            koikatsuCommons.setBoneCustomShapeScale(generatedRig, bone.name, 0.15)
        
    headBone = generatedRig.pose.bones[koikatsuCommons.originalBonePrefix + koikatsuCommons.headBoneName]
    koikatsuCommons.changeConstraintIndex(generatedRig, headBone.name, koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.headConstraintSuffix + koikatsuCommons.rotationConstraintSuffix, len(headBone.constraints) - 1)
    koikatsuCommons.changeConstraintIndex(generatedRig, headBone.name, koikatsuCommons.limitRotationConstraintBaseName + koikatsuCommons.headConstraintSuffix, len(headBone.constraints) - 1)
    
    headTweakLimitRotationConstraint = koikatsuCommons.addLimitRotationConstraint(generatedRig, koikatsuCommons.headTweakBoneName, None, 'LOCAL', koikatsuCommons.limitRotationConstraintBaseName + koikatsuCommons.headConstraintSuffix, 
    True, math.radians(-180), math.radians(180), True, math.radians(-180), math.radians(180), True, math.radians(-180), math.radians(180))
    
    for driver in generatedRig.animation_data.drivers:
        if driver.data_path.startswith("pose.bones"):
            driverOwnerName = driver.data_path.split('"')[1]
            driverProperty = driver.data_path.rsplit('.', 1)[1]
            if driverOwnerName == headBone.name:
                constraintName = driver.data_path.split('"')[3]
                if constraintName == koikatsuCommons.limitRotationConstraintBaseName + koikatsuCommons.headConstraintSuffix:
                    variable = driver.driver.variables[0]
                    newVariable = koikatsuCommons.DriverVariable(variable.name, variable.type, generatedRig, variable.targets[0].bone_target, None, None, None, None, variable.targets[0].data_path, None, None)
																  
																																																				  
                    koikatsuCommons.addDriver(headTweakLimitRotationConstraint, driverProperty, None, driver.driver.type, [newVariable], 
                    driver.driver.expression)
        
    for bone in generatedRig.pose.bones:
        for constraint in bone.constraints:
            if constraint.type == 'ARMATURE':
                for target in constraint.targets:
                    if target.subtarget:
                        target.target = generatedRig
                        if target.subtarget.endswith(koikatsuCommons.placeholderBoneSuffix):
                            target.subtarget = target.subtarget[:-len(koikatsuCommons.placeholderBoneSuffix)]
    
    for driver in bpy.data.objects[koikatsuCommons.bodyName].data.shape_keys.animation_data.drivers:
        if driver.data_path.startswith("key_blocks"):
            ownerName = driver.data_path.split('"')[1]
            if ownerName == koikatsuCommons.eyelidsShapeKeyCopyName:
                for variable in driver.driver.variables:
                    for target in variable.targets:
                        if target.id == metarig:
                            target.id = generatedRig 
    
    for driver in generatedRig.animation_data.drivers:    
        #print(driver.data_path)
        #print(driver.driver.variables[0].targets[0].bone_target)
        if driver.data_path.startswith("pose.bones"):
            driverOwnerName = driver.data_path.split('"')[1]
            driverProperty = driver.data_path.rsplit('.', 1)[1]
            if driverOwnerName in koikatsuCommons.bonesWithDrivers and driverProperty == "location":
                for variable in driver.driver.variables:
                    for target in variable.targets:
                        for targetToChange in koikatsuCommons.targetsToChange:
                            if target.bone_target == koikatsuCommons.originalBonePrefix + targetToChange:
                                target.bone_target = koikatsuCommons.deformBonePrefix + targetToChange
                                
    bpy.ops.object.mode_set(mode='EDIT')

    for bone in generatedRig.data.edit_bones:
        if generatedRig.data.bones[bone.name].layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.junkLayerName)] == True:
            koikatsuCommons.deleteBone(generatedRig, bone.name)
            continue
        if generatedRig.data.bones[bone.name].layers[koikatsuCommons.defLayerIndex] == True:
            bone.use_deform = True
            
    generatedRig.data.edit_bones[koikatsuCommons.eyesTrackTargetParentBoneName].parent = None
    generatedRig.data.edit_bones[koikatsuCommons.headTrackTargetParentBoneName].parent = None
    
    bpy.ops.object.mode_set(mode='OBJECT')
        
    #koikatsuCommons.setBoneManagerLayersFromRigifyLayers(generatedRig)

class rigify_after(bpy.types.Operator):
    bl_idname = "kkbp.rigafter"
    bl_label = "After Each Rigify Generate - Public"
    bl_description = 'Performs cleanup after a Rigify generation'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main()
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(rigify_after)

    # test call
    print((bpy.ops.kkbp.rigafter('INVOKE_DEFAULT')))   