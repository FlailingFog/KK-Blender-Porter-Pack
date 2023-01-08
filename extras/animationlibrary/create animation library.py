#This will take a folder full of fbx animation files ripped from the game and create a blender animation library using the current model (for thumbnails)

#  Usage instructions:
#  Export koikatsu fbx animation files using https://www.youtube.com/watch?v=XFt12n7ByBI&t=465s
#      but __don't__ export the mesh along with it. This can be avoided by closing the body 00 tab before exporting
#      You can also export multiple animations at the same time by shift clicking them in the window 
#  put all the fbx files you exported into one folder
#  any subfolder names in that folder will be used to tag them

#  import a character with a rigify armature
#  make sure you've got a camera and light pointed at the model
#  Use https://www.youtube.com/watch?v=Nyxeb48mUfs&t=713s to setup the Rokoko retargeting addon with a random koikatsu fbx animation file from your folder
#      (make sure torso, torso tweak, arm fk, fingers detail, leg fk Rigify layers are visible)
#      (make sure all iks are toggled off in rigify settings for the four limbs)
#      (make sure ALL rokoko remapping / naming schemes are already setup using the random file)
#      (Alternatively, you can import the included "Rokoko custom target naming" .json file included in the /extras/animationlibrary/ directory to set it automatically)
#      (it just needs to be done once, then you can hit the save button in the rokoko retargeting panel to use it in any other file)
#  delete the random fbx animation you imported (setup is complete at this point)

#  make sure the "folder" variable below is set properly:
folder = r"C:\Users\you\Desktop\my folder with all fbx exports"

#  Copy paste this script into the blender scripting tab and run it
#  It will take about six hours on a good CPU to generate the library (six hours for ~700 poses / animations which is about 2gb of fbx files)
#  You can also do it in small batches and rotate out the already imported fbx files for new ones
#  remember to save the library file when it's done
#  remember to purge orphan data when it's done




import bpy, mathutils, os, time
if __name__ == "__main__":
    start = time.time()
    rigify_armature = bpy.data.objects['RIG-Armature']
    bpy.ops.object.mode_set(mode = 'OBJECT')

    #import the fbx files
    fbx_files = []
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            if '.fbx' in file:
                fbx_files.append((subdir, file, os.path.join(subdir, file)))

    for file in fbx_files:
        category = file[0].replace(folder, '')[1:]
        filename = file[1]
        bpy.ops.import_scene.fbx(filepath=str(file[2]), global_scale=96)

        imported_armature = bpy.context.object
        '''bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        for bone in imported_armature.data.edit_bones:
            if (
                'k_f_' in bone.name
                or ('cf_hit_' in bone.name)
                or ('a_n_' in bone.name)
            ):
                bone.select_head, bone.select_tail, bone.select = True, True, True
        bpy.ops.object.mode_set(mode = 'OBJECT')'''

        #rokoko remap list still shows deleted bones for some fucking reason
        #clear all animation data from source armature, then re-key all bones for just this frame
        #duplicate source armature then delete the original source armature
        #rokoko list now shows correct bone list on source armature.002

        #setup rokoko remapping
        bpy.context.scene.rsl_retargeting_armature_source = imported_armature
        bpy.ops.rsl.build_bone_list()
        bpy.ops.rsl.retarget_animation()

        #select all rigify armature bones and create pose asset
        bpy.ops.object.select_all(action='DESELECT')
        rigify_armature.select_set(True)
        bpy.context.view_layer.objects.active=rigify_armature
        bpy.ops.object.mode_set(mode = 'POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.data.workspaces["Layout"].asset_library_ref = 'LOCAL'
        #translate name
        name = filename.replace('-p_cf_body_bone-0.fbx', '')
        translation_dict = {
            'isu_':'Chair_',
            'suwari':'Sit',
            'syagami':'Squat',
            'sadou':'Tea',
            'undou':'Excercise',
            'suiei':'Swim',
            'tachi':'Stand',
            'manken':'Read',
            'soine':'Lie (2)',
            'kasa':'Umbrella',
            'konbou':'Club',
            'aruki':'Walk',
            'haruki':'Run',
            'ne_0':'Lie_0',
            'nugi':'Undress',
        }
        for item in translation_dict:
            name = name.replace(item, translation_dict[item])
        action = rigify_armature.animation_data.action
        action.asset_mark()
        #render the first frame of the animation and set it as the preview
        bpy.context.scene.render.filepath = folder + r"\preview.png"
        print(file[2])
        bpy.ops.render.render(write_still = True)
        with bpy.context.temp_override(id=action):
            bpy.ops.ed.lib_id_load_custom_preview(
                filepath=folder + r"\preview.png"
            )
        action.name = name
        #bpy.ops.poselib.create_pose_asset(activate_new_action=True, pose_name = name) #for pose assets instead
        action.asset_data.tags.new(filename)
        action.asset_data.tags.new(category)
        #action.asset_data.tags.new('NSFW')
        action.asset_data.description = filename

        #delete the imported armature 
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.object.select_all(action ='DESELECT')
        imported_armature.select_set(True)
        bpy.context.view_layer.objects.active=imported_armature
        bpy.ops.object.delete(use_global=False, confirm=False)

        #save the file for crashes or pausing the imports
        #bpy.ops.wm.save_mainfile()

    print(str(time.time() - start))