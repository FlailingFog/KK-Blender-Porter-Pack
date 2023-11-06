[return to wiki home](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md)

# Armature

## Armature layers
The KKBP armature hides some bone layers so the view is less cluttered. These bones can be found in each layer.  
![2 3 armature layers](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/e50612d9-3780-4bb8-ad7b-77fa915f61ac)

The armature layer panel can be found by selecting the armature and looking in the Data tab. You can shift click a layer box to show multiple layers at a time. Blank boxes don't have any bones in them.  
![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/c43fac02-8f88-416a-bcb4-5195d97b1ca8)

## Joint corrections
The KKBP and Rigify armatures make use of helper bones to make the mesh look better when it deforms. These helper bones can be found in layers 2 and 3 of the KKBP armature. Some joint corrections are implemented by giving the helper bones bone contraints and other corrections are implemented by giving the helper bones drivers to automatically set their location and rotation when a specific bone is rotated. An example of a joint correction bone is shown below. In the default position, the cf_s_elboback_L bone stays in place. When the arm is bent the location drivers for cf_s_elboback_L cause the bone to move out and deform the arm properly. The third image is an example of what the arm would look like without the location drivers enabled. A list of all helper bones can be found in the create_joint_drivers function of [modifyarmature.py](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/importing/modifyarmature.py)

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/f424f59e-7346-49d3-9244-db2949ff9faf)

## KKBP Armature

The KKBP armature features the following:
* Eye controller bone
* Hand and Leg IKs
* A heel IK
* A center bone that lets you move all bones at once

![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/81043824-b4fb-4bc0-83d1-3870f7ad3180)
![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/df53809f-ebf3-4c8e-8851-ae5cc40b5ce2)
![image](https://github.com/FlailingFog/KK-Blender-Porter-Pack/assets/65811931/6069cce8-d72d-4f40-8a6d-067d0400e1b8)

## Rigify Armature

The Rigify armature includes many different features:
* Eye controller bone
* Hand and Leg IKs
* A heel IK
* A center bone that lets you move all bones at once
* IK to FK sliders
* IK to FK transition helpers
* IK limb stretches
* Tweak bones for limb deformation
* Easy-to-use finger bones
* Finger IKs
* Palm bones
* Foot spin bone
* Eye look target
* Individual eye bones
* FK eye bones
* Tongue IK
* Head and Neck follow sliders
* Head look target

Check [this video series for understanding what the Rigify addon is and how it can be used](https://www.youtube.com/watch?v=-JSFcSxsaTs&list=PLdcL5aF8ZcJv68SSdwxip33M7snakl6Dx).

Check [this page for information specific to the KKBP Rigify armature](https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/78).

[return to wiki home](https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/master/wiki/Wiki%20top.md)
