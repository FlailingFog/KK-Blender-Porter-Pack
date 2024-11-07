import bpy
from typing import NamedTuple
import mathutils
from mathutils import Matrix
import os
import collections
import json
import re
import bmesh
from rna_prop_ui import rna_idprop_ui_create
import random
import string

def generateRandomAlphanumericString():
    randomString = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return randomString

metarigIdBonePrefix = "Metarig_ID:"
leftNamePrefix = "Left "
rightNamePrefix = "Right "
leftNameSuffix1 = "_L"
rightNameSuffix1 = "_R"
leftNameSuffix2 = ".L"
rightNameSuffix2 = ".R"
copyNameSuffix = " copy"
renamedNameSuffix = " renamed"

def leftNameToRightName(leftName):
    if leftName.startswith(leftNamePrefix):
        leftName = rightNamePrefix + leftName[len(leftNamePrefix):]
    if leftName.endswith(leftNameSuffix1):
        leftName = leftName[:len(leftName) - len(leftNameSuffix1)] + rightNameSuffix1
    if leftName.endswith(leftNameSuffix2):
        leftName = leftName[:len(leftName) - len(leftNameSuffix2)] + rightNameSuffix2
    return leftName

bodyName = "Body"
riggedTongueName = "Tongue (rigged)"

eyelidsShapeKeyName = "KK Eyes_default_cl"
eyelidsShapeKeyCopyName = eyelidsShapeKeyName + copyNameSuffix

widgetCollectionName = "Bone Widgets"
widgetEyesName = "WidgetEyesRigify"
widgetEyeLeftName = "WidgetEyeLeftRigify"
widgetEyeRightName = "WidgetEyeRightRigify"
widgetFaceName = "WidgetFace"
originalWidgetBreastsName = "WidgetBust"
originalWidgetBreastLeftName = "WidgetBreastL"
originalWidgetBreastRightName = "WidgetBreastR"
widgetBreastsName = "WidgetBreasts"
widgetBreastLeftName = "WidgetBreastLeft"
widgetBreastRightName = "WidgetBreastRight"
widgetButtocksName = "WidgetButtocks"
widgetButtockLeftName = "WidgetButtockLeft"
widgetButtockRightName = "WidgetButtockRight"

handleBoneSuffix = " handle"
trackBoneSuffix = " track"
markerBoneSuffix = " marker"
parentBoneSuffix = " parent"
placeholderBoneSuffix = " placeholder"
xBoneSuffix = " x"
yBoneSuffix = " y"
zBoneSuffix = " z"

originalRootBoneName = "Center"
originalRootUpperBoneName = "cf_pv_root_upper"
rootBoneName = "root"
eyesXBoneName = "Eyesx"
originalEyesBoneName = "Eye Controller"
eyesBoneName = "Eyes target"
leftEyeBoneName = "Left eye target"
rightEyeBoneName = leftNameToRightName(leftEyeBoneName)
eyesHandleBoneName = "Eyes" + handleBoneSuffix
leftEyeHandleBoneName = "Left eye" + handleBoneSuffix
rightEyeHandleBoneName = leftNameToRightName(leftEyeHandleBoneName)
eyesTrackTargetBoneName = "Eyes track target"
eyesTrackTargetParentBoneName = eyesTrackTargetBoneName + parentBoneSuffix
eyesHandleMarkerBoneName = eyesHandleBoneName + markerBoneSuffix
leftEyeHandleMarkerBoneName = leftEyeHandleBoneName + markerBoneSuffix
rightEyeHandleMarkerBoneName = leftNameToRightName(leftEyeHandleMarkerBoneName)
leftEyeHandleMarkerXBoneName = leftEyeHandleBoneName + markerBoneSuffix + xBoneSuffix
rightEyeHandleMarkerXBoneName = leftNameToRightName(leftEyeHandleMarkerXBoneName)
leftEyeHandleMarkerZBoneName = leftEyeHandleBoneName + markerBoneSuffix + zBoneSuffix
rightEyeHandleMarkerZBoneName = leftNameToRightName(leftEyeHandleMarkerZBoneName)
eyeballsBoneName = "Eyeballs"
leftEyeballBoneName = "Left eyeball"
rightEyeballBoneName = leftNameToRightName(leftEyeballBoneName)
eyeballsTrackBoneName = eyeballsBoneName + trackBoneSuffix
leftEyeballTrackBoneName = leftEyeballBoneName + trackBoneSuffix
rightEyeballTrackBoneName = leftNameToRightName(leftEyeballTrackBoneName)
leftEyeballTrackCorrectionBoneName = leftEyeballTrackBoneName + " correction"
rightEyeballTrackCorrectionBoneName = leftNameToRightName(leftEyeballTrackCorrectionBoneName)
riggedTongueLeftBoneBaseName = "cf_j_tang_L"
riggedTongueRightBoneBaseName = leftNameToRightName(riggedTongueLeftBoneBaseName)
riggedTongueBone1Name = "cf_j_tang_01"
riggedTongueBone2Name = "cf_j_tang_02"
riggedTongueBone3Name = "cf_j_tang_03"
riggedTongueLeftBone3Name = riggedTongueLeftBoneBaseName + "_03"
riggedTongueRightBone3Name = riggedTongueRightBoneBaseName + "_03"
riggedTongueBone4Name = "cf_j_tang_04"
riggedTongueLeftBone4Name = riggedTongueLeftBoneBaseName + "_04"
riggedTongueRightBone4Name = riggedTongueRightBoneBaseName + "_04"
riggedTongueBone5Name = "cf_j_tang_05"
riggedTongueLeftBone5Name = riggedTongueLeftBoneBaseName + "_05"
riggedTongueRightBone5Name = riggedTongueRightBoneBaseName + "_05"
headBoneName = "Head"
leftHeadMarkerXBoneName = leftNamePrefix + headBoneName + markerBoneSuffix + xBoneSuffix
rightHeadMarkerXBoneName = leftNameToRightName(leftHeadMarkerXBoneName)
leftHeadMarkerZBoneName = leftNamePrefix + headBoneName + markerBoneSuffix + zBoneSuffix
rightHeadMarkerZBoneName = leftNameToRightName(leftHeadMarkerZBoneName)
headTrackTargetBoneName = "Head track target"
headTrackTargetParentBoneName = headTrackTargetBoneName + parentBoneSuffix
headTrackBoneName = "Head" + trackBoneSuffix
neckBoneName = "Neck"
torsoBoneName = "torso"
upperChestBoneName = "Upper Chest"
chestBoneName = "Chest"
spineBoneName = "Spine"
hipsBoneName = "Hips"
pelvisBoneName = "Pelvis"
waistBoneName = "cf_j_waist02"
crotchBoneName = "cf_j_kokan"
anusBoneName = "cf_j_ana"
betterPenetrationRootCrotchBoneName = "cf_J_Vagina_root"
betterPenetrationFrontCrotchBoneName = "cf_J_Vagina_F"
betterPenetrationLeftCrotchBoneBaseName = "cf_J_Vagina_L"
betterPenetrationRightCrotchBoneBaseName = leftNameToRightName(betterPenetrationLeftCrotchBoneBaseName)
betterPenetrationLeftCrotchBone1Name = betterPenetrationLeftCrotchBoneBaseName + ".001"
betterPenetrationRightCrotchBone1Name = betterPenetrationRightCrotchBoneBaseName + ".001"
betterPenetrationLeftCrotchBone2Name = betterPenetrationLeftCrotchBoneBaseName + ".002"
betterPenetrationRightCrotchBone2Name = betterPenetrationRightCrotchBoneBaseName + ".002"
betterPenetrationLeftCrotchBone3Name = betterPenetrationLeftCrotchBoneBaseName + ".003"
betterPenetrationRightCrotchBone3Name = betterPenetrationRightCrotchBoneBaseName + ".003"
betterPenetrationLeftCrotchBone4Name = betterPenetrationLeftCrotchBoneBaseName + ".004"
betterPenetrationRightCrotchBone4Name = betterPenetrationRightCrotchBoneBaseName + ".004"
betterPenetrationLeftCrotchBone5Name = betterPenetrationLeftCrotchBoneBaseName + ".005"
betterPenetrationRightCrotchBone5Name = betterPenetrationRightCrotchBoneBaseName + ".005"
betterPenetrationBackCrotchBoneName = "cf_J_Vagina_B"
buttocksBoneName = "Buttocks"
leftButtockBoneName = "cf_j_siri_L"
rightButtockBoneName = leftNameToRightName(leftButtockBoneName)
buttocksHandleBoneName = "Buttocks" + handleBoneSuffix
leftButtockHandleBoneName = "Left Buttock" + handleBoneSuffix
rightButtockHandleBoneName = leftNameToRightName(leftButtockHandleBoneName)
breastsBoneName = "cf_d_bust00"
leftBreastBone1Name = "cf_j_bust01_L"
rightBreastBone1Name = leftNameToRightName(leftBreastBone1Name)
leftBreastBone2Name = "cf_j_bust02_L"
rightBreastBone2Name = leftNameToRightName(leftBreastBone2Name)
leftBreastBone3Name = "cf_j_bust03_L"
rightBreastBone3Name = leftNameToRightName(leftBreastBone3Name)
leftNippleBone1Name = "cf_j_bnip02root_L"
rightNippleBone1Name = leftNameToRightName(leftNippleBone1Name)
leftNippleBone2Name = "cf_j_bnip02_L"
rightNippleBone2Name = leftNameToRightName(leftNippleBone2Name)
breastsHandleBoneName = "Breasts" + handleBoneSuffix
leftBreastHandleBoneName = "Left Breast" + handleBoneSuffix
rightBreastHandleBoneName = leftNameToRightName(leftBreastHandleBoneName)
leftShoulderBoneName = "Left shoulder"
rightShoulderBoneName = leftNameToRightName(leftShoulderBoneName)
leftArmBoneName = "Left arm"
rightArmBoneName = leftNameToRightName(leftArmBoneName)
leftElbowBoneName = "Left elbow"
rightElbowBoneName = leftNameToRightName(leftElbowBoneName)
originalLeftElbowPoleBoneName = "cf_pv_elbo_L"
originalRightElbowPoleBoneName = leftNameToRightName(originalLeftElbowPoleBoneName)
originalLeftWristBoneName = "cf_pv_hand_L"
originalRightWristBoneName = leftNameToRightName(originalLeftWristBoneName)
leftWristBoneName = "Left wrist"
rightWristBoneName = leftNameToRightName(leftWristBoneName)
leftThumbBone1Name = "Thumb0_L"
rightThumbBone1Name = leftNameToRightName(leftThumbBone1Name)
leftThumbBone2Name = "Thumb1_L"
rightThumbBone2Name = leftNameToRightName(leftThumbBone2Name)
leftThumbBone3Name = "Thumb2_L"
rightThumbBone3Name = leftNameToRightName(leftThumbBone3Name)
leftIndexFingerPalmBoneName = "IndexFingerPalm_L"
rightIndexFingerPalmBoneName = leftNameToRightName(leftIndexFingerPalmBoneName)
leftIndexFingerBone1Name = "IndexFinger1_L"
rightIndexFingerBone1Name = leftNameToRightName(leftIndexFingerBone1Name)
leftIndexFingerBone2Name = "IndexFinger2_L"
rightIndexFingerBone2Name = leftNameToRightName(leftIndexFingerBone2Name)
leftIndexFingerBone3Name = "IndexFinger3_L"
rightIndexFingerBone3Name = leftNameToRightName(leftIndexFingerBone3Name)
leftMiddleFingerPalmBoneName = "MiddleFingerPalm_L"
rightMiddleFingerPalmBoneName = leftNameToRightName(leftMiddleFingerPalmBoneName)
leftMiddleFingerBone1Name = "MiddleFinger1_L"
rightMiddleFingerBone1Name = leftNameToRightName(leftMiddleFingerBone1Name)
leftMiddleFingerBone2Name = "MiddleFinger2_L"
rightMiddleFingerBone2Name = leftNameToRightName(leftMiddleFingerBone2Name)
leftMiddleFingerBone3Name = "MiddleFinger3_L"
rightMiddleFingerBone3Name = leftNameToRightName(leftMiddleFingerBone3Name)
leftRingFingerPalmBoneName = "RingFingerPalm_L"
rightRingFingerPalmBoneName = leftNameToRightName(leftRingFingerPalmBoneName)
leftRingFingerBone1Name = "RingFinger1_L"
rightRingFingerBone1Name = leftNameToRightName(leftRingFingerBone1Name)
leftRingFingerBone2Name = "RingFinger2_L"
rightRingFingerBone2Name = leftNameToRightName(leftRingFingerBone2Name)
leftRingFingerBone3Name = "RingFinger3_L"
rightRingFingerBone3Name = leftNameToRightName(leftRingFingerBone3Name)
leftLittleFingerPalmBoneName = "LittleFingerPalm_L"
rightLittleFingerPalmBoneName = leftNameToRightName(leftLittleFingerPalmBoneName)
leftLittleFingerBone1Name = "LittleFinger1_L"
rightLittleFingerBone1Name = leftNameToRightName(leftLittleFingerBone1Name)
leftLittleFingerBone2Name = "LittleFinger2_L"
rightLittleFingerBone2Name = leftNameToRightName(leftLittleFingerBone2Name)
leftLittleFingerBone3Name = "LittleFinger3_L"
rightLittleFingerBone3Name = leftNameToRightName(leftLittleFingerBone3Name)
leftLegBoneName = "Left leg"
rightLegBoneName = leftNameToRightName(leftLegBoneName)
leftKneeBoneName = "Left knee"
rightKneeBoneName = leftNameToRightName(leftKneeBoneName)
originalLeftKneePoleBoneName = "cf_pv_knee_L"
originalRightKneePoleBoneName = leftNameToRightName(originalLeftKneePoleBoneName)
originalLeftAnkleBoneName = "MasterFootIK.L"
originalRightAnkleBoneName = leftNameToRightName(originalLeftAnkleBoneName)
leftAnkleBoneName = "Left ankle"
rightAnkleBoneName = leftNameToRightName(leftAnkleBoneName)
originalLeftToeBoneName = "ToeRotator.L"
originalRightToeBoneName = leftNameToRightName(originalLeftToeBoneName)
leftToeBoneName = "Left toe"
rightToeBoneName = leftNameToRightName(leftToeBoneName)
originalLeftHeelIkBoneName = "HeelIK.L"
originalRightHeelIkBoneName = leftNameToRightName(originalLeftHeelIkBoneName)
originalLeftHeelBoneName = "a_n_heel_L"
originalRightHeelBoneName = leftNameToRightName(originalLeftHeelBoneName)
leftHeelBoneName = "Left heel"
rightHeelBoneName = leftNameToRightName(leftHeelBoneName)

