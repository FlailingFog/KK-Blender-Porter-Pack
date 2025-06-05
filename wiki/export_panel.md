## Exporter Panel settings
Each setting in the exporter panel will be briefly detailed on this page.  

![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/exportpanel.png)

### Freeze current pose

The pose is usually reset to a T pose during export. Enable this option to not reset to a T pose, and to keep the pose you have selected in the character maker. Because a pose is pre-applied to the armature, the armature will not work correctly in blender. This setting may be useful for 3D prints of koikatsu models or for stills. This exporter setting will force the Koikatsu armature in blender. See the picture below for an example of a pose being applied to the model. 

![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/exporter4.png)

### Export without physics

Some outfits rely on in-game physics to look correct. Enable this option to disable the in-game physics during export. This may make certain outfits look weird because of the lack of physics, but it is useful if you want to apply your own physics to the model in blender.

![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/exporter2.1.png)

### Freeze shapekeys

Shapekeys are reverted to their default values during export. Enable this option to freeze any shapekeys you have enabled in the character maker to the base mesh. Because the mesh is pre-deformed, other shapekeys will not work correctly in blender. Tear and gag eye shapekeys will also not work in blender. See the picture below for an example of some shapekeys being pre-applied to the base mesh. 

![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/exporter3.png)

### Export variations

This will export any available clothing variations. Not all clothes have variations.  
When imported, the variations will be hidden in the outliner by default.

![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/exporter1.png)

### Export all outfits

This will make the exporter export all of the card's outfits instead of just the currently selected one. This will dramatically increase koikatsu export times and blender import times.

### Export hit meshes

This will export the hit mesh. An example of the hit mesh is shown below.

![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/exporter2.png)

### Enable pushups

Outfit pushups (shown below) are disabled during export. Enable this option to keep them on.

![ ](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/images/exporter2.2.png)

## Preparation for Target Applications

The "Prep for target application" dropdown in the main plugin panel (Import/Export tab) allows you to apply specific modifications tailored for different game engines or software.

### Preparing for Unreal Engine

When you select **Unreal Engine** from the "Prep for target application" dropdown, the plugin performs several operations to optimize your model for import into Unreal Engine:

*   **Bone Renaming:** Bones are automatically renamed to match the standard Unreal Engine mannequin skeleton (e.g., 'Hips' becomes 'pelvis', 'Left arm' becomes 'upperarm_l'). This greatly helps with animation retargeting inside Unreal Engine.
*   **Root Bone Creation:** A new 'root' bone is created at the world origin (0,0,0), and the 'pelvis' bone is parented to it. This is a common best practice for Unreal Engine skeletons.
*   **IK Adjustments:** Specific adjustments are made to leg and foot bone orientations to improve compatibility with Unreal Engine's IK systems. Inverse Kinematics (IK) constraints from Blender are cleared as they don't directly transfer.

Additionally, you have the following options when "Unreal Engine" is selected:

*   **Apply UE Scale (100x):**
    *   Default: On
    *   This option automatically scales your entire model (armature and meshes) by a factor of 100. This is crucial because Blender uses meters as its default unit, while Unreal Engine uses centimeters. Enabling this ensures your model imports at the correct size in Unreal.
*   **Triangulate Mesh for UE:**
    *   Default: Off
    *   If enabled, this option will convert all mesh geometry (quads and n-gons) into triangles before export. While Unreal Engine can triangulate meshes on import, doing it in Blender first can give you more control over the final triangulation and help avoid potential issues.
