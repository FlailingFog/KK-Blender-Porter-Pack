
#Switch to Object Mode and select Metarig

import bpy
from typing import NamedTuple
import math
from math import radians
import statistics
from mathutils import Matrix, Vector, Euler
import traceback
import sys
from . import commons as koikatsuCommons	
    
def main():
    metarig = bpy.context.active_object

    assert metarig.mode == "OBJECT", 'assert metarig.mode == "OBJECT"'
    assert metarig.type == "ARMATURE", 'assert metarig.type == "ARMATURE"'
    
    metarig.show_in_front = True
    metarig.display_type = 'TEXTURED'
    metarig.data.display_type = 'OCTAHEDRAL'
    
    reservedBoneNames = [koikatsuCommons.rootBoneName, koikatsuCommons.torsoBoneName, koikatsuCommons.headTweakBoneName]
    
    def fixReservedBoneName(rig, boneName):
        bone = metarig.pose.bones.get(koikatsuCommons.rootBoneName)
        if bone is not None:
            bone.name = bone.name + koikatsuCommons.renamedNameSuffix
    
    for boneName in reservedBoneNames:
        fixReservedBoneName(metarig, boneName)
                
    def fixDuplicateBoneName(rig, boneName, childBoneName):
        childBone = metarig.pose.bones.get(childBoneName)
        if childBone.parent.name != boneName:
            metarig.pose.bones.get(boneName).name = boneName + koikatsuCommons.renamedNameSuffix
            metarig.pose.bones.get(childBone.parent.name).name = boneName
    
    fixDuplicateBoneName(metarig, koikatsuCommons.headBoneName, koikatsuCommons.originalEyesBoneName)
    fixDuplicateBoneName(metarig, koikatsuCommons.neckBoneName, koikatsuCommons.headBoneName)
    fixDuplicateBoneName(metarig, koikatsuCommons.upperChestBoneName, koikatsuCommons.neckBoneName)
    fixDuplicateBoneName(metarig, koikatsuCommons.chestBoneName, koikatsuCommons.upperChestBoneName)
    fixDuplicateBoneName(metarig, koikatsuCommons.spineBoneName, koikatsuCommons.chestBoneName)
    fixDuplicateBoneName(metarig, koikatsuCommons.hipsBoneName, koikatsuCommons.spineBoneName)
    
    selectedLayers = []
    for i in range(32):
        if metarig.data.collections.get(str(i)) == True:
            selectedLayers.append(i)
        if i == koikatsuCommons.originalIkLayerIndex:
            if metarig.data.collections.get(str(i)):
                metarig.data.collections.get(str(i)).is_visible = True
        else:
            if metarig.data.collections.get(str(i)):
                metarig.data.collections.get(str(i)).is_visible = False
            
    hasSkirt = True    
    if koikatsuCommons.skirtParentBoneName not in metarig.pose.bones:
        hasSkirt = False
    else:
        for primaryIndex in range(8):
            if koikatsuCommons.getSkirtBoneName(True, primaryIndex) not in metarig.pose.bones:
                hasSkirt = False
                break
            for secondaryIndex in range(6):
                if koikatsuCommons.getSkirtBoneName(False, primaryIndex, secondaryIndex) not in metarig.pose.bones:
                    hasSkirt = False
                    break
    
    hasRiggedTongue = metarig.pose.bones.get(koikatsuCommons.riggedTongueBone1Name) and bpy.data.objects.get(koikatsuCommons.riggedTongueName)
    hasBetterPenetrationMod = metarig.pose.bones.get(koikatsuCommons.betterPenetrationRootCrotchBoneName)
    hasHeadMod = koikatsuCommons.isVertexGroupEmpty(koikatsuCommons.originalFaceUpDeformBoneName, koikatsuCommons.bodyName)
    isMale = koikatsuCommons.isVertexGroupEmpty(koikatsuCommons.leftNippleDeformBone1Name, koikatsuCommons.bodyName)

    def objToBone(obj, rig, boneName):
        """ 
        Places an object at the location/rotation/scale of the given bone.
        """
        assert bpy.context.mode != 'EDIT_ARMATURE', "assert bpy.context.mode != 'EDIT_ARMATURE'"

        bone = rig.pose.bones[boneName]
        if bpy.app.version[0] < 3:
            scale = bone.custom_shape_scale
        else:
            loc = bone.custom_shape_translation
            rot = bone.custom_shape_rotation_euler
            scale = Vector(bone.custom_shape_scale_xyz)

        if bone.use_custom_shape_bone_size:
            scale *= bone.length

        obj.rotation_mode = 'XYZ'
        
        if bpy.app.version[0] < 3:
            obj.matrix_basis = rig.matrix_world @ bone.bone.matrix_local @ Matrix.Scale(scale, 4)
        else:
            shape_mat = Matrix.LocRotScale(loc, Euler(rot), scale)
            obj.matrix_basis = rig.matrix_world @ bone.bone.matrix_local @ shape_mat

    def createWidget(objName, collectionName, rig, boneName):
        """ 
        Creates an empty widget object and returns the object.
        """
        scene = bpy.context.scene
        
        # Delete object if it already exists in the scene or if it exists
        # in blend data but not scene data.
        # This is necessary so we can then create the object without
        # name conflicts.
        if objName in scene.objects or objName in bpy.data.objects:
            obj = bpy.data.objects[objName]
            #obj.user_clear() #gives errors/crashes
            bpy.data.objects.remove(obj)

        # Create mesh object
        mesh = bpy.data.meshes.new(objName)
        obj = bpy.data.objects.new(objName, mesh)
        #scene.objects.link(obj)
        bpy.data.collections[collectionName].objects.link(obj)
        objToBone(obj, rig, boneName)
        return obj
        
    def createEyeWidget(objName, collectionName, rig, boneName, size = 1.0):
        obj = createWidget(objName, collectionName, rig, boneName)
        if obj is not None:
            verts = [(1.1920928955078125e-07*size, 0.5000000596046448*size, 0.0*size), (-0.12940943241119385*size, 0.482962965965271*size, 0.0*size), (-0.24999988079071045*size, 0.4330127537250519*size, 0.0*size), (-0.35355329513549805*size, 0.35355344414711*size, 0.0*size), (-0.43301260471343994*size, 0.2500000596046448*size, 0.0*size), (-0.4829627275466919*size, 0.12940959632396698*size, 0.0*size), (-0.49999988079071045*size, 1.0094120739267964e-07*size, 0.0*size), (-0.482962965965271*size, -0.12940940260887146*size, 0.0*size), (-0.43301260471343994*size, -0.24999986588954926*size, 0.0*size), (-0.3535534143447876*size, -0.35355323553085327*size, 0.0*size), (-0.25*size, -0.43301257491111755*size, 0.0*size), (-0.1294095516204834*size, -0.48296281695365906*size, 0.0*size), (-1.1920928955078125e-07*size, -0.4999999403953552*size, 0.0*size), (0.12940943241119385*size, -0.4829629063606262*size, 0.0*size), (0.24999988079071045*size, -0.4330127537250519*size, 0.0*size), (0.35355329513549805*size, -0.35355353355407715*size, 0.0*size), (0.4330127239227295*size, -0.25000008940696716*size, 0.0*size), (0.482962965965271*size, -0.12940965592861176*size, 0.0*size), (0.5000001192092896*size, -1.6926388468618825e-07*size, 0.0*size), (0.48296308517456055*size, 0.1294093281030655*size, 0.0*size), (0.4330129623413086*size, 0.24999980628490448*size, 0.0*size), (0.35355377197265625*size, 0.35355323553085327*size, 0.0*size), (0.25000035762786865*size, 0.43301260471343994*size, 0.0*size), (0.1294100284576416*size, 0.48296287655830383*size, 0.0*size), ]
            edges = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (8, 7), (9, 8), (10, 9), (11, 10), (12, 11), (13, 12), (14, 13), (15, 14), (16, 15), (17, 16), (18, 17), (19, 18), (20, 19), (21, 20), (22, 21), (23, 22), (0, 23), ]
            faces = []

            mesh = obj.data
            mesh.from_pydata(verts, edges, faces)
            mesh.update()
            return obj
        else:
            return None
        
    def createEyesWidget(objName, collectionName, rig, boneName, size = 1.0):
        obj = createWidget(objName, collectionName, rig, boneName)
        if obj is not None:
            verts = [(0.8928930759429932*size, -0.7071065902709961*size, 0.0*size), (0.8928932547569275*size, 0.7071067690849304*size, 0.0*size), (-1.8588197231292725*size, -0.9659252762794495*size, 0.0*size), (-2.100001096725464*size, -0.8660248517990112*size, 0.0*size), (-2.3071072101593018*size, -0.7071059942245483*size, 0.0*size), (-2.4660258293151855*size, -0.49999913573265076*size, 0.0*size), (-2.5659260749816895*size, -0.258818119764328*size, 0.0*size), (-2.5999999046325684*size, 8.575012770961621e-07*size, 0.0*size), (-2.5659255981445312*size, 0.2588198482990265*size, 0.0*size), (-2.4660253524780273*size, 0.5000006556510925*size, 0.0*size), (-2.3071064949035645*size, 0.7071075439453125*size, 0.0*size), (-2.099999189376831*size, 0.866025984287262*size, 0.0*size), (-1.8588184118270874*size, 0.9659261703491211*size, 0.0*size), (-1.5999996662139893*size, 1.000000238418579*size, 0.0*size), (-1.341180443763733*size, 0.9659258723258972*size, 0.0*size), (-1.0999995470046997*size, 0.8660253882408142*size, 0.0*size), (-0.8928929567337036*size, 0.7071067094802856*size, 0.0*size), (-0.892893373966217*size, -0.7071066498756409*size, 0.0*size), (-1.100000262260437*size, -0.8660252690315247*size, 0.0*size), (-1.3411810398101807*size, -0.9659255743026733*size, 0.0*size), (1.600000023841858*size, 1.0*size, 0.0*size), (1.3411810398101807*size, 0.9659258127212524*size, 0.0*size), (1.100000023841858*size, 0.8660253882408142*size, 0.0*size), (-1.600000262260437*size, -0.9999997615814209*size, 0.0*size), (1.0999997854232788*size, -0.8660252690315247*size, 0.0*size), (1.341180682182312*size, -0.9659257531166077*size, 0.0*size), (1.5999996662139893*size, -1.0*size, 0.0*size), (1.8588186502456665*size, -0.965925931930542*size, 0.0*size), (2.0999996662139893*size, -0.8660256266593933*size, 0.0*size), (2.3071064949035645*size, -0.7071071863174438*size, 0.0*size), (2.4660253524780273*size, -0.5000002980232239*size, 0.0*size), (2.5659255981445312*size, -0.25881943106651306*size, 0.0*size), (2.5999999046325684*size, -4.649122899991198e-07*size, 0.0*size), (2.5659260749816895*size, 0.25881853699684143*size, 0.0*size), (2.4660258293151855*size, 0.4999994933605194*size, 0.0*size), (2.3071072101593018*size, 0.707106351852417*size, 0.0*size), (2.1000006198883057*size, 0.8660250902175903*size, 0.0*size), (1.8588197231292725*size, 0.9659256339073181*size, 0.0*size), (-1.8070557117462158*size, -0.7727401852607727*size, 0.0*size), (-2.0000009536743164*size, -0.6928198337554932*size, 0.0*size), (-2.1656856536865234*size, -0.5656847357749939*size, 0.0*size), (-2.292820692062378*size, -0.3999992609024048*size, 0.0*size), (-2.3727407455444336*size, -0.20705445110797882*size, 0.0*size), (-2.3999998569488525*size, 7.336847716032935e-07*size, 0.0*size), (-2.3727405071258545*size, 0.207055926322937*size, 0.0*size), (-2.2928202152252197*size, 0.40000057220458984*size, 0.0*size), (-2.1656851768493652*size, 0.5656861066818237*size, 0.0*size), (-1.9999992847442627*size, 0.6928208470344543*size, 0.0*size), (-1.8070547580718994*size, 0.7727410197257996*size, 0.0*size), (-1.5999996662139893*size, 0.8000002503395081*size, 0.0*size), (-1.3929443359375*size, 0.7727407813072205*size, 0.0*size), (-1.1999995708465576*size, 0.6928203701972961*size, 0.0*size), (-1.0343143939971924*size, 0.5656854510307312*size, 0.0*size), (-1.0343146324157715*size, -0.5656852722167969*size, 0.0*size), (-1.2000001668930054*size, -0.6928201913833618*size, 0.0*size), (-1.3929448127746582*size, -0.7727404236793518*size, 0.0*size), (-1.6000001430511475*size, -0.7999997735023499*size, 0.0*size), (1.8070557117462158*size, 0.772739827632904*size, 0.0*size), (2.0000009536743164*size, 0.6928195953369141*size, 0.0*size), (2.1656856536865234*size, 0.5656843781471252*size, 0.0*size), (2.292820692062378*size, 0.39999890327453613*size, 0.0*size), (2.3727407455444336*size, 0.20705409348011017*size, 0.0*size), (2.3999998569488525*size, -1.0960745839838637e-06*size, 0.0*size), (2.3727405071258545*size, -0.20705628395080566*size, 0.0*size), (2.2928202152252197*size, -0.4000009298324585*size, 0.0*size), (2.1656851768493652*size, -0.5656863451004028*size, 0.0*size), (1.9999992847442627*size, -0.692821204662323*size, 0.0*size), (1.8070547580718994*size, -0.7727413773536682*size, 0.0*size), (1.5999996662139893*size, -0.8000004887580872*size, 0.0*size), (1.3929443359375*size, -0.7727410197257996*size, 0.0*size), (1.1999995708465576*size, -0.6928204894065857*size, 0.0*size), (1.0343143939971924*size, -0.5656855702400208*size, 0.0*size), (1.0343146324157715*size, 0.5656850337982178*size, 0.0*size), (1.2000004053115845*size, 0.6928199529647827*size, 0.0*size), (1.3929448127746582*size, 0.7727401852607727*size, 0.0*size), (1.6000001430511475*size, 0.7999995350837708*size, 0.0*size), ]
            edges = [(24, 0), (1, 22), (16, 1), (17, 0), (23, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (21, 20), (22, 21), (13, 14), (14, 15), (15, 16), (17, 18), (18, 19), (19, 23), (25, 24), (26, 25), (27, 26), (28, 27), (29, 28), (30, 29), (31, 30), (32, 31), (33, 32), (34, 33), (35, 34), (36, 35), (37, 36), (20, 37), (56, 38), (38, 39), (39, 40), (40, 41), (41, 42), (42, 43), (43, 44), (44, 45), (45, 46), (46, 47), (47, 48), (48, 49), (49, 50), (50, 51), (51, 52), (53, 54), (54, 55), (55, 56), (75, 57), (57, 58), (58, 59), (59, 60), (60, 61), (61, 62), (62, 63), (63, 64), (64, 65), (65, 66), (66, 67), (67, 68), (68, 69), (69, 70), (70, 71), (72, 73), (73, 74), (74, 75), (52, 72), (53, 71), ]
            faces = []

            mesh = obj.data
            mesh.from_pydata(verts, edges, faces)
            mesh.update()
            return obj
        else:
            return None

    bpy.ops.object.mode_set(mode='EDIT')
    
    metarigIdBoneName = None
    for bone in metarig.data.edit_bones:
        if bone.name.startswith(koikatsuCommons.metarigIdBonePrefix):
            metarigIdBoneName = bone.name
    if not metarigIdBoneName:
        metarigIdBoneName = koikatsuCommons.metarigIdBonePrefix + koikatsuCommons.generateRandomAlphanumericString()
        koikatsuCommons.createBone(metarig, metarigIdBoneName)
    
    eyesBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.originalEyesBoneName, koikatsuCommons.eyesBoneName)
    leftEyeBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.originalEyesBoneName, koikatsuCommons.leftEyeBoneName)
    rightEyeBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.originalEyesBoneName, koikatsuCommons.rightEyeBoneName)
    referenceEyesBone = metarig.data.edit_bones[koikatsuCommons.originalEyesBoneName]
    leftEyeBone.parent = eyesBone
    rightEyeBone.parent = eyesBone
    
    breastsBone = metarig.data.edit_bones[koikatsuCommons.breastsBoneName]
    leftBreastBone1 = metarig.data.edit_bones[koikatsuCommons.leftBreastBone1Name]
    rightBreastBone1 = metarig.data.edit_bones[koikatsuCommons.rightBreastBone1Name]
    breastsBone.head.y = statistics.mean([leftBreastBone1.head.y, rightBreastBone1.head.y])
    breastsBone.tail.y = statistics.mean([leftBreastBone1.tail.y, rightBreastBone1.tail.y])
    
    buttocksBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.waistBoneName, koikatsuCommons.buttocksBoneName)
    buttocksBone.parent = metarig.data.edit_bones[koikatsuCommons.waistBoneName]
    leftButtockBone = metarig.data.edit_bones[koikatsuCommons.leftButtockBoneName]
    leftButtockBone.parent = buttocksBone
    leftButtockBone.length = buttocksBone.length
    rightButtockBone = metarig.data.edit_bones[koikatsuCommons.rightButtockBoneName]
    rightButtockBone.parent = buttocksBone
    rightButtockBone.length = buttocksBone.length
    buttocksBone.head.y = statistics.mean([leftButtockBone.head.y, rightButtockBone.head.y])
    buttocksBone.tail.y = statistics.mean([leftButtockBone.tail.y, rightButtockBone.tail.y])
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    def arrangeTripleWidgetSet(widgetCollectionName, parentWidget, leftChildWidget, rightChildWidget, snapGeometryToOrigin, 
    vertexGroupObjectName, leftVertexGroupName, rightVertexGroupName, 
    rotate, rotateXRadians, rotateYRadians, rotateZRadians, 
    translate, vertexGroupMidXFactor, vertexGroupMinYFactor, parentWidgetTranslateZFactor, 
    resize, parentWidgetResizeXFactor, parentWidgetResizeYFactor, parentWidgetResizeZFactor, 
    createHandleBones, rig, parentBoneName, parentHandleBoneName, leftChildBoneName, leftChildHandleBoneName, rightChildBoneName, rightChildHandleBoneName):
        activeObject = bpy.context.view_layer.objects.active
        widgetCollection = bpy.context.view_layer.layer_collection.children[widgetCollectionName]
        bpy.ops.object.select_all(action='DESELECT')
        widgetCollection.exclude = False
        widgetCollection.hide_viewport = False
        parentWidget.select_set(True)
        bpy.context.view_layer.objects.active = parentWidget
        if snapGeometryToOrigin:  
            bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
        
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
        bpy.ops.mesh.select_all(action='SELECT')
        if rotate:
            if rotateXRadians:
                bpy.ops.transform.rotate(value=math.radians(rotateXRadians), orient_axis='X', orient_type='GLOBAL')
            if rotateYRadians:
                bpy.ops.transform.rotate(value=math.radians(rotateYRadians), orient_axis='Y', orient_type='GLOBAL')
            if rotateZRadians:
                bpy.ops.transform.rotate(value=math.radians(rotateZRadians), orient_axis='Z', orient_type='GLOBAL')
        leftVertexGroupExtremities = koikatsuCommons.findVertexGroupExtremities(leftVertexGroupName, vertexGroupObjectName)
        rightVertexGroupExtremities = koikatsuCommons.findVertexGroupExtremities(rightVertexGroupName, vertexGroupObjectName)
        leftVertexGroupMidZ = (leftVertexGroupExtremities.maxZ + leftVertexGroupExtremities.minZ) / 2
        rightVertexGroupMidZ = (rightVertexGroupExtremities.maxZ + rightVertexGroupExtremities.minZ) / 2
        averageVertexGroupMidZ = statistics.mean([leftVertexGroupMidZ, rightVertexGroupMidZ])
        averageVertexGroupMinY = statistics.mean([leftVertexGroupExtremities.minY, rightVertexGroupExtremities.minY])
        if translate and not createHandleBones:
            bpy.ops.transform.translate(value=(0, averageVertexGroupMinY * vertexGroupMinYFactor, -(parentWidget.location[2] - averageVertexGroupMidZ * parentWidgetTranslateZFactor)), orient_type='GLOBAL')
        leftVertexGroupMidX = (leftVertexGroupExtremities.maxX + leftVertexGroupExtremities.minX) / 2
        rightVertexGroupMidX = (rightVertexGroupExtremities.maxX + rightVertexGroupExtremities.minX) / 2
        if resize:
            bpy.ops.transform.resize(value=(parentWidgetResizeXFactor, parentWidgetResizeYFactor, parentWidgetResizeZFactor), orient_type='GLOBAL')
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        parentWidget.select_set(False)
        leftChildWidget.select_set(True)
        bpy.context.view_layer.objects.active = leftChildWidget
        if snapGeometryToOrigin:  
            bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')
        
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
        bpy.ops.mesh.select_all(action='SELECT')
        if rotate:
            if rotateXRadians:
                bpy.ops.transform.rotate(value=math.radians(rotateXRadians), orient_axis='X', orient_type='GLOBAL')
            if rotateYRadians:
                bpy.ops.transform.rotate(value=math.radians(rotateYRadians), orient_axis='Y', orient_type='GLOBAL')
            if rotateZRadians:
                bpy.ops.transform.rotate(value=math.radians(rotateZRadians), orient_axis='Z', orient_type='GLOBAL')
        if translate and not createHandleBones:
            bpy.ops.transform.translate(value=(leftVertexGroupMidX * vertexGroupMidXFactor, leftVertexGroupExtremities.minY * vertexGroupMinYFactor, -(leftChildWidget.location[2] - leftVertexGroupMidZ * parentWidgetTranslateZFactor)), orient_type='GLOBAL')
        #leftVertexGroupArea = (leftVertexGroupExtremities.maxX - leftVertexGroupExtremities.minX) * (leftVertexGroupExtremities.maxZ - leftVertexGroupExtremities.minZ) 
        #rightVertexGroupArea = (rightVertexGroupExtremities.maxX - rightVertexGroupExtremities.minX) * (rightVertexGroupExtremities.maxZ - rightVertexGroupExtremities.minZ) 
        #averageVertexGroupArea = statistics.mean([leftVertexGroupArea, rightVertexGroupArea])
        #leftChildWidgetResizeXFactor = statistics.mean([parentWidgetResizeXFactor, parentWidgetResizeXFactor * (leftVertexGroupArea / averageVertexGroupArea)])
        #leftChildWidgetResizeYFactor = statistics.mean([parentWidgetResizeYFactor, parentWidgetResizeYFactor * (leftVertexGroupArea / averageVertexGroupArea)])
        #leftChildWidgetResizeZFactor = statistics.mean([parentWidgetResizeZFactor, parentWidgetResizeZFactor * (leftVertexGroupArea / averageVertexGroupArea)])
        leftVertexGroupLengthX = leftVertexGroupExtremities.maxX - leftVertexGroupExtremities.minX
        rightVertexGroupLengthX = rightVertexGroupExtremities.maxX - rightVertexGroupExtremities.minX
        averageVertexGroupLengthX = statistics.mean([leftVertexGroupLengthX, rightVertexGroupLengthX])
        leftVertexGroupLengthY = leftVertexGroupExtremities.maxY - leftVertexGroupExtremities.minY
        rightVertexGroupLengthY = rightVertexGroupExtremities.maxY - rightVertexGroupExtremities.minY
        averageVertexGroupLengthY = statistics.mean([leftVertexGroupLengthY, rightVertexGroupLengthY])
        leftVertexGroupLengthZ = leftVertexGroupExtremities.maxZ - leftVertexGroupExtremities.minZ
        rightVertexGroupLengthZ = rightVertexGroupExtremities.maxZ - rightVertexGroupExtremities.minZ
        averageVertexGroupLengthZ = statistics.mean([leftVertexGroupLengthZ, rightVertexGroupLengthZ])
        leftChildWidgetResizeXFactor = statistics.mean([parentWidgetResizeXFactor, parentWidgetResizeXFactor * (leftVertexGroupLengthX / averageVertexGroupLengthX)])
        leftChildWidgetResizeYFactor = statistics.mean([parentWidgetResizeYFactor, parentWidgetResizeYFactor * (leftVertexGroupLengthY / averageVertexGroupLengthY)])
        leftChildWidgetResizeZFactor = statistics.mean([parentWidgetResizeZFactor, parentWidgetResizeZFactor * (leftVertexGroupLengthZ / averageVertexGroupLengthZ)])
        if resize:
            bpy.ops.transform.resize(value=(leftChildWidgetResizeXFactor, leftChildWidgetResizeYFactor, leftChildWidgetResizeZFactor), orient_type='GLOBAL')
            
        bpy.ops.object.mode_set(mode='OBJECT')

        leftChildWidget.select_set(False)
        rightChildWidget.select_set(True)
        bpy.context.view_layer.objects.active = rightChildWidget
        if snapGeometryToOrigin:  
            bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='BOUNDS')

        bpy.ops.object.mode_set(mode='EDIT')

        bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
        bpy.ops.mesh.select_all(action='SELECT')
        if rotate:
            if rotateXRadians:
                bpy.ops.transform.rotate(value=math.radians(rotateXRadians), orient_axis='X', orient_type='GLOBAL')
            if rotateYRadians:
                bpy.ops.transform.rotate(value=math.radians(rotateYRadians), orient_axis='Y', orient_type='GLOBAL')
            if rotateZRadians:
                bpy.ops.transform.rotate(value=math.radians(rotateZRadians), orient_axis='Z', orient_type='GLOBAL')
        if translate and not createHandleBones:
            bpy.ops.transform.translate(value=(rightVertexGroupMidX * vertexGroupMidXFactor, rightVertexGroupExtremities.minY * vertexGroupMinYFactor, -(rightChildWidget.location[2] - rightVertexGroupMidZ * parentWidgetTranslateZFactor)), orient_type='GLOBAL')
        #rightChildWidgetResizeXFactor = statistics.mean([parentWidgetResizeXFactor, parentWidgetResizeXFactor * (rightVertexGroupArea / averageVertexGroupArea)])
        #rightChildWidgetResizeYFactor = statistics.mean([parentWidgetResizeYFactor, parentWidgetResizeYFactor * (rightVertexGroupArea / averageVertexGroupArea)])
        #rightChildWidgetResizeZFactor = statistics.mean([parentWidgetResizeZFactor, parentWidgetResizeZFactor * (rightVertexGroupArea / averageVertexGroupArea)])
        rightChildWidgetResizeXFactor = statistics.mean([parentWidgetResizeXFactor, parentWidgetResizeXFactor * (rightVertexGroupLengthX / averageVertexGroupLengthX)])
        rightChildWidgetResizeYFactor = statistics.mean([parentWidgetResizeYFactor, parentWidgetResizeYFactor * (rightVertexGroupLengthY / averageVertexGroupLengthY)])
        rightChildWidgetResizeZFactor = statistics.mean([parentWidgetResizeZFactor, parentWidgetResizeZFactor * (rightVertexGroupLengthZ / averageVertexGroupLengthZ)])
        if resize:
            bpy.ops.transform.resize(value=(rightChildWidgetResizeXFactor, rightChildWidgetResizeYFactor, rightChildWidgetResizeZFactor), orient_type='GLOBAL')

        bpy.ops.object.mode_set(mode='OBJECT')

        rightChildWidget.select_set(False)
        widgetCollection.exclude = True
        widgetCollection.hide_viewport = True
        activeObject.select_set(True)
        bpy.context.view_layer.objects.active = activeObject
        if createHandleBones:
            
            bpy.ops.object.mode_set(mode='EDIT')
            
            parentHandleBone = koikatsuCommons.copyBone(rig, parentBoneName, parentHandleBoneName)
            if translate:
                parentHandleBone.tail.y = parentHandleBone.tail.y + averageVertexGroupMinY * vertexGroupMinYFactor
                parentHandleBone.head.y = parentHandleBone.head.y + averageVertexGroupMinY * vertexGroupMinYFactor
                parentHandleBone.tail.z = parentHandleBone.tail.z - (parentWidget.location[2] - averageVertexGroupMidZ * parentWidgetTranslateZFactor)
                parentHandleBone.head.z = parentHandleBone.head.z - (parentWidget.location[2] - averageVertexGroupMidZ * parentWidgetTranslateZFactor)
            leftChildHandleBone = koikatsuCommons.copyBone(rig, leftChildBoneName, leftChildHandleBoneName)
            if translate:
                leftChildHandleBone.tail.x = leftChildHandleBone.tail.x + leftVertexGroupMidX * vertexGroupMidXFactor
                leftChildHandleBone.head.x = leftChildHandleBone.head.x + leftVertexGroupMidX * vertexGroupMidXFactor
                leftChildHandleBone.tail.y = leftChildHandleBone.tail.y + leftVertexGroupExtremities.minY * vertexGroupMinYFactor
                leftChildHandleBone.head.y = leftChildHandleBone.head.y + leftVertexGroupExtremities.minY * vertexGroupMinYFactor
                leftChildHandleBone.tail.z = leftChildHandleBone.tail.z - (leftChildWidget.location[2] - leftVertexGroupMidZ * parentWidgetTranslateZFactor)
                leftChildHandleBone.head.z = leftChildHandleBone.head.z - (leftChildWidget.location[2] - leftVertexGroupMidZ * parentWidgetTranslateZFactor)
            leftChildHandleBone.parent = parentHandleBone
            rightChildHandleBone = koikatsuCommons.copyBone(rig, rightChildBoneName, rightChildHandleBoneName)
            if translate:
                rightChildHandleBone.tail.x = rightChildHandleBone.tail.x + rightVertexGroupMidX * vertexGroupMidXFactor
                rightChildHandleBone.head.x = rightChildHandleBone.head.x + rightVertexGroupMidX * vertexGroupMidXFactor
                rightChildHandleBone.tail.y = rightChildHandleBone.tail.y + rightVertexGroupExtremities.minY * vertexGroupMinYFactor
                rightChildHandleBone.head.y = rightChildHandleBone.head.y + rightVertexGroupExtremities.minY * vertexGroupMinYFactor
                rightChildHandleBone.tail.z = rightChildHandleBone.tail.z - (rightChildWidget.location[2] - rightVertexGroupMidZ * parentWidgetTranslateZFactor)
                rightChildHandleBone.head.z = rightChildHandleBone.head.z - (rightChildWidget.location[2] - rightVertexGroupMidZ * parentWidgetTranslateZFactor)
            rightChildHandleBone.parent = parentHandleBone
            
            bpy.ops.object.mode_set(mode='OBJECT')
            

    widgetEyes = createEyesWidget(koikatsuCommons.widgetEyesName, koikatsuCommons.widgetCollectionName, metarig, koikatsuCommons.eyesBoneName)
    widgetEyeLeft = createEyeWidget(koikatsuCommons.widgetEyeLeftName, koikatsuCommons.widgetCollectionName, metarig, koikatsuCommons.leftEyeBoneName)
    widgetEyeRight = createEyeWidget(koikatsuCommons.widgetEyeRightName, koikatsuCommons.widgetCollectionName, metarig, koikatsuCommons.rightEyeBoneName)

    arrangeTripleWidgetSet(koikatsuCommons.widgetCollectionName, widgetEyes, widgetEyeLeft, widgetEyeRight, False, 
    koikatsuCommons.bodyName, koikatsuCommons.leftEyeDeformBoneName, koikatsuCommons.rightEyeDeformBoneName, 
    True, 90, 0, 90, 
    True, 0.93, 1.66427, 1, 
    True, 1.16, 1, 1.65, 
    True, metarig, koikatsuCommons.eyesBoneName, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.leftEyeBoneName, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.rightEyeBoneName, koikatsuCommons.rightEyeHandleBoneName)
    
    widgetBreasts = koikatsuCommons.copyObject(koikatsuCommons.widgetCollectionName, koikatsuCommons.originalWidgetBreastsName, koikatsuCommons.widgetBreastsName)
    objToBone(widgetBreasts, metarig, koikatsuCommons.breastsBoneName)
    widgetBreastLeft = koikatsuCommons.copyObject(koikatsuCommons.widgetCollectionName, koikatsuCommons.originalWidgetBreastLeftName, koikatsuCommons.widgetBreastLeftName)
    objToBone(widgetBreastLeft, metarig, koikatsuCommons.breastsBoneName)
    widgetBreastRight = koikatsuCommons.copyObject(koikatsuCommons.widgetCollectionName, koikatsuCommons.originalWidgetBreastRightName, koikatsuCommons.widgetBreastRightName)
    objToBone(widgetBreastRight, metarig, koikatsuCommons.breastsBoneName)
        
    if not isMale:
        arrangeTripleWidgetSet(koikatsuCommons.widgetCollectionName, widgetBreasts, widgetBreastLeft, widgetBreastRight, True, 
        koikatsuCommons.bodyName, koikatsuCommons.leftNippleDeformBone1Name, koikatsuCommons.rightNippleDeformBone1Name, 
        False, None, None, None,
        True, 0.3, 1.66427, 0.9955, 
        True, 21, 1, 19, 
        True, metarig, koikatsuCommons.breastsBoneName, koikatsuCommons.breastsHandleBoneName, koikatsuCommons.leftBreastBone1Name, koikatsuCommons.leftBreastHandleBoneName, koikatsuCommons.rightBreastBone1Name, koikatsuCommons.rightBreastHandleBoneName)
        
    widgetButtocks = koikatsuCommons.copyObject(koikatsuCommons.widgetCollectionName, koikatsuCommons.originalWidgetBreastsName, koikatsuCommons.widgetButtocksName)
    objToBone(widgetButtocks, metarig, koikatsuCommons.buttocksBoneName)
    widgetButtockLeft = koikatsuCommons.copyObject(koikatsuCommons.widgetCollectionName, koikatsuCommons.originalWidgetBreastLeftName, koikatsuCommons.widgetButtockLeftName)
    objToBone(widgetButtockLeft, metarig, koikatsuCommons.buttocksBoneName)
    widgetButtockRight = koikatsuCommons.copyObject(koikatsuCommons.widgetCollectionName, koikatsuCommons.originalWidgetBreastRightName, koikatsuCommons.widgetButtockRightName)
    objToBone(widgetButtockRight, metarig, koikatsuCommons.buttocksBoneName)
        
    arrangeTripleWidgetSet(koikatsuCommons.widgetCollectionName, widgetButtocks, widgetButtockLeft, widgetButtockRight, True, 
    koikatsuCommons.bodyName, koikatsuCommons.leftButtockDeformBoneName, koikatsuCommons.rightButtockDeformBoneName, 
    False, None, None, None,
    True, 0, -3.6, 1, 
    True, 30, 1, 25, 
    True, metarig, koikatsuCommons.buttocksBoneName, koikatsuCommons.buttocksHandleBoneName, koikatsuCommons.leftButtockBoneName, koikatsuCommons.leftButtockHandleBoneName, koikatsuCommons.rightButtockBoneName, koikatsuCommons.rightButtockHandleBoneName)
    
    def finalizeHandleBone(isEyeHandleBone, rig, boneName, handleBoneName, widget):
        rig.pose.bones[boneName].custom_shape = None
        rig.pose.bones[handleBoneName].custom_shape = widget
        if isEyeHandleBone:
            rig.pose.bones[handleBoneName].lock_location[1] = True
            rig.pose.bones[handleBoneName].lock_rotation[0] = True
            rig.pose.bones[handleBoneName].lock_rotation[2] = True
            rig.pose.bones[handleBoneName].lock_scale[1] = True
        koikatsuCommons.addCopyTransformsConstraint(rig, boneName, handleBoneName, 'REPLACE', 'LOCAL', koikatsuCommons.copyTransformsConstraintBaseName + koikatsuCommons.handleConstraintSuffix)

    finalizeHandleBone(True, metarig, koikatsuCommons.eyesBoneName, koikatsuCommons.eyesHandleBoneName, widgetEyes)
    finalizeHandleBone(True, metarig, koikatsuCommons.leftEyeBoneName, koikatsuCommons.leftEyeHandleBoneName, widgetEyeLeft)
    finalizeHandleBone(True, metarig, koikatsuCommons.rightEyeBoneName, koikatsuCommons.rightEyeHandleBoneName, widgetEyeRight)
    metarig.pose.bones[koikatsuCommons.originalEyesBoneName].custom_shape = None
    #metarig.data.bones[koikatsuCommons.originalEyesBoneName].layers[koikatsuCommons.originalMchLayerIndex] = True
    #metarig.data.bones[koikatsuCommons.originalEyesBoneName].layers[koikatsuCommons.originalIkLayerIndex] = False
    if not isMale:
        finalizeHandleBone(False, metarig, koikatsuCommons.breastsBoneName, koikatsuCommons.breastsHandleBoneName, widgetBreasts)
        finalizeHandleBone(False, metarig, koikatsuCommons.leftBreastBone1Name, koikatsuCommons.leftBreastHandleBoneName, widgetBreastLeft)   
        finalizeHandleBone(False, metarig, koikatsuCommons.rightBreastBone1Name, koikatsuCommons.rightBreastHandleBoneName, widgetBreastRight)   
    finalizeHandleBone(False, metarig, koikatsuCommons.buttocksBoneName, koikatsuCommons.buttocksHandleBoneName, widgetButtocks)   
    finalizeHandleBone(False, metarig, koikatsuCommons.leftButtockBoneName, koikatsuCommons.leftButtockHandleBoneName, widgetButtockLeft)   
    finalizeHandleBone(False, metarig, koikatsuCommons.rightButtockBoneName, koikatsuCommons.rightButtockHandleBoneName, widgetButtockRight)
    copyTransformsConstraintName = koikatsuCommons.copyTransformsConstraintBaseName + koikatsuCommons.jointConstraintSuffix + koikatsuCommons.correctionConstraintSuffix
    koikatsuCommons.addCopyTransformsConstraint(metarig, koikatsuCommons.leftButtockHandleBoneName, koikatsuCommons.leftButtockJointCorrectionBoneName, 'AFTER', 'LOCAL', copyTransformsConstraintName)
    koikatsuCommons.addCopyTransformsConstraint(metarig, koikatsuCommons.rightButtockHandleBoneName, koikatsuCommons.rightButtockJointCorrectionBoneName, 'AFTER', 'LOCAL', copyTransformsConstraintName)

    bpy.ops.object.mode_set(mode='EDIT')
    
    eyesTrackTargetBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.eyesTrackTargetBoneName)
    eyesTrackTargetParentBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.eyesTrackTargetParentBoneName)
    eyesHandleMarkerBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.eyesHandleMarkerBoneName)
    leftEyeHandleMarkerBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftEyeHandleMarkerBoneName)
    rightEyeHandleMarkerBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightEyeHandleMarkerBoneName)
    leftEyeHandleMarkerXBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftEyeHandleMarkerXBoneName)
    rightEyeHandleMarkerXBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightEyeHandleMarkerXBoneName)
    leftEyeHandleMarkerXBone.head.z = eyesHandleMarkerBone.head.z
    rightEyeHandleMarkerXBone.head.z = eyesHandleMarkerBone.head.z
    leftEyeHandleMarkerXBone.tail.z = eyesHandleMarkerBone.head.z
    rightEyeHandleMarkerXBone.tail.z = eyesHandleMarkerBone.head.z
    leftEyeHandleMarkerZBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftEyeHandleMarkerZBoneName)
    rightEyeHandleMarkerZBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightEyeHandleMarkerZBoneName)
    leftEyeHandleMarkerZBone.head.x = eyesHandleMarkerBone.head.x
    rightEyeHandleMarkerZBone.head.x = eyesHandleMarkerBone.head.x
    leftEyeHandleMarkerZBone.tail.x = eyesHandleMarkerBone.head.x
    rightEyeHandleMarkerZBone.tail.x = eyesHandleMarkerBone.head.x
    eyesTrackTargetBone.parent = eyesTrackTargetParentBone
    eyesTrackTargetParentBone.parent = None
    headBone = metarig.data.edit_bones[koikatsuCommons.headBoneName]
    leftEyeHandleMarkerBone.parent = headBone
    rightEyeHandleMarkerBone.parent = headBone
    leftEyeHandleMarkerXBone.parent = headBone
    rightEyeHandleMarkerXBone.parent = headBone
    leftEyeHandleMarkerZBone.parent = headBone
    rightEyeHandleMarkerZBone.parent = headBone
    eyeballsBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.eyeballsBoneName)
    eyeballsBone.roll = radians(0)
    leftEyeballBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftEyeballBoneName)
    rightEyeballBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightEyeballBoneName)
    leftEyeballBone.parent = headBone
    rightEyeballBone.parent = headBone
    leftEyeballBone.roll = radians(0)
    rightEyeballBone.roll = radians(0)
    leftEyeballBone.head.y = metarig.data.edit_bones[koikatsuCommons.leftEyeDeformBoneName].head.y
    rightEyeballBone.head.y = metarig.data.edit_bones[koikatsuCommons.rightEyeDeformBoneName].head.y
    eyeballsBone.head.y = statistics.mean([leftEyeballBone.head.y, rightEyeballBone.head.y])    
    eyeballsBone.length = metarig.data.edit_bones[koikatsuCommons.eyesHandleBoneName].length
    leftEyeballBone.length = metarig.data.edit_bones[koikatsuCommons.leftEyeHandleBoneName].length
    rightEyeballBone.length = metarig.data.edit_bones[koikatsuCommons.rightEyeHandleBoneName].length    
    eyeballsTrackBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.eyeballsBoneName, koikatsuCommons.eyeballsTrackBoneName)
    leftEyeballTrackBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.leftEyeballBoneName, koikatsuCommons.leftEyeballTrackBoneName)
    rightEyeballTrackBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.rightEyeballBoneName, koikatsuCommons.rightEyeballTrackBoneName)
    leftEyeballTrackCorrectionBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.leftEyeballTrackBoneName, koikatsuCommons.leftEyeballTrackCorrectionBoneName)
    rightEyeballTrackCorrectionBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.rightEyeballTrackBoneName, koikatsuCommons.rightEyeballTrackCorrectionBoneName)
    leftHeadMarkerXBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftHeadMarkerXBoneName)
    rightHeadMarkerXBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightHeadMarkerXBoneName)
    leftHeadMarkerXBone.parent = headBone
    rightHeadMarkerXBone.parent = headBone
    leftHeadMarkerXBone.head.y = headBone.head.y
    rightHeadMarkerXBone.head.y = headBone.head.y
    leftHeadMarkerXBone.length = metarig.data.edit_bones[koikatsuCommons.leftEyeHandleBoneName].length
    rightHeadMarkerXBone.length = metarig.data.edit_bones[koikatsuCommons.rightEyeHandleBoneName].length
    leftHeadMarkerXBone.head.z = headBone.head.z
    rightHeadMarkerXBone.head.z = headBone.head.z
    leftHeadMarkerXBone.tail.z = headBone.head.z
    rightHeadMarkerXBone.tail.z = headBone.head.z
    leftHeadMarkerZBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftHeadMarkerZBoneName)
    rightHeadMarkerZBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightHeadMarkerZBoneName)
    leftHeadMarkerZBone.parent = headBone
    rightHeadMarkerZBone.parent = headBone
    leftHeadMarkerZBone.head.y = headBone.head.y
    rightHeadMarkerZBone.head.y = headBone.head.y
    leftHeadMarkerZBone.length = metarig.data.edit_bones[koikatsuCommons.leftEyeHandleBoneName].length
    rightHeadMarkerZBone.length = metarig.data.edit_bones[koikatsuCommons.rightEyeHandleBoneName].length
    leftHeadMarkerZBone.head.x = headBone.head.x
    rightHeadMarkerZBone.head.x = headBone.head.x
    leftHeadMarkerZBone.tail.x = headBone.head.x
    rightHeadMarkerZBone.tail.x = headBone.head.x
    headTrackTargetBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.headTrackTargetBoneName)
    headTrackTargetBone.length = headBone.length
    headTrackTargetParentBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.headTrackTargetBoneName, koikatsuCommons.headTrackTargetParentBoneName)
    headTrackTargetBone.parent = headTrackTargetParentBone
    headTrackTargetParentBone.parent = None
    headTrackBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.eyeballsBoneName, koikatsuCommons.headTrackBoneName)
    headTrackBone.parent = None
    headTrackBone.head.y = headBone.head.y
    placeholderHeadTweakBone = koikatsuCommons.createBone(metarig, koikatsuCommons.headTweakBoneName + koikatsuCommons.placeholderBoneSuffix)
    placeholderTorsoBone = koikatsuCommons.createBone(metarig, koikatsuCommons.torsoBoneName + koikatsuCommons.placeholderBoneSuffix)
    placeholderRootBone = koikatsuCommons.createBone(metarig, koikatsuCommons.rootBoneName + koikatsuCommons.placeholderBoneSuffix)
        
    placeholderHeadTweakBoneName = placeholderHeadTweakBone.name
    placeholderTorsoBoneName = placeholderTorsoBone.name
    placeholderRootBoneName = placeholderRootBone.name
        
    leftHeadDistX = leftHeadMarkerXBone.head.x - headBone.head.x
    rightHeadDistX = rightHeadMarkerXBone.head.x - headBone.head.x
    leftHeadDistZ = leftHeadMarkerZBone.head.z - headBone.head.z
    rightHeadDistZ = rightHeadMarkerZBone.head.z - headBone.head.z
    leftHeadDistXReference = 0.031159714929090754
    rightHeadDistXReference = -0.031183381431473478
    leftHeadDistZReference = 0.053977131843566895
    rightHeadDistZReference = 0.05397462844848633
    
    leftEyeballTrackCorrectionLeftEyeHandleDistY = leftEyeballTrackCorrectionBone.head.y - leftEyeHandleMarkerBone.head.y
    rightEyeballTrackCorrectionRightEyeHandleDistY = rightEyeballTrackCorrectionBone.head.y - rightEyeHandleMarkerBone.head.y
    leftEyeballTrackCorrectionLeftEyeHandleDistYReference = 0.09179527312517166
    rightEyeballTrackCorrectionRightEyeHandleDistYReference = 0.0917946808040142
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    eyesSizeFactor = 100.0
    
    """
    leftEyeVertexGroupExtremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftEyeDeformBoneName, koikatsuCommons.bodyName)
    rightEyeVertexGroupExtremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.rightEyeDeformBoneName, koikatsuCommons.bodyName)
    leftEyeVertexGroupArea = (leftEyeVertexGroupExtremities.maxX - leftEyeVertexGroupExtremities.minX) * (leftEyeVertexGroupExtremities.maxZ - leftEyeVertexGroupExtremities.minZ) 
    rightEyeVertexGroupArea = (rightEyeVertexGroupExtremities.maxX - rightEyeVertexGroupExtremities.minX) * (rightEyeVertexGroupExtremities.maxZ - rightEyeVertexGroupExtremities.minZ) 
    averageEyeVertexGroupArea = statistics.mean([leftEyeVertexGroupArea, rightEyeVertexGroupArea])
    averageEyeVertexGroupAreaReference = 0.0016523913975554083
    eyesSizeFactorCurrent = eyesSizeFactor * math.sqrt(averageEyeVertexGroupArea / averageEyeVertexGroupAreaReference)
    """    
    
    eyesHandleLimitLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesHandleBoneName, "01A) Limit location", "Limits the maximum reachable X and Y locations based on the left and right eye handles settings", 0.0, 0.0, 1.0)
    eyesHandleEyelidsAutomationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesHandleBoneName, "02A) Eyelids automation", "Enables eyelids shape key automation when both eyes move up and down", 0.0, 0.0, 1.0)
    eyesHandleDefaultEyelidsValueDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesHandleBoneName, "02B) Default eyelids value", "Eyelids shape key automation value when both eyes are at their default position", 0.05, 0.0, 1.0)
    eyesHandleMinEyelidsValueDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesHandleBoneName, "02C) Min eyelids value", "Minimum reachable eyelids shape key automation value when both eyes move down", 0.0, 0.0, 1.0)
    eyesHandleMaxEyelidsValueDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesHandleBoneName, "02D) Max eyelids value", "Maximum reachable eyelids shape key automation value when both eyes move up", 0.25, 0.0, 1.0)
    eyesHandleEyelidsSpeedFactorDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesHandleBoneName, "02E) Eyelids speed factor", "Determines how fast the eyelids shape key automation value will change when both eyes move up and down", 2.0, 0.0, eyesSizeFactor * 10)
    eyesHandleEyesSizeFactorDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesHandleBoneName, "03A) Eyes size factor", "Factors into many constraints and drivers for the eyes mechanics; it's better not to change this value", eyesSizeFactor, 0, eyesSizeFactor * 10)
    leftEyeHandleLimitLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.leftEyeHandleBoneName, "01A) Limit location", "Limits the maximum reachable X and Y locations based on the settings below", 0.0, 0.0, 1.0)
    leftEyeHandleMinXLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.leftEyeHandleBoneName, "01B) Min X location", "Minimum reachable X location limit", -0.075 - leftHeadDistXReference + leftHeadDistX, eyesSizeFactor * -10, eyesSizeFactor * 10)
    leftEyeHandleMaxXLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.leftEyeHandleBoneName, "01C) Max X location", "Maximum reachable X location limit", 0.25 - leftHeadDistXReference + leftHeadDistX, eyesSizeFactor * -10, eyesSizeFactor * 10)
    leftEyeHandleMinYLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.leftEyeHandleBoneName, "01D) Min Y location", "Minimum reachable Y location limit", -0.1 - leftHeadDistZReference + leftHeadDistZ, eyesSizeFactor * -10, eyesSizeFactor * 10)
    leftEyeHandleMaxYLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.leftEyeHandleBoneName, "01E) Max Y location", "Maximum reachable Y location limit", 0.13 - leftHeadDistZReference + leftHeadDistZ, eyesSizeFactor * -10, eyesSizeFactor * 10)
    leftEyeHandleSpeedCorrectionDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.leftEyeHandleBoneName, "02A) Speed correction", "Increases the speed at which the eye moves when not controlled directly in order to reach its maximum location limits at the same time as the other eye", 0.0, 0.0, 1.0)
    rightEyeHandleLimitLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.rightEyeHandleBoneName, "01A) Limit location", "Limits the maximum reachable X and Y locations based on the settings below", 0.0, 0.0, 1.0)
    rightEyeHandleMinXLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.rightEyeHandleBoneName, "01B) Min X location", "Minimum reachable X location limit", -0.25 - rightHeadDistXReference + rightHeadDistX, eyesSizeFactor * -10, eyesSizeFactor * 10)
    rightEyeHandleMaxXLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.rightEyeHandleBoneName, "01C) Max X location", "Maximum reachable X location limit", 0.075 - rightHeadDistXReference + rightHeadDistX, eyesSizeFactor * -10, eyesSizeFactor * 10)
    rightEyeHandleMinYLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.rightEyeHandleBoneName, "01D) Min Y location", "Minimum reachable Y location limit", -0.1 - rightHeadDistZReference + rightHeadDistZ, eyesSizeFactor * -10, eyesSizeFactor * 10)
    rightEyeHandleMaxYLocationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.rightEyeHandleBoneName, "01E) Max Y location", "Maximum reachable Y location limit", 0.13 - rightHeadDistZReference + rightHeadDistZ, eyesSizeFactor * -10, eyesSizeFactor * 10)
    rightEyeHandleSpeedCorrectionDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.rightEyeHandleBoneName, "02A) Speed correction", "Increases the speed at which the eye moves when not controlled directly in order to reach its maximum location limits at the same time as the other eye", 0.0, 0.0, 1.0)
    eyesTrackTargetParentToHeadDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesTrackTargetBoneName, "01A) Parent to head", "The bone will act as if it was parented to the head bone", 1, 0, 1)
    eyesTrackTargetParentToTorsoDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesTrackTargetBoneName, "01B) Parent to torso", "The bone will act as if it was parented to the torso bone", 0, 0, 1)
    eyesTrackTargetParentToRootDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyesTrackTargetBoneName, "01C) Parent to root", "The bone will act as if it was parented to the root bone", 0, 0, 1)
    eyeballsSpeedFactorDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyeballsBoneName, "01A) Eyeballs speed factor", "Determines how fast the eyes will move when rotating the eyeball bones manually", 0.26, 0.0, 1.0)
    eyeballsTrackTargetDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyeballsBoneName, "02A) Track target", "Enables tracking of the eyeballs track target bone", 0.0, 0.0, 1.0)
    eyeballsTrackSpeedFactorDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyeballsBoneName, "02B) Eyeballs track speed factor", "Determines how fast the eyes will move when the eyeballs are tracking their target", 0.04, 0.0, 1.0)
    eyeballsNearbyTargetTrackCorrectionDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyeballsBoneName, "02C) Nearby target track correction", "When tracking a target that moves closer to the middle of the face than its original location, the individual eyes will gradually point towards it instead of keeping the original distance between them", 0.0, 0.0, 1.0)
    eyeballsNearbyTargetSizeFactorDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.eyeballsBoneName, "02D) Nearby target track size factor", "Factors into the nearby target track correction, if the character is scaled up or down after running the first Rigify script this value should be changed proportionally", rightEyeballTrackCorrectionRightEyeHandleDistY / rightEyeballTrackCorrectionRightEyeHandleDistYReference, eyesSizeFactor * -10, eyesSizeFactor * 10)
    headTrackTargetLimitRotationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "01A) Limit rotation", "Limits the maximum reachable rotation of the head based on the settings below", 0.0, 0.0, 1.0)
    headTrackTargetMinXRotationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "01B) Min X rotation", "Minimum reachable X angle limit", -40.0, -180.0, 0.0)
    headTrackTargetMaxXRotationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "01C) Max X rotation", "Maximum reachable X angle limit", 50.0, 0.0, 180.0)
    headTrackTargetMinYRotationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "01D) Min Y rotation", "Minimum reachable Y angle limit", -80.0, -180.0, 0.0)
    headTrackTargetMaxYRotationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "01E) Max Y rotation", "Maximum reachable Y angle limit", 80.0, 0.0, 180.0)
    headTrackTargetMinZRotationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "01F) Min Z rotation", "Minimum reachable Z angle limit", -50.0, -180.0, 0.0)
    headTrackTargetMaxZRotationDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "01G) Max Z rotation", "Maximum reachable Z angle limit", 50.0, 0.0, 180.0)
    headTrackTargetTrackTargetDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "02A) Track target", "Enables tracking of the head track target bone", 0.0, 0.0, 1.0)
    headTrackTargetParentToHeadDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "03A) Parent to head", "The bone will act as if it was parented to the head bone", 1, 0, 1)
    headTrackTargetParentToTorsoDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "03B) Parent to torso", "The bone will act as if it was parented to the torso bone", 0, 0, 1)
    headTrackTargetParentToRootDataPath = koikatsuCommons.addBoneCustomProperty(metarig, koikatsuCommons.headTrackTargetBoneName, "03C) Parent to root", "The bone will act as if it was parented to the root bone", 0, 0, 1)
        
    eyesHandleTransformationConstraintEyeballLocation = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.eyeballsBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.locationConstraintSuffix, 
    'ROTATION', 'AUTO', math.radians(-180), math.radians(180), math.radians(0), math.radians(0), math.radians(-180), math.radians(180), 
    'LOCATION', None, eyesSizeFactor / -10, eyesSizeFactor / 10, 0, 0, eyesSizeFactor / -10, eyesSizeFactor / 10)    
    eyesHandleCopyRotationConstraintEyeball = koikatsuCommons.addCopyRotationConstraint(metarig, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.eyeballsBoneName, 'AFTER', 'LOCAL', koikatsuCommons.copyRotationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix, 
    False, False, True, False, False, False)
    eyesHandleTransformationContraintEyeballScale = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.eyeballsBoneName, 'MULTIPLY', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.scaleConstraintSuffix, 
    'SCALE', None, 0.0, 100.0, 1.0, 1.0, 0.0, 100.0, 
    'SCALE', None, 0.0, 100.0, 1.0, 1.0, 0.0, 100.0)
    eyesHandleLimitLocationConstraint = koikatsuCommons.addLimitLocationConstraint(metarig, koikatsuCommons.eyesHandleBoneName, koikatsuCommons.headBoneName, 'CUSTOM', koikatsuCommons.limitLocationConstraintBaseName + koikatsuCommons.handleConstraintSuffix, 
    True, -eyesSizeFactor, True, eyesSizeFactor, True, -eyesSizeFactor, True, eyesSizeFactor, False, 0.0, False, 0.0)
    leftEyeHandleTransformationConstraintEyeballLocation = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftEyeballBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.locationConstraintSuffix, 
    'ROTATION', 'AUTO', math.radians(-180), math.radians(180), math.radians(0), math.radians(0), math.radians(-180), math.radians(180), 
    'LOCATION', None, eyesSizeFactor / -10, eyesSizeFactor / 10, 0, 0, eyesSizeFactor / -10, eyesSizeFactor / 10)    
    leftEyeHandleTransformationConstraintEyeballLocationCorrectionMin = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftEyeballBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.locationConstraintSuffix + koikatsuCommons.correctionConstraintSuffix + koikatsuCommons.minConstraintSuffix, 
    'ROTATION', 'AUTO', math.radians(0), math.radians(0), math.radians(0), math.radians(0), math.radians(0), math.radians(0), 
    'LOCATION', None, 0, 0, 0, 0, 0, 0)
    leftEyeHandleTransformationConstraintEyeballLocationCorrectionMax = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftEyeballBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.locationConstraintSuffix + koikatsuCommons.correctionConstraintSuffix + koikatsuCommons.maxConstraintSuffix, 
    'ROTATION', 'AUTO', math.radians(0), math.radians(0), math.radians(0), math.radians(0), math.radians(0), math.radians(0), 
    'LOCATION', None, 0, 0, 0, 0, 0, 0)
    leftEyeHandleCopyRotationConstraintEyeball = koikatsuCommons.addCopyRotationConstraint(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftEyeballBoneName, 'AFTER', 'LOCAL', koikatsuCommons.copyRotationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix, 
    False, False, True, False, False, False)
    leftEyeHandleTransformationConstraintEyeballScale = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.leftEyeballBoneName, 'MULTIPLY', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.scaleConstraintSuffix, 
    'SCALE', None, 0.0, 100.0, 1.0, 1.0, 0.0, 100.0, 
    'SCALE', None, 0.0, 100.0, 1.0, 1.0, 0.0, 100.0)
    leftEyeHandleTransformationConstraintHandleLocationCorrectionMin = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.eyesHandleBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.handleConstraintSuffix + koikatsuCommons.locationConstraintSuffix + koikatsuCommons.correctionConstraintSuffix + koikatsuCommons.minConstraintSuffix, 
    'LOCATION', None, 0, 0, 0, 0, 0, 0, 
    'LOCATION', None, 0, 0, 0, 0, 0, 0)
    leftEyeHandleTransformationConstraintHandleLocationCorrectionMax = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.eyesHandleBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.handleConstraintSuffix + koikatsuCommons.locationConstraintSuffix + koikatsuCommons.correctionConstraintSuffix + koikatsuCommons.maxConstraintSuffix, 
    'LOCATION', None, 0, 0, 0, 0, 0, 0, 
    'LOCATION', None, 0, 0, 0, 0, 0, 0)
    leftEyeHandleLimitLocationConstraint = koikatsuCommons.addLimitLocationConstraint(metarig, koikatsuCommons.leftEyeHandleBoneName, koikatsuCommons.headBoneName, 'CUSTOM', koikatsuCommons.limitLocationConstraintBaseName + koikatsuCommons.handleConstraintSuffix, 
    True, -eyesSizeFactor, True, eyesSizeFactor, True, -eyesSizeFactor, True, eyesSizeFactor, False, 0.0, False, 0.0)
    rightEyeHandleTransformationConstraintEyeballLocation = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightEyeballBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.locationConstraintSuffix, 
    'ROTATION', 'AUTO', math.radians(-180), math.radians(180), math.radians(0), math.radians(0), math.radians(-180), math.radians(180), 
    'LOCATION', None, eyesSizeFactor / -10, eyesSizeFactor / 10, 0, 0, eyesSizeFactor / -10, eyesSizeFactor / 10)    
    rightEyeHandleTransformationConstraintEyeballLocationCorrectionMin = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightEyeballBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.locationConstraintSuffix + koikatsuCommons.correctionConstraintSuffix + koikatsuCommons.minConstraintSuffix, 
    'ROTATION', 'AUTO', math.radians(0), math.radians(0), math.radians(0), math.radians(0), math.radians(0), math.radians(0), 
    'LOCATION', None, 0, 0, 0, 0, 0, 0)
    rightEyeHandleTransformationConstraintEyeballLocationCorrectionMax = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightEyeballBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.locationConstraintSuffix + koikatsuCommons.correctionConstraintSuffix + koikatsuCommons.maxConstraintSuffix, 
    'ROTATION', 'AUTO', math.radians(0), math.radians(0), math.radians(0), math.radians(0), math.radians(0), math.radians(0), 
    'LOCATION', None, 0, 0, 0, 0, 0, 0)
    rightEyeHandleCopyRotationConstraintEyeball = koikatsuCommons.addCopyRotationConstraint(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightEyeballBoneName, 'AFTER', 'LOCAL', koikatsuCommons.copyRotationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix, 
    False, False, True, False, False, False)
    rightEyeHandleTransformationConstraintEyeballScale = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.rightEyeballBoneName, 'MULTIPLY', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.eyeballConstraintSuffix + koikatsuCommons.scaleConstraintSuffix, 
    'SCALE', None, 0.0, 100.0, 1.0, 1.0, 0.0, 100.0, 
    'SCALE', None, 0.0, 100.0, 1.0, 1.0, 0.0, 100.0)
    rightEyeHandleTransformationConstraintHandleLocationCorrectionMin = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.eyesHandleBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.handleConstraintSuffix + koikatsuCommons.locationConstraintSuffix + koikatsuCommons.correctionConstraintSuffix + koikatsuCommons.minConstraintSuffix, 
    'LOCATION', None, 0, 0, 0, 0, 0, 0, 
    'LOCATION', None, 0, 0, 0, 0, 0, 0)
    rightEyeHandleTransformationConstraintHandleLocationCorrectionMax = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.eyesHandleBoneName, 'ADD', 'LOCAL', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.handleConstraintSuffix + koikatsuCommons.locationConstraintSuffix + koikatsuCommons.correctionConstraintSuffix + koikatsuCommons.maxConstraintSuffix, 
    'LOCATION', None, 0, 0, 0, 0, 0, 0, 
    'LOCATION', None, 0, 0, 0, 0, 0, 0)
    rightEyeHandleLimitLocationConstraint = koikatsuCommons.addLimitLocationConstraint(metarig, koikatsuCommons.rightEyeHandleBoneName, koikatsuCommons.headBoneName, 'CUSTOM', koikatsuCommons.limitLocationConstraintBaseName + koikatsuCommons.handleConstraintSuffix, 
    True, -eyesSizeFactor, True, eyesSizeFactor, True, -eyesSizeFactor, True, eyesSizeFactor, False, 0.0, False, 0.0)
    eyesTrackTargetParentArmatureConstraint = koikatsuCommons.addArmatureConstraint(metarig, koikatsuCommons.eyesTrackTargetParentBoneName, [koikatsuCommons.headBoneName, placeholderTorsoBoneName, placeholderRootBoneName], koikatsuCommons.armatureConstraintBaseName + koikatsuCommons.parentConstraintSuffix) 
    eyeballsCopyRotationConstraintTrack = koikatsuCommons.addCopyRotationConstraint(metarig, koikatsuCommons.eyeballsBoneName, koikatsuCommons.eyeballsTrackBoneName, 'REPLACE', 'LOCAL', koikatsuCommons.copyRotationConstraintBaseName + koikatsuCommons.trackConstraintSuffix, 
    True, False, False, False, True, False)
    leftEyeballCopyRotationConstraintTrack = koikatsuCommons.addCopyRotationConstraint(metarig, koikatsuCommons.leftEyeballBoneName, koikatsuCommons.leftEyeballTrackCorrectionBoneName, 'REPLACE', 'LOCAL', koikatsuCommons.copyRotationConstraintBaseName + koikatsuCommons.trackConstraintSuffix + koikatsuCommons.correctionConstraintSuffix, 
    True, False, False, False, True, False)
    rightEyeballCopyRotationConstraintTrack = koikatsuCommons.addCopyRotationConstraint(metarig, koikatsuCommons.rightEyeballBoneName, koikatsuCommons.rightEyeballTrackCorrectionBoneName, 'REPLACE', 'LOCAL', koikatsuCommons.copyRotationConstraintBaseName + koikatsuCommons.trackConstraintSuffix + koikatsuCommons.correctionConstraintSuffix, 
    True, False, False, False, True, False)    
    eyeballsTrackDampedTrackConstraint = koikatsuCommons.addDampedTrackConstraint(metarig, koikatsuCommons.eyeballsTrackBoneName, koikatsuCommons.eyesTrackTargetBoneName, koikatsuCommons.dampedTrackConstraintBaseName + koikatsuCommons.trackConstraintSuffix)
    leftEyeballTrackDampedTrackConstraint = koikatsuCommons.addDampedTrackConstraint(metarig, koikatsuCommons.leftEyeballTrackBoneName, koikatsuCommons.eyesTrackTargetBoneName, koikatsuCommons.dampedTrackConstraintBaseName + koikatsuCommons.trackConstraintSuffix)
    rightEyeballTrackDampedTrackConstraint = koikatsuCommons.addDampedTrackConstraint(metarig, koikatsuCommons.rightEyeballTrackBoneName, koikatsuCommons.eyesTrackTargetBoneName, koikatsuCommons.dampedTrackConstraintBaseName + koikatsuCommons.trackConstraintSuffix)
    headTransformationConstraintHeadRotation = koikatsuCommons.addTransformationConstraint(metarig, koikatsuCommons.headBoneName, koikatsuCommons.headTrackBoneName, 'REPLACE', 'LOCAL_WITH_PARENT', koikatsuCommons.transformationConstraintBaseName + koikatsuCommons.headConstraintSuffix + koikatsuCommons.rotationConstraintSuffix, 
    'ROTATION', 'QUATERNION', math.radians(-180), math.radians(180), math.radians(-180), math.radians(180), math.radians(-180), math.radians(180), 
    'ROTATION', 'AUTO', math.radians(180), math.radians(-180), math.radians(-180), math.radians(180), math.radians(-180), math.radians(180), 
    'X', 'Z', 'Y')
    headLimitRotationConstraint = koikatsuCommons.addLimitRotationConstraint(metarig, koikatsuCommons.headBoneName, None, 'LOCAL', koikatsuCommons.limitRotationConstraintBaseName + koikatsuCommons.headConstraintSuffix, 
    True, math.radians(-180), math.radians(180), True, math.radians(-180), math.radians(180), True, math.radians(-180), math.radians(180))
    headTrackTargetParentArmatureConstraint = koikatsuCommons.addArmatureConstraint(metarig, koikatsuCommons.headTrackTargetParentBoneName, [placeholderHeadTweakBoneName, placeholderTorsoBoneName, placeholderRootBoneName], koikatsuCommons.armatureConstraintBaseName + koikatsuCommons.parentConstraintSuffix) 
    headTrackDampedTrackConstraint = koikatsuCommons.addDampedTrackConstraint(metarig, koikatsuCommons.headTrackBoneName, koikatsuCommons.headTrackTargetBoneName, koikatsuCommons.dampedTrackConstraintBaseName + koikatsuCommons.trackConstraintSuffix)
    
    eyelidsShapeKeyCopy = koikatsuCommons.duplicateShapeKey(koikatsuCommons.bodyName, koikatsuCommons.eyelidsShapeKeyName, koikatsuCommons.eyelidsShapeKeyCopyName)
    
    eyesHandleLocationXDriverVariable = koikatsuCommons.DriverVariable("locX", 'TRANSFORMS', metarig, koikatsuCommons.eyesHandleBoneName, 'LOCAL_SPACE', None, None, None, None, 'LOC_X', None)
    eyesHandleDefaultEyelidsValueDriverVariable = koikatsuCommons.DriverVariable("default", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesHandleDefaultEyelidsValueDataPath, None, None)
    eyesHandleMinEyelidsValueDriverVariable = koikatsuCommons.DriverVariable("min", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesHandleMinEyelidsValueDataPath, None, None)
    eyesHandleMaxEyelidsValueDriverVariable = koikatsuCommons.DriverVariable("max", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesHandleMaxEyelidsValueDataPath, None, None)
    eyesHandleEyelidsSpeedFactorDriverVariable = koikatsuCommons.DriverVariable("speed", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesHandleEyelidsSpeedFactorDataPath, None, None)
    eyesHandleEyelidsAutomationDriverVariable = koikatsuCommons.DriverVariable("enabled", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesHandleEyelidsAutomationDataPath, None, None)
    eyesHandleLimitLocationDriverVariable = koikatsuCommons.DriverVariable("limit", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesHandleLimitLocationDataPath, None, None)
    eyesHandleEyesSizeFactorDriverVariable = koikatsuCommons.DriverVariable("sizeFactor", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesHandleEyesSizeFactorDataPath, None, None)
    leftEyeHandleLimitLocationDriverVariable = koikatsuCommons.DriverVariable("limit_L", 'SINGLE_PROP', metarig, None, None, None, None, None, leftEyeHandleLimitLocationDataPath, None, None)
    leftEyeHandleMinXLocationDriverVariable = koikatsuCommons.DriverVariable("minX_L", 'SINGLE_PROP', metarig, None, None, None, None, None, leftEyeHandleMinXLocationDataPath, None, None)
    leftEyeHandleMaxXLocationDriverVariable = koikatsuCommons.DriverVariable("maxX_L", 'SINGLE_PROP', metarig, None, None, None, None, None, leftEyeHandleMaxXLocationDataPath, None, None)
    leftEyeHandleMinYLocationDriverVariable = koikatsuCommons.DriverVariable("minY_L", 'SINGLE_PROP', metarig, None, None, None, None, None, leftEyeHandleMinYLocationDataPath, None, None)
    leftEyeHandleMaxYLocationDriverVariable = koikatsuCommons.DriverVariable("maxY_L", 'SINGLE_PROP', metarig, None, None, None, None, None, leftEyeHandleMaxYLocationDataPath, None, None)
    leftEyeHandleSpeedCorrectionDriverVariable = koikatsuCommons.DriverVariable("corr_L", 'SINGLE_PROP', metarig, None, None, None, None, None, leftEyeHandleSpeedCorrectionDataPath, None, None)
    leftEyeHandleEyesHandleDistanceXDriverVariable = koikatsuCommons.DriverVariable("distX_L", 'LOC_DIFF', metarig, koikatsuCommons.eyesHandleMarkerBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.leftEyeHandleMarkerXBoneName, 'WORLD_SPACE', None, None, None)
    leftEyeHandleEyesHandleDistanceYDriverVariable = koikatsuCommons.DriverVariable("distY_L", 'LOC_DIFF', metarig, koikatsuCommons.eyesHandleMarkerBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.leftEyeHandleMarkerZBoneName, 'WORLD_SPACE', None, None, None)
    leftEyeHandleHeadDistanceXDriverVariable = koikatsuCommons.DriverVariable("headDistX_L", 'LOC_DIFF', metarig, koikatsuCommons.headBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.leftHeadMarkerXBoneName, 'WORLD_SPACE', None, None, None)
    leftEyeHandleHeadDistanceYDriverVariable = koikatsuCommons.DriverVariable("headDistY_L", 'LOC_DIFF', metarig, koikatsuCommons.headBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.leftHeadMarkerZBoneName, 'WORLD_SPACE', None, None, None)
    rightEyeHandleLimitLocationDriverVariable = koikatsuCommons.DriverVariable("limit_R", 'SINGLE_PROP', metarig, None, None, None, None, None, rightEyeHandleLimitLocationDataPath, None, None)
    rightEyeHandleMinXLocationDriverVariable = koikatsuCommons.DriverVariable("minX_R", 'SINGLE_PROP', metarig, None, None, None, None, None, rightEyeHandleMinXLocationDataPath, None, None)
    rightEyeHandleMaxXLocationDriverVariable = koikatsuCommons.DriverVariable("maxX_R", 'SINGLE_PROP', metarig, None, None, None, None, None, rightEyeHandleMaxXLocationDataPath, None, None)
    rightEyeHandleMinYLocationDriverVariable = koikatsuCommons.DriverVariable("minY_R", 'SINGLE_PROP', metarig, None, None, None, None, None, rightEyeHandleMinYLocationDataPath, None, None)
    rightEyeHandleMaxYLocationDriverVariable = koikatsuCommons.DriverVariable("maxY_R", 'SINGLE_PROP', metarig, None, None, None, None, None, rightEyeHandleMaxYLocationDataPath, None, None)
    rightEyeHandleSpeedCorrectionDriverVariable = koikatsuCommons.DriverVariable("corr_R", 'SINGLE_PROP', metarig, None, None, None, None, None, rightEyeHandleSpeedCorrectionDataPath, None, None)
    rightEyeHandleEyesHandleDistanceXDriverVariable = koikatsuCommons.DriverVariable("distX_R", 'LOC_DIFF', metarig, koikatsuCommons.eyesHandleMarkerBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.rightEyeHandleMarkerXBoneName, 'WORLD_SPACE', None, None, None)
    rightEyeHandleEyesHandleDistanceYDriverVariable = koikatsuCommons.DriverVariable("distY_R", 'LOC_DIFF', metarig, koikatsuCommons.eyesHandleMarkerBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.rightEyeHandleMarkerZBoneName, 'WORLD_SPACE', None, None, None)
    rightEyeHandleHeadDistanceXDriverVariable = koikatsuCommons.DriverVariable("headdDistX_R", 'LOC_DIFF', metarig, koikatsuCommons.headBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.rightHeadMarkerXBoneName, 'WORLD_SPACE', None, None, None)
    rightEyeHandleHeadDistanceYDriverVariable = koikatsuCommons.DriverVariable("headDistY_R", 'LOC_DIFF', metarig, koikatsuCommons.headBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.rightHeadMarkerZBoneName, 'WORLD_SPACE', None, None, None)
    eyesTrackTargetParentToHeadDriverVariable = koikatsuCommons.DriverVariable("parentHead", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesTrackTargetParentToHeadDataPath, None, None)
    eyesTrackTargetParentToTorsoDriverVariable = koikatsuCommons.DriverVariable("parentTorso", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesTrackTargetParentToTorsoDataPath, None, None)
    eyesTrackTargetParentToRootDriverVariable = koikatsuCommons.DriverVariable("parentRoot", 'SINGLE_PROP', metarig, None, None, None, None, None, eyesTrackTargetParentToRootDataPath, None, None)
    eyeballsSpeedFactorDriverVariable = koikatsuCommons.DriverVariable("rotSpeed", 'SINGLE_PROP', metarig, None, None, None, None, None, eyeballsSpeedFactorDataPath, None, None)
    eyeballsTrackTargetDriverVariable = koikatsuCommons.DriverVariable("track", 'SINGLE_PROP', metarig, None, None, None, None, None, eyeballsTrackTargetDataPath, None, None)
    eyeballsTrackSpeedFactorDriverVariable = koikatsuCommons.DriverVariable("trackSpeed", 'SINGLE_PROP', metarig, None, None, None, None, None, eyeballsTrackSpeedFactorDataPath, None, None)
    eyeballsNearbyTargetTrackCorrectionDriverVariable = koikatsuCommons.DriverVariable("trackCorr", 'SINGLE_PROP', metarig, None, None, None, None, None, eyeballsNearbyTargetTrackCorrectionDataPath, None, None)
    eyeballsNearbyTargetSizeFactorDriverVariable = koikatsuCommons.DriverVariable("factor", 'SINGLE_PROP', metarig, None, None, None, None, None, eyeballsNearbyTargetSizeFactorDataPath, None, None)
    leftEyeballRightEyeHandleMarkerDistanceDriverVariable = koikatsuCommons.DriverVariable("orgDist_L", 'LOC_DIFF', metarig, koikatsuCommons.leftEyeballTrackCorrectionBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.leftEyeHandleMarkerBoneName, 'WORLD_SPACE', None, None, None)
    rightEyeballRightEyeHandleMarkerDistanceDriverVariable = koikatsuCommons.DriverVariable("orgDist_R", 'LOC_DIFF', metarig, koikatsuCommons.rightEyeballTrackCorrectionBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.rightEyeHandleMarkerBoneName, 'WORLD_SPACE', None, None, None)
    leftEyeballEyesTrackTargetDistanceDriverVariable = koikatsuCommons.DriverVariable("currDist_L", 'LOC_DIFF', metarig, koikatsuCommons.leftEyeballTrackCorrectionBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.eyesTrackTargetBoneName, 'WORLD_SPACE', None, None, None)
    rightEyeballEyesTrackTargetDistanceDriverVariable = koikatsuCommons.DriverVariable("currDist_R", 'LOC_DIFF', metarig, koikatsuCommons.rightEyeballTrackCorrectionBoneName, 'WORLD_SPACE', metarig, koikatsuCommons.eyesTrackTargetBoneName, 'WORLD_SPACE', None, None, None)
    eyeballsTrackBoneRotationZDriverVariable = koikatsuCommons.DriverVariable("rotZ", 'TRANSFORMS', metarig, koikatsuCommons.eyeballsTrackBoneName, 'LOCAL_SPACE', None, None, None, None, 'ROT_Z', 'QUATERNION')
    leftEyeballTrackBoneRotationZDriverVariable = koikatsuCommons.DriverVariable("rotZ_L", 'TRANSFORMS', metarig, koikatsuCommons.leftEyeballTrackBoneName, 'LOCAL_SPACE', None, None, None, None, 'ROT_Z', 'QUATERNION')
    rightEyeballTrackBoneRotationZDriverVariable = koikatsuCommons.DriverVariable("rotZ_R", 'TRANSFORMS', metarig, koikatsuCommons.rightEyeballTrackBoneName, 'LOCAL_SPACE', None, None, None, None, 'ROT_Z', 'QUATERNION')
    headTrackTargetLimitRotationDriverVariable = koikatsuCommons.DriverVariable("limit", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetLimitRotationDataPath, None, None)
    headTrackTargetMinXRotationDriverVariable = koikatsuCommons.DriverVariable("minX", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetMinXRotationDataPath, None, None)
    headTrackTargetMaxXRotationDriverVariable = koikatsuCommons.DriverVariable("maxX", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetMaxXRotationDataPath, None, None)
    headTrackTargetMinYRotationDriverVariable = koikatsuCommons.DriverVariable("minY", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetMinYRotationDataPath, None, None)
    headTrackTargetMaxYRotationDriverVariable = koikatsuCommons.DriverVariable("maxY", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetMaxYRotationDataPath, None, None)
    headTrackTargetMinZRotationDriverVariable = koikatsuCommons.DriverVariable("minZ", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetMinZRotationDataPath, None, None)
    headTrackTargetMaxZRotationDriverVariable = koikatsuCommons.DriverVariable("maxZ", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetMaxZRotationDataPath, None, None)
    headTrackTargetParentToHeadDriverVariable = koikatsuCommons.DriverVariable("parentHead", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetParentToHeadDataPath, None, None)
    headTrackTargetParentToTorsoDriverVariable = koikatsuCommons.DriverVariable("parentTorso", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetParentToTorsoDataPath, None, None)
    headTrackTargetParentToRootDriverVariable = koikatsuCommons.DriverVariable("parentRoot", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetParentToRootDataPath, None, None)
    headTrackTargetDriverVariable = koikatsuCommons.DriverVariable("track", 'SINGLE_PROP', metarig, None, None, None, None, None, headTrackTargetTrackTargetDataPath, None, None)
    
    koikatsuCommons.addDriver(eyelidsShapeKeyCopy, "value", None, 'SCRIPTED', [eyesHandleLocationXDriverVariable, eyesHandleDefaultEyelidsValueDriverVariable, eyesHandleMinEyelidsValueDriverVariable, eyesHandleMaxEyelidsValueDriverVariable, eyesHandleEyelidsSpeedFactorDriverVariable, eyesHandleEyelidsAutomationDriverVariable], 
    eyesHandleEyelidsAutomationDriverVariable.name + " * (" + eyesHandleMinEyelidsValueDriverVariable.name + " if (" + eyesHandleDefaultEyelidsValueDriverVariable.name + " + " + eyesHandleLocationXDriverVariable.name + " * -" + eyesHandleEyelidsSpeedFactorDriverVariable.name + " if " + eyesHandleLocationXDriverVariable.name + " < 0 else " + eyesHandleDefaultEyelidsValueDriverVariable.name + " - " + eyesHandleLocationXDriverVariable.name + " * " + eyesHandleEyelidsSpeedFactorDriverVariable.name + ") < " + eyesHandleMinEyelidsValueDriverVariable.name + " else " + eyesHandleMaxEyelidsValueDriverVariable.name + " if (" + eyesHandleDefaultEyelidsValueDriverVariable.name + " + " + eyesHandleLocationXDriverVariable.name + " * -" + eyesHandleEyelidsSpeedFactorDriverVariable.name + " if " + eyesHandleLocationXDriverVariable.name + " < 0 else " + eyesHandleDefaultEyelidsValueDriverVariable.name + " - " + eyesHandleLocationXDriverVariable.name + " * " + eyesHandleEyelidsSpeedFactorDriverVariable.name + ") > " + eyesHandleMaxEyelidsValueDriverVariable.name + " else (" + eyesHandleDefaultEyelidsValueDriverVariable.name + " + " + eyesHandleLocationXDriverVariable.name + " * -" + eyesHandleEyelidsSpeedFactorDriverVariable.name + " if " + eyesHandleLocationXDriverVariable.name + " < 0 else " + eyesHandleDefaultEyelidsValueDriverVariable.name + " - " + eyesHandleLocationXDriverVariable.name + " * " + eyesHandleEyelidsSpeedFactorDriverVariable.name + "))")
    koikatsuCommons.addDriver(eyesHandleLimitLocationConstraint, "influence", None, 'AVERAGE', [eyesHandleLimitLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(eyesHandleLimitLocationConstraint, "min_x", None, 'SCRIPTED', [leftEyeHandleMinXLocationDriverVariable, rightEyeHandleMinXLocationDriverVariable, leftEyeHandleEyesHandleDistanceXDriverVariable, rightEyeHandleEyesHandleDistanceXDriverVariable], 
    leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleEyesHandleDistanceXDriverVariable.name + " if " + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleEyesHandleDistanceXDriverVariable.name + " <= " + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleEyesHandleDistanceXDriverVariable.name + " else " + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleEyesHandleDistanceXDriverVariable.name)
    koikatsuCommons.addDriver(eyesHandleLimitLocationConstraint, "max_x", None, 'SCRIPTED', [leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleEyesHandleDistanceXDriverVariable, rightEyeHandleEyesHandleDistanceXDriverVariable], 
    rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleEyesHandleDistanceXDriverVariable.name + " if " + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleEyesHandleDistanceXDriverVariable.name + " > " + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleEyesHandleDistanceXDriverVariable.name + " else " + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleEyesHandleDistanceXDriverVariable.name)
    koikatsuCommons.addDriver(eyesHandleLimitLocationConstraint, "min_y", None, 'SCRIPTED', [leftEyeHandleMinYLocationDriverVariable, rightEyeHandleMinYLocationDriverVariable, leftEyeHandleEyesHandleDistanceYDriverVariable, rightEyeHandleEyesHandleDistanceYDriverVariable], 
    leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleEyesHandleDistanceYDriverVariable.name + " if " + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleEyesHandleDistanceYDriverVariable.name + " <= " + rightEyeHandleMinYLocationDriverVariable.name + " + " + rightEyeHandleEyesHandleDistanceYDriverVariable.name + " else " + rightEyeHandleMinYLocationDriverVariable.name + " + " + rightEyeHandleEyesHandleDistanceYDriverVariable.name)
    koikatsuCommons.addDriver(eyesHandleLimitLocationConstraint, "max_y", None, 'SCRIPTED', [leftEyeHandleMaxYLocationDriverVariable, rightEyeHandleMaxYLocationDriverVariable, leftEyeHandleEyesHandleDistanceYDriverVariable, rightEyeHandleEyesHandleDistanceYDriverVariable], 
    rightEyeHandleMaxYLocationDriverVariable.name + " + " + rightEyeHandleEyesHandleDistanceYDriverVariable.name + " if " + rightEyeHandleMaxYLocationDriverVariable.name + " + " + rightEyeHandleEyesHandleDistanceYDriverVariable.name + " > " + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleEyesHandleDistanceYDriverVariable.name + " else " + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleEyesHandleDistanceYDriverVariable.name)
    koikatsuCommons.addDriver(eyesHandleTransformationConstraintEyeballLocation, "influence", None, 'SCRIPTED', [eyeballsSpeedFactorDriverVariable, eyeballsTrackTargetDriverVariable, eyeballsTrackSpeedFactorDriverVariable], 
    eyeballsSpeedFactorDriverVariable.name + " * (1 - " + eyeballsTrackTargetDriverVariable.name + ") + " + eyeballsTrackSpeedFactorDriverVariable.name + " * " + eyeballsTrackTargetDriverVariable.name)
    koikatsuCommons.addDriver(eyesHandleTransformationConstraintEyeballLocation, "to_min_x", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    "-" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(eyesHandleTransformationConstraintEyeballLocation, "to_max_x", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(eyesHandleTransformationConstraintEyeballLocation, "to_min_z", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    "-" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(eyesHandleTransformationConstraintEyeballLocation, "to_max_z", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(leftEyeHandleLimitLocationConstraint, "min_x", None, 'AVERAGE', [leftEyeHandleMinXLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(leftEyeHandleLimitLocationConstraint, "max_x", None, 'AVERAGE', [leftEyeHandleMaxXLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(leftEyeHandleLimitLocationConstraint, "min_y", None, 'AVERAGE', [leftEyeHandleMinYLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(leftEyeHandleLimitLocationConstraint, "max_y", None, 'AVERAGE', [leftEyeHandleMaxYLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMax, "to_max_z", None, 'SCRIPTED', [leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") * " + eyesHandleEyesSizeFactorDriverVariable.name + " / (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleLimitLocationConstraint, "influence", None, 'AVERAGE', [leftEyeHandleLimitLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMax, "influence", None, 'AVERAGE', [leftEyeHandleSpeedCorrectionDriverVariable], 
    None)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMax, "from_max_z", None, 'SCRIPTED', [leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMin, "from_min_z", None, 'SCRIPTED', [leftEyeHandleMinXLocationDriverVariable, rightEyeHandleMinXLocationDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else -" + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMin, "to_min_z", None, 'SCRIPTED', [leftEyeHandleMinXLocationDriverVariable, rightEyeHandleMinXLocationDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") * -" + eyesHandleEyesSizeFactorDriverVariable.name + " / (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") + " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMin, "influence", None, 'AVERAGE', [leftEyeHandleSpeedCorrectionDriverVariable], 
    None)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMax, "from_max_x", None, 'SCRIPTED', [leftEyeHandleMaxYLocationDriverVariable, rightEyeHandleMaxYLocationDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMax, "to_max_x", None, 'SCRIPTED', [leftEyeHandleMaxYLocationDriverVariable, rightEyeHandleMaxYLocationDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") * " + eyesHandleEyesSizeFactorDriverVariable.name + " / (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMin, "from_min_x", None, 'SCRIPTED', [leftEyeHandleMinYLocationDriverVariable, rightEyeHandleMinYLocationDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else -" + eyesHandleEyesSizeFactorDriverVariable.name + "")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintHandleLocationCorrectionMin, "to_min_x", None, 'SCRIPTED', [leftEyeHandleMinYLocationDriverVariable, rightEyeHandleMinYLocationDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") * -" + eyesHandleEyesSizeFactorDriverVariable.name + " / (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") + " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocation, "influence", None, 'SCRIPTED', [eyeballsSpeedFactorDriverVariable, eyeballsTrackTargetDriverVariable, eyeballsTrackSpeedFactorDriverVariable], 
    eyeballsSpeedFactorDriverVariable.name + " * (1 - " + eyeballsTrackTargetDriverVariable.name + ") + " + eyeballsTrackSpeedFactorDriverVariable.name + " * " + eyeballsTrackTargetDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "influence", None, 'SCRIPTED', [eyeballsSpeedFactorDriverVariable, eyeballsTrackTargetDriverVariable, leftEyeHandleSpeedCorrectionDriverVariable], 
    leftEyeHandleSpeedCorrectionDriverVariable.name + " * (1 - " + eyeballsTrackTargetDriverVariable.name + ") * " + eyeballsSpeedFactorDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "influence", None, 'SCRIPTED', [eyeballsSpeedFactorDriverVariable, eyeballsTrackTargetDriverVariable, leftEyeHandleSpeedCorrectionDriverVariable], 
    leftEyeHandleSpeedCorrectionDriverVariable.name + " * (1 - " + eyeballsTrackTargetDriverVariable.name + ") * " + eyeballsSpeedFactorDriverVariable.name)
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "to_max_z", None, 'SCRIPTED', [leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") * " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10 / (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "to_max_x", None, 'SCRIPTED', [leftEyeHandleMaxYLocationDriverVariable, rightEyeHandleMaxYLocationDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") * " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10 / (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "from_max_z_rot", None, 'SCRIPTED', [leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "radians(0) if (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else radians(180)")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "from_max_x_rot", None, 'SCRIPTED', [leftEyeHandleMaxYLocationDriverVariable, rightEyeHandleMaxYLocationDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "radians(0) if (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else radians(180)")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "to_min_z", None, 'SCRIPTED', [leftEyeHandleMinXLocationDriverVariable, rightEyeHandleMinXLocationDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") * -" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10 / (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") + " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "to_min_x", None, 'SCRIPTED', [leftEyeHandleMinYLocationDriverVariable, rightEyeHandleMinYLocationDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") * -" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10 / (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") + " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "from_min_z_rot", None, 'SCRIPTED', [leftEyeHandleMinXLocationDriverVariable, rightEyeHandleMinXLocationDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "radians(0) if (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else radians(-180)")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "from_min_x_rot", None, 'SCRIPTED', [leftEyeHandleMinYLocationDriverVariable, rightEyeHandleMinYLocationDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "radians(0) if (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else radians(-180)")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocation, "to_min_x", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    "-" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocation, "to_max_x", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocation, "to_min_z", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    "-" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(leftEyeHandleTransformationConstraintEyeballLocation, "to_max_z", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(rightEyeHandleLimitLocationConstraint, "min_x", None, 'AVERAGE', [rightEyeHandleMinXLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(rightEyeHandleLimitLocationConstraint, "max_x", None, 'AVERAGE', [rightEyeHandleMaxXLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(rightEyeHandleLimitLocationConstraint, "min_y", None, 'AVERAGE', [rightEyeHandleMinYLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(rightEyeHandleLimitLocationConstraint, "max_y", None, 'AVERAGE', [rightEyeHandleMaxYLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMax, "to_max_z", None, 'SCRIPTED', [rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") * " + eyesHandleEyesSizeFactorDriverVariable.name + " / (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleLimitLocationConstraint, "influence", None, 'AVERAGE', [rightEyeHandleLimitLocationDriverVariable], 
    None)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMax, "influence", None, 'AVERAGE', [rightEyeHandleSpeedCorrectionDriverVariable], 
    None)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMax, "from_max_z", None, 'SCRIPTED', [rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMin, "from_min_z", None, 'SCRIPTED', [rightEyeHandleMinXLocationDriverVariable, leftEyeHandleMinXLocationDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else -" + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMin, "to_min_z", None, 'SCRIPTED', [rightEyeHandleMinXLocationDriverVariable, leftEyeHandleMinXLocationDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") * -" + eyesHandleEyesSizeFactorDriverVariable.name + " / (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") + " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMin, "influence", None, 'AVERAGE', [rightEyeHandleSpeedCorrectionDriverVariable], 
    None)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMax, "from_max_x", None, 'SCRIPTED', [rightEyeHandleMaxYLocationDriverVariable, leftEyeHandleMaxYLocationDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMax, "to_max_x", None, 'SCRIPTED', [rightEyeHandleMaxYLocationDriverVariable, leftEyeHandleMaxYLocationDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") * " + eyesHandleEyesSizeFactorDriverVariable.name + " / (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMin, "from_min_x", None, 'SCRIPTED', [rightEyeHandleMinYLocationDriverVariable, leftEyeHandleMinYLocationDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else -" + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintHandleLocationCorrectionMin, "to_min_x", None, 'SCRIPTED', [rightEyeHandleMinYLocationDriverVariable, leftEyeHandleMinYLocationDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") * -" + eyesHandleEyesSizeFactorDriverVariable.name + " / (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") + " + eyesHandleEyesSizeFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocation, "influence", None, 'SCRIPTED', [eyeballsSpeedFactorDriverVariable, eyeballsTrackTargetDriverVariable, eyeballsTrackSpeedFactorDriverVariable], 
    eyeballsSpeedFactorDriverVariable.name + " * (1 - " + eyeballsTrackTargetDriverVariable.name + ") + " + eyeballsTrackSpeedFactorDriverVariable.name + " * " + eyeballsTrackTargetDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "influence", None, 'SCRIPTED', [eyeballsSpeedFactorDriverVariable, eyeballsTrackTargetDriverVariable, rightEyeHandleSpeedCorrectionDriverVariable], 
    rightEyeHandleSpeedCorrectionDriverVariable.name + " * (1 - " + eyeballsTrackTargetDriverVariable.name + ") * " + eyeballsSpeedFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "influence", None, 'SCRIPTED', [eyeballsSpeedFactorDriverVariable, eyeballsTrackTargetDriverVariable, rightEyeHandleSpeedCorrectionDriverVariable], 
    rightEyeHandleSpeedCorrectionDriverVariable.name + " * (1 - " + eyeballsTrackTargetDriverVariable.name + ") * " + eyeballsSpeedFactorDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "to_max_z", None, 'SCRIPTED', [rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") * " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10 / (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") - " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "to_max_x", None, 'SCRIPTED', [rightEyeHandleMaxYLocationDriverVariable, leftEyeHandleMaxYLocationDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") * " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10 / (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") - " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "from_max_z_rot", None, 'SCRIPTED', [rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "radians(0) if (" + rightEyeHandleMaxXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - (" + leftEyeHandleMaxXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else radians(180)")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMax, "from_max_x_rot", None, 'SCRIPTED', [rightEyeHandleMaxYLocationDriverVariable, leftEyeHandleMaxYLocationDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "radians(0) if (" + rightEyeHandleMaxYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - (" + leftEyeHandleMaxYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") <= 0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else radians(180)")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "to_min_z", None, 'SCRIPTED', [rightEyeHandleMinXLocationDriverVariable, leftEyeHandleMinXLocationDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") * -" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10 / (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") + " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "to_min_x", None, 'SCRIPTED', [rightEyeHandleMinYLocationDriverVariable, leftEyeHandleMinYLocationDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "0 if (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") * -" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10 / (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") + " + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "from_min_z_rot", None, 'SCRIPTED', [rightEyeHandleMinXLocationDriverVariable, leftEyeHandleMinXLocationDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "radians(0) if (" + rightEyeHandleMinXLocationDriverVariable.name + " + " + rightEyeHandleHeadDistanceXDriverVariable.name + ") - (" + leftEyeHandleMinXLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceXDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else radians(-180)")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocationCorrectionMin, "from_min_x_rot", None, 'SCRIPTED', [rightEyeHandleMinYLocationDriverVariable, leftEyeHandleMinYLocationDriverVariable, rightEyeHandleHeadDistanceYDriverVariable, leftEyeHandleHeadDistanceYDriverVariable, eyesHandleEyesSizeFactorDriverVariable], 
    "radians(0) if (" + rightEyeHandleMinYLocationDriverVariable.name + " - " + rightEyeHandleHeadDistanceYDriverVariable.name + ") - (" + leftEyeHandleMinYLocationDriverVariable.name + " - " + leftEyeHandleHeadDistanceYDriverVariable.name + ") >= -0.000001 * " + eyesHandleEyesSizeFactorDriverVariable.name + " else radians(-180)")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocation, "to_min_x", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    "-" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocation, "to_max_x", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocation, "to_min_z", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    "-" + eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(rightEyeHandleTransformationConstraintEyeballLocation, "to_max_z", None, 'SCRIPTED', [eyesHandleEyesSizeFactorDriverVariable], 
    eyesHandleEyesSizeFactorDriverVariable.name + " / 10")
    koikatsuCommons.addDriver(eyesTrackTargetParentArmatureConstraint.targets[0], "weight", None, 'AVERAGE', [eyesTrackTargetParentToHeadDriverVariable], 
    None)
    koikatsuCommons.addDriver(eyesTrackTargetParentArmatureConstraint.targets[1], "weight", None, 'AVERAGE', [eyesTrackTargetParentToTorsoDriverVariable], 
    None)
    koikatsuCommons.addDriver(eyesTrackTargetParentArmatureConstraint.targets[2], "weight", None, 'AVERAGE', [eyesTrackTargetParentToRootDriverVariable], 
    None)
    koikatsuCommons.addDriver(eyeballsCopyRotationConstraintTrack, "influence", None, 'AVERAGE', [eyeballsTrackTargetDriverVariable], 
    None)
    koikatsuCommons.addDriver(leftEyeballCopyRotationConstraintTrack, "influence", None, 'SCRIPTED', [eyeballsTrackTargetDriverVariable, eyeballsNearbyTargetTrackCorrectionDriverVariable], 
    eyeballsTrackTargetDriverVariable.name + " * " + eyeballsNearbyTargetTrackCorrectionDriverVariable.name)
    koikatsuCommons.addDriver(rightEyeballCopyRotationConstraintTrack, "influence", None, 'SCRIPTED', [eyeballsTrackTargetDriverVariable, eyeballsNearbyTargetTrackCorrectionDriverVariable], 
    eyeballsTrackTargetDriverVariable.name + " * " + eyeballsNearbyTargetTrackCorrectionDriverVariable.name)
    """
    koikatsuCommons.addDriver(metarig.pose.bones[koikatsuCommons.leftEyeballTrackCorrectionBoneName], "rotation_quaternion", 3, 'SCRIPTED', [leftEyeballRightEyeHandleMarkerDistanceDriverVariable, leftEyeballEyesTrackTargetDistanceDriverVariable, leftEyeballTrackBoneRotationZDriverVariable], 
    "radians(0) if " + leftEyeballRightEyeHandleMarkerDistanceDriverVariable.name + " - " + leftEyeballEyesTrackTargetDistanceDriverVariable.name + " <= 0 else (radians(-45) + " + leftEyeballTrackBoneRotationZDriverVariable.name + ") * (" + leftEyeballRightEyeHandleMarkerDistanceDriverVariable.name + " - " + leftEyeballEyesTrackTargetDistanceDriverVariable.name + ") * 15")
    koikatsuCommons.addDriver(metarig.pose.bones[koikatsuCommons.rightEyeballTrackCorrectionBoneName], "rotation_quaternion", 3, 'SCRIPTED', [rightEyeballRightEyeHandleMarkerDistanceDriverVariable, rightEyeballEyesTrackTargetDistanceDriverVariable, rightEyeballTrackBoneRotationZDriverVariable], 
    "radians(0) if " + rightEyeballRightEyeHandleMarkerDistanceDriverVariable.name + " - " + rightEyeballEyesTrackTargetDistanceDriverVariable.name + " <= 0 else (radians(45) + " + rightEyeballTrackBoneRotationZDriverVariable.name + ") * (" + rightEyeballRightEyeHandleMarkerDistanceDriverVariable.name + " - " + rightEyeballEyesTrackTargetDistanceDriverVariable.name + ") * 15")
    """
    koikatsuCommons.addDriver(metarig.pose.bones[koikatsuCommons.leftEyeballTrackCorrectionBoneName], "rotation_quaternion", 3, 'SCRIPTED', [leftEyeballRightEyeHandleMarkerDistanceDriverVariable, leftEyeballEyesTrackTargetDistanceDriverVariable, eyeballsTrackBoneRotationZDriverVariable, leftEyeballTrackBoneRotationZDriverVariable, leftEyeHandleSpeedCorrectionDriverVariable, leftEyeHandleMaxXLocationDriverVariable, rightEyeHandleMaxXLocationDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, eyeballsNearbyTargetSizeFactorDriverVariable], 
    "0 if " + leftEyeballRightEyeHandleMarkerDistanceDriverVariable.name + "-" + leftEyeballEyesTrackTargetDistanceDriverVariable.name + "<=0 else (radians(-45)+" + leftEyeballTrackBoneRotationZDriverVariable.name + ")*(" + leftEyeballRightEyeHandleMarkerDistanceDriverVariable.name + "-" + leftEyeballEyesTrackTargetDistanceDriverVariable.name + ")/" + eyeballsNearbyTargetSizeFactorDriverVariable.name + "*(" + eyeballsTrackBoneRotationZDriverVariable.name + "-" + leftEyeballTrackBoneRotationZDriverVariable.name + ")*20*(1 if (" + leftEyeHandleMaxXLocationDriverVariable.name + "-" + leftEyeHandleHeadDistanceXDriverVariable.name + ")-(" + rightEyeHandleMaxXLocationDriverVariable.name + "+" + rightEyeHandleHeadDistanceXDriverVariable.name + ")<=0.000001 else 1+" + leftEyeHandleSpeedCorrectionDriverVariable.name + "*(" + leftEyeHandleMaxXLocationDriverVariable.name + "-" + leftEyeHandleHeadDistanceXDriverVariable.name + ")/(" + rightEyeHandleMaxXLocationDriverVariable.name + "+" + rightEyeHandleHeadDistanceXDriverVariable.name + "))")
    koikatsuCommons.addDriver(metarig.pose.bones[koikatsuCommons.rightEyeballTrackCorrectionBoneName], "rotation_quaternion", 3, 'SCRIPTED', [rightEyeballRightEyeHandleMarkerDistanceDriverVariable, rightEyeballEyesTrackTargetDistanceDriverVariable, eyeballsTrackBoneRotationZDriverVariable, rightEyeballTrackBoneRotationZDriverVariable, rightEyeHandleSpeedCorrectionDriverVariable, rightEyeHandleMinXLocationDriverVariable, leftEyeHandleMinXLocationDriverVariable, rightEyeHandleHeadDistanceXDriverVariable, leftEyeHandleHeadDistanceXDriverVariable, eyeballsNearbyTargetSizeFactorDriverVariable], 
    "0 if " + rightEyeballRightEyeHandleMarkerDistanceDriverVariable.name + "-" + rightEyeballEyesTrackTargetDistanceDriverVariable.name + "<=0 else (radians(45)+" + rightEyeballTrackBoneRotationZDriverVariable.name + ")*(" + rightEyeballRightEyeHandleMarkerDistanceDriverVariable.name + "-" + rightEyeballEyesTrackTargetDistanceDriverVariable.name + ")/" + eyeballsNearbyTargetSizeFactorDriverVariable.name + "*(" + rightEyeballTrackBoneRotationZDriverVariable.name + "-" + eyeballsTrackBoneRotationZDriverVariable.name + ")*20*(1 if (" + rightEyeHandleMinXLocationDriverVariable.name + "+" + rightEyeHandleHeadDistanceXDriverVariable.name + ")-(" + leftEyeHandleMinXLocationDriverVariable.name + "-" + leftEyeHandleHeadDistanceXDriverVariable.name + ")>=-0.000001 else 1+" + rightEyeHandleSpeedCorrectionDriverVariable.name + "*(" + rightEyeHandleMinXLocationDriverVariable.name + "+" + rightEyeHandleHeadDistanceXDriverVariable.name + ")/(" + leftEyeHandleMinXLocationDriverVariable.name + "-" + leftEyeHandleHeadDistanceXDriverVariable.name + "))")
    koikatsuCommons.addDriver(headTransformationConstraintHeadRotation, "influence", None, 'AVERAGE', [headTrackTargetDriverVariable], 
    None)
    koikatsuCommons.addDriver(headLimitRotationConstraint, "influence", None, 'AVERAGE', [headTrackTargetLimitRotationDriverVariable], 
    None)
    koikatsuCommons.addDriver(headLimitRotationConstraint, "min_x", None, 'SCRIPTED', [headTrackTargetMinXRotationDriverVariable], 
    "radians(" + headTrackTargetMinXRotationDriverVariable.name + ")")
    koikatsuCommons.addDriver(headLimitRotationConstraint, "max_x", None, 'SCRIPTED', [headTrackTargetMaxXRotationDriverVariable], 
    "radians(" + headTrackTargetMaxXRotationDriverVariable.name + ")")
    koikatsuCommons.addDriver(headLimitRotationConstraint, "min_y", None, 'SCRIPTED', [headTrackTargetMinYRotationDriverVariable], 
    "radians(" + headTrackTargetMinYRotationDriverVariable.name + ")")
    koikatsuCommons.addDriver(headLimitRotationConstraint, "max_y", None, 'SCRIPTED', [headTrackTargetMaxYRotationDriverVariable], 
    "radians(" + headTrackTargetMaxYRotationDriverVariable.name + ")")
    koikatsuCommons.addDriver(headLimitRotationConstraint, "min_z", None, 'SCRIPTED', [headTrackTargetMinZRotationDriverVariable], 
    "radians(" + headTrackTargetMinZRotationDriverVariable.name + ")")
    koikatsuCommons.addDriver(headLimitRotationConstraint, "max_z", None, 'SCRIPTED', [headTrackTargetMaxZRotationDriverVariable], 
    "radians(" + headTrackTargetMaxZRotationDriverVariable.name + ")")    
    koikatsuCommons.addDriver(headTrackTargetParentArmatureConstraint.targets[0], "weight", None, 'AVERAGE', [headTrackTargetParentToHeadDriverVariable], 
    None)
    koikatsuCommons.addDriver(headTrackTargetParentArmatureConstraint.targets[1], "weight", None, 'AVERAGE', [headTrackTargetParentToTorsoDriverVariable], 
    None)
    koikatsuCommons.addDriver(headTrackTargetParentArmatureConstraint.targets[2], "weight", None, 'AVERAGE', [headTrackTargetParentToRootDriverVariable], 
    None)
    
    def finalizeEyeballBone(rig, boneName):
        rig.pose.bones[boneName].lock_location[0] = True
        rig.pose.bones[boneName].lock_location[1] = True
        rig.pose.bones[boneName].lock_location[2] = True
        
    finalizeEyeballBone(metarig, koikatsuCommons.eyeballsBoneName)
    finalizeEyeballBone(metarig, koikatsuCommons.leftEyeballBoneName)
    finalizeEyeballBone(metarig, koikatsuCommons.rightEyeballBoneName)
    
    """
    Begin Rigifying
    """
        
    # bpy.ops.pose.rigify_layer_init()
    # bpy.ops.armature.rigify_add_bone_groups()
    bpy.ops.armature.rigify_collection_select(index=2)
    bpy.ops.armature.rigify_collection_set_ui_row(index=2, row=1)
        
    for index, rigifyLayer in enumerate(koikatsuCommons.rigifyLayers):
        koikatsuCommons.setRigifyLayer(metarig, index, rigifyLayer)
    koikatsuCommons.setRootRigifyLayer(metarig, koikatsuCommons.rootBoneGroupIndex)

    bpy.ops.object.mode_set(mode='EDIT')
    
    def removeAllConstraints(rig, boneName):
        boneToEmpty = rig.pose.bones[boneName]
        for constraint in boneToEmpty.constraints:
            koikatsuCommons.removeConstraint(rig, boneName, constraint.name)

    removeAllConstraints(metarig, koikatsuCommons.leftElbowBoneName)
    removeAllConstraints(metarig, koikatsuCommons.rightElbowBoneName)
    removeAllConstraints(metarig, koikatsuCommons.leftWristBoneName)
    removeAllConstraints(metarig, koikatsuCommons.rightWristBoneName)
    removeAllConstraints(metarig, koikatsuCommons.leftToeBoneName)
    removeAllConstraints(metarig, koikatsuCommons.rightToeBoneName)
    removeAllConstraints(metarig, koikatsuCommons.leftAnkleBoneName)
    removeAllConstraints(metarig, koikatsuCommons.rightAnkleBoneName)
    removeAllConstraints(metarig, koikatsuCommons.leftKneeBoneName)
    removeAllConstraints(metarig, koikatsuCommons.rightKneeBoneName)

    def renameAllVertexGroups(vertexGroupNameOld, vertexGroupNameNew):
        for obj in bpy.context.scene.objects: 
            if obj.type == 'MESH':
                vertexGroup = bpy.data.objects[obj.name].vertex_groups.get(vertexGroupNameOld)
                if vertexGroup is not None:
                    vertexGroup.name = vertexGroupNameNew
    
    renameAllVertexGroups(koikatsuCommons.originalHeadDeformBoneName, koikatsuCommons.headDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.originalNeckDeformBoneName, koikatsuCommons.neckDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.originalUpperChestDeformBoneName, koikatsuCommons.upperChestDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.originalChestDeformBoneName, koikatsuCommons.chestDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.originalSpineDeformBoneName, koikatsuCommons.spineDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.originalHipsDeformBoneName, koikatsuCommons.hipsDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.originalLeftArmDeformBone1Name, koikatsuCommons.leftArmDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalRightArmDeformBone1Name, koikatsuCommons.rightArmDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftArmDeformBone2Name, koikatsuCommons.leftArmDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalRightArmDeformBone2Name, koikatsuCommons.rightArmDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftArmDeformBone3Name, koikatsuCommons.leftArmDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalRightArmDeformBone3Name, koikatsuCommons.rightArmDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftElbowDeformBone1Name, koikatsuCommons.leftElbowDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalRightElbowDeformBone1Name, koikatsuCommons.rightElbowDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftElbowDeformBone2Name, koikatsuCommons.leftElbowDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalRightElbowDeformBone2Name, koikatsuCommons.rightElbowDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftElbowDeformBone3Name, koikatsuCommons.leftElbowDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalRightElbowDeformBone3Name, koikatsuCommons.rightElbowDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftWristDeformBoneName, koikatsuCommons.leftWristDeformBoneName)    
    renameAllVertexGroups(koikatsuCommons.originalRightWristDeformBoneName, koikatsuCommons.rightWristDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.originalLeftThumbDeformBone1Name, koikatsuCommons.leftThumbDeformBone1Name)  
    renameAllVertexGroups(koikatsuCommons.originalRightThumbDeformBone1Name, koikatsuCommons.rightThumbDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftThumbDeformBone2Name, koikatsuCommons.leftThumbDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalRightThumbDeformBone2Name, koikatsuCommons.rightThumbDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftThumbDeformBone3Name, koikatsuCommons.leftThumbDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalRightThumbDeformBone3Name, koikatsuCommons.rightThumbDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftIndexFingerDeformBone1Name, koikatsuCommons.leftIndexFingerDeformBone1Name)   
    renameAllVertexGroups(koikatsuCommons.originalRightIndexFingerDeformBone1Name, koikatsuCommons.rightIndexFingerDeformBone1Name)  
    renameAllVertexGroups(koikatsuCommons.originalLeftIndexFingerDeformBone2Name, koikatsuCommons.leftIndexFingerDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalRightIndexFingerDeformBone2Name, koikatsuCommons.rightIndexFingerDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftIndexFingerDeformBone3Name, koikatsuCommons.leftIndexFingerDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalRightIndexFingerDeformBone3Name, koikatsuCommons.rightIndexFingerDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftMiddleFingerDeformBone1Name, koikatsuCommons.leftMiddleFingerDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalRightMiddleFingerDeformBone1Name, koikatsuCommons.rightMiddleFingerDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftMiddleFingerDeformBone2Name, koikatsuCommons.leftMiddleFingerDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalRightMiddleFingerDeformBone2Name, koikatsuCommons.rightMiddleFingerDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftMiddleFingerDeformBone3Name, koikatsuCommons.leftMiddleFingerDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalRightMiddleFingerDeformBone3Name, koikatsuCommons.rightMiddleFingerDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftRingFingerDeformBone1Name, koikatsuCommons.leftRingFingerDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalRightRingFingerDeformBone1Name, koikatsuCommons.rightRingFingerDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftRingFingerDeformBone2Name, koikatsuCommons.leftRingFingerDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalRightRingFingerDeformBone2Name, koikatsuCommons.rightRingFingerDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftRingFingerDeformBone3Name, koikatsuCommons.leftRingFingerDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalRightRingFingerDeformBone3Name, koikatsuCommons.rightRingFingerDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftLittleFingerDeformBone1Name, koikatsuCommons.leftLittleFingerDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalRightLittleFingerDeformBone1Name, koikatsuCommons.rightLittleFingerDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftLittleFingerDeformBone2Name, koikatsuCommons.leftLittleFingerDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalRightLittleFingerDeformBone2Name, koikatsuCommons.rightLittleFingerDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftLittleFingerDeformBone3Name, koikatsuCommons.leftLittleFingerDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalRightLittleFingerDeformBone3Name, koikatsuCommons.rightLittleFingerDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftThighDeformBone1Name, koikatsuCommons.leftThighDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalRightThighDeformBone1Name, koikatsuCommons.rightThighDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftThighDeformBone2Name, koikatsuCommons.leftThighDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalRightThighDeformBone2Name, koikatsuCommons.rightThighDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftThighDeformBone3Name, koikatsuCommons.leftThighDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalRightThighDeformBone3Name, koikatsuCommons.rightThighDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftLegDeformBone1Name, koikatsuCommons.leftLegDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalRightLegDeformBone1Name, koikatsuCommons.rightLegDeformBone1Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftLegDeformBone2Name, koikatsuCommons.leftLegDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalRightLegDeformBone2Name, koikatsuCommons.rightLegDeformBone2Name)
    renameAllVertexGroups(koikatsuCommons.originalLeftLegDeformBone3Name, koikatsuCommons.leftLegDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.originalRightLegDeformBone3Name, koikatsuCommons.rightLegDeformBone3Name)
    renameAllVertexGroups(koikatsuCommons.leftAnkleBoneName, koikatsuCommons.leftAnkleDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.rightAnkleBoneName, koikatsuCommons.rightAnkleDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.leftToeBoneName, koikatsuCommons.leftToeDeformBoneName)
    renameAllVertexGroups(koikatsuCommons.rightToeBoneName, koikatsuCommons.rightToeDeformBoneName)
    
    if hasSkirt:
        for primaryIndex in range(8):
            for secondaryIndex in range(6):
                renameAllVertexGroups(koikatsuCommons.getSkirtBoneName(False, primaryIndex, secondaryIndex), koikatsuCommons.getSkirtDeformBoneName(primaryIndex, secondaryIndex)) 
    
    def fix_bone_orientations(armature):
        # Connect all bones with their children if they have exactly one
        for bone in armature.data.edit_bones:
            if len(bone.children) == 1 and (metarig.data.bones[bone.name].collections.get(str(koikatsuCommons.originalAccessoryLayerIndex)) or metarig.data.bones[bone.name].collections.get(str(koikatsuCommons.originalMchLayerIndex))):
                p1 = bone.head
                p2 = bone.children[0].head
                dist = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2) ** (1/2)

                # Only connect them if the other bone is a certain distance away, otherwise blender will delete them
                if dist > 0.005:
                    bone.tail = bone.children[0].head
                    if len(bone.parent.children) == 1:  # if the bone's parent bone only has one child, connect the bones (Don't connect them all because that would mess up hand/finger bones)
                        bone.use_connect = True
                    
    fix_bone_orientations(metarig)
    
    accessoryBoneNames = []
    accessoryMchBoneNames = []
    faceMchBoneNames = []    
    for bone in metarig.data.edit_bones:
        if metarig.data.bones[bone.name].collections.get(str(koikatsuCommons.originalUpperFaceLayerIndex)) or metarig.data.bones[bone.name].collections.get(str(koikatsuCommons.originalLowerFaceLayerIndex)):
            if metarig.data.bones[bone.parent.name].collections.get(str(koikatsuCommons.originalMchLayerIndex)) and bone.parent.name not in faceMchBoneNames and not metarig.data.bones[bone.parent.name].collections.get(str(koikatsuCommons.originalUpperFaceLayerIndex)) and not metarig.data.bones[bone.parent.name].collections.get(str(koikatsuCommons.originalLowerFaceLayerIndex)):
                faceMchBoneNames.append(bone.parent.name)
        if metarig.data.bones[bone.name].collections.get(str(koikatsuCommons.originalAccessoryLayerIndex)):
            accessoryBoneNames.append(bone.name)
            if metarig.data.bones[bone.parent.name].collections.get(str(koikatsuCommons.originalMchLayerIndex)) and not metarig.data.bones[bone.parent.name].collections.get(str(koikatsuCommons.originalAccessoryLayerIndex)):
                accessoryMchBoneNames.append(bone.parent.name)
    
    def finalizeMchList(rig, mchBoneNames, sourceLayerIndex, excludedLayerIndexes, excludedList = None):
        for childBoneName in mchBoneNames:
            childBone = metarig.data.edit_bones[childBoneName]
            #childBone.length = childBone.length / 4
            if childBone.name == 'Center':
                continue
            if rig.data.bones[childBone.parent.name].collections.get(str(sourceLayerIndex)) and childBone.parent.name not in mchBoneNames:
                insideExcludedLayer = False
                for excludedLayerIndex in excludedLayerIndexes:
                    if rig.data.bones[childBone.parent.name].collections.get(str(excludedLayerIndex)):
                        insideExcludedLayer = True
                        break
                if not insideExcludedLayer and (excludedList is None or childBone.parent.name not in excludedList):
                    mchBoneNames.append(childBone.parent.name)
            
    finalizeMchList(metarig, faceMchBoneNames, koikatsuCommons.originalMchLayerIndex, [koikatsuCommons.originalUpperFaceLayerIndex, koikatsuCommons.originalLowerFaceLayerIndex])
    finalizeMchList(metarig, accessoryMchBoneNames, koikatsuCommons.originalMchLayerIndex, [koikatsuCommons.originalAccessoryLayerIndex], faceMchBoneNames)    
            
    accessoryBoneConnectedChildNames = [] 
    accessoryBoneConnectedParentNames = [] 
    accessoryMchConnectedParentNames = []
    for boneName in accessoryBoneNames:
        renameAllVertexGroups(boneName, koikatsuCommons.deformBonePrefix + boneName)
        bone = metarig.data.edit_bones[boneName]
        if bone.use_connect == False or bone.parent.name not in accessoryBoneNames:
            for childBone in bone.children:
                if childBone.use_connect == True and childBone.name in accessoryBoneNames:
                    accessoryBoneConnectedParentNames.append(bone.name)
                    break
            if bone.use_connect == True and bone.parent.name in accessoryMchBoneNames:
                accessoryMchConnectedParentNames.append(bone.parent.name)
        elif bone.use_connect == True:
            accessoryBoneConnectedChildNames.append(bone.name)
            if bone.parent.name in accessoryMchBoneNames:
                accessoryMchConnectedParentNames.append(bone.parent.name)
    
    def connectAndParentBones(rig, childBoneName, parentBoneName, connected):
        childBone = rig.data.edit_bones[childBoneName]
        parentBone = rig.data.edit_bones[parentBoneName]
        parentBone.tail = childBone.head
        childBone.parent = parentBone
        childBone.use_connect = connected
    
    if hasRiggedTongue:
        connectAndParentBones(metarig, koikatsuCommons.riggedTongueBone5Name, koikatsuCommons.riggedTongueBone4Name, True)
        connectAndParentBones(metarig, koikatsuCommons.riggedTongueBone4Name, koikatsuCommons.riggedTongueBone3Name, True)
        connectAndParentBones(metarig, koikatsuCommons.riggedTongueBone3Name, koikatsuCommons.riggedTongueBone2Name, True)
        connectAndParentBones(metarig, koikatsuCommons.riggedTongueBone2Name, koikatsuCommons.riggedTongueBone1Name, False)
    connectAndParentBones(metarig, koikatsuCommons.headBoneName, koikatsuCommons.neckBoneName, True)
    connectAndParentBones(metarig, koikatsuCommons.neckBoneName, koikatsuCommons.upperChestBoneName, False)
    connectAndParentBones(metarig, koikatsuCommons.upperChestBoneName, koikatsuCommons.chestBoneName, True)
    connectAndParentBones(metarig, koikatsuCommons.chestBoneName, koikatsuCommons.spineBoneName, True)
    connectAndParentBones(metarig, koikatsuCommons.spineBoneName, koikatsuCommons.hipsBoneName, True) 
    connectAndParentBones(metarig, koikatsuCommons.leftWristBoneName, koikatsuCommons.leftElbowBoneName, True) 
    connectAndParentBones(metarig, koikatsuCommons.rightWristBoneName, koikatsuCommons.rightElbowBoneName, True) 
    connectAndParentBones(metarig, koikatsuCommons.leftElbowBoneName, koikatsuCommons.leftArmBoneName, True) 
    connectAndParentBones(metarig, koikatsuCommons.rightElbowBoneName, koikatsuCommons.rightArmBoneName, True) 
    connectAndParentBones(metarig, koikatsuCommons.leftArmBoneName, koikatsuCommons.leftShoulderBoneName, False)
    connectAndParentBones(metarig, koikatsuCommons.rightArmBoneName, koikatsuCommons.rightShoulderBoneName, False)
    connectAndParentBones(metarig, koikatsuCommons.leftThumbBone3Name, koikatsuCommons.leftThumbBone2Name, True)  
    connectAndParentBones(metarig, koikatsuCommons.rightThumbBone3Name, koikatsuCommons.rightThumbBone2Name, True)  
    connectAndParentBones(metarig, koikatsuCommons.leftThumbBone2Name, koikatsuCommons.leftThumbBone1Name, True)  
    connectAndParentBones(metarig, koikatsuCommons.rightThumbBone2Name, koikatsuCommons.rightThumbBone1Name, True)  
    connectAndParentBones(metarig, koikatsuCommons.leftIndexFingerBone3Name, koikatsuCommons.leftIndexFingerBone2Name, True)
    connectAndParentBones(metarig, koikatsuCommons.rightIndexFingerBone3Name, koikatsuCommons.rightIndexFingerBone2Name, True)
    connectAndParentBones(metarig, koikatsuCommons.leftIndexFingerBone2Name, koikatsuCommons.leftIndexFingerBone1Name, True)
    connectAndParentBones(metarig, koikatsuCommons.rightIndexFingerBone2Name, koikatsuCommons.rightIndexFingerBone1Name, True)
    connectAndParentBones(metarig, koikatsuCommons.leftMiddleFingerBone3Name, koikatsuCommons.leftMiddleFingerBone2Name, True) 
    connectAndParentBones(metarig, koikatsuCommons.rightMiddleFingerBone3Name, koikatsuCommons.rightMiddleFingerBone2Name, True) 
    connectAndParentBones(metarig, koikatsuCommons.leftMiddleFingerBone2Name, koikatsuCommons.leftMiddleFingerBone1Name, True)   
    connectAndParentBones(metarig, koikatsuCommons.rightMiddleFingerBone2Name, koikatsuCommons.rightMiddleFingerBone1Name, True)   
    connectAndParentBones(metarig, koikatsuCommons.leftRingFingerBone3Name, koikatsuCommons.leftRingFingerBone2Name, True) 
    connectAndParentBones(metarig, koikatsuCommons.rightRingFingerBone3Name, koikatsuCommons.rightRingFingerBone2Name, True) 
    connectAndParentBones(metarig, koikatsuCommons.leftRingFingerBone2Name, koikatsuCommons.leftRingFingerBone1Name, True)   
    connectAndParentBones(metarig, koikatsuCommons.rightRingFingerBone2Name, koikatsuCommons.rightRingFingerBone1Name, True)   
    connectAndParentBones(metarig, koikatsuCommons.leftLittleFingerBone3Name, koikatsuCommons.leftLittleFingerBone2Name, True) 
    connectAndParentBones(metarig, koikatsuCommons.rightLittleFingerBone3Name, koikatsuCommons.rightLittleFingerBone2Name, True)  
    connectAndParentBones(metarig, koikatsuCommons.leftLittleFingerBone2Name, koikatsuCommons.leftLittleFingerBone1Name, True)       
    connectAndParentBones(metarig, koikatsuCommons.rightLittleFingerBone2Name, koikatsuCommons.rightLittleFingerBone1Name, True)      
    connectAndParentBones(metarig, koikatsuCommons.leftToeBoneName, koikatsuCommons.leftAnkleBoneName, True)
    connectAndParentBones(metarig, koikatsuCommons.rightToeBoneName, koikatsuCommons.rightAnkleBoneName, True)
    connectAndParentBones(metarig, koikatsuCommons.leftAnkleBoneName, koikatsuCommons.leftKneeBoneName, True)
    connectAndParentBones(metarig, koikatsuCommons.rightAnkleBoneName, koikatsuCommons.rightKneeBoneName, True)
    connectAndParentBones(metarig, koikatsuCommons.leftKneeBoneName, koikatsuCommons.leftLegBoneName, True)
    connectAndParentBones(metarig, koikatsuCommons.rightKneeBoneName, koikatsuCommons.rightLegBoneName, True)
    
    #using left vertex groups as reference for right bones because of inconsistent right group values
    def finalizeRiggedTongueSideBones(rig, leftBoneName, rightBoneName, length, factorX, factorY = None, factorZ = None):
        leftBone = rig.data.edit_bones[leftBoneName]
        rightBone = rig.data.edit_bones[rightBoneName]
        riggedTongueLeftBoneVertexGroupExtremities = koikatsuCommons.findVertexGroupExtremities(leftBoneName, koikatsuCommons.riggedTongueName)
        leftBone.head.x = riggedTongueLeftBoneVertexGroupExtremities.minX + math.dist([riggedTongueLeftBoneVertexGroupExtremities.minX], [riggedTongueLeftBoneVertexGroupExtremities.maxX]) * factorX
        leftBone.tail.x = leftBone.head.x
        rightBone.head.x = -leftBone.head.x
        rightBone.tail.x = rightBone.head.x
        if factorY:
            leftBone.head.y = riggedTongueLeftBoneVertexGroupExtremities.minY + math.dist([riggedTongueLeftBoneVertexGroupExtremities.minY], [riggedTongueLeftBoneVertexGroupExtremities.maxY]) * factorY
            leftBone.tail.y = leftBone.head.y
            rightBone.head.y = leftBone.head.y
            rightBone.tail.y = rightBone.head.y
        if factorZ:
            leftBone.head.z = riggedTongueLeftBoneVertexGroupExtremities.minZ + math.dist([riggedTongueLeftBoneVertexGroupExtremities.minZ], [riggedTongueLeftBoneVertexGroupExtremities.maxZ]) * factorZ
            rightBone.head.z = leftBone.head.z
        leftBone.length = length
        rightBone.length = length
    
    if hasRiggedTongue:
        riggedTongueBone2 = metarig.data.edit_bones[koikatsuCommons.riggedTongueBone2Name]
        finalizeRiggedTongueSideBones(metarig, koikatsuCommons.riggedTongueLeftBone3Name, koikatsuCommons.riggedTongueRightBone3Name, riggedTongueBone2.length, 0.75)
        finalizeRiggedTongueSideBones(metarig, koikatsuCommons.riggedTongueLeftBone4Name, koikatsuCommons.riggedTongueRightBone4Name, riggedTongueBone2.length, 0.65, 0.5, 0.5)
        finalizeRiggedTongueSideBones(metarig, koikatsuCommons.riggedTongueLeftBone5Name, koikatsuCommons.riggedTongueRightBone5Name, riggedTongueBone2.length, 0.65, 0.2, 0.3)
        riggedTongueBone5 = metarig.data.edit_bones[koikatsuCommons.riggedTongueBone5Name]
        riggedTongueLeftBone5VertexGroupExtremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.riggedTongueLeftBone5Name, koikatsuCommons.riggedTongueName)
        riggedTongueBone5.tail.z = riggedTongueLeftBone5VertexGroupExtremities.minZ + math.dist([riggedTongueLeftBone5VertexGroupExtremities.minZ], [riggedTongueLeftBone5VertexGroupExtremities.maxZ]) * 0.17
        riggedTongueBone5.tail.y = riggedTongueLeftBone5VertexGroupExtremities.minY
    if not hasHeadMod:
        metarig.data.edit_bones[koikatsuCommons.headBoneName].tail.z = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.originalFaceUpDeformBoneName, koikatsuCommons.bodyName).maxZ
    else:
        metarig.data.edit_bones[koikatsuCommons.headBoneName].tail.z = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.originalFaceBaseDeformBoneName, koikatsuCommons.bodyName).maxZ
    metarig.data.edit_bones[koikatsuCommons.hipsBoneName].head = metarig.data.edit_bones[koikatsuCommons.waistBoneName].head
    leftShoulderJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.leftShoulderJointCorrectionBoneName]
    rightShoulderJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.rightShoulderJointCorrectionBoneName]
    midLeftElbowJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.midLeftElbowJointCorrectionBoneName]
    midRightElbowJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.midRightElbowJointCorrectionBoneName]
    backLeftElbowJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.backLeftElbowJointCorrectionBoneName]
    backRightElbowJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.backRightElbowJointCorrectionBoneName]
    frontLeftElbowJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.frontLeftElbowJointCorrectionBoneName]
    frontRightElbowJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.frontRightElbowJointCorrectionBoneName]
    leftShoulderDeformBone = metarig.data.edit_bones[koikatsuCommons.leftShoulderDeformBoneName]
    rightShoulderDeformBone = metarig.data.edit_bones[koikatsuCommons.rightShoulderDeformBoneName]
    leftArmBone = metarig.data.edit_bones[koikatsuCommons.leftArmBoneName]
    rightArmBone = metarig.data.edit_bones[koikatsuCommons.rightArmBoneName]
    leftElbowBone = metarig.data.edit_bones[koikatsuCommons.leftElbowBoneName]
    rightElbowBone = metarig.data.edit_bones[koikatsuCommons.rightElbowBoneName]
    leftElbowBone.head.y = midLeftElbowJointCorrectionBone.head.y + math.dist([midLeftElbowJointCorrectionBone.head.y], [frontLeftElbowJointCorrectionBone.head.y]) * 0.33
    rightElbowBone.head.y = midRightElbowJointCorrectionBone.head.y + math.dist([midRightElbowJointCorrectionBone.head.y], [frontRightElbowJointCorrectionBone.head.y]) * 0.33
    leftElbowBone.roll = radians(0)
    rightElbowBone.roll = radians(0)
    frontLeftElbowJointCorrectionBone.roll = radians(180)
    #frontRightElbowJointCorrectionBone.roll = radians(180)
    backLeftElbowJointCorrectionBone.roll = radians(180)
    #backRightElbowJointCorrectionBone.roll = radians(180)
    leftShoulderJointCorrectionBone.tail = leftArmBone.tail
    rightShoulderJointCorrectionBone.tail = rightArmBone.tail
    leftShoulderJointCorrectionBone.roll = radians(90)
    rightShoulderJointCorrectionBone.roll = radians(-90)
    leftShoulderDeformBone.tail = leftArmBone.tail
    rightShoulderDeformBone.tail = rightArmBone.tail
    leftShoulderDeformBone.roll = radians(90)
    rightShoulderDeformBone.roll = radians(-90)
    leftWristBone = metarig.data.edit_bones[koikatsuCommons.leftWristBoneName]
    rightWristBone = metarig.data.edit_bones[koikatsuCommons.rightWristBoneName]
    leftWristBone.head.y = midLeftElbowJointCorrectionBone.head.y - math.dist([midLeftElbowJointCorrectionBone.head.y], [backLeftElbowJointCorrectionBone.head.y]) * 0.15
    rightWristBone.head.y = midRightElbowJointCorrectionBone.head.y - math.dist([midRightElbowJointCorrectionBone.head.y], [backRightElbowJointCorrectionBone.head.y]) * 0.15
    if leftWristBone.tail.z != leftWristBone.head.z:
        leftWristBone.tail.y = leftWristBone.head.y
        leftWristBone.tail.z = leftWristBone.head.z
        leftWristGroupExtremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftWristDeformBoneName, koikatsuCommons.bodyName)
        leftWristBone.tail.x = leftWristGroupExtremities.minX + math.dist([leftWristGroupExtremities.minX], [leftWristGroupExtremities.maxX]) * 0.66
    if rightWristBone.tail.z != rightWristBone.head.z:
        rightWristBone.tail.y = rightWristBone.head.y
        rightWristBone.tail.z = rightWristBone.head.z
        rightWristGroupExtremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.rightWristDeformBoneName, koikatsuCommons.bodyName)
        rightWristBone.tail.x = rightWristGroupExtremities.maxX - math.dist([rightWristGroupExtremities.minX], [rightWristGroupExtremities.maxX]) * 0.66
    leftToeBone = metarig.data.edit_bones[koikatsuCommons.leftToeBoneName]
    rightToeBone = metarig.data.edit_bones[koikatsuCommons.rightToeBoneName]
    leftToeBone.tail.z = leftToeBone.head.z
    rightToeBone.tail.z = rightToeBone.head.z
    leftToeBone.tail.y = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftToeDeformBoneName, koikatsuCommons.bodyName).minY
    rightToeBone.tail.y = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.rightToeDeformBoneName, koikatsuCommons.bodyName).minY
    leftAnkleGroupExtremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.leftAnkleDeformBoneName, koikatsuCommons.bodyName)
    rightAnkleGroupExtremities = koikatsuCommons.findVertexGroupExtremities(koikatsuCommons.rightAnkleDeformBoneName, koikatsuCommons.bodyName)
    midLeftKneeJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.midLeftKneeJointCorrectionBoneName]
    midRightKneeJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.midRightKneeJointCorrectionBoneName]
    backLeftKneeJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.backLeftKneeJointCorrectionBoneName]
    backRightKneeJointCorrectionBone = metarig.data.edit_bones[koikatsuCommons.backRightKneeJointCorrectionBoneName]
    metarig.data.edit_bones[koikatsuCommons.leftLegBoneName].head.y = midLeftKneeJointCorrectionBone.head.y + math.dist([midLeftKneeJointCorrectionBone.head.y], [backLeftKneeJointCorrectionBone.head.y]) * 0.33
    metarig.data.edit_bones[koikatsuCommons.rightLegBoneName].head.y = midRightKneeJointCorrectionBone.head.y + math.dist([midRightKneeJointCorrectionBone.head.y], [backRightKneeJointCorrectionBone.head.y]) * 0.33
    leftHeelBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.originalLeftHeelBoneName, koikatsuCommons.leftHeelBoneName)
    rightHeelBone = koikatsuCommons.copyBone(metarig, koikatsuCommons.originalRightHeelBoneName, koikatsuCommons.rightHeelBoneName)
    leftHeelBone.head.x = leftAnkleGroupExtremities.minX
    rightHeelBone.head.x = rightAnkleGroupExtremities.maxX
    leftHeelBone.head.y = leftAnkleGroupExtremities.maxY
    rightHeelBone.head.y = rightAnkleGroupExtremities.maxY
    leftHeelBone.head.z = leftAnkleGroupExtremities.minZ
    rightHeelBone.head.z = rightAnkleGroupExtremities.minZ
    leftHeelBone.tail.x = leftAnkleGroupExtremities.maxX
    rightHeelBone.tail.x = rightAnkleGroupExtremities.minX
    leftHeelBone.tail.y = leftAnkleGroupExtremities.maxY
    rightHeelBone.tail.y = rightAnkleGroupExtremities.maxY
    leftHeelBone.tail.z = leftAnkleGroupExtremities.minZ
    rightHeelBone.tail.z = rightAnkleGroupExtremities.minZ
    leftHeelBone.parent = metarig.data.edit_bones[koikatsuCommons.leftAnkleBoneName]
    rightHeelBone.parent = metarig.data.edit_bones[koikatsuCommons.rightAnkleBoneName]
    leftAnkleBone = metarig.data.edit_bones[koikatsuCommons.leftAnkleBoneName]
    rightAnkleBone = metarig.data.edit_bones[koikatsuCommons.rightAnkleBoneName]
    originalLeftLegDeformBone3 = metarig.data.edit_bones[koikatsuCommons.originalLeftLegDeformBone3Name]
    originalRightLegDeformBone3 = metarig.data.edit_bones[koikatsuCommons.originalRightLegDeformBone3Name]
    leftAnkleBone.head.z = leftAnkleBone.tail.z + math.dist([leftAnkleBone.tail.z], [originalLeftLegDeformBone3.head.z]) * 0.7
    rightAnkleBone.head.z = rightAnkleBone.tail.z + math.dist([rightAnkleBone.tail.z], [originalRightLegDeformBone3.head.z]) * 0.7
    leftAnkleBone.head.y = originalLeftLegDeformBone3.head.y + math.dist([originalLeftLegDeformBone3.head.y], [leftHeelBone.head.y]) * 0.2
    rightAnkleBone.head.y = originalRightLegDeformBone3.head.y + math.dist([originalRightLegDeformBone3.head.y], [rightHeelBone.head.y]) * 0.2
    
    def createPalmVertexGroups(wristVertexGroupName, palmVertexGroupName, rightSide, palmMinX, palmMaxX, palmMidY, lowerPalmMidY, higherPalmMidY):
        for object in bpy.context.scene.objects: 
            if object.type == 'MESH':
                wristVertexGroup = object.vertex_groups.get(wristVertexGroupName)
                if wristVertexGroup is not None:
                    wristVertexGroupExtremities = koikatsuCommons.findVertexGroupExtremities(wristVertexGroupName, object.name)
                    palmVertexGroup = object.vertex_groups.get(palmVertexGroupName)
                    if palmVertexGroup is None:
                        palmVertexGroup = object.vertex_groups.new(name = palmVertexGroupName)
                    for vertex in wristVertexGroupExtremities.vertices:
                        if (not rightSide and wristVertexGroupExtremities.coordinates[vertex.index][0] > palmMinX) or (rightSide and wristVertexGroupExtremities.coordinates[vertex.index][0] < palmMaxX):
                            if lowerPalmMidY is None or math.dist([wristVertexGroupExtremities.coordinates[vertex.index][1]], [palmMidY]) < math.dist([wristVertexGroupExtremities.coordinates[vertex.index][1]], [lowerPalmMidY]):
                                if higherPalmMidY is None or math.dist([wristVertexGroupExtremities.coordinates[vertex.index][1]], [palmMidY]) < math.dist([wristVertexGroupExtremities.coordinates[vertex.index][1]], [higherPalmMidY]):
                                    palmVertexGroup.add([vertex.index], wristVertexGroup.weight(vertex.index), 'REPLACE')
                                    wristVertexGroup.remove([vertex.index])
    
    leftIndexFingerBone1 = metarig.data.edit_bones[koikatsuCommons.leftIndexFingerBone1Name]
    rightIndexFingerBone1 = metarig.data.edit_bones[koikatsuCommons.rightIndexFingerBone1Name]
    leftMiddleFingerBone1 = metarig.data.edit_bones[koikatsuCommons.leftMiddleFingerBone1Name]
    rightMiddleFingerBone1 = metarig.data.edit_bones[koikatsuCommons.rightMiddleFingerBone1Name]
    leftRingFingerBone1 = metarig.data.edit_bones[koikatsuCommons.leftRingFingerBone1Name]
    rightRingFingerBone1 = metarig.data.edit_bones[koikatsuCommons.rightRingFingerBone1Name]
    leftLittleFingerBone1 = metarig.data.edit_bones[koikatsuCommons.leftLittleFingerBone1Name]
    rightLittleFingerBone1 = metarig.data.edit_bones[koikatsuCommons.rightLittleFingerBone1Name]
    leftPalmMinX = leftWristBone.tail.x - math.dist([leftWristBone.head.x], [leftWristBone.tail.x]) * 0.85
    rightPalmMaxX = rightWristBone.tail.x + math.dist([rightWristBone.head.x], [rightWristBone.tail.x]) * 0.85
    createPalmVertexGroups(koikatsuCommons.leftWristDeformBoneName, koikatsuCommons.leftIndexFingerPalmDeformBoneName, False, leftPalmMinX, None, leftIndexFingerBone1.head.y, None, leftMiddleFingerBone1.head.y)
    createPalmVertexGroups(koikatsuCommons.rightWristDeformBoneName, koikatsuCommons.rightIndexFingerPalmDeformBoneName, True, None, rightPalmMaxX, rightIndexFingerBone1.head.y, None, rightMiddleFingerBone1.head.y)
    createPalmVertexGroups(koikatsuCommons.leftWristDeformBoneName, koikatsuCommons.leftMiddleFingerPalmDeformBoneName, False, leftPalmMinX, None, leftMiddleFingerBone1.head.y, None, leftRingFingerBone1.head.y)
    createPalmVertexGroups(koikatsuCommons.rightWristDeformBoneName, koikatsuCommons.rightMiddleFingerPalmDeformBoneName, True, None, rightPalmMaxX, rightMiddleFingerBone1.head.y, None, rightRingFingerBone1.head.y)
    createPalmVertexGroups(koikatsuCommons.leftWristDeformBoneName, koikatsuCommons.leftRingFingerPalmDeformBoneName, False, leftPalmMinX, None, leftRingFingerBone1.head.y, None, leftLittleFingerBone1.head.y)
    createPalmVertexGroups(koikatsuCommons.rightWristDeformBoneName, koikatsuCommons.rightRingFingerPalmDeformBoneName, True, None, rightPalmMaxX, rightRingFingerBone1.head.y, None, rightLittleFingerBone1.head.y)
    createPalmVertexGroups(koikatsuCommons.leftWristDeformBoneName, koikatsuCommons.leftLittleFingerPalmDeformBoneName, False, leftPalmMinX, None, leftLittleFingerBone1.head.y, None, None)
    createPalmVertexGroups(koikatsuCommons.rightWristDeformBoneName, koikatsuCommons.rightLittleFingerPalmDeformBoneName, True, None, rightPalmMaxX, rightLittleFingerBone1.head.y, None, None)
    
    def finalizeFingerBones(leftSide, rig, wristBoneName, fingerPalmBoneName, fingerBone1Name, fingerBone2Name, fingerBone3Name, fingerDeformBone1Name, fingerDeformBone2Name, fingerDeformBone3Name, objectName, palmBoneRoll, fingerBone1Roll, fingerBone2Roll, fingerBone3Roll, middle = False, thumb = False):
        fingerBone1 = rig.data.edit_bones[fingerBone1Name]
        fingerBone2 = rig.data.edit_bones[fingerBone2Name]
        fingerBone3 = rig.data.edit_bones[fingerBone3Name]
        fingerDeformBone1Extremities = koikatsuCommons.findVertexGroupExtremities(fingerDeformBone1Name, objectName)
        fingerDeformBone2Extremities = koikatsuCommons.findVertexGroupExtremities(fingerDeformBone2Name, objectName)
        fingerDeformBone3Extremities = koikatsuCommons.findVertexGroupExtremities(fingerDeformBone3Name, objectName)
        if not thumb:
            if not middle:
                fingerBone1.head.z = fingerDeformBone1Extremities.minZ + math.dist([fingerDeformBone1Extremities.minZ], [fingerDeformBone1Extremities.maxZ]) * 0.4
            else:
                fingerBone1.head.z = fingerDeformBone1Extremities.minZ + math.dist([fingerDeformBone1Extremities.minZ], [fingerDeformBone1Extremities.maxZ]) * 0.5
            fingerBone2.head.z = fingerDeformBone2Extremities.minZ + math.dist([fingerDeformBone2Extremities.minZ], [fingerDeformBone2Extremities.maxZ]) * 0.6
            fingerBone3.head.z = fingerDeformBone3Extremities.minZ + math.dist([fingerDeformBone3Extremities.minZ], [fingerDeformBone3Extremities.maxZ]) * 0.6
            if leftSide:
                fingerBone3.tail.x = fingerDeformBone3Extremities.minX + math.dist([fingerDeformBone3Extremities.minX], [fingerDeformBone3Extremities.maxX]) * 0.95
            else:
                fingerBone3.tail.x = fingerDeformBone3Extremities.maxX - math.dist([fingerDeformBone3Extremities.minX], [fingerDeformBone3Extremities.maxX]) * 0.95
            fingerBone3.tail.y = fingerBone3.head.y + (fingerBone2.tail.y - fingerBone2.head.y)
            fingerBone3.tail.z = fingerDeformBone3Extremities.minZ + math.dist([fingerDeformBone3Extremities.minZ], [fingerDeformBone3Extremities.maxZ]) * 0.4
            wristBone = rig.data.edit_bones[wristBoneName]
            fingerPalmBone = koikatsuCommons.copyBone(rig, fingerBone1Name, fingerPalmBoneName)
            fingerPalmBone.parent = rig.data.edit_bones[wristBoneName]
            connectAndParentBones(rig, fingerBone1Name, fingerPalmBoneName, False)            
            fingerPalmBone.head.z = fingerPalmBone.tail.z
            if leftSide:
                fingerPalmBone.head.x = wristBone.tail.x - math.dist([wristBone.tail.x], [wristBone.head.x]) * 0.6
            else:
                fingerPalmBone.head.x = wristBone.tail.x + math.dist([wristBone.tail.x], [wristBone.head.x]) * 0.6
            fingerPalmBone.head.y = fingerPalmBone.head.y + (fingerBone1.head.y - fingerBone1.tail.y)
            fingerPalmBone.roll = palmBoneRoll
        else:
            if leftSide:
                fingerBone1.head.x = fingerDeformBone1Extremities.minX + math.dist([fingerDeformBone1Extremities.minX], [fingerDeformBone1Extremities.maxX]) * 0.2
                fingerBone2.head.x = fingerDeformBone2Extremities.minX + math.dist([fingerDeformBone2Extremities.minX], [fingerDeformBone2Extremities.maxX]) * 0.5
                fingerBone3.head.x = fingerDeformBone3Extremities.minX + math.dist([fingerDeformBone3Extremities.minX], [fingerDeformBone3Extremities.maxX]) * 0.4
                fingerBone3.tail.x = fingerDeformBone3Extremities.minX + math.dist([fingerDeformBone3Extremities.minX], [fingerDeformBone3Extremities.maxX]) * 0.95
            else:
                fingerBone1.head.x = fingerDeformBone1Extremities.maxX - math.dist([fingerDeformBone1Extremities.minX], [fingerDeformBone1Extremities.maxX]) * 0.2
                fingerBone2.head.x = fingerDeformBone2Extremities.maxX - math.dist([fingerDeformBone2Extremities.minX], [fingerDeformBone2Extremities.maxX]) * 0.5
                fingerBone3.head.x = fingerDeformBone3Extremities.maxX - math.dist([fingerDeformBone3Extremities.minX], [fingerDeformBone3Extremities.maxX]) * 0.4
                fingerBone3.tail.x = fingerDeformBone3Extremities.maxX - math.dist([fingerDeformBone3Extremities.minX], [fingerDeformBone3Extremities.maxX]) * 0.95
            fingerBone1.head.y = fingerDeformBone1Extremities.minY + math.dist([fingerDeformBone1Extremities.minY], [fingerDeformBone1Extremities.maxY]) * 0.45
            fingerBone1.head.z = fingerDeformBone1Extremities.minZ + math.dist([fingerDeformBone1Extremities.minZ], [fingerDeformBone1Extremities.maxZ]) * 0.35
            fingerBone2.head.y = fingerDeformBone2Extremities.minY + math.dist([fingerDeformBone2Extremities.minY], [fingerDeformBone2Extremities.maxY]) * 0.35
            fingerBone2.head.z = fingerDeformBone2Extremities.minZ + math.dist([fingerDeformBone2Extremities.minZ], [fingerDeformBone2Extremities.maxZ]) * 0.3
            fingerBone3.head.y = fingerDeformBone3Extremities.minY + math.dist([fingerDeformBone3Extremities.minY], [fingerDeformBone3Extremities.maxY]) * 0.4
            fingerBone3.head.z = fingerDeformBone3Extremities.minZ + math.dist([fingerDeformBone3Extremities.minZ], [fingerDeformBone3Extremities.maxZ]) * 0.45
            fingerBone3.tail.y = fingerDeformBone3Extremities.minY + math.dist([fingerDeformBone3Extremities.minY], [fingerDeformBone3Extremities.maxY]) * 0.1
            fingerBone3.tail.z = fingerDeformBone3Extremities.minZ + math.dist([fingerDeformBone3Extremities.minZ], [fingerDeformBone3Extremities.maxZ]) * 0.25
            fingerBone1.parent = rig.data.edit_bones[fingerPalmBoneName]
        fingerBone1.roll = fingerBone1Roll
        fingerBone2.roll = fingerBone2Roll
        fingerBone3.roll = fingerBone3Roll
        
    finalizeFingerBones(True, metarig, koikatsuCommons.leftWristBoneName, koikatsuCommons.leftIndexFingerPalmBoneName, koikatsuCommons.leftIndexFingerBone1Name, koikatsuCommons.leftIndexFingerBone2Name, koikatsuCommons.leftIndexFingerBone3Name, koikatsuCommons.leftIndexFingerDeformBone1Name, koikatsuCommons.leftIndexFingerDeformBone2Name, koikatsuCommons.leftIndexFingerDeformBone3Name, koikatsuCommons.bodyName, radians(0), radians(0), radians(5), radians(10))
    finalizeFingerBones(False, metarig, koikatsuCommons.rightWristBoneName, koikatsuCommons.rightIndexFingerPalmBoneName, koikatsuCommons.rightIndexFingerBone1Name, koikatsuCommons.rightIndexFingerBone2Name, koikatsuCommons.rightIndexFingerBone3Name, koikatsuCommons.rightIndexFingerDeformBone1Name, koikatsuCommons.rightIndexFingerDeformBone2Name, koikatsuCommons.rightIndexFingerDeformBone3Name, koikatsuCommons.bodyName, radians(0), radians(0), radians(-5), radians(-10))
    finalizeFingerBones(True, metarig, koikatsuCommons.leftWristBoneName, koikatsuCommons.leftMiddleFingerPalmBoneName, koikatsuCommons.leftMiddleFingerBone1Name, koikatsuCommons.leftMiddleFingerBone2Name, koikatsuCommons.leftMiddleFingerBone3Name, koikatsuCommons.leftMiddleFingerDeformBone1Name, koikatsuCommons.leftMiddleFingerDeformBone2Name, koikatsuCommons.leftMiddleFingerDeformBone3Name, koikatsuCommons.bodyName, radians(0), radians(-10), radians(-2), radians(6), True)
    finalizeFingerBones(False, metarig, koikatsuCommons.rightWristBoneName, koikatsuCommons.rightMiddleFingerPalmBoneName, koikatsuCommons.rightMiddleFingerBone1Name, koikatsuCommons.rightMiddleFingerBone2Name, koikatsuCommons.rightMiddleFingerBone3Name, koikatsuCommons.rightMiddleFingerDeformBone1Name, koikatsuCommons.rightMiddleFingerDeformBone2Name, koikatsuCommons.rightMiddleFingerDeformBone3Name, koikatsuCommons.bodyName, radians(0), radians(10), radians(2), radians(-6), True)
    finalizeFingerBones(True, metarig, koikatsuCommons.leftWristBoneName, koikatsuCommons.leftRingFingerPalmBoneName, koikatsuCommons.leftRingFingerBone1Name, koikatsuCommons.leftRingFingerBone2Name, koikatsuCommons.leftRingFingerBone3Name, koikatsuCommons.leftRingFingerDeformBone1Name, koikatsuCommons.leftRingFingerDeformBone2Name, koikatsuCommons.leftRingFingerDeformBone3Name, koikatsuCommons.bodyName, radians(0), radians(-15), radians(-10), radians(-5))
    finalizeFingerBones(False, metarig, koikatsuCommons.rightWristBoneName, koikatsuCommons.rightRingFingerPalmBoneName, koikatsuCommons.rightRingFingerBone1Name, koikatsuCommons.rightRingFingerBone2Name, koikatsuCommons.rightRingFingerBone3Name, koikatsuCommons.rightRingFingerDeformBone1Name, koikatsuCommons.rightRingFingerDeformBone2Name, koikatsuCommons.rightRingFingerDeformBone3Name, koikatsuCommons.bodyName, radians(0), radians(15), radians(10), radians(5))
    finalizeFingerBones(True, metarig, koikatsuCommons.leftWristBoneName, koikatsuCommons.leftLittleFingerPalmBoneName, koikatsuCommons.leftLittleFingerBone1Name, koikatsuCommons.leftLittleFingerBone2Name, koikatsuCommons.leftLittleFingerBone3Name, koikatsuCommons.leftLittleFingerDeformBone1Name, koikatsuCommons.leftLittleFingerDeformBone2Name, koikatsuCommons.leftLittleFingerDeformBone3Name, koikatsuCommons.bodyName, radians(0), radians(-20), radians(-18), radians(-16))
    finalizeFingerBones(False, metarig, koikatsuCommons.rightWristBoneName, koikatsuCommons.rightLittleFingerPalmBoneName, koikatsuCommons.rightLittleFingerBone1Name, koikatsuCommons.rightLittleFingerBone2Name, koikatsuCommons.rightLittleFingerBone3Name, koikatsuCommons.rightLittleFingerDeformBone1Name, koikatsuCommons.rightLittleFingerDeformBone2Name, koikatsuCommons.rightLittleFingerDeformBone3Name, koikatsuCommons.bodyName, radians(0), radians(20), radians(18), radians(16))
    finalizeFingerBones(True, metarig, koikatsuCommons.leftWristBoneName, koikatsuCommons.leftIndexFingerPalmBoneName, koikatsuCommons.leftThumbBone1Name, koikatsuCommons.leftThumbBone2Name, koikatsuCommons.leftThumbBone3Name, koikatsuCommons.leftThumbDeformBone1Name, koikatsuCommons.leftThumbDeformBone2Name, koikatsuCommons.leftThumbDeformBone3Name, koikatsuCommons.bodyName, None, radians(-257), radians(-260), radians(-263), False, True)
    finalizeFingerBones(False, metarig, koikatsuCommons.rightWristBoneName, koikatsuCommons.rightIndexFingerPalmBoneName, koikatsuCommons.rightThumbBone1Name, koikatsuCommons.rightThumbBone2Name, koikatsuCommons.rightThumbBone3Name, koikatsuCommons.rightThumbDeformBone1Name, koikatsuCommons.rightThumbDeformBone2Name, koikatsuCommons.rightThumbDeformBone3Name, koikatsuCommons.bodyName, None, radians(-103), radians(-106), radians(-109), False, True)
        
    skirtPalmBoneRatioReferences = [Vector((-0.0000, -0.0083, 0.0287)), Vector((-0.0057, -0.0080, 0.0294)), Vector((-0.0136, -0.0002, 0.0317)), Vector((-0.0094, 0.0151, 0.0360)), Vector((-0.0010, 0.0153, 0.0333)), Vector((0.0094, 0.0151, 0.0360)), Vector((0.0136, -0.0002, 0.0317)), Vector((0.0057, -0.0080, 0.0294))]
    if hasSkirt and not metarig.data.edit_bones.get(koikatsuCommons.skirtParentBoneCopyName):
        koikatsuCommons.copyBone(metarig, koikatsuCommons.skirtParentBoneName, koikatsuCommons.skirtParentBoneCopyName)
        for primaryIndex in range(8):
            skirtPalmBone = metarig.data.edit_bones[koikatsuCommons.getSkirtBoneName(True, primaryIndex)]
            skirtBone0 = metarig.data.edit_bones[koikatsuCommons.getSkirtBoneName(False, primaryIndex, 0)]
            skirtBone4 = metarig.data.edit_bones[koikatsuCommons.getSkirtBoneName(False, primaryIndex, 4)]
            skirtBone5 = metarig.data.edit_bones[koikatsuCommons.getSkirtBoneName(False, primaryIndex, 5)]
            skirtPalmBone.tail = skirtPalmBone.head - skirtPalmBoneRatioReferences[primaryIndex]
            skirtPalmBone.length = skirtBone0.length / 2
            headPos = skirtPalmBone.head.copy()
            skirtPalmBone.head = skirtPalmBone.tail
            skirtPalmBone.tail = headPos            
            skirtBone5.tail = skirtBone5.head - (skirtBone4.head - skirtBone4.tail)            
            skirtPalmBoneLength = skirtPalmBone.length
            shrinkFactorX = skirtPalmBone.head.x * 0.1
            shrinkFactorY = skirtPalmBone.head.y * 0.1
            skirtPalmBone.head = skirtPalmBone.head - Vector((shrinkFactorX, shrinkFactorY, 0))
            skirtPalmBone.tail = skirtPalmBone.tail - Vector((shrinkFactorX, shrinkFactorY, 0))
            skirtBoneLengths = []
            skirtBoneOrientations = []
            for secondaryIndex in range(6):
                skirtBone = metarig.data.edit_bones[koikatsuCommons.getSkirtBoneName(False, primaryIndex, secondaryIndex)]
                skirtBoneLengths.append(skirtBone.length)
                skirtBoneOrientations.append(skirtBone.tail - skirtBone.head)
                shrinkFactorX = skirtBone.head.x * 0.1
                shrinkFactorY = skirtBone.head.y * 0.1
                skirtBone.head = skirtBone.head - Vector((shrinkFactorX, shrinkFactorY, 0))
                skirtBone.tail = skirtBone.tail - Vector((shrinkFactorX, shrinkFactorY, 0))
            skirtPalmBone.length = skirtPalmBoneLength
            previousBoneOrientation = skirtPalmBone.tail - skirtPalmBone.head
            for secondaryIndex in range(6):
                skirtBone = metarig.data.edit_bones[koikatsuCommons.getSkirtBoneName(False, primaryIndex, secondaryIndex)]
                if secondaryIndex == 0:
                    skirtBone.tail = skirtBone.head + previousBoneOrientation * Vector((0.4, 0.4, 0.4)) + skirtBoneOrientations[secondaryIndex] * Vector((0.6, 0.6, 0.6))
                else:
                    skirtBone.tail = skirtBone.head + previousBoneOrientation * Vector((0.5, 0.5, 0.5)) + skirtBoneOrientations[secondaryIndex] * Vector((0, 0, 0.5))
                skirtBone.length = skirtBoneLengths[secondaryIndex]
                previousBoneOrientation = skirtBone.tail - skirtBone.head
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    legConstrainedBoneNames = [koikatsuCommons.waistJointCorrectionBoneName, koikatsuCommons.leftButtockJointCorrectionBoneName, koikatsuCommons.rightButtockJointCorrectionBoneName, koikatsuCommons.leftLegJointCorrectionBoneName, koikatsuCommons.rightLegJointCorrectionBoneName]
    for legConstrainedBoneName in legConstrainedBoneNames:
        for constraint in metarig.pose.bones[legConstrainedBoneName].constraints:
            if constraint.type == 'COPY_ROTATION' and (constraint.subtarget == koikatsuCommons.leftLegBoneName or constraint.subtarget == koikatsuCommons.rightLegBoneName):
                constraint.invert_y = True
                constraint.invert_z = True
                
    for driver in metarig.animation_data.drivers:
        if driver.data_path.startswith("pose.bones"):
            ownerName = driver.data_path.split('"')[1]
            property = driver.data_path.rsplit('.', 1)[1]
            if ownerName == koikatsuCommons.leftWristJointCorrectionBoneName and property == "location":
                driver.driver.expression = driver.driver.expression.replace(">", "<")
            elif (ownerName == koikatsuCommons.leftShoulderJointCorrectionBoneName or ownerName == koikatsuCommons.rightShoulderJointCorrectionBoneName) and property == "location":
                for variable in driver.driver.variables:
                    if len(variable.targets) == 1:
                        if variable.targets[0].bone_target == koikatsuCommons.leftArmBoneName:
                            if driver.array_index == 0:
                                leftShoulderJointCorrectionBoneDriverX = driver
                            elif driver.array_index == 1:
                                leftShoulderJointCorrectionBoneDriverY = driver
                            elif driver.array_index == 2:
                                leftShoulderJointCorrectionBoneDriverZ = driver
                        elif variable.targets[0].bone_target == koikatsuCommons.rightArmBoneName:
                            if driver.array_index == 0:
                                rightShoulderJointCorrectionBoneDriverX = driver
                            elif driver.array_index == 1:
                                rightShoulderJointCorrectionBoneDriverY = driver
                            elif driver.array_index == 2:
                                rightShoulderJointCorrectionBoneDriverZ = driver
                    
    shoulderJointCorrectionBoneDriverExpressionPrefix = "(-1)*"
    if not leftShoulderJointCorrectionBoneDriverX.driver.expression.startswith(shoulderJointCorrectionBoneDriverExpressionPrefix):
        originalExpressionX = leftShoulderJointCorrectionBoneDriverX.driver.expression
        leftShoulderJointCorrectionBoneDriverX.driver.expression = shoulderJointCorrectionBoneDriverExpressionPrefix + leftShoulderJointCorrectionBoneDriverY.driver.expression
        leftShoulderJointCorrectionBoneDriverX.driver.variables[0].targets[0].transform_type = 'ROT_Z'
        leftShoulderJointCorrectionBoneDriverY.driver.expression = originalExpressionX
        leftShoulderJointCorrectionBoneDriverY.driver.variables[0].targets[0].transform_type = 'ROT_X'
        leftShoulderJointCorrectionBoneDriverZ.driver.expression = shoulderJointCorrectionBoneDriverExpressionPrefix + leftShoulderJointCorrectionBoneDriverZ.driver.expression
        leftShoulderJointCorrectionBoneDriverZ.driver.variables[0].targets[0].transform_type = 'ROT_X'        
    if not rightShoulderJointCorrectionBoneDriverY.driver.expression.startswith(shoulderJointCorrectionBoneDriverExpressionPrefix):
        originalExpressionX = rightShoulderJointCorrectionBoneDriverX.driver.expression
        rightShoulderJointCorrectionBoneDriverX.driver.expression = rightShoulderJointCorrectionBoneDriverY.driver.expression
        rightShoulderJointCorrectionBoneDriverX.driver.variables[0].targets[0].transform_type = 'ROT_Z'
        rightShoulderJointCorrectionBoneDriverY.driver.expression = shoulderJointCorrectionBoneDriverExpressionPrefix + originalExpressionX
        rightShoulderJointCorrectionBoneDriverY.driver.variables[0].targets[0].transform_type = 'ROT_X'
        rightShoulderJointCorrectionBoneDriverZ.driver.expression = rightShoulderJointCorrectionBoneDriverZ.driver.expression
        rightShoulderJointCorrectionBoneDriverZ.driver.variables[0].targets[0].transform_type = 'ROT_X'
    
    for bone in metarig.pose.bones[:]:
        bone.rigify_type = "basic.raw_copy"
                       
    def finalizeFingerBoneParameters(rig, fingerBone1Name, fingerBone2Name, fingerBone3Name):
        metarig.pose.bones[fingerBone1Name].rigify_type = "limbs.super_finger"
        metarig.pose.bones[fingerBone1Name].rigify_parameters.primary_rotation_axis = "-X"
        metarig.pose.bones[fingerBone1Name].rigify_parameters.make_extra_ik_control = True
        metarig.pose.bones[fingerBone1Name].custom_shape = None
        # metarig.pose.bones[fingerBone1Name].rigify_parameters.tweak_layers[1] = False
        # metarig.pose.bones[fingerBone1Name].rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.fingersLayerName + koikatsuCommons.detailLayerSuffix)] = True
        metarig.pose.bones[fingerBone2Name].rigify_type = ""
        metarig.pose.bones[fingerBone2Name].custom_shape = None
        metarig.pose.bones[fingerBone3Name].rigify_type = ""
        metarig.pose.bones[fingerBone3Name].custom_shape = None
        
    metarig.pose.bones[koikatsuCommons.originalRootBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.eyesTrackTargetBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.eyesTrackTargetBoneName].rigify_parameters.optional_widget_type = "pivot_cross"
    metarig.pose.bones[koikatsuCommons.eyeballsBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.eyeballsBoneName].rigify_parameters.optional_widget_type = "bone"
    metarig.pose.bones[koikatsuCommons.leftEyeballBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftEyeballBoneName].rigify_parameters.optional_widget_type = "bone"
    metarig.pose.bones[koikatsuCommons.rightEyeballBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightEyeballBoneName].rigify_parameters.optional_widget_type = "bone"   
    if hasRiggedTongue:
        metarig.pose.bones[koikatsuCommons.riggedTongueBone1Name].rigify_parameters.optional_widget_type = "jaw" 
        metarig.pose.bones[koikatsuCommons.riggedTongueBone2Name].rigify_type = "limbs.super_finger"
        metarig.pose.bones[koikatsuCommons.riggedTongueBone2Name].rigify_parameters.primary_rotation_axis = "-X"
        metarig.pose.bones[koikatsuCommons.riggedTongueBone2Name].rigify_parameters.make_extra_ik_control = True
        metarig.pose.bones[koikatsuCommons.riggedTongueBone2Name].custom_shape = None
        # metarig.pose.bones[koikatsuCommons.riggedTongueBone2Name].rigify_parameters.tweak_layers[1] = False
        # metarig.pose.bones[koikatsuCommons.riggedTongueBone2Name].rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.eyesLayerName + koikatsuCommons.secondaryLayerSuffix)] = True
        metarig.pose.bones[koikatsuCommons.riggedTongueBone3Name].rigify_type = ""
        metarig.pose.bones[koikatsuCommons.riggedTongueBone3Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.riggedTongueLeftBone3Name].rigify_parameters.optional_widget_type = "sphere"
        metarig.pose.bones[koikatsuCommons.riggedTongueRightBone3Name].rigify_parameters.optional_widget_type = "sphere"
        metarig.pose.bones[koikatsuCommons.riggedTongueBone4Name].rigify_type = ""
        metarig.pose.bones[koikatsuCommons.riggedTongueBone4Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.riggedTongueLeftBone4Name].rigify_parameters.optional_widget_type = "sphere"
        metarig.pose.bones[koikatsuCommons.riggedTongueRightBone4Name].rigify_parameters.optional_widget_type = "sphere"
        metarig.pose.bones[koikatsuCommons.riggedTongueBone5Name].rigify_type = ""
        metarig.pose.bones[koikatsuCommons.riggedTongueBone5Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.riggedTongueLeftBone5Name].rigify_parameters.optional_widget_type = "sphere"
        metarig.pose.bones[koikatsuCommons.riggedTongueRightBone5Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.headBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.headBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.headTrackBoneName].rigify_parameters.relink_constraints = True
    metarig.pose.bones[koikatsuCommons.headTrackBoneName].rigify_parameters.parent_bone = koikatsuCommons.headTweakBoneName
    metarig.pose.bones[koikatsuCommons.headTrackTargetBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.headTrackTargetBoneName].rigify_parameters.optional_widget_type = "pivot_cross"  
    metarig.pose.bones[koikatsuCommons.neckBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.neckBoneName].rigify_type = "spines.super_head"
    metarig.pose.bones[koikatsuCommons.neckBoneName].rigify_parameters.connect_chain = True
    # metarig.pose.bones[koikatsuCommons.neckBoneName].rigify_parameters.tweak_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.neckBoneName].rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.torsoLayerName + koikatsuCommons.tweakLayerSuffix)] = True
    metarig.pose.bones[koikatsuCommons.upperChestBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.upperChestBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.chestBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.chestBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.spineBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.spineBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.hipsBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.hipsBoneName].rigify_type = "spines.basic_spine"
    metarig.pose.bones[koikatsuCommons.hipsBoneName].rigify_parameters.pivot_pos = 1
    # metarig.pose.bones[koikatsuCommons.hipsBoneName].rigify_parameters.tweak_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.hipsBoneName].rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.torsoLayerName + koikatsuCommons.tweakLayerSuffix)] = True
    # metarig.pose.bones[koikatsuCommons.hipsBoneName].rigify_parameters.fk_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.hipsBoneName].rigify_parameters.fk_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.torsoLayerName + koikatsuCommons.tweakLayerSuffix)] = True
    metarig.pose.bones[koikatsuCommons.waistBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.waistBoneName].rigify_parameters.optional_widget_type = "diamond"
    metarig.pose.bones[koikatsuCommons.crotchBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.crotchBoneName].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.anusBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.anusBoneName].rigify_parameters.optional_widget_type = "sphere"
    if hasBetterPenetrationMod:
        metarig.pose.bones[koikatsuCommons.betterPenetrationRootCrotchBoneName].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationRootCrotchBoneName].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationFrontCrotchBoneName].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationFrontCrotchBoneName].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone1Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone1Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone1Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone1Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone2Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone2Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone2Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone2Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone3Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone3Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone3Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone3Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone4Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone4Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone4Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone4Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone5Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationLeftCrotchBone5Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone5Name].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationRightCrotchBone5Name].rigify_parameters.optional_widget_type = "circle"
        metarig.pose.bones[koikatsuCommons.betterPenetrationBackCrotchBoneName].custom_shape = None
        metarig.pose.bones[koikatsuCommons.betterPenetrationBackCrotchBoneName].rigify_parameters.optional_widget_type = "circle"   
    metarig.pose.bones[koikatsuCommons.leftBreastDeformBone1Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.rightBreastDeformBone1Name].rigify_parameters.optional_widget_type = "sphere"
    widgetFace = bpy.data.objects[koikatsuCommons.widgetFaceName]
    metarig.pose.bones[koikatsuCommons.leftBreastBone2Name].custom_shape = widgetFace
    metarig.pose.bones[koikatsuCommons.rightBreastBone2Name].custom_shape = widgetFace
    def set_layer(bone_name, show_layer):
        if metarig.data.bones.get(str(bone_name)):
                if metarig.data.collections.get(str(show_layer)):
                    metarig.data.collections[str(show_layer)].assign(metarig.data.bones.get(bone_name))
                else:
                    metarig.data.collections.new(str(show_layer))
                    metarig.data.collections[str(show_layer)].assign(metarig.data.bones.get(bone_name))
    set_layer(koikatsuCommons.leftBreastBone2Name, koikatsuCommons.originalFkLayerIndex)
    set_layer(koikatsuCommons.rightBreastBone2Name, koikatsuCommons.originalFkLayerIndex)
    metarig.pose.bones[koikatsuCommons.leftBreastDeformBone2Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.rightBreastDeformBone2Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.leftBreastBone3Name].custom_shape = widgetFace
    metarig.pose.bones[koikatsuCommons.rightBreastBone3Name].custom_shape = widgetFace
    metarig.pose.bones[koikatsuCommons.leftBreastDeformBone3Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.rightBreastDeformBone3Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.leftNippleBone1Name].custom_shape = widgetFace
    metarig.pose.bones[koikatsuCommons.rightNippleBone1Name].custom_shape = widgetFace
    metarig.pose.bones[koikatsuCommons.leftNippleDeformBone1Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.rightNippleDeformBone1Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.leftNippleBone2Name].custom_shape = widgetFace
    metarig.pose.bones[koikatsuCommons.rightNippleBone2Name].custom_shape = widgetFace
    metarig.pose.bones[koikatsuCommons.leftNippleDeformBone2Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.rightNippleDeformBone2Name].rigify_parameters.optional_widget_type = "sphere"
    metarig.pose.bones[koikatsuCommons.leftShoulderBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightShoulderBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftShoulderBoneName].rigify_parameters.optional_widget_type = "shoulder"
    metarig.pose.bones[koikatsuCommons.rightShoulderBoneName].rigify_parameters.optional_widget_type = "shoulder"
    metarig.pose.bones[koikatsuCommons.leftArmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightArmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_type = "limbs.arm"
    metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_type = "limbs.arm"
    metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_parameters.segments = 3
    metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_parameters.segments = 3
    metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_parameters.rotation_axis = "automatic"
    metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_parameters.rotation_axis = "automatic"
    if (bpy.app.version[0] == 3 and bpy.app.version[1] >= 3) or bpy.app.version[0] > 3:
        metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_parameters.limb_uniform_scale = True
        metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_parameters.limb_uniform_scale = True
    metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_parameters.auto_align_extremity = True
    metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_parameters.auto_align_extremity = True
    metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_parameters.make_ik_wrist_pivot = True
    metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_parameters.make_ik_wrist_pivot = True
    # metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_parameters.tweak_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_parameters.tweak_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.leftArmLayerName + koikatsuCommons.tweakLayerSuffix)] = True
    # metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.rightArmLayerName + koikatsuCommons.tweakLayerSuffix)] = True
    # metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_parameters.fk_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_parameters.fk_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.leftArmBoneName].rigify_parameters.fk_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.leftArmLayerName + koikatsuCommons.fkLayerSuffix)] = True
    # metarig.pose.bones[koikatsuCommons.rightArmBoneName].rigify_parameters.fk_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.rightArmLayerName + koikatsuCommons.fkLayerSuffix)] = True
    metarig.pose.bones[koikatsuCommons.leftElbowBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightElbowBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftElbowBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.rightElbowBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.originalLeftElbowPoleBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalRightElbowPoleBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalLeftWristBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalRightWristBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalRightElbowPoleBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftWristBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.rightWristBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.frontLeftElbowJointCorrectionBoneName].rigify_parameters.relink_constraints = True
    metarig.pose.bones[koikatsuCommons.frontRightElbowJointCorrectionBoneName].rigify_parameters.relink_constraints = True
    metarig.pose.bones[koikatsuCommons.frontLeftElbowJointCorrectionBoneName].rigify_parameters.parent_bone = koikatsuCommons.leftElbowDeformBone1Name
    metarig.pose.bones[koikatsuCommons.frontRightElbowJointCorrectionBoneName].rigify_parameters.parent_bone = koikatsuCommons.rightElbowDeformBone1Name
    metarig.pose.bones[koikatsuCommons.midLeftElbowJointCorrectionBoneName].rigify_parameters.relink_constraints = True
    metarig.pose.bones[koikatsuCommons.midRightElbowJointCorrectionBoneName].rigify_parameters.relink_constraints = True
    metarig.pose.bones[koikatsuCommons.midLeftElbowJointCorrectionBoneName].rigify_parameters.parent_bone = koikatsuCommons.leftElbowDeformBone1Name
    metarig.pose.bones[koikatsuCommons.midRightElbowJointCorrectionBoneName].rigify_parameters.parent_bone = koikatsuCommons.rightElbowDeformBone1Name
    metarig.pose.bones[koikatsuCommons.leftIndexFingerPalmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightIndexFingerPalmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftIndexFingerPalmBoneName].rigify_type = "limbs.super_palm"
    metarig.pose.bones[koikatsuCommons.rightIndexFingerPalmBoneName].rigify_type = "limbs.super_palm"
    metarig.pose.bones[koikatsuCommons.leftIndexFingerPalmBoneName].rigify_parameters.palm_both_sides = True
    metarig.pose.bones[koikatsuCommons.rightIndexFingerPalmBoneName].rigify_parameters.palm_both_sides = True
    metarig.pose.bones[koikatsuCommons.leftIndexFingerPalmBoneName].rigify_parameters.palm_rotation_axis = 'X'
    metarig.pose.bones[koikatsuCommons.rightIndexFingerPalmBoneName].rigify_parameters.palm_rotation_axis = 'X'
    metarig.pose.bones[koikatsuCommons.leftIndexFingerPalmBoneName].rigify_parameters.make_extra_control = True
    metarig.pose.bones[koikatsuCommons.rightIndexFingerPalmBoneName].rigify_parameters.make_extra_control = True
    metarig.pose.bones[koikatsuCommons.leftMiddleFingerPalmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightMiddleFingerPalmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftMiddleFingerPalmBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.rightMiddleFingerPalmBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.leftRingFingerPalmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightRingFingerPalmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftRingFingerPalmBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.rightRingFingerPalmBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.leftLittleFingerPalmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightLittleFingerPalmBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftLittleFingerPalmBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.rightLittleFingerPalmBoneName].rigify_type = ""
    finalizeFingerBoneParameters(metarig, koikatsuCommons.leftThumbBone1Name, koikatsuCommons.leftThumbBone2Name, koikatsuCommons.leftThumbBone3Name)
    finalizeFingerBoneParameters(metarig, koikatsuCommons.rightThumbBone1Name, koikatsuCommons.rightThumbBone2Name, koikatsuCommons.rightThumbBone3Name)
    finalizeFingerBoneParameters(metarig, koikatsuCommons.leftIndexFingerBone1Name, koikatsuCommons.leftIndexFingerBone2Name, koikatsuCommons.leftIndexFingerBone3Name)
    finalizeFingerBoneParameters(metarig, koikatsuCommons.rightIndexFingerBone1Name, koikatsuCommons.rightIndexFingerBone2Name, koikatsuCommons.rightIndexFingerBone3Name)
    finalizeFingerBoneParameters(metarig, koikatsuCommons.leftMiddleFingerBone1Name, koikatsuCommons.leftMiddleFingerBone2Name, koikatsuCommons.leftMiddleFingerBone3Name)
    finalizeFingerBoneParameters(metarig, koikatsuCommons.rightMiddleFingerBone1Name, koikatsuCommons.rightMiddleFingerBone2Name, koikatsuCommons.rightMiddleFingerBone3Name)
    finalizeFingerBoneParameters(metarig, koikatsuCommons.leftRingFingerBone1Name, koikatsuCommons.leftRingFingerBone2Name, koikatsuCommons.leftRingFingerBone3Name)
    finalizeFingerBoneParameters(metarig, koikatsuCommons.rightRingFingerBone1Name, koikatsuCommons.rightRingFingerBone2Name, koikatsuCommons.rightRingFingerBone3Name)
    finalizeFingerBoneParameters(metarig, koikatsuCommons.leftLittleFingerBone1Name, koikatsuCommons.leftLittleFingerBone2Name, koikatsuCommons.leftLittleFingerBone3Name)
    finalizeFingerBoneParameters(metarig, koikatsuCommons.rightLittleFingerBone1Name, koikatsuCommons.rightLittleFingerBone2Name, koikatsuCommons.rightLittleFingerBone3Name)
    metarig.pose.bones[koikatsuCommons.leftLegBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightLegBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftLegBoneName].rigify_type = "limbs.leg"
    metarig.pose.bones[koikatsuCommons.rightLegBoneName].rigify_type = "limbs.leg"
    if (bpy.app.version[0] == 3 and bpy.app.version[1] >= 2) or bpy.app.version[0] > 3:
        metarig.pose.bones[koikatsuCommons.leftLegBoneName].rigify_parameters.extra_ik_toe = True
        metarig.pose.bones[koikatsuCommons.rightLegBoneName].rigify_parameters.extra_ik_toe = True
    metarig.pose.bones[koikatsuCommons.leftLegBoneName].rigify_parameters.segments = 3
    metarig.pose.bones[koikatsuCommons.rightLegBoneName].rigify_parameters.segments = 3
    metarig.pose.bones[koikatsuCommons.leftLegBoneName].rigify_parameters.rotation_axis = "automatic"
    metarig.pose.bones[koikatsuCommons.rightLegBoneName].rigify_parameters.rotation_axis = "automatic"
    if (bpy.app.version[0] == 3 and bpy.app.version[1] >= 3) or bpy.app.version[0] > 3:
        metarig.pose.bones[koikatsuCommons.leftLegBoneName].rigify_parameters.limb_uniform_scale = True
        metarig.pose.bones[koikatsuCommons.rightLegBoneName].rigify_parameters.limb_uniform_scale = True
    # metarig.pose.bones[koikatsuCommons.leftLegBoneName].rigify_parameters.tweak_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.rightLegBoneName].rigify_parameters.tweak_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.leftLegBoneName].rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.leftLegLayerName + koikatsuCommons.tweakLayerSuffix)] = True
    # metarig.pose.bones[koikatsuCommons.rightLegBoneName].rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.rightLegLayerName + koikatsuCommons.tweakLayerSuffix)] = True
    # metarig.pose.bones[koikatsuCommons.leftLegBoneName].rigify_parameters.fk_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.rightLegBoneName].rigify_parameters.fk_layers[1] = False
    # metarig.pose.bones[koikatsuCommons.leftLegBoneName].rigify_parameters.fk_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.leftLegLayerName + koikatsuCommons.fkLayerSuffix)] = True
    # metarig.pose.bones[koikatsuCommons.rightLegBoneName].rigify_parameters.fk_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.rightLegLayerName + koikatsuCommons.fkLayerSuffix)] = True
    metarig.pose.bones[koikatsuCommons.leftKneeBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightKneeBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftKneeBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.rightKneeBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.originalLeftKneePoleBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalRightKneePoleBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalLeftAnkleBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalRightAnkleBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftAnkleBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightAnkleBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftAnkleBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.rightAnkleBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.originalLeftToeBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalRightToeBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftToeBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightToeBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftToeBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.rightToeBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.originalLeftHeelIkBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalRightHeelIkBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalLeftHeelBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.originalRightHeelBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftHeelBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.rightHeelBoneName].custom_shape = None
    metarig.pose.bones[koikatsuCommons.leftHeelBoneName].rigify_type = ""
    metarig.pose.bones[koikatsuCommons.rightHeelBoneName].rigify_type = ""
    set_layer(koikatsuCommons.leftHeelBoneName, koikatsuCommons.originalFkLayerIndex)
    set_layer(koikatsuCommons.rightHeelBoneName, koikatsuCommons.originalFkLayerIndex)
    metarig.pose.bones[koikatsuCommons.frontLeftKneeJointCorrectionBoneName].rigify_parameters.relink_constraints = True
    metarig.pose.bones[koikatsuCommons.frontRightKneeJointCorrectionBoneName].rigify_parameters.relink_constraints = True
    metarig.pose.bones[koikatsuCommons.frontLeftKneeJointCorrectionBoneName].rigify_parameters.parent_bone = koikatsuCommons.leftLegDeformBone1Name
    metarig.pose.bones[koikatsuCommons.frontRightKneeJointCorrectionBoneName].rigify_parameters.parent_bone = koikatsuCommons.rightLegDeformBone1Name
    metarig.pose.bones[koikatsuCommons.midLeftKneeJointCorrectionBoneName].rigify_parameters.relink_constraints = True
    metarig.pose.bones[koikatsuCommons.midRightKneeJointCorrectionBoneName].rigify_parameters.relink_constraints = True
    metarig.pose.bones[koikatsuCommons.midLeftKneeJointCorrectionBoneName].rigify_parameters.parent_bone = koikatsuCommons.leftLegDeformBone1Name
    metarig.pose.bones[koikatsuCommons.midRightKneeJointCorrectionBoneName].rigify_parameters.parent_bone = koikatsuCommons.rightLegDeformBone1Name
    
    if isMale:
        koikatsuCommons.torsoLayerBoneNames.remove(koikatsuCommons.breastsHandleBoneName)
        koikatsuCommons.torsoLayerBoneNames.remove(koikatsuCommons.leftBreastHandleBoneName)
        koikatsuCommons.torsoLayerBoneNames.remove(koikatsuCommons.rightBreastHandleBoneName) 
        
    if not hasRiggedTongue:
        try:
            koikatsuCommons.eyesPrimaryLayerBoneNames.remove(koikatsuCommons.riggedTongueBone1Name)
            koikatsuCommons.eyesPrimaryLayerBoneNames.remove(koikatsuCommons.riggedTongueBone2Name)
            koikatsuCommons.eyesPrimaryLayerBoneNames.remove(koikatsuCommons.riggedTongueBone3Name)
            koikatsuCommons.eyesPrimaryLayerBoneNames.remove(koikatsuCommons.riggedTongueBone4Name)
            koikatsuCommons.eyesPrimaryLayerBoneNames.remove(koikatsuCommons.riggedTongueBone5Name)
            koikatsuCommons.eyesSecondaryLayerBoneNames.remove(koikatsuCommons.riggedTongueLeftBone3Name)
            koikatsuCommons.eyesSecondaryLayerBoneNames.remove(koikatsuCommons.riggedTongueRightBone3Name)
            koikatsuCommons.eyesSecondaryLayerBoneNames.remove(koikatsuCommons.riggedTongueLeftBone4Name)
            koikatsuCommons.eyesSecondaryLayerBoneNames.remove(koikatsuCommons.riggedTongueRightBone4Name)
            koikatsuCommons.eyesSecondaryLayerBoneNames.remove(koikatsuCommons.riggedTongueLeftBone5Name)
            koikatsuCommons.eyesSecondaryLayerBoneNames.remove(koikatsuCommons.riggedTongueRightBone5Name)
        except:
            pass
               
    if not hasBetterPenetrationMod:
        try:
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationRootCrotchBoneName)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationFrontCrotchBoneName)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationLeftCrotchBone1Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationRightCrotchBone1Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationLeftCrotchBone2Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationRightCrotchBone2Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationLeftCrotchBone3Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationRightCrotchBone3Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationLeftCrotchBone4Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationRightCrotchBone4Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationLeftCrotchBone5Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationRightCrotchBone5Name)
            koikatsuCommons.torsoTweakLayerBoneNames.remove(koikatsuCommons.betterPenetrationBackCrotchBoneName)
        except:
            pass
                
    ctrlBoneNames = []
    ctrlBoneNames.extend(koikatsuCommons.eyesPrimaryLayerBoneNames)
    ctrlBoneNames.extend(koikatsuCommons.eyesSecondaryLayerBoneNames)
    ctrlBoneNames.extend(koikatsuCommons.torsoLayerBoneNames)
    ctrlBoneNames.extend(koikatsuCommons.torsoTweakLayerBoneNames)
    ctrlBoneNames.extend(koikatsuCommons.leftArmIkLayerBoneNames)
    ctrlBoneNames.extend(koikatsuCommons.rightArmIkLayerBoneNames)
    ctrlBoneNames.extend(koikatsuCommons.fingersLayerBoneNames)
    ctrlBoneNames.extend(koikatsuCommons.leftLegIkLayerBoneNames)
    ctrlBoneNames.extend(koikatsuCommons.rightLegIkLayerBoneNames)
    
    for bone in metarig.data.bones:
        if bone.collections.get(str(koikatsuCommons.originalUpperFaceLayerIndex)) or bone.collections.get(str(koikatsuCommons.originalLowerFaceLayerIndex)):
            if bone.name == koikatsuCommons.originalRootUpperBoneName:
                continue
            if bone.name not in ctrlBoneNames:
                ctrlBoneNames.append(bone.name)
            koikatsuCommons.assignSingleBoneLayer(metarig, bone.name, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.faceLayerName))
            
    koikatsuCommons.assignSingleBoneLayerToList(metarig, koikatsuCommons.eyesPrimaryLayerBoneNames, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.eyesLayerName + koikatsuCommons.primaryLayerSuffix))
    koikatsuCommons.assignSingleBoneLayerToList(metarig, koikatsuCommons.eyesSecondaryLayerBoneNames, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.eyesLayerName + koikatsuCommons.secondaryLayerSuffix))
    koikatsuCommons.assignSingleBoneLayerToList(metarig, koikatsuCommons.torsoLayerBoneNames, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.torsoLayerName))
    koikatsuCommons.assignSingleBoneLayerToList(metarig, koikatsuCommons.torsoTweakLayerBoneNames, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.torsoLayerName + koikatsuCommons.tweakLayerSuffix))
    koikatsuCommons.assignSingleBoneLayerToList(metarig, koikatsuCommons.leftArmIkLayerBoneNames, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.leftArmLayerName + koikatsuCommons.ikLayerSuffix))
    koikatsuCommons.assignSingleBoneLayerToList(metarig, koikatsuCommons.rightArmIkLayerBoneNames, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.rightArmLayerName + koikatsuCommons.ikLayerSuffix))
    koikatsuCommons.assignSingleBoneLayerToList(metarig, koikatsuCommons.fingersLayerBoneNames, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.fingersLayerName))
    koikatsuCommons.assignSingleBoneLayerToList(metarig, koikatsuCommons.leftLegIkLayerBoneNames, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.leftLegLayerName + koikatsuCommons.ikLayerSuffix))
    koikatsuCommons.assignSingleBoneLayerToList(metarig, koikatsuCommons.rightLegIkLayerBoneNames, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.rightLegLayerName + koikatsuCommons.ikLayerSuffix))
    
    usefulBoneNames = [metarigIdBoneName, koikatsuCommons.eyesXBoneName, koikatsuCommons.eyesBoneName, koikatsuCommons.leftEyeBoneName, koikatsuCommons.rightEyeBoneName, koikatsuCommons.eyesTrackTargetParentBoneName, 
    koikatsuCommons.eyesHandleMarkerBoneName, koikatsuCommons.leftEyeHandleMarkerBoneName, koikatsuCommons.rightEyeHandleMarkerBoneName, koikatsuCommons.leftEyeHandleMarkerXBoneName, koikatsuCommons.rightEyeHandleMarkerXBoneName, 
    koikatsuCommons.leftEyeHandleMarkerZBoneName, koikatsuCommons.rightEyeHandleMarkerZBoneName, koikatsuCommons.eyeballsTrackBoneName, koikatsuCommons.leftEyeballTrackBoneName, koikatsuCommons.rightEyeballTrackBoneName, 
    koikatsuCommons.leftEyeballTrackCorrectionBoneName, koikatsuCommons.rightEyeballTrackCorrectionBoneName, koikatsuCommons.leftHeadMarkerXBoneName, koikatsuCommons.rightHeadMarkerXBoneName, koikatsuCommons.leftHeadMarkerZBoneName, 
    koikatsuCommons.rightHeadMarkerZBoneName, koikatsuCommons.headTrackBoneName, koikatsuCommons.headTrackTargetParentBoneName]
    usefulBoneNames.extend(ctrlBoneNames)
    
    defBoneNames = koikatsuCommons.getDeformBoneNames(metarig)
    
    for name in defBoneNames:
        if name not in usefulBoneNames:
            usefulBoneNames.append(name)
    
    if hasSkirt:
        for primaryIndex in range(8):
            skirtPalmBoneName = koikatsuCommons.getSkirtBoneName(True, primaryIndex)
            if skirtPalmBoneName not in ctrlBoneNames:
                ctrlBoneNames.append(skirtPalmBoneName)
            if skirtPalmBoneName not in usefulBoneNames:
                usefulBoneNames.append(skirtPalmBoneName)
            metarig.pose.bones[skirtPalmBoneName].custom_shape = None
            koikatsuCommons.assignSingleBoneLayer(metarig, skirtPalmBoneName, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.skirtLayerName))
            if primaryIndex == 2:
                metarig.pose.bones[skirtPalmBoneName].rigify_type = "limbs.super_palm"
                metarig.pose.bones[skirtPalmBoneName].rigify_parameters.palm_both_sides = True
                metarig.pose.bones[skirtPalmBoneName].rigify_parameters.palm_rotation_axis = 'X'
                metarig.pose.bones[skirtPalmBoneName].rigify_parameters.make_extra_control = True
            else:
                metarig.pose.bones[skirtPalmBoneName].rigify_type = ""
            for secondaryIndex in range(6):
                skirtBoneName = koikatsuCommons.getSkirtBoneName(False, primaryIndex, secondaryIndex)
                if skirtBoneName not in ctrlBoneNames:
                    ctrlBoneNames.append(skirtBoneName)
                if skirtBoneName not in usefulBoneNames:
                    usefulBoneNames.append(skirtBoneName)
                metarig.pose.bones[skirtBoneName].custom_shape = None
                koikatsuCommons.assignSingleBoneLayer(metarig, skirtBoneName, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.skirtLayerName))
                if secondaryIndex == 0:
                    metarig.pose.bones[skirtBoneName].rigify_type = "limbs.super_finger"
                    metarig.pose.bones[skirtBoneName].rigify_parameters.make_extra_ik_control = True
                    # metarig.pose.bones[skirtBoneName].rigify_parameters.tweak_layers[1] = False
                    # metarig.pose.bones[skirtBoneName].rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.skirtLayerName + koikatsuCommons.detailLayerSuffix)] = True
                else:
                    metarig.pose.bones[skirtBoneName].rigify_type = ""
                
    for boneName in accessoryBoneNames:
        if boneName not in usefulBoneNames:
            usefulBoneNames.append(boneName)
        if boneName == koikatsuCommons.originalRootUpperBoneName:
            continue
        if boneName not in ctrlBoneNames:
            ctrlBoneNames.append(boneName)
        bone = metarig.pose.bones[boneName]
        bone.custom_shape = None
        koikatsuCommons.assignSingleBoneLayer(metarig, boneName, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.hairLayerName))
        if boneName in accessoryBoneConnectedParentNames:
            bone.rigify_type = "limbs.super_finger"
            bone.rigify_parameters.make_extra_ik_control = True
            # bone.rigify_parameters.tweak_layers[1] = False
            # bone.rigify_parameters.tweak_layers[koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.hairLayerName + koikatsuCommons.detailLayerSuffix)] = True
        elif boneName in accessoryBoneConnectedChildNames:
            bone.rigify_type = ""
        else:
            bone.rigify_type = "basic.super_copy"
            bone.rigify_parameters.make_control = True
            bone.rigify_parameters.make_widget = True
            bone.rigify_parameters.super_copy_widget_type = "limb"  
            bone.rigify_parameters.make_deform = True
    
    accessoryMchPalmBoneNames = []
    for boneName in accessoryMchBoneNames:
        #metarig.data.bones[boneName].layers[koikatsuCommons.temporaryAccessoryMchLayerIndex] = True
        if boneName not in ctrlBoneNames:
            ctrlBoneNames.append(boneName)
        if boneName not in usefulBoneNames:
            usefulBoneNames.append(boneName)
        bone = metarig.pose.bones[boneName]
        bone.custom_shape = None        
        koikatsuCommons.assignSingleBoneLayer(metarig, boneName, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.hairLayerName + koikatsuCommons.mchLayerSuffix))
        if boneName in accessoryMchPalmBoneNames:
            continue
        if boneName in accessoryMchConnectedParentNames:
            accessoryMchPalmBones = []
            for connectedParentBoneName in accessoryMchConnectedParentNames:
                if boneName == connectedParentBoneName:
                    continue
                connectedParentBone = metarig.pose.bones[connectedParentBoneName]
                if bone.parent == connectedParentBone.parent:
                    accessoryMchPalmBoneNames.append(connectedParentBone.name)
                    accessoryMchPalmBones.append(connectedParentBone)
                    connectedParentBone.rigify_type = ""
            if accessoryMchPalmBones:
                accessoryMchPalmBoneNames.append(bone.name)
                accessoryMchPalmBones.append(bone)
                bone.rigify_type = ""
                maxHeadDistance = 0
                for palmBone1 in accessoryMchPalmBones:
                    for palmBone2 in accessoryMchPalmBones:
                        headDistance = (palmBone1.head - palmBone2.head).length
                        if headDistance > maxHeadDistance:
                            bone = palmBone1
                            maxHeadDistance = headDistance                    
                bone.rigify_type = "limbs.super_palm"
                bone.rigify_parameters.palm_both_sides = True
                bone.rigify_parameters.make_extra_control = True
                continue
            bone.rigify_parameters.optional_widget_type  = "limb"
        else:
            bone.rigify_parameters.optional_widget_type = "limb"
            
    for boneName in faceMchBoneNames:
        #metarig.data.bones[boneName].layers[koikatsuCommons.temporaryFaceMchLayerIndex] = True
        #metarig.data.bones[boneName].layers[koikatsuCommons.originalMchLayerIndex] = False
        if boneName not in ctrlBoneNames:
            ctrlBoneNames.append(boneName)
        if boneName not in usefulBoneNames:
            usefulBoneNames.append(boneName)
        bone = metarig.pose.bones[boneName]
        bone.custom_shape = None
        bone.rigify_parameters.optional_widget_type = "pivot"
        koikatsuCommons.assignSingleBoneLayer(metarig, boneName, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.faceLayerName + koikatsuCommons.mchLayerSuffix))
        
    for boneName in usefulBoneNames:
        if boneName in defBoneNames:
            if boneName in ctrlBoneNames:
                set_layer(boneName, koikatsuCommons.defLayerIndex)
            else:
                koikatsuCommons.assignSingleBoneLayer(metarig, boneName, koikatsuCommons.defLayerIndex)
                koikatsuCommons.lockAllPoseTransforms(metarig, boneName)
        else:
            if boneName not in ctrlBoneNames:
                koikatsuCommons.assignSingleBoneLayer(metarig, boneName, koikatsuCommons.mchLayerIndex)
                koikatsuCommons.lockAllPoseTransforms(metarig, boneName)                
        relatedBoneNames = koikatsuCommons.getRelatedBoneNames(metarig, boneName)
        for relatedBoneName in relatedBoneNames:
            if relatedBoneName not in usefulBoneNames:
                usefulBoneNames.append(relatedBoneName)       
    
    for bone in metarig.pose.bones:
        if bpy.app.version[0] >= 3:
            bone['mmd_bone'] = None
        if bone.name not in usefulBoneNames:
            koikatsuCommons.assignSingleBoneLayer(metarig, bone.name, koikatsuCommons.getRigifyLayerIndexByName(koikatsuCommons.junkLayerName))
            continue
        if bone.rigify_type == "basic.raw_copy" or bone.rigify_type == "basic.super_copy":
            for targetToChange in koikatsuCommons.targetsToChange:
                if bone.parent == targetToChange:
                    bone.rigify_parameters.relink_constraints = True
                    bone.rigify_parameters.parent_bone = koikatsuCommons.deformBonePrefix + targetToChange
            for constraint in bone.constraints:
                for targetToChange in koikatsuCommons.targetsToChange:
                    try:
                        if constraint.subtarget == targetToChange:
                            bone.rigify_parameters.relink_constraints = True
                            try:
                                index = constraint.name.index("@")
                                constraint.name = constraint.name[:index] + "@" + koikatsuCommons.deformBonePrefix + targetToChange
                            except ValueError as ex:
                                constraint.name = constraint.name + "@" + koikatsuCommons.deformBonePrefix + targetToChange
                    except AttributeError as ex:
                        pass
                    
    bpy.ops.object.mode_set(mode='EDIT')
    
    for bone in metarig.data.edit_bones:
        if bone.name in defBoneNames:
            bone.use_deform = True
        else:
            bone.use_deform = False
            if bone.name not in usefulBoneNames and bone.parent and bone.parent.name in usefulBoneNames:
                bone.use_connect = False #may otherwise cause Rigify generation failure if part of a finger chain
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    for i in range(32):
        index = 31 - i
        if index in selectedLayers:
            if metarig.data.collections.get(str(index)):
                metarig.data.collections[str(index)].is_visible = True
            else:
                metarig.data.collections.new(str(index))
                metarig.data.collections[str(index)].is_visible = True
        else:
            if metarig.data.collections.get(str(index)):
                metarig.data.collections[str(index)].is_visible = False
            else:
                metarig.data.collections.new(str(index))
                metarig.data.collections[str(index)].is_visible = False
    metarig.data.collections
            
    #bpy.ops.bone_layer_man.get_rigify_layers()
    #koikatsuCommons.setBoneManagerLayersFromRigifyLayers(metarig)

class rigify_before(bpy.types.Operator):
    bl_idname = "kkbp.rigbefore"
    bl_label = "Before First Rigify Generate - Public"
    bl_description = 'Converts the KKBP armature to a Rigify metarig'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main()
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(rigify_before)

    # test call
    print((bpy.ops.kkbp.rigbefore('INVOKE_DEFAULT')))