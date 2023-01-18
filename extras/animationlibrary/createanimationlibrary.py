#This will take a folder full of fbx animation files ripped from the game and create a blender animation library using the current model (for thumbnails)

#  Usage instructions:
#  Export koikatsu fbx animation files using https://www.youtube.com/watch?v=XFt12n7ByBI&t=465s
#      You can also export multiple animations at the same time by shift clicking them in the window 
#  put all the fbx files you exported into one folder
#  any subfolder names in that folder will be used to tag them

#  import a character with a rigify armature
#  make sure you've got a camera and light pointed at the model (put it at an angle for better thumbnails)
#      Suggested sun rotation [78.2739°, -40.516°, 27.3479°]
#      Suggested camera location + rotation [-0.695381 m, -1.90263 m, 0.813071 m], [83.6°, -0°, -20°]
#      Suggested camera resolution [100 x 100]
#      Suggested Tpose model location + rotation [0,0,0], [0,0,0]
#  Use https://www.youtube.com/watch?v=Nyxeb48mUfs&t=713s to setup the Rokoko retargeting addon with a random koikatsu fbx animation file from your folder
#      (make sure torso, torso tweak, arm fk, fingers detail, leg fk Rigify layers are visible)
#      (make sure all iks are toggled off in rigify settings for the four limbs)
#      (make sure ALL rokoko remapping / naming schemes are already setup using the random file)
#      (Alternatively, you can import the included "Rokoko custom target naming" .json file included in the /extras/animationlibrary/ directory to set it automatically)
#      (it just needs to be done once, then you can hit the save button in the rokoko retargeting panel to use it in any other file)
#  delete the random fbx animation you imported (setup is complete at this point)
#  save the file

#  Run the script by pressing the button in the panel
#  It will take about six hours on a good CPU to generate the library (six hours for ~700 poses / animations which is about 2gb of fbx files)
#  You can also do it in small batches and rotate out the already imported fbx files for new ones
#  Or you can put a large list and kill blender when you want to pause the import process (it will automatically save the file every 35 imports)

#  recall that blender resets the fps to the framerate of the fbx file when importing


import bpy, os, time
from bpy.props import StringProperty
def main(folder):
    start = time.time()
    rigify_armature = bpy.data.objects['RIG-Armature']
    bpy.ops.object.mode_set(mode = 'OBJECT')

    #import the fbx files
    fbx_files = []
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            if '.fbx' in file:
                fbx_files.append((subdir, file, os.path.join(subdir, file)))

    save_counter = 0
    save_file_counter = 0

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
            'isu_':'Seated_',
            'suwari':'Sitting',
            'syagami':'Squat',
            'sadou':'Tea',
            'undou':'Excercise',
            'suiei':'Swimming',
            'tachi':'Standing',
            'manken':'Reading',
            'soine':'Laying2',
            'kasa':'Umbrella',
            'konbou':'Club',
            'aruki':'Walking',
            'haruki':'Running',
            'ne_0':'Laying_0',
            'nugi':'Undressing',
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
        bpy.data.armatures.remove(imported_armature)

        #start from a new file every 35 imoprts because the asset seems to behave better with multiple small files vs one large file
        if save_counter == 35:
            save_counter = 0
            bpy.ops.wm.save_as_mainfile(filepath = bpy.data.filepath.replace('.blend', str(save_file_counter) + '.blend'))
        else:
            save_counter +=1

    print(str(time.time() - start))
    bpy.ops.wm.save_mainfile()


class anim_asset_lib(bpy.types.Operator):
    bl_idname = "kkb.createanimassetlib"
    bl_label = "Create animation asset library"
    bl_description = "Creates an animation library using the current file and current character. Open the folder containing the animation files exported with SB3Utility"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context):        
        main(self.directory)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
if __name__ == "__main__":
    bpy.utils.register_class(anim_asset_lib)
    
    # test call
    print((bpy.ops.kkb.importstudio('INVOKE_DEFAULT')))