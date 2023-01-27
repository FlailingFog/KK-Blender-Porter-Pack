
#Switch to Object Mode and select Generated Rig

import bpy
import traceback
import sys
from . import commons as koikatsuCommons

def main():
    generatedRig = bpy.context.active_object

    assert generatedRig.mode == "OBJECT", 'assert generated_rig.mode == "OBJECT"'
    assert generatedRig.type == "ARMATURE", 'assert generatedRig.type == "ARMATURE"'
    
    generatedRig.show_in_front = True
    generatedRig.display_type = 'TEXTURED'

    bpy.ops.object.mode_set(mode='EDIT')

    for bone in generatedRig.data.edit_bones:
        if generatedRig.data.bones[bone.name].layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.junkLayerName)] == True:
            koikatsuCommons.deleteBone(generatedRig, bone.name)
            continue
        if generatedRig.data.bones[bone.name].layers[koikatsuCommons.defLayerIndex] == True:
            bone.use_deform = True
            
    generatedRig.data.edit_bones[koikatsuCommons.eyesTrackTargetParentBoneName].parent = None

    bpy.ops.object.mode_set(mode='OBJECT')

    """
    for i in range(32):
        if i == 0 or i == 1:
            generatedRig.data.layers[i] = True
        else:
            generatedRig.data.layers[i] = False
    """
    
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
    
    """
    bpy.ops.object.mode_set(mode='EDIT')
    
    sourceBoneNameAndBoneWidgetHolderNameTuples = []
    
    def createOffsetBoneWidgetHolder(rig, sourceBoneName, vertexGroupExtremities, xFactor, yFactor, zFactor):
        boneWidgetHolderName = koikatsuCommons.getBoneWidgetHolderName(sourceBoneName)
        boneWidgetHolder = koikatsuCommons.copyBone(rig, sourceBoneName, boneWidgetHolderName)
        sourceBone = rig.data.edit_bones.get(sourceBoneName)
        if xFactor is not None:
            vertexGroupPosX = (vertexGroupExtremities.maxX - vertexGroupExtremities.minX) * xFactor + vertexGroupExtremities.minX
            boneWidgetHolder.head.x = vertexGroupPosX
        else:
            boneWidgetHolder.head.x = sourceBone.head.x
        if yFactor is not None:
            vertexGroupPosY = (vertexGroupExtremities.maxY - vertexGroupExtremities.minY) * yFactor + vertexGroupExtremities.minY
            boneWidgetHolder.head.y = vertexGroupPosY
        else:
            boneWidgetHolder.head.y = sourceBone.head.y
        if zFactor is not None:
            vertexGroupPosZ = (vertexGroupExtremities.maxZ - vertexGroupExtremities.minZ) * zFactor + vertexGroupExtremities.minZ
            boneWidgetHolder.head.z = vertexGroupPosZ
        else:
            boneWidgetHolder.head.z = sourceBone.head.z
        boneWidgetHolder.tail = sourceBone.tail - (sourceBone.head - boneWidgetHolder.head)    
        boneWidgetHolder.roll = sourceBone.roll
        sourceBoneNameAndBoneWidgetHolderNameTuples.append((sourceBoneName, boneWidgetHolderName))                 
        return boneWidgetHolder
    
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftShoulderBoneName, koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.originalShoulderDeformBoneName, koikatsuCommons.bodyName), 0.1, 0.6, 0.66)
    armDeformBone1Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.armDeformBone1Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.armTweakBone1Name, armDeformBone1Extremities, 0.33, None, None)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.armParentBoneName, armDeformBone1Extremities, 0.33, None, None)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.armIkBoneName, armDeformBone1Extremities, 0.33, None, None)
    wristDeformBoneExtremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.wristDeformBoneName, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.wristFkBoneName, wristDeformBoneExtremities, None, 0.57, 0.53)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.wristIkBoneName, wristDeformBoneExtremities, None, 0.57, 0.53)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.wristTweakBoneName, wristDeformBoneExtremities, None, 0.57, 0.53)
    thumbDeformBone1Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.thumbDeformBone1Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftThumbBo1Name, thumbDeformBone1Extremities, 0.15, 0.55, 0.5)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.thumbMasterBoneName, thumbDeformBone1Extremities, 0.15, 0.55, 0.5)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftThumbBo2Name, koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.thumbDeformBone2Name, koikatsuCommons.bodyName), 0.42, 0.47, 0.3)
    thumbDeformBone3Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.thumbDeformBone3Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftThumbBo3Name, thumbDeformBone3Extremities, 0.3, 0.6, 0.55)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.thumbTweakBoneName, thumbDeformBone3Extremities, 0.97, 0.03, 0.35)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.thumbIkBoneName, thumbDeformBone3Extremities, 0.97, 0.03, 0.35)
    leftIndexFingerDeformBone1Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftIndexFingerDeformBone1Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftIndexFingerBone1Name, leftIndexFingerDeformBone1Extremities, None, 0.5, 0.4)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftIndexFingerMasterBoneName, leftIndexFingerDeformBone1Extremities, None, 0.5, 0.4)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftIndexFingerBone2Name, koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftIndexFingerDeformBone2Name, koikatsuCommons.bodyName), None, 0.45, 0.47)
    leftIndexFingerDeformBone3Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftIndexFingerDeformBone3Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftIndexFingerTweakBoneName, leftIndexFingerDeformBone3Extremities, 1, None, 0.6)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftIndexFingerIkBoneName, leftIndexFingerDeformBone3Extremities, 1, None, 0.6)
    leftMiddleFingerDeformBone1Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftMiddleFingerDeformBone1Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftMiddleFingerBone1Name, leftMiddleFingerDeformBone1Extremities, None, None, 0.4)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftMiddleFingerMasterBoneName, leftMiddleFingerDeformBone1Extremities, None, None, 0.4)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftMiddleFingerBone2Name, koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftMiddleFingerDeformBone2Name, koikatsuCommons.bodyName), None, None, 0.5)
    leftMiddleFingerDeformBone3Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftMiddleFingerDeformBone3Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftMiddleFingerTweakBoneName, leftMiddleFingerDeformBone3Extremities, 1, None, 0.6)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftMiddleFingerIkBoneName, leftMiddleFingerDeformBone3Extremities, 1, None, 0.6)
    leftRingFingerDeformBone1Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftRingFingerDeformBone1Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftRingFingerBone1Name, leftRingFingerDeformBone1Extremities, None, None, 0.45)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftRingFingerMasterBoneName, leftRingFingerDeformBone1Extremities, None, None, 0.45)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftRingFingerBone2Name, koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftRingFingerDeformBone2Name, koikatsuCommons.bodyName), None, None, 0.5)
    leftRingFingerDeformBone3Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftRingFingerDeformBone3Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftRingFingerBone3Name, leftRingFingerDeformBone3Extremities, None, 0.5, 0.5)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftRingFingerTweakBoneName, leftRingFingerDeformBone3Extremities, 1, None, 0.6)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftRingFingerIkBoneName, leftRingFingerDeformBone3Extremities, 1, None, 0.6)
    leftLittleFingerDeformBone1Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftLittleFingerDeformBone1Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftLittleFingerBone1Name, leftLittleFingerDeformBone1Extremities, None, None, 0.4)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftLittleFingerMasterBoneName, leftLittleFingerDeformBone1Extremities, None, None, 0.4)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftLittleFingerBone2Name, koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftLittleFingerDeformBone2Name, koikatsuCommons.bodyName), None, 0.535, 0.52)
    leftLittleFingerDeformBone3Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftLittleFingerDeformBone3Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftLittleFingerTweakBoneName, leftLittleFingerDeformBone3Extremities, 1, None, 0.6)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.leftLittleFingerIkBoneName, leftLittleFingerDeformBone3Extremities, 1, None, 0.6)
    thighDeformBone1Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.thighDeformBone1Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.legTweakBone1Name, thighDeformBone1Extremities, None, 0.45, 0.66)
    thighDeformBone2Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.thighDeformBone2Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.legTweakBone2Name, thighDeformBone2Extremities, None, 0.5, None)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.legTweakBone3Name, koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.thighDeformBone3Name, koikatsuCommons.bodyName), None, 0.5, None)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.legParentBoneName, thighDeformBone1Extremities, None, 0.45, 0.66)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.legIkBoneName, thighDeformBone1Extremities, None, 0.45, 0.66)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.legFkBoneName, thighDeformBone2Extremities, None, 0.5, None)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.kneeTweakBone1Name, koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.legDeformBone1Name, koikatsuCommons.bodyName), None, 0.45, None)
    legDeformBone2Extremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.legDeformBone2Name, koikatsuCommons.bodyName)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.kneeTweakBone2Name, legDeformBone2Extremities, None, 0.6, None)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.kneeTweakBone3Name, koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.legDeformBone3Name, koikatsuCommons.bodyName), None, 0.62, None)
    createOffsetBoneWidgetHolder(generatedRig, koikatsuCommons.kneeFkBoneName, legDeformBone2Extremities, None, 0.45, None)
    
    bpy.ops.object.mode_set(mode='OBJECT')
 
    for tuple in sourceBoneNameAndBoneWidgetHolderNameTuples: 
        sourceBoneName = tuple[0]
        boneWidgetHolderName = tuple[1]
        copyTransformsConstraint = generatedRig.pose.bones[boneWidgetHolderName].constraints.new('COPY_TRANSFORMS')
        copyTransformsConstraint.target = generatedRig
        copyTransformsConstraint.subtarget = sourceBoneName
        copyTransformsConstraint.owner_space = 'LOCAL'
        copyTransformsConstraint.target_space = 'LOCAL'
        generatedRig.pose.bones[sourceBoneName].custom_shape_transform = generatedRig.pose.bones[boneWidgetHolderName]    
    """
    
    for constraint in generatedRig.pose.bones[koikatsuCommons.eyesTrackTargetParentBoneName].constraints:
        if constraint.type == 'ARMATURE':
            for target in constraint.targets:
                if target.subtarget:
                    target.target = generatedRig
    
    for driver in bpy.data.objects[koikatsuCommons.bodyName].data.shape_keys.animation_data.drivers:
        if driver.data_path.startswith("key_blocks"):
            ownerName = driver.data_path.split('"')[1]
            if ownerName == koikatsuCommons.eyelidsShapeKeyCopyName:
                for variable in driver.driver.variables:
                    for target in variable.targets:
                        if target.bone_target:
                            target.id = generatedRig 
    
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

class rigify_after(bpy.types.Operator):
    bl_idname = "kkb.rigafter"
    bl_label = "After Each Rigify Generate - Public"
    bl_description = 'why is the context wrong'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main()
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(rigify_after)

    # test call
    print((bpy.ops.kkb.rigafter('INVOKE_DEFAULT')))