skirtPalmBonePrefix = "cf_d_sk"
skirtParentBoneName = skirtPalmBonePrefix + "_top"
skirtParentBoneCopyName = skirtParentBoneName + copyNameSuffix
skirtBonePrefix = "cf_j_sk"

def getSkirtBoneName(palm, primaryIndex, secondaryIndex = 0):
    if palm:
        prefix = skirtPalmBonePrefix
    else:
        prefix = skirtBonePrefix
    return prefix + "_" + str(primaryIndex).zfill(2) + "_" + str(secondaryIndex).zfill(2)
    
originalBonePrefix = "ORG-"

deformBonePrefix = "DEF-"
leftEyeDeformBoneName = "Left Eye"
rightEyeDeformBoneName = "Right Eye"
headDeformBoneName = deformBonePrefix + headBoneName
neckDeformBoneName = deformBonePrefix + neckBoneName
upperChestDeformBoneName = deformBonePrefix + upperChestBoneName
chestDeformBoneName = deformBonePrefix + chestBoneName
spineDeformBoneName = deformBonePrefix + spineBoneName
hipsDeformBoneName = deformBonePrefix + hipsBoneName
leftButtockDeformBoneName = "cf_s_siri_L"
rightButtockDeformBoneName = leftNameToRightName(leftButtockDeformBoneName)
leftBreastDeformBone1Name = "cf_s_bust01_L"
rightBreastDeformBone1Name = leftNameToRightName(leftBreastDeformBone1Name)
leftBreastDeformBone2Name = "cf_s_bust02_L"
rightBreastDeformBone2Name = leftNameToRightName(leftBreastDeformBone2Name)
leftBreastDeformBone3Name = "cf_s_bust03_L"
rightBreastDeformBone3Name = leftNameToRightName(leftBreastDeformBone3Name)
leftNippleDeformBone1Name = "cf_s_bnip01_L"
rightNippleDeformBone1Name = leftNameToRightName(leftNippleDeformBone1Name)
leftNippleDeformBone2Name = "cf_s_bnip025_L"
rightNippleDeformBone2Name = leftNameToRightName(leftNippleDeformBone2Name)
leftShoulderDeformBoneName = "cf_s_shoulder02_L"
rightShoulderDeformBoneName = leftNameToRightName(leftShoulderDeformBoneName)
leftArmDeformBone1Name = deformBonePrefix + leftArmBoneName
rightArmDeformBone1Name = deformBonePrefix + rightArmBoneName
leftArmDeformBone2Name = deformBonePrefix + leftArmBoneName + ".001"
rightArmDeformBone2Name = deformBonePrefix + rightArmBoneName + ".001"
leftArmDeformBone3Name = deformBonePrefix + leftArmBoneName + ".002"
rightArmDeformBone3Name = deformBonePrefix + rightArmBoneName + ".002"
leftElbowDeformBone1Name = deformBonePrefix + leftElbowBoneName
rightElbowDeformBone1Name = deformBonePrefix + rightElbowBoneName
leftElbowDeformBone2Name = deformBonePrefix + leftElbowBoneName + ".001"
rightElbowDeformBone2Name = deformBonePrefix + rightElbowBoneName + ".001"
leftElbowDeformBone3Name = deformBonePrefix + leftElbowBoneName + ".002"
rightElbowDeformBone3Name = deformBonePrefix + rightElbowBoneName + ".002"
leftWristDeformBoneName = deformBonePrefix + leftWristBoneName
rightWristDeformBoneName = deformBonePrefix + rightWristBoneName
leftThighDeformBone1Name = deformBonePrefix + leftLegBoneName
rightThighDeformBone1Name = deformBonePrefix + rightLegBoneName
leftThighDeformBone2Name = deformBonePrefix + leftLegBoneName + ".001"
rightThighDeformBone2Name = deformBonePrefix + rightLegBoneName + ".001"
leftThighDeformBone3Name = deformBonePrefix + leftLegBoneName + ".002"
rightThighDeformBone3Name = deformBonePrefix + rightLegBoneName + ".002"
leftLegDeformBone1Name = deformBonePrefix + leftKneeBoneName
rightLegDeformBone1Name = deformBonePrefix + rightKneeBoneName
leftLegDeformBone2Name = deformBonePrefix + leftKneeBoneName + ".001"
rightLegDeformBone2Name = deformBonePrefix + rightKneeBoneName + ".001"
leftLegDeformBone3Name = deformBonePrefix + leftKneeBoneName + ".002"
rightLegDeformBone3Name = deformBonePrefix + rightKneeBoneName + ".002"
leftAnkleDeformBoneName = deformBonePrefix + leftAnkleBoneName
rightAnkleDeformBoneName = deformBonePrefix + rightAnkleBoneName
leftToeDeformBoneName = deformBonePrefix + leftToeBoneName
rightToeDeformBoneName = deformBonePrefix + rightToeBoneName
leftThumbDeformBone1Name = deformBonePrefix + leftThumbBone1Name
rightThumbDeformBone1Name = deformBonePrefix + rightThumbBone1Name
leftThumbDeformBone2Name = deformBonePrefix + leftThumbBone2Name
rightThumbDeformBone2Name = deformBonePrefix + rightThumbBone2Name
leftThumbDeformBone3Name = deformBonePrefix + leftThumbBone3Name
rightThumbDeformBone3Name = deformBonePrefix + rightThumbBone3Name
leftIndexFingerPalmDeformBoneName = deformBonePrefix + leftIndexFingerPalmBoneName
rightIndexFingerPalmDeformBoneName = deformBonePrefix + rightIndexFingerPalmBoneName
leftIndexFingerDeformBone1Name = deformBonePrefix + leftIndexFingerBone1Name
rightIndexFingerDeformBone1Name = deformBonePrefix + rightIndexFingerBone1Name
leftIndexFingerDeformBone2Name = deformBonePrefix + leftIndexFingerBone2Name
rightIndexFingerDeformBone2Name = deformBonePrefix + rightIndexFingerBone2Name
leftIndexFingerDeformBone3Name = deformBonePrefix + leftIndexFingerBone3Name
rightIndexFingerDeformBone3Name = deformBonePrefix + rightIndexFingerBone3Name
leftMiddleFingerPalmDeformBoneName = deformBonePrefix + leftMiddleFingerPalmBoneName
rightMiddleFingerPalmDeformBoneName = deformBonePrefix + rightMiddleFingerPalmBoneName
leftMiddleFingerDeformBone1Name = deformBonePrefix + leftMiddleFingerBone1Name
rightMiddleFingerDeformBone1Name = deformBonePrefix + rightMiddleFingerBone1Name
leftMiddleFingerDeformBone2Name = deformBonePrefix + leftMiddleFingerBone2Name
rightMiddleFingerDeformBone2Name = deformBonePrefix + rightMiddleFingerBone2Name
leftMiddleFingerDeformBone3Name = deformBonePrefix + leftMiddleFingerBone3Name
rightMiddleFingerDeformBone3Name = deformBonePrefix + rightMiddleFingerBone3Name
leftRingFingerPalmDeformBoneName = deformBonePrefix + leftRingFingerPalmBoneName
rightRingFingerPalmDeformBoneName = deformBonePrefix + rightRingFingerPalmBoneName
leftRingFingerDeformBone1Name = deformBonePrefix + leftRingFingerBone1Name
rightRingFingerDeformBone1Name = deformBonePrefix + rightRingFingerBone1Name
leftRingFingerDeformBone2Name = deformBonePrefix + leftRingFingerBone2Name
rightRingFingerDeformBone2Name = deformBonePrefix + rightRingFingerBone2Name
leftRingFingerDeformBone3Name = deformBonePrefix + leftRingFingerBone3Name
rightRingFingerDeformBone3Name = deformBonePrefix + rightRingFingerBone3Name
leftLittleFingerPalmDeformBoneName = deformBonePrefix + leftLittleFingerPalmBoneName
rightLittleFingerPalmDeformBoneName = deformBonePrefix + rightLittleFingerPalmBoneName
leftLittleFingerDeformBone1Name = deformBonePrefix + leftLittleFingerBone1Name
rightLittleFingerDeformBone1Name = deformBonePrefix + rightLittleFingerBone1Name
leftLittleFingerDeformBone2Name = deformBonePrefix + leftLittleFingerBone2Name
rightLittleFingerDeformBone2Name = deformBonePrefix + rightLittleFingerBone2Name
leftLittleFingerDeformBone3Name = deformBonePrefix + leftLittleFingerBone3Name
rightLittleFingerDeformBone3Name = deformBonePrefix + rightLittleFingerBone3Name

