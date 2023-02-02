#This will take a folder full of fbx animation files ripped from the game and create a blender animation library using the current model (for thumbnails)

#  Usage instructions:
#  Export koikatsu fbx animation files using https://www.youtube.com/watch?v=XFt12n7ByBI&t=465s
#      You can also export multiple animations at the same time by shift clicking them in the window 
#  put all the fbx files you exported into one folder
#  any subfolder names in that folder will be used to tag them

#  import a character with a rigify armature
#  make sure you've got a camera and light pointed at the model (put it at an angle for better thumbnails)
#  make sure you've disabled the armature visibility (in the 3d view settings on the top bar, not in the outliner)
#      Suggested X and Y axis lines: ON
#      Suggested sun location and rotation [-1 m, 0 m, 0 m] , [78°, -40°, 27°]
#      Suggested world color [0,0,0]
#      Suggested camera location + rotation [-0.7 m, -1.9 m, 0.8 m] , [83.6°, -0°, -20°]
#      Suggested camera resolution [150 x 150]
#      Suggested Tpose model location + rotation [0,0,0], [0°,0°,0°]
#  Use https://www.youtube.com/watch?v=Nyxeb48mUfs&t=713s to setup the Rokoko retargeting addon with a random koikatsu fbx animation file from your folder
#      (make sure torso, torso tweak, arm fk, fingers detail, leg fk Rigify layers are visible)
#      (make sure ALL rokoko remapping / naming schemes are already setup using the random file)
#      (Alternatively, you can import the included "Rokoko custom target naming" .json file included in the /extras/animationlibrary/ directory to set it automatically)
#      (it just needs to be done once, then you can hit the save button in the rokoko retargeting panel to use it in any other file)
#  delete the random fbx animation you imported (setup is complete at this point)
#  save the file

#  enter rendered view
#  Run the script by pressing the button in the panel
#  It will take about two hours on a good CPU to generate the library (three minutes per 11 poses, or 2 hours for ~440 poses / animations which adds up to about 1.2gb of fbx files)
#  You can also do it in small batches and rotate out the already imported fbx files for new ones (change your filename after each batch or the previous batches will be overwritten)
#  Or you can put a large list and kill blender when you want to pause the import process (it will automatically save a new file for every subfolder, and pick up from the previous subfolder)

#  when finished, open every asset file and run the script on the bottom of this file to reduce the filesize 
#      (You can also copy paste the script into a text editor before running the script so you can have it automatically loaded on every asset file that will be produced)
#  also recall that blender resets the fps to the framerate of the fbx file when importing

