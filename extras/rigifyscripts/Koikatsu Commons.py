import bpy
from typing import NamedTuple
import mathutils
from mathutils import Matrix

leftNamePrefix = "Left "
rightNamePrefix = "Right "
leftNameSuffix1 = "_L"
rightNameSuffix1 = "_R"
leftNameSuffix2 = ".L"
rightNameSuffix2 = ".R"

def leftNameToRightName(leftName):
    if leftName.startswith(leftNamePrefix):
        leftName = rightNamePrefix + leftName[len(leftNamePrefix):]
    if leftName.endswith(leftNameSuffix1):
        leftName = leftName[:len(leftName) - len(leftNameSuffix1)] + rightNameSuffix1
    if leftName.endswith(leftNameSuffix2):
        leftName = leftName[:len(leftName) - len(leftNameSuffix2)] + rightNameSuffix2
    return leftName

bodyName = "Body"

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

originalRootBoneName = "Center"
originalRootUpperBoneName = "cf_pv_root_upper"
rootBoneName = "root"
eyesXBoneName = "Eyesx"
originalEyesBoneName = "Eye Controller"
eyesBoneName = "Eyes target";
leftEyeBoneName = "Left eye target"
rightEyeBoneName = leftNameToRightName(leftEyeBoneName)
eyesHandleBoneName = "Eyes" + handleBoneSuffix
leftEyeHandleBoneName = "Left eye" + handleBoneSuffix
rightEyeHandleBoneName = leftNameToRightName(leftEyeHandleBoneName)
headBoneName = "Head"
neckBoneName = "Neck"
upperChestBoneName = "Upper Chest"
chestBoneName = "Chest"
spineBoneName = "Spine"
hipsBoneName = "Hips"
pelvisBoneName = "Pelvis"
waistBoneName = "cf_j_waist02"
crotchBoneName = "cf_j_kokan"
anusBoneName = "cf_j_ana"
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
skirtParentBoneCopyName = skirtParentBoneName + " copy"
skirtBonePrefix = "cf_j_sk"

def getSkirtBoneName(palm, primaryIndex, secondaryIndex = 0):
    if palm:
        prefix = skirtPalmBonePrefix
    else:
        prefix = skirtBonePrefix
    return prefix + "_" + str(primaryIndex).zfill(2) + "_" + str(secondaryIndex).zfill(2)
    
targetsToChange = [leftArmBoneName, rightArmBoneName, leftElbowBoneName, rightElbowBoneName, leftLegBoneName, rightLegBoneName, leftKneeBoneName, rightKneeBoneName]

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

leftButtockJointCorrectionBoneName = "cf_d_siri_L"
rightButtockJointCorrectionBoneName = leftNameToRightName(leftButtockJointCorrectionBoneName)
frontLeftElbowJointCorrectionBoneName = "cf_s_elbo_L";
frontRightElbowJointCorrectionBoneName = leftNameToRightName(frontLeftElbowJointCorrectionBoneName)
midLeftElbowJointCorrectionBoneName = "cf_s_forearm01_L"
midRightElbowJointCorrectionBoneName = leftNameToRightName(midLeftElbowJointCorrectionBoneName)
backLeftElbowJointCorrectionBoneName = "cf_s_elboback_L";
backRightElbowJointCorrectionBoneName = leftNameToRightName(backLeftElbowJointCorrectionBoneName)
leftWristJointCorrectionBoneName = "cf_d_hand_L"
rightWristJointCorrectionBoneName = leftNameToRightName(leftWristJointCorrectionBoneName)
frontLeftKneeJointCorrectionBoneName = "cf_d_kneeF_L";
frontRightKneeJointCorrectionBoneName = leftNameToRightName(frontLeftKneeJointCorrectionBoneName)
midLeftKneeJointCorrectionBoneName = "cf_s_leg01_L"
midRightKneeJointCorrectionBoneName = leftNameToRightName(midLeftKneeJointCorrectionBoneName)
backLeftKneeJointCorrectionBoneName = "cf_s_kneeB_L";
backRightKneeJointCorrectionBoneName = leftNameToRightName(backLeftKneeJointCorrectionBoneName)

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
handleConstraintSuffix = "_Handle"
jointCorrectionConstraintSuffix = "_Joint Correction"

