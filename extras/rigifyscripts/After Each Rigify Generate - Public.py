
#Switch to Object Mode and select Generated Rig

import bpy
import traceback
import sys
    
def main():
    koikatsuCommonsName = "Koikatsu Commons.py";
    """
    koikatsuCommonsPath = "C:\\Users\\UserName\\Desktop\\"

    text = bpy.data.texts.get(koikatsuCommonsName)
    if text is not None:
        bpy.data.texts.remove(text)
    text = bpy.data.texts.load(koikatsuCommonsPath + koikatsuCommonsName)
    koikatsuCommons = text.as_module()
    """
    koikatsuCommons = bpy.data.texts[koikatsuCommonsName].as_module()

    generatedRig = bpy.context.active_object

    assert generatedRig.mode == "OBJECT", 'assert generated_rig.mode == "OBJECT"'
    assert generatedRig.type == "ARMATURE", 'assert generatedRig.type == "ARMATURE"'

    bpy.ops.object.mode_set(mode='EDIT')

    for bone in generatedRig.data.edit_bones:
        if generatedRig.data.bones[bone.name].layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.junkLayerName)] == True:
            koikatsuCommons.deleteBone(generatedRig, bone.name)
            continue
        if generatedRig.data.bones[bone.name].layers[koikatsuCommons.defLayerIndex] == True:
            bone.use_deform = True

    bpy.ops.object.mode_set(mode='OBJECT')

    """
    for i in range(32):
        if i == 0 or i == 1:
            generatedRig.data.layers[i] = True
        else:
            generatedRig.data.layers[i] = False
    """

    body = bpy.data.objects[koikatsuCommons.bodyName]
    leftEyeModifier = body.modifiers["Left Eye UV warp"]
    leftEyeModifier.object_from = generatedRig
    leftEyeModifier.bone_from = koikatsuCommons.eyesXBoneName
    leftEyeModifier.object_to = generatedRig
    leftEyeModifier.bone_to = koikatsuCommons.leftEyeBoneName
    rightEyeModifier = body.modifiers["Right Eye UV warp"]
    rightEyeModifier.object_from = generatedRig
    rightEyeModifier.bone_from = koikatsuCommons.eyesXBoneName
    rightEyeModifier.object_to = generatedRig
    rightEyeModifier.bone_to = koikatsuCommons.rightEyeBoneName

    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.headTweakBoneName, 1.1)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.crotchBoneName, 25)
    koikatsuCommons.setBoneCustomShapeScale(generatedRig, koikatsuCommons.anusBoneName, 3.5)
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
    
    for driver in generatedRig.animation_data.drivers:    
        #print(driver.data_path)
        #print(driver.driver.variables[0].targets[0].bone_target)
        if driver.data_path.startswith("pose.bones"):
            ownerName = driver.data_path.split('"')[1]
            property = driver.data_path.rsplit('.', 1)[1]
            if ownerName in koikatsuCommons.bonesWithDrivers and property == "location":
                for variable in driver.driver.variables:
                    for target in variable.targets:
                        for targetToChange in koikatsuCommons.targetsToChange:
                            if target.bone_target == koikatsuCommons.originalBonePrefix + targetToChange:
                                target.bone_target = koikatsuCommons.deformBonePrefix + targetToChange
                                
    #koikatsuCommons.setBoneManagerLayersFromRigifyLayers(generatedRig)

try:
    main()
    print("\nSuccess\n")
except Exception as ex:
    return_value = "ERROR!"
    print(traceback.format_exc(), file=sys.stderr)
    print("Failure\n")
    