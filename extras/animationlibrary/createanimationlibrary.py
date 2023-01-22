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
#      Suggested camera resolution [150 x 150]
#      Suggested Tpose model location + rotation [0,0,0], [0°,0°,0°]
#  Use https://www.youtube.com/watch?v=Nyxeb48mUfs&t=713s to setup the Rokoko retargeting addon with a random koikatsu fbx animation file from your folder
#      (make sure torso, torso tweak, arm fk, fingers detail, leg fk Rigify layers are visible)
#      (make sure all iks are toggled off in rigify settings for the four limbs)
#      (make sure ALL rokoko remapping / naming schemes are already setup using the random file)
#      (Alternatively, you can import the included "Rokoko custom target naming" .json file included in the /extras/animationlibrary/ directory to set it automatically)
#      (it just needs to be done once, then you can hit the save button in the rokoko retargeting panel to use it in any other file)
#  delete the random fbx animation you imported (setup is complete at this point)
#  save the file

#  Run the script by pressing the button in the panel
#  It will take about twelve hours on a good CPU to generate the library (one hour per 35 poses, or twelve hours for ~700 poses / animations which adds up to about 2gb of fbx files)
#  You can also do it in small batches and rotate out the already imported fbx files for new ones
#  Or you can put a large list and kill blender when you want to pause the import process (it will automatically save the file every hour / every 35 imports)
#  It does NOT pick up where it left off, so remove any animations that were already imported when you restart the import process

#  also recall that blender resets the fps to the framerate of the fbx file when importing


import bpy, os, time
from bpy.props import StringProperty
from...importing.importbuttons import kklog, toggle_console
def main(folder):
    #delete the armature before starting to reduce console spam
    if bpy.data.objects.get('Armature'):
        n = bpy.data.objects['Armature'].data.name
        bpy.data.objects.remove(bpy.data.objects['Armature'])
        bpy.data.armatures.remove(bpy.data.armatures[n])
    toggle_console() #open console for some kind of progression
    start = time.time()
    rigify_armature = bpy.data.objects['RIG-Armature']
    bpy.context.view_layer.objects.active=rigify_armature
    bpy.ops.object.mode_set(mode = 'OBJECT')

    #import the fbx files
    fbx_files = []
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            if '.fbx' in file:
                fbx_files.append((subdir, file, os.path.join(subdir, file)))

    save_counter = 0
    save_file_counter = 0
    actions_from_set = []

    for file in fbx_files:
        category = file[0].replace(folder, '')[1:]
        filename = file[1]

        #skip this file if the animation is for larger characters, or is a partial animation
        skip = False
        no_use = ['L_', 'M_', 'ML_', 'SM_', 'Te_', 'Yubi_', 'Sita_', 'Denma_', 'Vibe_']
        for item in no_use:
            if filename.startswith(item):
                skip = True
        if skip:
            continue

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

        #save the source action name so I can delete it later
        current_action_name = imported_armature.animation_data.action.name

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
        translation_dict_normal = {
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
        translation_dict_h = {
            '_A_idle':'Crotch grope idle',
            '_A_Loop':'Crotch grope',
            '_A_Touch':'Crotch grope start',
            '_K_Loop':'Kiss',
            '_K_Touch':'Kiss start',
            '_M_idle':'Breast grope idle',
            '_M_Loop':'Breast grope',
            '_M_Touch':'Breast grope start',
            '_Orgasm_A':'Climax end',
            '_Orgasm_Loop':'Climax',
            '_Orgasm_Start':'Climax start',
            '_S_idle':'Butt grope idle',
            '_S_Loop':'Butt grope',
            '_S_Touch':'Butt grope start',

            '_OLoop':'Idling',
            '_OUT_Start':'Climax outside start',
            '_OUT_Loop':'Climax outside',
            '_OUT_A':'Climax outside end',
            '_SLoop':'Fast loop',
            '_WLoop':'Slow loop',
            '_Oral_Idle': 'Cum in mouth',
            '_Oral_idle_IN': 'Cum in mouth start',
            '_Drink_IN':'Swallow cum start',
            '_Drink':'Swallow cum',
            '_Drink_A':'Swallow cum end',
            '_Vomit_IN': 'Spit out cum start',
            '_Vomit': 'Spit out cum',
            '_Vomit_A': 'Spit out cum end',
        }

        for item in translation_dict_normal:
            name = name.replace(item, translation_dict_normal[item])
        for item in translation_dict_h:
            if item in name:
                name = category + ' ' + name[1:] #add the description onto it because h animations don't have names, remove the S at the beginning of the name
                name = name.replace(item, translation_dict_h[item])
        
        action = rigify_armature.animation_data.action
        action.asset_mark()
        #render the first frame of the animation and set it as the preview
        bpy.context.scene.render.filepath = folder + r"\preview.png"
        print(file[2])
        bpy.ops.render.render(write_still = True)
        with bpy.context.temp_override(id=action):
            bpy.ops.ed.lib_id_load_custom_preview(filepath=folder + r"\preview.png")
        action.name = name
        print(file[2]) #print the filename again so it gets through console spam
        #bpy.ops.poselib.create_pose_asset(activate_new_action=True, pose_name = name) #for pose assets instead
        action.asset_data.tags.new(filename)
        action.asset_data.tags.new(category)
        #action.asset_data.tags.new('NSFW')
        action.asset_data.description = filename
        actions_from_set.append(action.name)

        #delete the imported action, object and armature
        bpy.data.actions.remove(bpy.data.actions[current_action_name])
        imported_armature_armaturename = imported_armature.data.name
        bpy.data.objects.remove(imported_armature)
        bpy.data.armatures.remove(bpy.data.armatures[imported_armature_armaturename])
        print(file[2]) #print the filename AGAIN so it gets through console spam
        
        #start from a new file every 35 imoprts because the asset seems to behave better with multiple small files vs one large file
        if save_counter == 34:
            save_counter = 0
            this_one = bpy.data.filepath.replace('.blend', str(0) + '.blend') if save_file_counter == 0  else bpy.data.filepath.replace(str(save_file_counter-1) + '.blend', str(save_file_counter) + '.blend')
            bpy.ops.wm.save_as_mainfile(filepath = this_one)
            save_file_counter+=1
            #After the file is saved, delete the previous 35 imported asset animations 
            for act in actions_from_set:
                bpy.data.actions.remove(bpy.data.actions[act])
            actions_from_set = []
        else:
            save_counter +=1

    print(str(time.time() - start))
    that_one = bpy.data.filepath.replace('.blend', str(0) + '.blend') if save_file_counter == 0  else bpy.data.filepath.replace(str(save_file_counter-1) + '.blend', str(save_file_counter) + '.blend')
    bpy.ops.wm.save_as_mainfile(filepath = that_one)
    toggle_console() #close console


class anim_asset_lib(bpy.types.Operator):
    bl_idname = "kkb.createanimassetlib"
    bl_label = "Create animation asset library"
    bl_description = "Creates an animation library using the current file and current character. Will not save over the current file in case you want to reuse it. Open the folder containing the animation files exported with SB3Utility"
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


'''

#this script reduces the filesize of the library file to just the action data
import bpy, time
for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)
for arm in bpy.data.armatures:
    bpy.data.armatures.remove(arm)
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh)
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat)
for img in bpy.data.images:
    bpy.data.images.remove(img)
for node in bpy.data.node_groups:
    bpy.data.node_groups.remove(node)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
time.sleep(3)
bpy.ops.wm.quit_blender()


'''