def getSkirtDeformBoneName(primaryIndex, secondaryIndex):
    return deformBonePrefix + getSkirtBoneName(False, primaryIndex, secondaryIndex)

originalFaceUpDeformBoneName = "cf_J_FaceUp_ty"
originalFaceBaseDeformBoneName = "cf_J_FaceBase"
originalHeadDeformBoneName = "cf_s_head"
originalNeckDeformBoneName = "cf_s_neck"
originalUpperChestDeformBoneName = "cf_s_spine03"
originalChestDeformBoneName = "cf_s_spine02"
originalSpineDeformBoneName = "cf_s_spine01"
originalHipsDeformBoneName = "cf_s_waist01"
originalLeftShoulderDeformBoneName = "cf_s_shoulder02_L"
originalRightShoulderDeformBoneName = leftNameToRightName(originalLeftShoulderDeformBoneName)
originalLeftArmDeformBone1Name = "cf_s_arm01_L"
originalRightArmDeformBone1Name = leftNameToRightName(originalLeftArmDeformBone1Name)
originalLeftArmDeformBone2Name = "cf_s_arm02_L"
originalRightArmDeformBone2Name = leftNameToRightName(originalLeftArmDeformBone2Name)
originalLeftArmDeformBone3Name = "cf_s_arm03_L"
originalRightArmDeformBone3Name = leftNameToRightName(originalLeftArmDeformBone3Name)
originalLeftElbowDeformBone1Name = "cf_s_forearm01_L"
originalRightElbowDeformBone1Name = leftNameToRightName(originalLeftElbowDeformBone1Name)
originalLeftElbowDeformBone2Name = "cf_s_forearm02_L"
originalRightElbowDeformBone2Name = leftNameToRightName(originalLeftElbowDeformBone2Name)
originalLeftElbowDeformBone3Name = "cf_s_wrist_L"
originalRightElbowDeformBone3Name = leftNameToRightName(originalLeftElbowDeformBone3Name)
originalLeftWristDeformBoneName = "cf_s_hand_L"
originalRightWristDeformBoneName = leftNameToRightName(originalLeftWristDeformBoneName)
originalLeftThumbDeformBone1Name = leftThumbBone1Name
originalRightThumbDeformBone1Name = rightThumbBone1Name
originalLeftThumbDeformBone2Name = leftThumbBone2Name
originalRightThumbDeformBone2Name = rightThumbBone2Name
originalLeftThumbDeformBone3Name = leftThumbBone3Name
originalRightThumbDeformBone3Name = rightThumbBone3Name
originalLeftIndexFingerDeformBone1Name = leftIndexFingerBone1Name
originalRightIndexFingerDeformBone1Name = rightIndexFingerBone1Name
originalLeftIndexFingerDeformBone2Name = leftIndexFingerBone2Name
originalRightIndexFingerDeformBone2Name = rightIndexFingerBone2Name
originalLeftIndexFingerDeformBone3Name = leftIndexFingerBone3Name
originalRightIndexFingerDeformBone3Name = rightIndexFingerBone3Name
originalLeftMiddleFingerDeformBone1Name = leftMiddleFingerBone1Name
originalRightMiddleFingerDeformBone1Name = rightMiddleFingerBone1Name
originalLeftMiddleFingerDeformBone2Name = leftMiddleFingerBone2Name
originalRightMiddleFingerDeformBone2Name = rightMiddleFingerBone2Name
originalLeftMiddleFingerDeformBone3Name = leftMiddleFingerBone3Name
originalRightMiddleFingerDeformBone3Name = rightMiddleFingerBone3Name
originalLeftRingFingerDeformBone1Name = leftRingFingerBone1Name
originalRightRingFingerDeformBone1Name = rightRingFingerBone1Name
originalLeftRingFingerDeformBone2Name = leftRingFingerBone2Name
originalRightRingFingerDeformBone2Name = rightRingFingerBone2Name
originalLeftRingFingerDeformBone3Name = leftRingFingerBone3Name
originalRightRingFingerDeformBone3Name = rightRingFingerBone3Name
originalLeftLittleFingerDeformBone1Name = leftLittleFingerBone1Name
originalRightLittleFingerDeformBone1Name = rightLittleFingerBone1Name
originalLeftLittleFingerDeformBone2Name = leftLittleFingerBone2Name
originalRightLittleFingerDeformBone2Name = rightLittleFingerBone2Name
originalLeftLittleFingerDeformBone3Name = leftLittleFingerBone3Name
originalRightLittleFingerDeformBone3Name = rightLittleFingerBone3Name
originalLeftThighDeformBone1Name = "cf_s_thigh01_L"
originalRightThighDeformBone1Name = leftNameToRightName(originalLeftThighDeformBone1Name)
originalLeftThighDeformBone2Name = "cf_s_thigh02_L"
originalRightThighDeformBone2Name = leftNameToRightName(originalLeftThighDeformBone2Name)
originalLeftThighDeformBone3Name = "cf_s_thigh03_L"
originalRightThighDeformBone3Name = leftNameToRightName(originalLeftThighDeformBone3Name)
originalLeftLegDeformBone1Name = "cf_s_leg01_L"
originalRightLegDeformBone1Name = leftNameToRightName(originalLeftLegDeformBone1Name)
originalLeftLegDeformBone2Name = "cf_s_leg02_L"
originalRightLegDeformBone2Name = leftNameToRightName(originalLeftLegDeformBone2Name)
originalLeftLegDeformBone3Name = "cf_s_leg03_L"
originalRightLegDeformBone3Name = leftNameToRightName(originalLeftLegDeformBone3Name)

