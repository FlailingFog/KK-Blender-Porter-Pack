import bpy, os, time, mathutils, json, pathlib
from .. import common as c
from ..interface.dictionary_en import t
def main(file):

    kkbp_character = False
    #delete the armature before starting to reduce console spam
    if bpy.data.objects.get('Body') and bpy.data.objects.get('RIG-Armature'):
        if bpy.data.objects['Body'].get('SMR materials'):
            kkbp_character = True
    c.toggle_console() #open console for some kind of progression
    start = time.time()
    rigify_armature = bpy.data.objects['RIG-Armature']
    bpy.context.view_layer.objects.active=rigify_armature
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.rsl.clear_custom_bones()

    if kkbp_character:
        #disable IKs
        rigify_armature.pose.bones["Right arm_parent"]["IK_FK"] = 1
        rigify_armature.pose.bones["Left arm_parent"]["IK_FK"] = 1
        rigify_armature.pose.bones["Right leg_parent"]["IK_FK"] = 1
        rigify_armature.pose.bones["Left leg_parent"]["IK_FK"] = 1

        #disable head follow
        rigify_armature.pose.bones['torso']['neck_follow'] = 1.0
        rigify_armature.pose.bones['torso']['head_follow'] = 1.0

    bpy.ops.import_scene.fbx(filepath=str(file), global_scale=96)

    imported_armature = bpy.context.object

    #save the source action name so I can delete it later
    current_action_name = imported_armature.animation_data.action.name

    #setup rokoko remapping
    my_areas = bpy.context.workspace.screens[0].areas
    for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.show_object_viewport_armature = True
    bpy.context.scene.rsl_retargeting_armature_source = imported_armature
    bpy.context.scene.rsl_retargeting_armature_target = rigify_armature
    bpy.ops.rsl.build_bone_list()
    #setup all remapping stuff if this is the first imported animation
    script_dir=pathlib.Path(__file__).parent
    if bpy.context.scene.kkbp.animation_import_type:
        remap_file = (script_dir / "animationlibrary" / "Rokoko retargeting list (mixamo to KKBP Rigify).json").resolve()
    else:
        remap_file = (script_dir / "animationlibrary" / "ARP retargeting list (koikatsu fbx to KKBP Rigify).json").resolve()

    if kkbp_character:
        script_dir=pathlib.Path(__file__).parent
        jfile = remap_file
        json_file = open(jfile)
        data = json.load(json_file)
        for row in bpy.context.scene.rsl_retargeting_bone_list:
            row.bone_name_target = "" #clear all bones
        for bone in data['bones']:
            for row in bpy.context.scene.rsl_retargeting_bone_list:
                if row.bone_name_source == data['bones'][bone][0]:
                    row.bone_name_target = data['bones'][bone][1]
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
    if kkbp_character:
        for index, action in enumerate(rigify_armature.animation_data.action.fcurves):
            bone_name = action.data_path[action.data_path.find('[')+2:action.data_path.find('].')-1]
            print('{}  {} / {}'.format(action.data_path, index, len(rigify_armature.animation_data.action.fcurves)))
            if bone_name not in retargeting_list:
                rigify_armature.animation_data.action.fcurves.remove(action) #remove keyframes
                if rigify_armature.pose.bones.get(bone_name):
                    rigify_armature.pose.bones[bone_name].matrix_basis = mathutils.Matrix() #reset rotation matrix

        
    if bpy.context.scene.kkbp.animation_library_scale:
        #also scale the arms on the y axis by 5% because it makes the animation more accurate to the in-game one for some poses
        already_got_both_arms = False
        if kkbp_character:
            for y_scale_curve in [curve for curve in rigify_armature.animation_data.action.fcurves if (curve.array_index == 1) and ('scale' in curve.data_path)]:
                bone_name = y_scale_curve.data_path[y_scale_curve.data_path.find('[')+2:y_scale_curve.data_path.find('].')-1]
                if bone_name in ['Left arm_fk', 'Right arm_fk']:
                    keyframe_limits = [int(y_scale_curve.keyframe_points[0].co.x), int(y_scale_curve.keyframe_points[-1].co.x)]
                    for frame_number in range(keyframe_limits[0], keyframe_limits[1]+1):
                        original_scale = y_scale_curve.evaluate(frame_number)
                        y_scale_curve.keyframe_points.insert(frame_number, original_scale * 1.05)
                    if already_got_both_arms:
                        break #skip the rest
                    already_got_both_arms = True

    #select all rigify armature bones and create pose asset
    bpy.ops.object.select_all(action='DESELECT')
    rigify_armature.select_set(True)
    bpy.context.view_layer.objects.active=rigify_armature
    bpy.ops.object.mode_set(mode = 'POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.data.workspaces["Layout"].asset_library_reference = 'LOCAL'
    #translate name
    name = file.replace('-p_cf_body_bone-0.fbx', '')
    name = name.replace('-p_cf_body_bone-1.fbx', '')
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
        'ne_0':'Sleep',
        'nugi':'Undressing',
    }
    translation_dict_h = {
        '_A_Idle':'Crotch grope idle',
        '_A_Loop':'Crotch grope',
        '_A_Touch':'Crotch grope start',
        '_K_Loop':'Kiss',
        '_K_Touch':'Kiss start',
        '_M_Idle':'Breast grope idle',
        '_M_Loop':'Breast grope',
        '_M_Touch':'Breast grope start',
        '_MLoop1': 'Masturbate',
        '_MLoop2': 'Masturbate2',
        '_Orgasm-': 'Climax-',
        '_Orgasm_A':'Climax end',
        '_Orgasm_B':'Climax end',
        '_Orgasm_Loop':'Climax',
        '_Orgasm_Start':'Climax start',
        '_S_Idle':'Butt grope idle',
        '_S_Loop':'Butt grope',
        '_S_Touch':'Butt grope start',
        '_Back_Dislikes':'Embarrassed back',
        '_Front_Dislikes':'Embarrassed front',

        '_Oral_Idle_IN': 'Cum in mouth start',
        '_Oral_Idle': 'Cum in mouth',
        '_Stop_Idle':  'Idling stop',
        '_InsertIdle': 'Insert idle',
        '_Idle-':  'Idling-',
        '_Insert-': 'Insert-',
        '_M_IN_Start':'Climax inside start',
        '_SF_IN_Start':'Climax inside start',
        '_A_SS_IN_Start':'Climax inside start',
        '_SS_IN_Start':'Climax inside start',
        '_A_WF_IN_Start':'Climax inside start',
        '_A_WS_IN_Start':'Climax inside start',
        '_WF_IN_Start':'Climax inside start',
        '_A_M_IN_Start':'Climax inside start',
        '_WS_IN_Start':'Climax inside start',
        '_IN_Start':'Climax inside start',
        '_M_IN_Loop':'Climax inside',
        '_SF_IN_Loop':'Climax inside',
        '_SS_IN_Loop':'Climax inside',
        '_WF_IN_Loop':'Climax inside',
        '_WS_IN_Loop':'Climax inside',
        '_IN_Loop':'Climax inside',
        '_A_IN_A':'Climax inside end',
        '_SS_IN_A':'Climax inside end',
        '_A_WS_IN_A':'Climax inside end',
        '_WS_IN_A':'Climax inside end',
        '_IN_A':'Climax inside end',
        '_Pull':'Pull out',
        '_OUT_Start':'Climax outside start',
        '_M_OUT_Loop':'Climax outside',
        '_OUT_Loop':'Climax outside',
        '_OUT_A':'Climax outside end',
        '_OLoop': 'Loop',
        '_SLoop':'Fast loop',
        '_WLoop':'Slow loop',
        '_Drink_IN':'Swallow cum start',
        '_Drink_A':'Swallow cum end',
        '_Drink':'Swallow cum',
        '_Vomit_IN': 'Spit out cum start',
        '_Vomit_A': 'Spit out cum end',
        '_Vomit': 'Spit out cum',
    }

    for item in translation_dict_normal:
        name = name.replace(item, translation_dict_normal[item])
    h_dict_used = False
    for item in translation_dict_h:
        if item in name:
            name = name[1:] #add the description onto it because h animations don't have names, remove the S at the beginning of the name because all of them start with that
            name = name.replace(item, translation_dict_h[item])
            h_dict_used = True
            break
    
    action = rigify_armature.animation_data.action
    rigify_armature.asset_mark()
    action.asset_mark()
    action.use_fake_user = True
    my_areas = bpy.context.workspace.screens[0].areas
    for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.show_object_viewport_armature = False 
    my_areas = bpy.context.workspace.screens[0].areas
    for area in my_areas:
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.show_object_viewport_armature = True 
    action.name = os.path.basename(str(name))
    action.asset_data.tags.new(file)
    if h_dict_used:
        action.asset_data.tags.new('NSFW')
    action.asset_data.description = file

    #delete the imported action, object and armature
    bpy.data.actions.remove(bpy.data.actions[current_action_name])
    imported_armature_armaturename = imported_armature.data.name
    bpy.data.objects.remove(imported_armature)
    try:
        bpy.data.objects.remove(bpy.data.objects['Beta_Joints'])
        bpy.data.objects.remove(bpy.data.objects['Beta_Surface'])
    except:
        #oh well
        pass
    bpy.data.armatures.remove(bpy.data.armatures[imported_armature_armaturename])
    print(file)

    print(str(time.time() - start))
    c.toggle_console() #close console

class anim_import(bpy.types.Operator):
    bl_idname = "kkbp.importanimation"
    bl_label = "Import .fbx animation file"
    bl_description = t('single_animation_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    filepath : bpy.props.StringProperty(maxlen=1024, default='', options={'HIDDEN'})
    filter_glob : bpy.props.StringProperty(default='*.fbx', options={'HIDDEN'})
    
    def execute(self, context):        
        main(self.filepath)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