import bpy, os, time, mathutils
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

    #disable IKs
    rigify_armature.pose.bones["Right arm_parent"]["IK_FK"] = 1
    rigify_armature.pose.bones["Left arm_parent"]["IK_FK"] = 1
    rigify_armature.pose.bones["Right leg_parent"]["IK_FK"] = 1
    rigify_armature.pose.bones["Left leg_parent"]["IK_FK"] = 1

    #disable head follow
    rigify_armature.pose.bones['torso']['neck_follow'] = 1.0
    rigify_armature.pose.bones['torso']['head_follow'] = 1.0

    '''#reset all bone transforms
    for pb in bpy.context.selected_pose_bones_from_active_object:
        pb.matrix_basis = mathutils.Matrix() #  == Matrix.Identity(4)
    '''

    #import the fbx files
    fbx_files = []
    for subdir, dirs, files in os.walk(folder):
        for file in files:
            if '.fbx' in file:
                fbx_files.append((subdir, file, os.path.join(subdir, file)))

    actions_from_set = []
    last_category = ''
    original_file_name = bpy.data.filepath

    for file in fbx_files:
        original_file_number = file[0].replace(folder, '')[1:file[0].replace(folder, '')[1:].find('\\') + 1]
        category = file[0].replace(folder, '')[file[0].replace(folder, '')[1:].find('\\') + 2:]
        filename = file[1]

        #skip this file if the animation is for larger characters, or is a partial animation
        skip = False
        no_use = ['L_', 'M_', 'ML_', 'SM_', 'Te_', 'Yubi_', 'Sita_', 'Denma_', 'Vibe_']
        for item in no_use:
            if filename.startswith(item):
                skip = True
        if skip:
            continue

        #also skip if this a file for this category already exists
        if os.path.exists(bpy.data.filepath.replace('.blend', ' ' + category + '.blend')):
            continue

        #create a new file for every category because the asset browser seems to behave better with multiple small files vs one large file
        if last_category != category:
            #save, then create new file
            if last_category: #skip save for first file
                bpy.ops.wm.save_as_mainfile(filepath = bpy.data.filepath)
            bpy.ops.wm.save_as_mainfile(filepath = original_file_name.replace('.blend', ' ' + category + '.blend'))
            last_category = category

            #new file, so delete the previous imported asset animations 
            for act in actions_from_set:
                bpy.data.actions.remove(bpy.data.actions[act])
            actions_from_set = []

            #load a script into the layout tab
            if bpy.data.screens.get('Layout'):
                for area in bpy.data.screens['Layout'].areas:
                    if area.type == 'DOPESHEET_EDITOR':
                        area.ui_type = 'TEXT_EDITOR'
                        area.spaces[0].text = bpy.data.texts.new(name='Generate previews, save and close')
                        area.spaces[0].text.write(
'''#this script reduces the filesize of the library file to just the action data
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

''')

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
        my_areas = bpy.context.workspace.screens[0].areas
        for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.show_object_viewport_armature = True
        bpy.context.scene.rsl_retargeting_armature_source = imported_armature
        bpy.ops.rsl.build_bone_list()
        bpy.ops.rsl.retarget_animation()

        # then remove the fcurves of the retargeted bones that were not present in the retargeting list.
        # A lot of popping and fluctuation is present if these aren't removed
        retargeting_list = [
            'torso',
             'Spine_fk',
             'Chest_fk',
             'Upper Chest_fk',
             'Left arm_fk',
             'Left elbow_fk',
            'Left wrist_fk',
            'IndexFinger1_L',
            'IndexFinger2_L',
            'IndexFinger3_L',
             'LittleFinger1_L',
             'LittleFinger2_L',
             'LittleFinger3_L',
             'MiddleFinger1_L',
             'MiddleFinger2_L',
             'MiddleFinger3_L',
           'RingFinger1_L',
           'RingFinger2_L',
           'RingFinger3_L',
            'Thumb0_L',
            'Thumb1_L',
            'Thumb2_L',
             'Right arm_fk',
             'Right elbow_fk',
             'Right wrist_fk',
            'IndexFinger1_R',
            'IndexFinger2_R',
            'IndexFinger3_R',
            'LittleFinger1_R',
            'LittleFinger2_R',
            'LittleFinger3_R',
            'MiddleFinger1_R',
            'MiddleFinger2_R',
            'MiddleFinger3_R',
            'RingFinger1_R',
            'RingFinger2_R',
            'RingFinger3_R',
            'Thumb0_R',
            'Thumb1_R',
            'Thumb2_R',
            'neck',
            'head',
            'Hips_fk',
            'Left leg_fk',
            'Left knee_fk',
            'Left ankle_fk',
            'Left toe_fk',
             'Right leg_fk',
             'Right knee_fk',
             'Right ankle_fk',
             'Right toe_fk',
             'Left shoulder',
             'cf_j_waist02',
             'Right shoulder',
             'cf_j_kokan',
            #'cf_j_ana',
             'Breasts handle',
             'Left Breast handle',
             'cf_j_bust02_l',
             'cf_j_bust03_l',
             'cf_j_bnip02root_l',
             'cf_j_bnip02_l',
             'Right Breast handle',
             'cf_j_bust02_r',
             'cf_j_bust03_r',
             'cf_j_bnip02root_r',
              'cf_j_bnip02_r',
             #'Left Buttock handle',
             #'Right Buttock handle',
        ]
        for action in rigify_armature.animation_data.action.fcurves:
            bone_name = action.data_path[action.data_path.find('[')+2:action.data_path.find('].')-1]
            if bone_name not in retargeting_list:
                rigify_armature.animation_data.action.fcurves.remove(action) #remove keyframes
                rigify_armature.pose.bones[bone_name].matrix_basis = mathutils.Matrix()

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

            '_Idle': 'Idling',
            '_Stop_Idle': 'Idling stop',
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
        h_dict_used = False
        for item in translation_dict_h:
            if item in name:
                name = category + ' ' + name[1:] #add the description onto it because h animations don't have names, remove the S at the beginning of the name because all of them start with that
                name = name.replace(item, translation_dict_h[item])
                h_dict_used = True
        
        action = rigify_armature.animation_data.action
        action.asset_mark()
        #render the first frame of the animation and set it as the preview
        bpy.context.scene.render.filepath = folder + r"\preview.png"
        #print(file[2])
        my_areas = bpy.context.workspace.screens[0].areas
        for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.show_object_viewport_armature = False 
        bpy.ops.render.opengl(write_still = True)
        with bpy.context.temp_override(id=action):
            bpy.ops.ed.lib_id_load_custom_preview(filepath=folder + r"\preview.png")
        my_areas = bpy.context.workspace.screens[0].areas
        for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.show_object_viewport_armature = True 
        action.name = name
        #bpy.ops.poselib.create_pose_asset(activate_new_action=True, pose_name = name) #for pose assets instead
        action.asset_data.tags.new(filename)
        action.asset_data.tags.new(category)
        action.asset_data.tags.new(original_file_number)
        if h_dict_used:
            action.asset_data.tags.new('NSFW')
        action.asset_data.description = filename
        actions_from_set.append(action.name)

        #delete the imported action, object and armature
        bpy.data.actions.remove(bpy.data.actions[current_action_name])
        imported_armature_armaturename = imported_armature.data.name
        bpy.data.objects.remove(imported_armature)
        bpy.data.armatures.remove(bpy.data.armatures[imported_armature_armaturename])
        print(file[2])

    print(str(time.time() - start))
    bpy.ops.wm.save_as_mainfile(filepath = bpy.data.filepath.replace('.blend', ' ' + category + '.blend'))
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