tweakBoneSuffix = "_tweak"
parentBoneSuffix = "_parent"
fkBoneSuffix = "_fk"
ikBoneSuffix = "_ik"
masterBoneSuffix = "_master"
headTweakBoneName = "head"
leftArmTweakBone1Name = leftArmBoneName + tweakBoneSuffix
rightArmTweakBone1Name = leftNameToRightName(leftArmTweakBone1Name)
leftArmParentBoneName = leftArmBoneName + parentBoneSuffix
rightArmParentBoneName = leftNameToRightName(leftArmParentBoneName)
leftArmIkBoneName = leftArmBoneName + ikBoneSuffix
rightArmArmIkBoneName = leftNameToRightName(leftArmIkBoneName)
leftWristFkBoneName = leftWristBoneName + fkBoneSuffix
rightWristFkBoneName = leftNameToRightName(leftWristFkBoneName)
leftWristIkBoneName = leftWristBoneName + ikBoneSuffix
rightWristIkBoneName = leftNameToRightName(leftWristIkBoneName)
leftWristTweakBoneName = leftWristBoneName + tweakBoneSuffix
rightWristTweakBoneName = leftNameToRightName(leftWristTweakBoneName)
leftThumbTweakBoneName = leftThumbBone1Name + ".001"
rightThumbTweakBoneName = leftNameToRightName(leftThumbTweakBoneName)
leftThumbIkBoneName = leftThumbBone1Name[:leftThumbBone1Name.index(leftNameSuffix1)] + ikBoneSuffix + leftNameSuffix1
rightThumbIkBoneName = leftNameToRightName(leftThumbIkBoneName)
leftThumbMasterBoneName = leftThumbBone1Name[:leftThumbBone1Name.index(leftNameSuffix1)] + masterBoneSuffix + leftNameSuffix1
rightThumbMasterBoneName = leftNameToRightName(leftThumbMasterBoneName)
leftIndexFingerTweakBoneName = leftIndexFingerBone1Name + ".001"
rightIndexFingerTweakBoneName = leftNameToRightName(leftIndexFingerTweakBoneName)
leftIndexFingerIkBoneName = leftIndexFingerBone1Name[:leftIndexFingerBone1Name.index(leftNameSuffix1)] + ikBoneSuffix + leftNameSuffix1
rightIndexFingerIkBoneName = leftNameToRightName(leftIndexFingerIkBoneName)
leftIndexFingerMasterBoneName = leftIndexFingerBone1Name[:leftIndexFingerBone1Name.index(leftNameSuffix1)] + masterBoneSuffix + leftNameSuffix1
rightIndexFingerMasterBoneName = leftNameToRightName(leftIndexFingerMasterBoneName)
leftMiddleFingerTweakBoneName = leftMiddleFingerBone1Name + ".001"
rightMiddleFingerTweakBoneName = leftNameToRightName(leftMiddleFingerTweakBoneName)
leftMiddleFingerIkBoneName = leftMiddleFingerBone1Name[:leftMiddleFingerBone1Name.index(leftNameSuffix1)] + ikBoneSuffix + leftNameSuffix1
rightMiddleFingerIkBoneName = leftNameToRightName(leftMiddleFingerIkBoneName)
leftMiddleFingerMasterBoneName = leftMiddleFingerBone1Name[:leftMiddleFingerBone1Name.index(leftNameSuffix1)] + masterBoneSuffix + leftNameSuffix1
rightMiddleFingerMasterBoneName = leftNameToRightName(leftMiddleFingerMasterBoneName)
leftRingFingerTweakBoneName = leftRingFingerBone1Name + ".001"
rightRingFingerTweakBoneName = leftNameToRightName(leftRingFingerTweakBoneName)
leftRingFingerIkBoneName = leftRingFingerBone1Name[:leftRingFingerBone1Name.index(leftNameSuffix1)] + ikBoneSuffix + leftNameSuffix1
rightRingFingerIkBoneName = leftNameToRightName(leftRingFingerIkBoneName)
leftRingFingerMasterBoneName = leftRingFingerBone1Name[:leftRingFingerBone1Name.index(leftNameSuffix1)] + masterBoneSuffix + leftNameSuffix1
rightingFingerMasterBoneName = leftNameToRightName(leftRingFingerMasterBoneName)
leftLittleFingerPalmFkBoneName = leftLittleFingerPalmBoneName[:leftLittleFingerPalmBoneName.index(leftNameSuffix1)] + fkBoneSuffix + leftNameSuffix1
rightLittleFingerPalmFkBoneName = leftNameToRightName(leftLittleFingerPalmFkBoneName)
leftLittleFingerTweakBoneName = leftLittleFingerBone1Name + ".001"
rightLittleFingerTweakBoneName = leftNameToRightName(leftLittleFingerTweakBoneName)
leftLittleFingerIkBoneName = leftLittleFingerBone1Name[:leftLittleFingerBone1Name.index(leftNameSuffix1)] + ikBoneSuffix + leftNameSuffix1
rightLittleFingerIkBoneName = leftNameToRightName(leftLittleFingerIkBoneName)
leftLittleFingerMasterBoneName = leftLittleFingerBone1Name[:leftLittleFingerBone1Name.index(leftNameSuffix1)] + masterBoneSuffix + leftNameSuffix1
rightLittleFingerMasterBoneName = leftNameToRightName(leftLittleFingerMasterBoneName)
leftLegTweakBone1Name = leftLegBoneName + tweakBoneSuffix
rightLegTweakBone1Name = leftNameToRightName(leftLegTweakBone1Name)
leftLegTweakBone2Name = leftLegBoneName + tweakBoneSuffix + ".001"
rightLegTweakBone2Name = leftNameToRightName(leftLegTweakBone2Name)
leftLegTweakBone3Name = leftLegBoneName + tweakBoneSuffix + ".002"
rightLegTweakBone3Name = leftNameToRightName(leftLegTweakBone3Name)
leftLegParentBoneName = leftLegBoneName + parentBoneSuffix
rightLegParentBoneName = leftNameToRightName(leftLegParentBoneName)
leftLegIkBoneName = leftLegBoneName + ikBoneSuffix
rightLegIkBoneName = leftNameToRightName(leftLegIkBoneName)
leftLegFkBoneName = leftLegBoneName + fkBoneSuffix
rightLegFkBoneName = leftNameToRightName(leftLegFkBoneName)
leftKneeTweakBone1Name = leftKneeBoneName + tweakBoneSuffix
rightKneeTweakBone1Name = leftNameToRightName(leftKneeTweakBone1Name)
leftKneeTweakBone2Name = leftKneeBoneName + tweakBoneSuffix + ".001"
rightKneeTweakBone2Name = leftNameToRightName(leftKneeTweakBone2Name)
leftKneeTweakBone3Name = leftKneeBoneName + tweakBoneSuffix + ".002"
rightKneeTweakBone3Name = leftNameToRightName(leftKneeTweakBone3Name)
leftKneeFkBoneName = leftKneeBoneName + fkBoneSuffix
rightKneeFkBoneName = leftNameToRightName(leftKneeFkBoneName)

waistJointCorrectionBoneName = "cf_s_waist02"
leftButtockJointCorrectionBoneName = "cf_d_siri_L"
rightButtockJointCorrectionBoneName = leftNameToRightName(leftButtockJointCorrectionBoneName)
leftShoulderJointCorrectionBoneName = "cf_d_shoulder02_L"
rightShoulderJointCorrectionBoneName = leftNameToRightName(leftShoulderJointCorrectionBoneName)
frontLeftElbowJointCorrectionBoneName = "cf_s_elbo_L"
frontRightElbowJointCorrectionBoneName = leftNameToRightName(frontLeftElbowJointCorrectionBoneName)
midLeftElbowJointCorrectionBoneName = "cf_s_forearm01_L"
midRightElbowJointCorrectionBoneName = leftNameToRightName(midLeftElbowJointCorrectionBoneName)
backLeftElbowJointCorrectionBoneName = "cf_s_elboback_L";
backRightElbowJointCorrectionBoneName = leftNameToRightName(backLeftElbowJointCorrectionBoneName)
leftWristJointCorrectionBoneName = "cf_d_hand_L"
rightWristJointCorrectionBoneName = leftNameToRightName(leftWristJointCorrectionBoneName)
leftLegJointCorrectionBoneName = "cf_s_leg_L"
rightLegJointCorrectionBoneName = leftNameToRightName(leftLegJointCorrectionBoneName)
frontLeftKneeJointCorrectionBoneName = "cf_d_kneeF_L";
frontRightKneeJointCorrectionBoneName = leftNameToRightName(frontLeftKneeJointCorrectionBoneName)
midLeftKneeJointCorrectionBoneName = "cf_s_leg01_L"
midRightKneeJointCorrectionBoneName = leftNameToRightName(midLeftKneeJointCorrectionBoneName)
backLeftKneeJointCorrectionBoneName = "cf_s_kneeB_L";
backRightKneeJointCorrectionBoneName = leftNameToRightName(backLeftKneeJointCorrectionBoneName)

def duplicateShapeKey(objectName, shapeKeyName, shapeKeyCopyName):
    object = bpy.data.objects[objectName]
    for shapeKey in object.data.shape_keys.key_blocks:
        if shapeKey.name == shapeKeyName:
            shapeKey.mute = False
            oldShapeKeyValue = shapeKey.value
            shapeKey.value = 1
        elif shapeKey.name == shapeKeyCopyName:
            if object.data.shape_keys.animation_data:
                for driver in object.data.shape_keys.animation_data.drivers:
                    if driver.data_path.startswith("key_blocks"):
                        ownerName = driver.data_path.split('"')[1]
                        if ownerName == shapeKey.name:
                            object.data.shape_keys.animation_data.drivers.remove(driver)
            object.shape_key_remove(key = shapeKey)
        else:
            shapeKey.mute = True
    shapeKeyCopy = object.shape_key_add(name = shapeKeyCopyName, from_mix = True)
    shapeKeyCopy.value = 0
    for shapeKey in object.data.shape_keys.key_blocks:
        shapeKey.mute = False
        if shapeKey.name == shapeKeyName:
            shapeKey.value = oldShapeKeyValue
    return shapeKeyCopy

def isVertexGroupEmpty(vertexGroupName, objectName):
    object = bpy.data.objects[objectName]
    vertexGroup = object.vertex_groups[vertexGroupName]
    return not any(vertexGroup.index in [g.group for g in v.groups] for v in object.data.vertices)
                
class Extremities:
    vertices = None
    coordinates = None
    minX = None
    minY = None
    minZ = None
    maxX = None
    maxY = None
    maxZ = None
    
def returnLower(value1, value2):
    if value1 is None or value2 < value1:
        return value2
    return value1

def returnHigher(value1, value2):
    if value1 is None or value2 > value1:
        return value2
    return value1
    
def findVertexGroupExtremities(vertexGroupName, objectName):
    extremities = Extremities()
    object = bpy.data.objects[objectName]
    coordinates = [(object.matrix_world @ v.co) for v in object.data.vertices]
    vertexGroupIndex = object.vertex_groups[vertexGroupName].index
    vertices = [ v for v in object.data.vertices if vertexGroupIndex in [ vg.group for vg in v.groups ] ]
    extremities.vertices = vertices
    extremities.coordinates = coordinates
    for vertex in vertices:
        extremities.minX = returnLower(extremities.minX, coordinates[vertex.index][0])
        extremities.minY = returnLower(extremities.minY, coordinates[vertex.index][1])
        extremities.minZ = returnLower(extremities.minZ, coordinates[vertex.index][2])
        extremities.maxX = returnHigher(extremities.maxX, coordinates[vertex.index][0])
        extremities.maxY = returnHigher(extremities.maxY, coordinates[vertex.index][1])
        extremities.maxZ = returnHigher(extremities.maxZ, coordinates[vertex.index][2])
    return extremities

copyTransformsConstraintBaseName = "Copy Transforms"
copyRotationConstraintBaseName = "Copy Rotation"
transformationConstraintBaseName = "Transformation"
limitLocationConstraintBaseName = "Limit Location"
limitRotationConstraintBaseName = "Limit Rotation"
armatureConstraintBaseName = "Armature"
dampedTrackConstraintBaseName = "Damped Track"
handleConstraintSuffix = "_Handle"
jointConstraintSuffix = "_Joint"
eyeballConstraintSuffix = "_Eyeball"
headConstraintSuffix = "_Head"
parentConstraintSuffix = "_Parent"
trackConstraintSuffix = "_Track"
locationConstraintSuffix = " Location"
rotationConstraintSuffix = " Rotation"
scaleConstraintSuffix = " Scale"
correctionConstraintSuffix = " Correction"
minConstraintSuffix = " Min"
maxConstraintSuffix = " Max"

def removeConstraint(rig, boneName, constraintName):
    constraint = rig.pose.bones[boneName].constraints.get(constraintName)
    if constraint:
        rig.pose.bones[boneName].constraints.remove(constraint)
        
def changeConstraintIndex(rig, boneName, constraintName, newIndex):
    bone = rig.pose.bones[boneName]
    for index, constraint in enumerate(bone.constraints):
        if constraint.name == constraintName:
            bone.constraints.move(index, newIndex)
            break

def addCopyTransformsConstraint(rig, boneName, subTargetBoneName, mixMode, space, constraintName):
    removeConstraint(rig, boneName, constraintName)
    copyTransformsConstraint = rig.pose.bones[boneName].constraints.new('COPY_TRANSFORMS')
    copyTransformsConstraint.name = constraintName
    copyTransformsConstraint.target = rig
    copyTransformsConstraint.subtarget = subTargetBoneName
    copyTransformsConstraint.mix_mode = mixMode
    copyTransformsConstraint.owner_space = space
    copyTransformsConstraint.target_space = space
    return copyTransformsConstraint
    