def addCopyTransformsConstraint(rig, boneName, subTargetBoneName, mixMode, space, constraintName):
    copyTransformsConstraintName = constraintName
    copyTransformsConstraint = rig.pose.bones[boneName].constraints.get(copyTransformsConstraintName)
    if copyTransformsConstraint:
        rig.pose.bones[boneName].constraints.remove(copyTransformsConstraint)
    copyTransformsConstraint = rig.pose.bones[boneName].constraints.new('COPY_TRANSFORMS')
    copyTransformsConstraint.name = copyTransformsConstraintName
    copyTransformsConstraint.target = rig
    copyTransformsConstraint.subtarget = subTargetBoneName
    copyTransformsConstraint.mix_mode = mixMode
    copyTransformsConstraint.owner_space = space
    copyTransformsConstraint.target_space = space

def removeAllConstraints(rig, boneName):
        boneToMute = rig.pose.bones[boneName]
        for constraint in boneToMute.constraints:
            boneToMute.constraints.remove(constraint)
            
def deleteBone(rig, boneName):
    bone = rig.data.edit_bones.get(boneName)
    removeAllConstraints(rig, boneName)
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

def copyObject(collectionName, sourceObjectName, newObjectName):
    if newObjectName in bpy.context.scene.objects or newObjectName in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[newObjectName])
    sourceObject = bpy.data.objects[sourceObjectName]
    newObject = sourceObject.copy()
    newObject.data = sourceObject.data.copy()
    newObject.name = newObjectName
    bpy.data.collections[collectionName].objects.link(newObject)
    return newObject

def moveObjectOriginToBoneHead(objectName, rig, boneName):
    bpy.context.view_layer.update() #updates matrices
    object = bpy.data.objects[objectName]
    globalBoneHeadLocation = rig.location + rig.pose.bones[boneName].head
    localBoneHeadLocation = object.matrix_world.inverted() @ globalBoneHeadLocation
    object.data.transform(Matrix.Translation(-localBoneHeadLocation))
    object.matrix_world.translation = object.matrix_world @ localBoneHeadLocation
    
faceLayerBoneNames = [eyesHandleBoneName, leftEyeHandleBoneName, rightEyeHandleBoneName]
torsoLayerBoneNames = [headBoneName, neckBoneName, upperChestBoneName, chestBoneName, spineBoneName, 
hipsBoneName, pelvisBoneName, waistBoneName, buttocksHandleBoneName, leftButtockHandleBoneName, rightButtockHandleBoneName,
breastsHandleBoneName, leftBreastHandleBoneName, rightBreastHandleBoneName, leftShoulderBoneName, rightShoulderBoneName]
torsoTweakLayerBoneNames = [crotchBoneName, anusBoneName, leftBreastBone2Name, rightBreastBone2Name, leftBreastBone3Name,
rightBreastBone3Name, leftNippleBone1Name, rightNippleBone1Name, leftNippleBone2Name, rightNippleBone2Name, leftBreastDeformBone1Name, 
rightBreastDeformBone1Name, leftBreastDeformBone2Name, rightBreastDeformBone2Name, leftBreastDeformBone3Name, rightBreastDeformBone3Name, 
leftNippleDeformBone1Name, rightNippleDeformBone1Name, leftNippleDeformBone2Name, rightNippleDeformBone2Name]
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

temporaryAccessoryMchLayerIndex = 7
temporaryFaceMchLayerIndex = 18
temporaryOriginalDeformLayerIndex = 26

detailLayerSuffix =  " (Detail)"
mchLayerSuffix =  " (MCH)"
tweakLayerSuffix = " (Tweak)"
ikLayerSuffix = " IK"
fkLayerSuffix = " FK"