"""
import bpy, json


file = r"ARP retargeting list (koikatsu fbx to KKBP Rigify).json"

rigify_armature = bpy.data.objects['RIG-Armature']

rigify_armature.pose.bones["Right arm_parent"]["IK_FK"] = 1
rigify_armature.pose.bones["Left arm_parent"]["IK_FK"] = 1
rigify_armature.pose.bones["Right leg_parent"]["IK_FK"] = 1
rigify_armature.pose.bones["Left leg_parent"]["IK_FK"] = 1

#disable head follow
rigify_armature.pose.bones['torso']['neck_follow'] = 1.0
rigify_armature.pose.bones['torso']['head_follow'] = 1.0
    
#bpy.context.object.pose.bones["Left leg_parent"]["pole_vector"] = 1
#bpy.context.object.pose.bones["Right leg_parent"]["pole_vector"] = 1
#bpy.context.object.pose.bones["Left arm_parent"]["pole_vector"] = 1
#bpy.context.object.pose.bones["Right arm_parent"]["pole_vector"] = 1
json_file = open(file)
data = json.load(json_file)
bpy.context.scene.bones_map_index = 1
for row in bpy.context.scene.bones_map:
    row.name = "None"

for bone in data['bones']:
    for row in bpy.context.scene.bones_map:
        if row.source_bone == data['bones'][bone][0]:
            row.name = data['bones'][bone][1]
        if row.name == 'torso':
            row.set_as_root = True
        #if '_ik' in row.name:
        #    row.ik = True
        #    if ' wrist' in row.name:
        #        row.ik_pole = (('Left' if 'Left' in row.name else 'Right') + " arm_ik_target")
        #    else:
        #        row.ik_pole = (('Left' if 'Left' in row.name else 'Right') + " leg_ik_target")"""