def addCopyRotationConstraint(rig, boneName, subTargetBoneName, mixMode, space, constraintName, 
useX, invertX, useY, invertY, useZ, invertZ):
    removeConstraint(rig, boneName, constraintName)
    copyRotationConstraint = rig.pose.bones[boneName].constraints.new('COPY_ROTATION')
    copyRotationConstraint.name = constraintName
    copyRotationConstraint.target = rig
    copyRotationConstraint.subtarget = subTargetBoneName
    copyRotationConstraint.mix_mode = mixMode
    copyRotationConstraint.owner_space = space
    copyRotationConstraint.target_space = space
    copyRotationConstraint.use_x = useX
    copyRotationConstraint.invert_x = invertX
    copyRotationConstraint.use_y = useY
    copyRotationConstraint.invert_y = invertY
    copyRotationConstraint.use_z = useZ
    copyRotationConstraint.invert_z = invertZ
    return copyRotationConstraint

def addCopyScaleConstraint(rig, boneName, targetRig, subTargetBoneName, space, constraintName, 
useX, useY, useZ):
    removeConstraint(rig, boneName, constraintName)
    copyRotationConstraint = rig.pose.bones[boneName].constraints.new('COPY_SCALE')
    copyRotationConstraint.name = constraintName
    copyRotationConstraint.target = targetRig
    copyRotationConstraint.subtarget = subTargetBoneName
    copyRotationConstraint.owner_space = space
    copyRotationConstraint.target_space = space
    copyRotationConstraint.use_x = useX
    copyRotationConstraint.use_y = useY
    copyRotationConstraint.use_z = useZ
    return copyRotationConstraint
        
def addTransformationConstraint(rig, boneName, subTargetBoneName, mixMode, space, constraintName, 
mapFrom, fromRotationMode, fromMinX, fromMaxX, fromMinY, fromMaxY, fromMinZ, fromMaxZ, 
mapTo, toEulerOrder, toMinX, toMaxX, toMinY, toMaxY, toMinZ, toMaxZ, 
mapToXFrom = 'X', mapToYFrom = 'Y', mapToZFrom = 'Z'):
    removeConstraint(rig, boneName, constraintName)
    transformationConstraint = rig.pose.bones[boneName].constraints.new('TRANSFORM')
    transformationConstraint.name = constraintName
    transformationConstraint.target = rig
    transformationConstraint.subtarget = subTargetBoneName
    transformationConstraint.owner_space = space
    transformationConstraint.target_space = space
    transformationConstraint.map_from = mapFrom
    if mapFrom == 'LOCATION':
        transformationConstraint.from_min_x = fromMinX
        transformationConstraint.from_max_x = fromMaxX
        transformationConstraint.from_min_y = fromMinY
        transformationConstraint.from_max_y = fromMaxY
        transformationConstraint.from_min_z = fromMinZ
        transformationConstraint.from_max_z = fromMaxZ
    elif mapFrom == 'ROTATION':
        transformationConstraint.from_rotation_mode = fromRotationMode
        transformationConstraint.from_min_x_rot = fromMinX
        transformationConstraint.from_max_x_rot = fromMaxX
        transformationConstraint.from_min_y_rot = fromMinY
        transformationConstraint.from_max_y_rot = fromMaxY
        transformationConstraint.from_min_z_rot = fromMinZ
        transformationConstraint.from_max_z_rot = fromMaxZ
    elif mapFrom == 'SCALE':
        transformationConstraint.from_min_x_scale = fromMinX
        transformationConstraint.from_max_x_scale = fromMaxX
        transformationConstraint.from_min_y_scale = fromMinY
        transformationConstraint.from_max_y_scale = fromMaxY
        transformationConstraint.from_min_z_scale = fromMinZ
        transformationConstraint.from_max_z_scale = fromMaxZ
    transformationConstraint.map_to = mapTo
    if mapTo == 'LOCATION':
        transformationConstraint.to_min_x = toMinX
        transformationConstraint.to_max_x = toMaxX
        transformationConstraint.to_min_y = toMinY
        transformationConstraint.to_max_y = toMaxY
        transformationConstraint.to_min_z = toMinZ
        transformationConstraint.to_max_z = toMaxZ
        transformationConstraint.mix_mode = mixMode
    elif mapFrom == 'ROTATION':
        transformationConstraint.to_euler_order = toEulerOrder
        transformationConstraint.to_min_x_rot = toMinX
        transformationConstraint.to_max_x_rot = toMaxX
        transformationConstraint.to_min_y_rot = toMinY
        transformationConstraint.to_max_y_rot = toMaxY
        transformationConstraint.to_min_z_rot = toMinZ
        transformationConstraint.to_max_z_rot = toMaxZ
        transformationConstraint.mix_mode_rot = mixMode
    elif mapFrom == 'SCALE':
        transformationConstraint.to_min_x_scale = toMinX
        transformationConstraint.to_max_x_scale = toMaxX
        transformationConstraint.to_min_y_scale = toMinY
        transformationConstraint.to_max_y_scale = toMaxY
        transformationConstraint.to_min_z_scale = toMinZ
        transformationConstraint.to_max_z_scale = toMaxZ
        transformationConstraint.mix_mode_scale = mixMode
    transformationConstraint.map_to_x_from = mapToXFrom
    transformationConstraint.map_to_y_from = mapToYFrom
    transformationConstraint.map_to_z_from = mapToZFrom
    return transformationConstraint
        
def addLimitLocationConstraint(rig, boneName, subTargetBoneName, space, constraintName, 
useMinX, minX, useMaxX, maxX, useMinY, minY, useMaxY, maxY, useMinZ, minZ, useMaxZ, maxZ):
    removeConstraint(rig, boneName, constraintName)
    limitLocationConstraint = rig.pose.bones[boneName].constraints.new('LIMIT_LOCATION')
    limitLocationConstraint.name = constraintName
    limitLocationConstraint.owner_space = space
    if space == 'CUSTOM':
        limitLocationConstraint.space_object = rig
        limitLocationConstraint.space_subtarget = subTargetBoneName
    limitLocationConstraint.use_min_x = useMinX
    limitLocationConstraint.min_x = minX
    limitLocationConstraint.use_max_x = useMaxX
    limitLocationConstraint.max_x = maxX
    limitLocationConstraint.use_min_y = useMinY
    limitLocationConstraint.min_y = minY
    limitLocationConstraint.use_max_y = useMaxY
    limitLocationConstraint.max_y = maxY
    limitLocationConstraint.use_min_z = useMinZ
    limitLocationConstraint.min_z = minZ
    limitLocationConstraint.use_max_z = useMaxZ
    limitLocationConstraint.max_z = maxZ
    return limitLocationConstraint

def addLimitRotationConstraint(rig, boneName, subTargetBoneName, space, constraintName, 
useX, minX, maxX, useY, minY, maxY, useZ, minZ, maxZ):
    removeConstraint(rig, boneName, constraintName)
    limitRotationConstraint = rig.pose.bones[boneName].constraints.new('LIMIT_ROTATION')
    limitRotationConstraint.name = constraintName
    limitRotationConstraint.owner_space = space
    if space == 'CUSTOM':
        limitRotationConstraint.space_object = rig
        limitRotationConstraint.space_subtarget = subTargetBoneName
    limitRotationConstraint.use_limit_x = useX
    limitRotationConstraint.min_x = minX
    limitRotationConstraint.max_x = maxX
    limitRotationConstraint.use_limit_y = useY
    limitRotationConstraint.min_y = minY
    limitRotationConstraint.max_y = maxY
    limitRotationConstraint.use_limit_z = useZ
    limitRotationConstraint.min_z = minZ
    limitRotationConstraint.max_z = maxZ
    return limitRotationConstraint
    
def addArmatureConstraint(rig, boneName, subTargetBoneNames, constraintName):
    removeConstraint(rig, boneName, constraintName)
    armatureConstraint = rig.pose.bones[boneName].constraints.new('ARMATURE')
    armatureConstraint.name = constraintName
    for index, subTargetBoneName in enumerate(subTargetBoneNames):
        armatureConstraint.targets.new()
        armatureConstraint.targets[index].target = rig
        armatureConstraint.targets[index].subtarget = subTargetBoneName
    return armatureConstraint
        
def addDampedTrackConstraint(rig, boneName, subTargetBoneName, constraintName):
    removeConstraint(rig, boneName, constraintName)
    dampedTrackConstraint = rig.pose.bones[boneName].constraints.new('DAMPED_TRACK')
    dampedTrackConstraint.name = constraintName
    dampedTrackConstraint.target = rig
    dampedTrackConstraint.subtarget = subTargetBoneName
    return dampedTrackConstraint

class DriverVariable(NamedTuple):
    name: str
    type: str
    targetObject1: bpy.types.Object
    targetBone1: str
    targetTransformSpace1: str
    targetObject2: bpy.types.Object
    targetBone2: str
    targetTransformSpace2: str
    targetCustomPropertyDataPath: str
    targetTransformType: str
    targetRotationMode: str
    
def addDriver(object, objectProperty, objectPropertyCoordinateIndex, driverType, driverVariables, driverExpression):
    if objectPropertyCoordinateIndex:
        driver = object.driver_add(objectProperty, objectPropertyCoordinateIndex)
    else:
        driver = object.driver_add(objectProperty)
    driver.driver.type = driverType
    for driverVariable in driverVariables:
        variable = driver.driver.variables.new()
        variable.name = driverVariable.name
        variable.type = driverVariable.type
        variable.targets[0].id = driverVariable.targetObject1
        if driverVariable.targetCustomPropertyDataPath:
            variable.targets[0].data_path = driverVariable.targetCustomPropertyDataPath
        if driverVariable.targetBone1:
            variable.targets[0].bone_target = driverVariable.targetBone1
        if driverVariable.targetTransformSpace1:
            variable.targets[0].transform_space = driverVariable.targetTransformSpace1
        if driverVariable.targetTransformType:
            variable.targets[0].transform_type = driverVariable.targetTransformType
        if driverVariable.targetRotationMode:
            variable.targets[0].rotation_mode = driverVariable.targetRotationMode
        if driverVariable.targetObject2:
            variable.targets[1].id = driverVariable.targetObject2
        if driverVariable.targetBone2:
            variable.targets[1].bone_target = driverVariable.targetBone2
        if driverVariable.targetTransformSpace2   :
            variable.targets[1].transform_space = driverVariable.targetTransformSpace2
        if driverExpression:         
            driver.driver.expression = driverExpression
    return driver

def removeAllConstraints(rig, boneName):
        boneToMute = rig.pose.bones[boneName]
        for constraint in boneToMute.constraints:
            boneToMute.constraints.remove(constraint)
            
def removeAllDrivers(rig, boneName):
    if rig.animation_data:
        for driver in rig.animation_data.drivers:
            if driver.data_path.startswith("pose.bones"):
                ownerName = driver.data_path.split('"')[1]
                if ownerName == boneName:
                    rig.animation_data.drivers.remove(driver)
            
def createBone(rig, newBoneName):
    newBone = rig.data.edit_bones.new(newBoneName)
    newBone.head = (0, 1, 1) # if the head and tail are the same, the bone is deleted
    newBone.tail = (0, 1, 2)
    return newBone