hairLayerName = "Hair/Accessories"
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
RigifyLayer(faceLayerName, 4, fkBoneGroupIndex),
RigifyLayer(faceLayerName + mchLayerSuffix, 5, rootBoneGroupIndex),
RigifyLayer(torsoLayerName, 6, specialBoneGroupIndex),
RigifyLayer(torsoLayerName + tweakLayerSuffix, 7, tweakBoneGroupIndex),
RigifyLayer(leftArmLayerName + ikLayerSuffix, 8, ikBoneGroupIndex),
RigifyLayer(leftArmLayerName + fkLayerSuffix, 9, fkBoneGroupIndex),
RigifyLayer(leftArmLayerName + tweakLayerSuffix, 10, tweakBoneGroupIndex),
RigifyLayer(rightArmLayerName + ikLayerSuffix, 8, ikBoneGroupIndex),
RigifyLayer(rightArmLayerName + fkLayerSuffix, 9, fkBoneGroupIndex),
RigifyLayer(rightArmLayerName + tweakLayerSuffix, 10, tweakBoneGroupIndex),
RigifyLayer(fingersLayerName, 11, extraBoneGroupIndex),
RigifyLayer(fingersLayerName + detailLayerSuffix, 12, fkBoneGroupIndex),
RigifyLayer(leftLegLayerName + ikLayerSuffix, 13, ikBoneGroupIndex),
RigifyLayer(leftLegLayerName + fkLayerSuffix, 14, fkBoneGroupIndex),
RigifyLayer(leftLegLayerName + tweakLayerSuffix, 15, tweakBoneGroupIndex),
RigifyLayer(rightLegLayerName + ikLayerSuffix, 13, ikBoneGroupIndex),
RigifyLayer(rightLegLayerName + fkLayerSuffix, 14, fkBoneGroupIndex),
RigifyLayer(rightLegLayerName + tweakLayerSuffix, 15, tweakBoneGroupIndex),
RigifyLayer(skirtLayerName, 16, extraBoneGroupIndex),
RigifyLayer(skirtLayerName + detailLayerSuffix, 17, fkBoneGroupIndex),
RigifyLayer("", 28, noneBoneGroupIndex),
RigifyLayer("", 28, noneBoneGroupIndex),
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
    rig.data.rigify_layers[index].name = rigifyLayer.name
    rig.data.rigify_layers[index].row = rigifyLayer.row
    rig.data.rigify_layers[index].group = rigifyLayer.group
    
def setRootRigifyLayer(rig, boneGroupIndex):
    rig.data.rigify_layers[rootLayerIndex].group = boneGroupIndex
    
def setBoneManagerLayer(rig, layerIndex, layerName, layerRow):
    bpy.data.armatures[rig.data.name]["layer_name_" + str(layerIndex)] = layerName
    bpy.data.armatures[rig.data.name]["rigui_id_" + str(layerIndex)] = layerRow
    
def setBoneManagerLayersFromRigifyLayers(rig):
    for index, rigifyLayer in enumerate(rigifyLayers):
        if rigifyLayer.name != "":
            setBoneManagerLayer(rig, index, rigifyLayer.name, rigifyLayer.row)
    setBoneManagerLayer(rig, rootLayerIndex, rootLayerName, rootLayerRow)
    setBoneManagerLayer(rig, defLayerIndex, defLayerName, defLayerRow)
    setBoneManagerLayer(rig, mchLayerIndex, mchLayerName, mchLayerRow)
    setBoneManagerLayer(rig, orgLayerIndex, orgLayerName, orgLayerRow)

    
def assignSingleBoneLayer(rig, boneName, layerIndex):
    bone = rig.data.bones[boneName]
    bone.layers[layerIndex] = True
    for index in range(32):
        if index != layerIndex:
            bone.layers[index] = False
            
def assignSingleBoneLayerToList(rig, boneNamesList, layerIndex):
    for boneName in boneNamesList:
        assignSingleBoneLayer(rig, boneName, layerIndex)
        
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
backRightKneeJointCorrectionBoneName, 
backLeftKneeJointCorrectionBoneName, 
frontLeftKneeJointCorrectionBoneName,
frontRightKneeJointCorrectionBoneName,
leftButtockJointCorrectionBoneName, 
rightButtockJointCorrectionBoneName, 
leftWristJointCorrectionBoneName, 
rightWristJointCorrectionBoneName,
backLeftElbowJointCorrectionBoneName,   
backRightElbowJointCorrectionBoneName,
frontLeftElbowJointCorrectionBoneName, 
frontRightElbowJointCorrectionBoneName,
"cf_d_leftShoulder02_L", 
"cf_d_leftShoulder02_R", 
"cf_s_leg_L", 
"cf_s_leg_R", 
"cf_s_waist02"]

driverTargets = [leftKneeBoneName, rightKneeBoneName, leftLegBoneName, rightLegBoneName, leftWristBoneName, rightWristBoneName, leftElbowBoneName, rightElbowBoneName, leftArmBoneName, rightArmBoneName, waistBoneName]

def setBoneCustomShapeScale(rig, boneName, scale):
    if bpy.app.version[0] < 3:
        rig.pose.bones[boneName].custom_shape_scale = scale
    else:
        rig.pose.bones[boneName].custom_shape_scale_xyz = [scale, scale, scale]