def deleteBone(rig, boneName):
    bone = rig.data.edit_bones.get(boneName)
    removeAllConstraints(rig, boneName)
    removeAllDrivers(rig, boneName)
    rig.data.edit_bones.remove(bone)

def copyBone(rig, sourceBoneName, newBoneName):
    newBone = rig.data.edit_bones.get(newBoneName)
    if newBone is not None:
        deleteBone(rig, newBoneName)	  
    newBone = rig.data.edit_bones.new(newBoneName)
    sourceBone = rig.data.edit_bones.get(sourceBoneName)
    newBone.tail = sourceBone.tail
    newBone.head = sourceBone.head
    newBone.roll = sourceBone.roll
    newBone.parent = sourceBone.parent
    return newBone

def addBoneCustomProperty(rig, boneName, propertyName, propertyTooltip, propertyValue, propertyMinValue, propertyMaxValue):
    """ malfunctioning version
    bone = rig.pose.bones[boneName]
    bone[propertyName] = propertyValue
    if "_RNA_UI" not in bone.keys():
        bone["_RNA_UI"] = {}
    bone["_RNA_UI"].update({propertyName: {"description":propertyTooltip, "default":propertyValue, "min":propertyMinValue, "max":propertyMaxValue}})
    """
    rna_idprop_ui_create(rig.pose.bones[boneName], propertyName, default = propertyValue, min = propertyMinValue, max = propertyMaxValue, soft_min = None, soft_max = None, description = propertyTooltip)
    return 'pose.bones["' + boneName + '"]["' + propertyName + '"]'
        
def copyObject(collectionName, sourceObjectName, newObjectName):
    if newObjectName in bpy.context.scene.objects or newObjectName in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[newObjectName])
    sourceObject = bpy.data.objects[sourceObjectName]
    newObject = sourceObject.copy()
    newObject.data = sourceObject.data.copy()
    newObject.name = newObjectName
    bpy.data.collections[collectionName].objects.link(newObject)
    return newObject

def moveObjectOriginToBoneHead(objectName, rig, boneName): #doesn't work after transform changes
    bpy.context.view_layer.update() #updates matrices
    object = bpy.data.objects[objectName]
    globalBoneHeadLocation = rig.location + rig.pose.bones[boneName].head
    localBoneHeadLocation = object.matrix_world.inverted() @ globalBoneHeadLocation
    object.data.transform(Matrix.Translation(-localBoneHeadLocation))
    object.matrix_world.translation = object.matrix_world @ localBoneHeadLocation
    
def lockUnlockAllObjectTransforms(objectName, lock):
    object = bpy.data.objects[objectName]
    object.lock_location[0] = lock
    object.lock_location[1] = lock
    object.lock_location[2] = lock
    object.lock_rotation[0] = lock
    object.lock_rotation[1] = lock
    object.lock_rotation[2] = lock
    object.lock_scale[0] = lock
    object.lock_scale[1] = lock
    object.lock_scale[2] = lock
    
eyesPrimaryLayerBoneNames = [eyesHandleBoneName, leftEyeHandleBoneName, rightEyeHandleBoneName, riggedTongueBone1Name, riggedTongueBone2Name, 
riggedTongueBone3Name, riggedTongueBone4Name, riggedTongueBone5Name]
eyesSecondaryLayerBoneNames = [eyesTrackTargetBoneName, eyeballsBoneName, leftEyeballBoneName, rightEyeballBoneName, riggedTongueLeftBone3Name, 
riggedTongueRightBone3Name, riggedTongueLeftBone4Name, riggedTongueRightBone4Name, riggedTongueLeftBone5Name, riggedTongueRightBone5Name]
torsoLayerBoneNames = [headBoneName, headTrackTargetBoneName, neckBoneName, upperChestBoneName, chestBoneName, spineBoneName, 
hipsBoneName, pelvisBoneName, waistBoneName, buttocksHandleBoneName, leftButtockHandleBoneName, rightButtockHandleBoneName,
breastsHandleBoneName, leftBreastHandleBoneName, rightBreastHandleBoneName, leftShoulderBoneName, rightShoulderBoneName]
torsoTweakLayerBoneNames = [crotchBoneName, anusBoneName, leftBreastBone2Name, rightBreastBone2Name, leftBreastBone3Name,
rightBreastBone3Name, leftNippleBone1Name, rightNippleBone1Name, leftNippleBone2Name, rightNippleBone2Name, leftBreastDeformBone1Name, 
rightBreastDeformBone1Name, leftBreastDeformBone2Name, rightBreastDeformBone2Name, leftBreastDeformBone3Name, rightBreastDeformBone3Name, 
leftNippleDeformBone1Name, rightNippleDeformBone1Name, leftNippleDeformBone2Name, rightNippleDeformBone2Name, betterPenetrationRootCrotchBoneName, 
betterPenetrationFrontCrotchBoneName, betterPenetrationLeftCrotchBone1Name, betterPenetrationRightCrotchBone1Name, betterPenetrationLeftCrotchBone2Name, 
betterPenetrationRightCrotchBone2Name, betterPenetrationLeftCrotchBone3Name, betterPenetrationRightCrotchBone3Name, betterPenetrationLeftCrotchBone4Name, 
betterPenetrationRightCrotchBone4Name, betterPenetrationLeftCrotchBone5Name, betterPenetrationRightCrotchBone5Name, betterPenetrationBackCrotchBoneName]
leftArmIkLayerBoneNames = [leftArmBoneName, leftElbowBoneName, leftWristBoneName]
rightArmIkLayerBoneNames = [rightArmBoneName, rightElbowBoneName, rightWristBoneName]
leftLegIkLayerBoneNames = [leftLegBoneName, leftKneeBoneName, leftAnkleBoneName, leftToeBoneName, leftHeelBoneName]
rightLegIkLayerBoneNames = [rightLegBoneName, rightKneeBoneName, rightAnkleBoneName, rightToeBoneName, rightHeelBoneName]
fingersLayerBoneNames = [leftThumbBone1Name, rightThumbBone1Name, leftThumbBone2Name, rightThumbBone2Name, leftThumbBone3Name,
rightThumbBone3Name, leftIndexFingerPalmBoneName, rightIndexFingerPalmBoneName, leftIndexFingerBone1Name, rightIndexFingerBone1Name,
leftIndexFingerBone2Name, rightIndexFingerBone2Name, leftIndexFingerBone3Name, rightIndexFingerBone3Name, leftMiddleFingerPalmBoneName,
rightMiddleFingerPalmBoneName, leftMiddleFingerBone1Name, rightMiddleFingerBone1Name, leftMiddleFingerBone2Name, rightMiddleFingerBone2Name,
leftMiddleFingerBone3Name, rightMiddleFingerBone3Name, leftRingFingerPalmBoneName, rightRingFingerPalmBoneName, leftRingFingerBone1Name,
rightRingFingerBone1Name, leftRingFingerBone2Name, rightRingFingerBone2Name, leftRingFingerBone3Name, rightRingFingerBone3Name,
leftLittleFingerPalmBoneName, rightLittleFingerPalmBoneName, leftLittleFingerBone1Name, rightLittleFingerBone1Name, leftLittleFingerBone2Name,
rightLittleFingerBone2Name, leftLittleFingerBone3Name, rightLittleFingerBone3Name]

originalIkLayerIndex = 0
originalFkLayerIndex = 1
originalPrimaryJointCorrectionLayerIndex = 2
originalSecondaryJointCorrectionLayerIndex = 3
originalBetterPenetrationLayerIndex = 4
originalSkirtLayerIndex = 8
originalAccessoryLayerIndex = 9
originalMchLayerIndex = 10
originalPhysicsLayerIndex = 11
originalExtraLayerIndex = 12
originalUpperFaceLayerIndex = 16
originalLowerFaceLayerIndex = 17
originalRiggedTongueLayerIndex = 18

temporaryAccessoryMchLayerIndex = 7
temporaryFaceMchLayerIndex = 19
temporaryOriginalDeformLayerIndex = 26

detailLayerSuffix =  " (Detail)"
primaryLayerSuffix =  " (Primary)"
secondaryLayerSuffix =  " (Secondary)"
mchLayerSuffix =  " (MCH)"
tweakLayerSuffix = " (Tweak)"
ikLayerSuffix = " IK"
fkLayerSuffix = " FK"

hairLayerName = "Hair/Accessories"
eyesLayerName = "Eyes/Rig.Tongue"
faceLayerName = "Face"
torsoLayerName = "Torso"
leftArmLayerName = "Arm.L"
rightArmLayerName = leftNameToRightName(leftArmLayerName)
fingersLayerName = "Fingers"
leftLegLayerName = "Leg.L"
rightLegLayerName = leftNameToRightName(leftLegLayerName)
skirtLayerName = "Skirt"
junkLayerName = "Junk"
rootLayerName = "Root"
defLayerName = "DEF"
mchLayerName = "MCH"
orgLayerName = "ORG"

noneBoneGroupIndex = 0
rootBoneGroupIndex = 1
ikBoneGroupIndex = 2
specialBoneGroupIndex = 3
tweakBoneGroupIndex = 4
fkBoneGroupIndex = 5
extraBoneGroupIndex = 6

class RigifyLayer(NamedTuple):
        name: str
        row: int
        group: int
        
rigifyLayers = [
RigifyLayer(hairLayerName, 1, extraBoneGroupIndex),
RigifyLayer(hairLayerName + detailLayerSuffix, 2, fkBoneGroupIndex),
RigifyLayer(hairLayerName + mchLayerSuffix, 3, rootBoneGroupIndex),
RigifyLayer(eyesLayerName + primaryLayerSuffix, 4, extraBoneGroupIndex),
RigifyLayer(eyesLayerName + secondaryLayerSuffix, 5, fkBoneGroupIndex),
RigifyLayer(faceLayerName, 6, tweakBoneGroupIndex),
RigifyLayer(faceLayerName + mchLayerSuffix, 7, rootBoneGroupIndex),
RigifyLayer(torsoLayerName, 8, specialBoneGroupIndex),
RigifyLayer(torsoLayerName + detailLayerSuffix, 9, tweakBoneGroupIndex),
RigifyLayer(leftArmLayerName + ikLayerSuffix, 10, ikBoneGroupIndex),
RigifyLayer(leftArmLayerName + fkLayerSuffix, 11, fkBoneGroupIndex),
RigifyLayer(leftArmLayerName + tweakLayerSuffix, 12, tweakBoneGroupIndex),
RigifyLayer(rightArmLayerName + ikLayerSuffix, 10, ikBoneGroupIndex),
RigifyLayer(rightArmLayerName + fkLayerSuffix, 11, fkBoneGroupIndex),
RigifyLayer(rightArmLayerName + tweakLayerSuffix, 12, tweakBoneGroupIndex),
RigifyLayer(fingersLayerName, 13, extraBoneGroupIndex),
RigifyLayer(fingersLayerName + detailLayerSuffix, 14, fkBoneGroupIndex),
RigifyLayer(leftLegLayerName + ikLayerSuffix, 15, ikBoneGroupIndex),
RigifyLayer(leftLegLayerName + fkLayerSuffix, 16, fkBoneGroupIndex),
RigifyLayer(leftLegLayerName + tweakLayerSuffix, 17, tweakBoneGroupIndex),
RigifyLayer(rightLegLayerName + ikLayerSuffix, 15, ikBoneGroupIndex),
RigifyLayer(rightLegLayerName + fkLayerSuffix, 16, fkBoneGroupIndex),
RigifyLayer(rightLegLayerName + tweakLayerSuffix, 17, tweakBoneGroupIndex),
RigifyLayer(skirtLayerName, 18, extraBoneGroupIndex),
RigifyLayer(skirtLayerName + detailLayerSuffix, 19, fkBoneGroupIndex),
RigifyLayer("", 28, noneBoneGroupIndex),
RigifyLayer("", 28, noneBoneGroupIndex),
RigifyLayer(junkLayerName, 29, noneBoneGroupIndex)
]

rootLayerIndex = 28
rootLayerRow = 30
defLayerIndex = 29
defLayerRow = 31
mchLayerIndex = 30
mchLayerRow = 31
orgLayerIndex = 31
orgLayerRow = 31

def getRigifyLayerIndexByName(rigifyLayerName):
    for index, rigifyLayer in enumerate(rigifyLayers):
        if rigifyLayer.name == rigifyLayerName:
            return index

def setRigifyLayer(rig, index, rigifyLayer):
    if bpy.app.version[0] == 3:
        rig.data.rigify_layers[index].name = rigifyLayer.name
        rig.data.rigify_layers[index].row = rigifyLayer.row
        rig.data.rigify_layers[index].group = rigifyLayer.group
    else:
        if rig.data.collections_all.get(str(index)):
            rig.data.collections_all[str(index)].rigify_ui_title = rigifyLayer.name
            rig.data.collections_all[str(index)].rigify_ui_row = rigifyLayer.row
            rig.data.collections_all[str(index)].rigify_color_set_id = rigifyLayer.group
    
def setRootRigifyLayer(rig, boneGroupIndex):
    if bpy.app.version[0] == 3:
        rig.data.rigify_layers[rootLayerIndex].group = boneGroupIndex
    else:
        if rig.data.collections_all.get(str(rootLayerIndex)):
            rig.data.collections_all[str(rootLayerIndex)].rigify_color_set_id = boneGroupIndex

mmdOriginalBoneLayerName = "Original bones"        
mmdRenamedRequiredDictionaryLayerName = "Renamed required dictionary"
mmdRenamedWordDictionaryLayerName = "Renamed word dictionary"
mmdRenamedExtraDictionaryLayerName = "Renamed extra dictionary"
mmdRenamedMmdBoneLayerName = "Renamed mmd_bone"
mmdNotRenamedLayerName = "Not renamed"
mmdOriginalShadowLayerName = "Original shadow"
mmdOriginalDummyLayerName = "Original dummy"
mmdShadowLayerName = "Shadow"
mmdDummyLayerName = "Dummy"
mmdHiddenBonesLayerName = "Hidden bones"
mmdDeformBonesLayerName = "Deform bones"
mmdUsefulBonesLayerName = "Useful bones"
mmdUselessBonesLayerName = "Useless bones"
    
class BoneManagerLayer(NamedTuple):
        name: str
        row: int
        
mmdBoneManagerLayers = [
BoneManagerLayer(mmdOriginalBoneLayerName, 0),
BoneManagerLayer(mmdRenamedRequiredDictionaryLayerName, 1),
BoneManagerLayer(mmdRenamedWordDictionaryLayerName, 2),
BoneManagerLayer(mmdRenamedExtraDictionaryLayerName, 3),
BoneManagerLayer(mmdRenamedMmdBoneLayerName, 4),
BoneManagerLayer(mmdNotRenamedLayerName, 5),
BoneManagerLayer(mmdShadowLayerName, 6),
BoneManagerLayer(mmdDummyLayerName, 7),
BoneManagerLayer(mmdOriginalShadowLayerName, 8),
BoneManagerLayer(mmdOriginalDummyLayerName, 9),
BoneManagerLayer(mmdHiddenBonesLayerName, 10),
BoneManagerLayer(mmdDeformBonesLayerName, 11),
BoneManagerLayer(mmdUsefulBonesLayerName, 12),
BoneManagerLayer(mmdUselessBonesLayerName, 13),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28)
]

def getMmdBoneManagerLayerIndexByName(mmdBoneManagerLayerName):
    for index, mmdBoneManagerLayer in enumerate(mmdBoneManagerLayers):
        if mmdBoneManagerLayer.name == mmdBoneManagerLayerName:
            return index
        
koikatsuOriginalBoneLayerName = "Original bones"
koikatsuRetargetingBonesLayerName = "Retargeting bones"
koikatsuNonRetargetingBonesLayerName = "Non-retargeting bones"
koikatsuHiddenBonesLayerName = "Hidden bones"
koikatsuDeformBonesLayerName = "Deform bones"
koikatsuUsefulBonesLayerName = "Useful bones"
koikatsuUselessBonesLayerName = "Useless bones"

koikatsuBoneManagerLayers = [
BoneManagerLayer(koikatsuOriginalBoneLayerName, 0),
BoneManagerLayer(koikatsuRetargetingBonesLayerName, 1),
BoneManagerLayer(koikatsuNonRetargetingBonesLayerName, 2),
BoneManagerLayer(koikatsuHiddenBonesLayerName, 3),
BoneManagerLayer(koikatsuDeformBonesLayerName, 4),
BoneManagerLayer(koikatsuUsefulBonesLayerName, 5),
BoneManagerLayer(koikatsuUselessBonesLayerName, 6),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28),
BoneManagerLayer("", 28)
]

def getKoikatsuBoneManagerLayerIndexByName(koikatsuBoneManagerLayerName):
    for index, koikatsuBoneManagerLayer in enumerate(koikatsuBoneManagerLayers):
        if koikatsuBoneManagerLayer.name == koikatsuBoneManagerLayerName:
            return index
    
def setBoneManagerLayer(rig, layer, boneManagerLayer):
    bpy.data.armatures[rig.data.name]["layer_name_" + str(layer)] = boneManagerLayer.name
    bpy.data.armatures[rig.data.name]["rigui_id_" + str(layer)] = boneManagerLayer.row
    
def setBoneManagerLayersFromRigifyLayers(rig):
    for index, rigifyLayer in enumerate(rigifyLayers):
        if rigifyLayer.name != "":
            setBoneManagerLayer(rig, index, BoneManagerLayer(rigifyLayer.name, rigifyLayer.row))
    setBoneManagerLayer(rig, rootLayerIndex, BoneManagerLayer(rootLayerName, rootLayerRow))
    setBoneManagerLayer(rig, defLayerIndex, BoneManagerLayer(defLayerName, defLayerRow))
    setBoneManagerLayer(rig, mchLayerIndex, BoneManagerLayer(mchLayerName, mchLayerRow))
    setBoneManagerLayer(rig, orgLayerIndex, BoneManagerLayer(orgLayerName, orgLayerRow))
    
def assignSingleBoneLayer_except(rig, boneName, layerIndex):
    try:
        assignSingleBoneLayer(rig, boneName, layerIndex)
    except:
        pass
        #bone didn't exist

def assignSingleBoneLayer(rig, boneName, layerIndex):
    if bpy.app.version[0] == 3:
        original_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode = 'POSE')
        bone = rig.data.bones[boneName]
        bone.layers[layerIndex] = True
        for index in range(32):
            if index != layerIndex:
                bone.layers[index] = False
    else:
        original_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bone = rig.data.bones[boneName]
        bone.collections.clear()
        if rig.data.collections.get(str(layerIndex)):
            rig.data.collections[str(layerIndex)].assign(bone)
        else:
            rig.data.collections.new(str(layerIndex))
            rig.data.collections[str(layerIndex)].assign(bone)
    bpy.ops.object.mode_set(mode = original_mode)

def assignMultipleBoneLayer(rig, boneName, layerIndexes):
    if bpy.app.version[0] == 3:
        for layerIndex in layerIndexes:
            bone.layers[layerIndex] = True
        for index in range(32):
            if index not in layerIndexes:
                bone.layers[index] = False
    else:
        original_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bone = rig.data.bones[boneName]
        bone.collections.clear()
        for layerIndex in layerIndexes:
            if rig.data.collections.get(str(layerIndex)):
                rig.data.collections[str(layerIndex)].assign(bone)
            else:
                rig.data.collections.new(str(layerIndex))
                rig.data.collections[str(layerIndex)].assign(bone)
        bpy.ops.object.mode_set(mode = original_mode)

            
def assignSingleBoneLayerToList(rig, boneNamesList, layerIndex):
    for boneName in boneNamesList:
        assignSingleBoneLayer(rig, boneName, layerIndex)
        
def getDeformBoneNames(rig):
    deformBoneNames = []
    for obj in bpy.context.scene.objects: 
        if obj.type == 'MESH':
            me = obj.data
            bm = bmesh.new()
            bm.from_mesh(me)
            #groupIndex = obj.vertex_groups.active_index
            dvertLay = bm.verts.layers.deform.active
            vgIndexes = []
            if dvertLay is not None:
                for vert in bm.verts:
                    dvert = vert[dvertLay]
                    for tuple in dvert.items():
                        if tuple[1] != 0 and tuple[0] not in vgIndexes:
                            vgIndexes.append(tuple[0])
                            indexBone = rig.pose.bones.get(obj.vertex_groups[tuple[0]].name)
                            if indexBone is not None and indexBone.name not in deformBoneNames:
                                deformBoneNames.append(indexBone.name)
    return deformBoneNames

def getRelatedBoneNames(rig, boneName):
    relatedBoneNames = []
    bone = rig.pose.bones[boneName]                          
    if bone.parent and bone.parent.name not in relatedBoneNames and rig.pose.bones.get(bone.parent.name):
        relatedBoneNames.append(bone.parent.name)
    for constraint in bone.constraints:
        try:
            if constraint.subtarget not in relatedBoneNames and rig.pose.bones.get(constraint.subtarget):
                relatedBoneNames.append(constraint.subtarget)
        except AttributeError as ex:
            pass
    if rig.animation_data:
        for driver in rig.animation_data.drivers:
            if driver.data_path.startswith("pose.bones"):
                ownerName = driver.data_path.split('"')[1]
                if ownerName == boneName:
                    for variable in driver.driver.variables:
                        for target in variable.targets:
                            if target.bone_target not in relatedBoneNames and rig.pose.bones.get(target.bone_target):
                                relatedBoneNames.append(target.bone_target)
    return relatedBoneNames
        
def lockAllPoseTransforms(rig, boneName):
    rig.pose.bones[boneName].lock_location[0] = True
    rig.pose.bones[boneName].lock_location[1] = True
    rig.pose.bones[boneName].lock_location[2] = True
    rig.pose.bones[boneName].lock_rotation[0] = True
    rig.pose.bones[boneName].lock_rotation[1] = True
    rig.pose.bones[boneName].lock_rotation[2] = True
    rig.pose.bones[boneName].lock_rotation_w = True
    rig.pose.bones[boneName].lock_scale[0] = True
    rig.pose.bones[boneName].lock_scale[1] = True
    rig.pose.bones[boneName].lock_scale[2] = True
                
bonesWithDrivers = [
waistJointCorrectionBoneName,
leftButtockJointCorrectionBoneName, 
rightButtockJointCorrectionBoneName,
leftShoulderJointCorrectionBoneName, 
rightShoulderJointCorrectionBoneName, 
backLeftElbowJointCorrectionBoneName,   
backRightElbowJointCorrectionBoneName,
frontLeftElbowJointCorrectionBoneName, 
frontRightElbowJointCorrectionBoneName,
leftWristJointCorrectionBoneName, 
rightWristJointCorrectionBoneName,
leftLegJointCorrectionBoneName, 
rightLegJointCorrectionBoneName, 
backRightKneeJointCorrectionBoneName, 
backLeftKneeJointCorrectionBoneName, 
frontLeftKneeJointCorrectionBoneName,
frontRightKneeJointCorrectionBoneName
]

driverTargets = [leftKneeBoneName, rightKneeBoneName, leftLegBoneName, rightLegBoneName, leftWristBoneName, rightWristBoneName, leftElbowBoneName, rightElbowBoneName, leftArmBoneName, rightArmBoneName, waistBoneName]

targetsToChange = [leftArmBoneName, rightArmBoneName, leftElbowBoneName, rightElbowBoneName, leftLegBoneName, rightLegBoneName, leftKneeBoneName, rightKneeBoneName]

def setBoneCustomShapeScale(rig, boneName, scale):
    if bpy.app.version[0] < 3:
        rig.pose.bones[boneName].custom_shape_scale = scale
    else:
        rig.pose.bones[boneName].custom_shape_scale_xyz = [scale, scale, scale]

japHalfToFullTuples = (
('ｳﾞ', 'ヴ'), ('ｶﾞ', 'ガ'), ('ｷﾞ', 'ギ'), ('ｸﾞ', 'グ'), ('ｹﾞ', 'ゲ'),
('ｺﾞ', 'ゴ'), ('ｻﾞ', 'ザ'), ('ｼﾞ', 'ジ'), ('ｽﾞ', 'ズ'), ('ｾﾞ', 'ゼ'),
('ｿﾞ', 'ゾ'), ('ﾀﾞ', 'ダ'), ('ﾁﾞ', 'ヂ'), ('ﾂﾞ', 'ヅ'), ('ﾃﾞ', 'デ'),
('ﾄﾞ', 'ド'), ('ﾊﾞ', 'バ'), ('ﾊﾟ', 'パ'), ('ﾋﾞ', 'ビ'), ('ﾋﾟ', 'ピ'),
('ﾌﾞ', 'ブ'), ('ﾌﾟ', 'プ'), ('ﾍﾞ', 'ベ'), ('ﾍﾟ', 'ペ'), ('ﾎﾞ', 'ボ'),
('ﾎﾟ', 'ポ'), ('｡', '。'), ('｢', '「'), ('｣', '」'), ('､', '、'),
('･', '・'), ('ｦ', 'ヲ'), ('ｧ', 'ァ'), ('ｨ', 'ィ'), ('ｩ', 'ゥ'),
('ｪ', 'ェ'), ('ｫ', 'ォ'), ('ｬ', 'ャ'), ('ｭ', 'ュ'), ('ｮ', 'ョ'),
('ｯ', 'ッ'), ('ｰ', 'ー'), ('ｱ', 'ア'), ('ｲ', 'イ'), ('ｳ', 'ウ'),
('ｴ', 'エ'), ('ｵ', 'オ'), ('ｶ', 'カ'), ('ｷ', 'キ'), ('ｸ', 'ク'),
('ｹ', 'ケ'), ('ｺ', 'コ'), ('ｻ', 'サ'), ('ｼ', 'シ'), ('ｽ', 'ス'),
('ｾ', 'セ'), ('ｿ', 'ソ'), ('ﾀ', 'タ'), ('ﾁ', 'チ'), ('ﾂ', 'ツ'),
('ﾃ', 'テ'), ('ﾄ', 'ト'), ('ﾅ', 'ナ'), ('ﾆ', 'ニ'), ('ﾇ', 'ヌ'),
('ﾈ', 'ネ'), ('ﾉ', 'ノ'), ('ﾊ', 'ハ'), ('ﾋ', 'ヒ'), ('ﾌ', 'フ'),
('ﾍ', 'ヘ'), ('ﾎ', 'ホ'), ('ﾏ', 'マ'), ('ﾐ', 'ミ'), ('ﾑ', 'ム'),
('ﾒ', 'メ'), ('ﾓ', 'モ'), ('ﾔ', 'ヤ'), ('ﾕ', 'ユ'), ('ﾖ', 'ヨ'),
('ﾗ', 'ラ'), ('ﾘ', 'リ'), ('ﾙ', 'ル'), ('ﾚ', 'レ'), ('ﾛ', 'ロ'),
('ﾜ', 'ワ'), ('ﾝ', 'ン')
)

def fixJapChars(name):
    for values in japHalfToFullTuples:
        if values[0] in name:
            name = name.replace(values[0], values[1])
    return name

japEngRequiredBoneNamesDictionary = {
'全ての親':'mother',
'グルーブ':'groove',
'センター':'center',
'上半身':'upper body',
'上半身2':'upper body 2',
'首':'neck',
'頭':'head',
'左目':'eye L',
'下半身':'lower body',
'左肩':'shoulder L',
'左腕':'arm L',
'左ひじ':'elbow L',
'左手首':'wrist L',
'左親指０':'thumb0L',
'左親指１':'thumb1L',
'左親指２':'thumb2L',
'左人指１':'fore1L',
'左人指２':'fore2L',
'左人指３':'fore3L',
'左中指１':'middle1L',
'左中指２':'middle2L',
'左中指３':'middle3L',
'左薬指１':'third1L',
'左薬指２':'third2L',
'左薬指３':'third3L',
'左小指１':'little1L',
'左小指２':'little2L',
'左小指３':'little3L',
'左足':'legL',
'左ひざ':'kneeL',
'左足首':'ankleL',
'両目':'eyes',
'右目':'eye R',
'右肩':'shoulderR',
'右腕':'armR',
'右ひじ':'elbowR',
'右手首':'wristR',
'右親指０':'thumb0R',
'右親指１':'thumb1R',
'右親指２':'thumb2R',
'右人指１':'fore1R',
'右人指２':'fore2R',
'右人指３':'fore3R',
'右中指１':'middle1R',
'右中指２':'middle2R',
'右中指３':'middle3R',
'右薬指１':'third1R',
'右薬指２':'third2R',
'右薬指３':'third3R',
'右小指１':'little1R',
'右小指２':'little2R',
'右小指３':'little3R',
'右足':'legR',
'右ひざ':'kneeR',
'右足首':'ankleR',
'左足ＩＫ':'leg IK L',
'左つま先ＩＫ':'toe IK L',
'右足ＩＫ':'leg IK R',
'右つま先ＩＫ':'toe IK R'
}

japEngWordsDictionaryFileName = "dictionary.json"

def loadJsonDictionaryFile(filePath, fileName):
    dictionaryFile = os.path.join(filePath, fileName)
    with open(dictionaryFile, encoding="utf8") as file:
        return json.load(file, object_pairs_hook=collections.OrderedDict)

japEngExtraBoneNamesDictionary = {
'テール1':'tail 1',
'テール2':'tail 2'
}

japCharactersRegex = u'[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff\uff00-\uff9f\u4e00-\u9faf\u3400-\u4dbf]+'  # Regex to look for japanese chars

def getContainedJapCharacters(string):
    return re.findall(japCharactersRegex, string)

koikatsuRetargetingBoneNames = [
"cf_j_hips",
"cf_j_spine01",
"cf_j_spine02",
"cf_j_spine03",
"cf_j_arm00_L",
"cf_j_forearm01_L",
"cf_j_hand_L",
"cf_j_index01_L",
"cf_j_index02_L",
"cf_j_index03_L",
"cf_j_little01_L",
"cf_j_little02_L",
"cf_j_little03_L",
"cf_j_middle01_L",
"cf_j_middle02_L",
"cf_j_middle03_L",
"cf_j_ring01_L",
"cf_j_ring02_L",
"cf_j_ring03_L",
"cf_j_thumb01_L",
"cf_j_thumb02_L",
"cf_j_thumb03_L",
"cf_j_arm00_R",
"cf_j_forearm01_R",
"cf_j_hand_R",
"cf_j_index01_R",
"cf_j_index02_R",
"cf_j_index03_R",
"cf_j_little01_R",
"cf_j_little02_R",
"cf_j_little03_R",
"cf_j_middle01_R",
"cf_j_middle02_R",
"cf_j_middle03_R",
"cf_j_ring01_R",
"cf_j_ring02_R",
"cf_j_ring03_R",
"cf_j_thumb01_R",
"cf_j_thumb02_R",
"cf_j_thumb03_R",
"cf_j_neck",
"cf_j_head",
"cf_j_waist01",
"cf_j_thigh00_L",
"cf_j_leg01_L",
"cf_j_foot_L",
"cf_j_toes_L",
"cf_j_thigh00_R",
"cf_j_leg01_R",
"cf_j_foot_R",
"cf_j_toes_R",
"cf_j_shoulder_L",
"cf_j_shoulder_R",
"cf_j_kokan",
"cf_j_ana",
"cf_j_waist02",
"cf_j_siri_L",
"cf_j_siri_R",
"cf_j_bust01_L",
"cf_j_bust01_R",
"cf_j_bust02_L",
"cf_j_bust02_R",
"cf_j_bust03_L",
"cf_j_bust03_R",
"cf_j_bnip02root_L",
"cf_j_bnip02root_R",
"cf_j_bnip02_L",
"cf_j_bnip02_R"
]

autoRigProCopyRotationConstraintName = "Copy RotationREMAP"
autoRigProCopyScaleConstraintName = "Copy ScaleREMAP"
