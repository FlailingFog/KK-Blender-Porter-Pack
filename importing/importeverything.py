'''
IMPORT TEXTURES SCRIPT
- Loads the material templates from the KK shader .blend
- Loads in the textures received from the KKBP Exporter
Usage:
- Click the button and choose the folder that contains the textures

Texture Postfix Legend:

    _MT_CT -> _MainTex_ColorTexture
    _MT -> _MainTex
    _AM -> _AlphaMask
    _CM -> _ColorMask
    _DM -> _DetailMask
    _LM -> _LineMask
    _NM -> _NormalMask
    _NMP -> _NormalMap
    _NMPD -> _NormalMapDetail
    _ot1 -> _overtex1
    _ot2 -> _overtex2
    _ot3 -> _overtex3
    _lqdm -> _liquidmask
    _HGLS -> _HairGloss
    _T2 -> _Texture2
    _T3 -> _Texture3
    _T4 -> _Texture4
    _T5 -> _Texture5
    _T6 -> _Texture6
    _T7 -> _Texture7
    _PM1 -> _PatternMask1
    _PM1 -> _PatternMask2
    _PM1 -> _PatternMask3
        
'''

import bpy, os, traceback, json, time
from pathlib import Path
from bpy.props import StringProperty
from .importbuttons import kklog
from .cleanarmature import get_bone_list

#Stop if this is the wrong folder
def wrong_folder_error(self, context):
    self.layout.label(text="The PMX folder was not selected. (Hint: go into the .pmx folder before confirming)")

#Stop if no face mc or body mc files were found
def missing_texture_error(self, context):
    self.layout.label(text="The files cf_m_body_CM.png and cf_m_face_00_CM.png were not found in the folder.\nMake sure to open the exported folder. \nHit undo and try again")

def get_templates_and_apply(directory, use_fake_user):
    #if a single thing was separated but the user forgot to rename it, it's probably the hair object
    #if bpy.data.objects.get('Clothes.001') and len(bpy.data.objects) == 6:
    #    bpy.data.objects['Clothes.001'].name = 'Hair'
    
    #Clean material list
    bpy.ops.object.mode_set(mode='OBJECT')
    armature = bpy.data.objects['Armature']    
    armature.hide = False
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.view_layer.objects:
        if ob.type == 'MESH':
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
    
    armature.hide = True
    bpy.ops.object.material_slot_remove_unused()
    
    #import all material templates
    fileList = Path(directory).glob('*.*')
    files = [file for file in fileList if file.is_file()]
    
    pmx_file_missing = True
    for file in files:
        if '.pmx' in str(file):
            pmx_file_missing = False
    if pmx_file_missing:
        bpy.context.window_manager.popup_menu(wrong_folder_error, title="Error", icon='ERROR')
        return True

    blend_file_missing = True
    for file in files:
        if '.blend' in str(file) and '.blend1' not in str(file) and 'KK Shader' in str(file):
            filepath = str(file)
            blend_file_missing = False
    
    if blend_file_missing:
        #grab it from the plugin directory
        script_dir=Path(__file__).parent
        template_path=(script_dir / '../KK Shader V6.0.blend').resolve()
        filepath = str(template_path)
    
    innerpath = 'Material'
    templateList = [
        'KK Body',
        'KK Outline',
        'KK Body Outline',
        'KK Tears',
        'KK Eye (hitomi)',
        'KK Eyebrows (mayuge)',
        'KK Eyeline down',
        'KK Eyeline Kage',
        'KK Eyeline up',
        'KK Eyewhites (sirome)',
        'KK Face',
        'KK General',
        'KK Hair',
        'KK Mixed Metal or Shiny',
        'KK Nose',
        'KK Shadowcast',
        'KK Teeth (tooth)',
        'KK Fangs (tooth.001)'
    ]

    for template in templateList:
        bpy.ops.wm.append(
            filepath=os.path.join(filepath, innerpath, template),
            directory=os.path.join(filepath, innerpath),
            filename=template,
            set_fake=use_fake_user
            )
    
    #Replace all materials on the body with templates
    body = bpy.data.objects['Body']
    def swap_body_material(original, template):
        try:
            body.material_slots[original].material = bpy.data.materials[template]
        except:
            kklog('material or template wasn\'t found: ' + original + ' / ' + template, 'warn')
    
    swap_body_material('cf_m_face_00','KK Face')
    swap_body_material('cf_m_mayuge_00','KK Eyebrows (mayuge)')
    swap_body_material('cf_m_noseline_00','KK Nose')
    swap_body_material('cf_m_eyeline_00_up','KK Eyeline up')
    swap_body_material('cf_m_eyeline_down','KK Eyeline down')
    swap_body_material('cf_m_eyeline_kage','KK Eyeline Kage')
    swap_body_material('cf_m_sirome_00','KK Eyewhites (sirome)')
    swap_body_material('cf_m_sirome_00.001','KK Eyewhites (sirome)')
    swap_body_material('cf_m_hitomi_00','KK Eye (hitomi)')
    swap_body_material('cf_m_hitomi_00.001','KK Eye (hitomi)')
    swap_body_material('cf_m_body','KK Body') #female
    swap_body_material('cm_m_body','KK Body') #male
    swap_body_material('cf_m_tooth','KK Teeth (tooth)')
    swap_body_material('cf_m_tooth.001','KK Fangs (tooth.001)')
    swap_body_material('cf_m_tang','KK General')
    
    #Make the tongue material unique so parts of the General Template aren't overwritten
    tongue_template = bpy.data.materials['KK General'].copy()
    tongue_template.name = 'KK Tongue'
    body.material_slots['KK General'].material = tongue_template
    
    #Make the texture group unique
    newNode = tongue_template.node_tree.nodes['Gentex'].node_tree.copy()
    tongue_template.node_tree.nodes['Gentex'].node_tree = newNode
    newNode.name = 'Tongue Textures'
    
    #Make the shader group unique
    newNode = tongue_template.node_tree.nodes['KKShader'].node_tree.copy()
    tongue_template.node_tree.nodes['KKShader'].node_tree = newNode
    newNode.name = 'Tongue Shader'
    
    #Make sure the hair object's name is correctly capitalized
    try:
        bpy.data.objects['hair'].name = 'Hair'
    except:
        try:
            bpy.data.objects['HAIR'].name = 'Hair'
        except:
            #The hair object's name was already correctly capitalized
            pass
    
    #Replace all of the Hair materials with hair templates and name accordingly
    hair_objects = [obj for obj in bpy.data.objects if 'Hair Outfit ' in obj.name]
    for hair in hair_objects:
        for original_material in hair.material_slots:
            template = bpy.data.materials['KK Hair'].copy()
            template.name = 'KK ' + original_material.name
            original_material.material = bpy.data.materials[template.name]
    
    outfit_objects = [obj for obj in bpy.data.objects if 'Outfit ' in obj.name and 'Hair Outfit ' not in obj.name and obj.type == 'MESH']
    #Replace all other materials with the general template and name accordingly
    for ob in outfit_objects:
        for original_material in ob.material_slots:
            template = bpy.data.materials['KK General'].copy()
            template.name = 'KK ' + original_material.name
            original_material.material = bpy.data.materials[template.name]
    
    #give the shadowcast object a template as well
    if bpy.data.objects.get('Shadowcast'):
        shadowcast = bpy.data.objects['Shadowcast']
        template = bpy.data.materials['KK Shadowcast']
        shadowcast.material_slots[0].material = bpy.data.materials[template.name]

    #give the tears a material template
    if bpy.data.objects.get('Tears'):
        tears = bpy.data.objects['Tears']
        template = bpy.data.materials['KK Tears']
        tears.material_slots[0].material = bpy.data.materials[template.name]

    # Get rid of the duplicate node groups cause there's a lot
    #stolen from somewhere
    def eliminate(node):
        node_groups = bpy.data.node_groups

        # Get the node group name as 3-tuple (base, separator, extension)
        (base, sep, ext) = node.node_tree.name.rpartition('.')

        # Replace the numeric duplicate
        if ext.isnumeric():
            if base in node_groups:
                #print("  Replace '%s' with '%s'" % (node.node_tree.name, base))
                node.node_tree.use_fake_user = False
                node.node_tree = node_groups.get(base)

    #--- Search for duplicates in actual node groups
    node_groups = bpy.data.node_groups

    for group in node_groups:
        for node in group.nodes:
            if node.type == 'GROUP':
                eliminate(node)

    #--- Search for duplicates in materials
    mats = list(bpy.data.materials)
    worlds = list(bpy.data.worlds)

    for mat in mats + worlds:
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'GROUP':
                    eliminate(node)

    #Import custom bone shapes
    innerpath = 'Collection'
    
    templateList = ['Bone Widgets']

    for template in templateList:
        bpy.ops.wm.append(
            filepath=os.path.join(filepath, innerpath, template),
            directory=os.path.join(filepath, innerpath),
            filename=template,
            #set_fake=True
            )

    return False

def apply_bone_widgets():
    #apply custom bone shapes
    #Select the armature and make it active
    bpy.ops.object.select_all(action='DESELECT')
    armature = bpy.data.objects['Armature']
    armature.hide = False
    armature.select_set(True)
    bpy.context.view_layer.objects.active=armature
    
    #Add custom shapes to the armature        
    armature.data.show_bone_custom_shapes = True
    bpy.ops.object.mode_set(mode='POSE')

    #Remove the .001 tag from all bone widgets
    #This is because the KK shader has to hold duplicate widgets for pmx and fbx
    for object in bpy.data.objects:
        if 'Widget' in object.name:
            object.name = object.name.replace(".001", "")
    
    bpy.context.object.pose.bones["Spine"].custom_shape = bpy.data.objects["WidgetChest"]
    bpy.context.object.pose.bones["Chest"].custom_shape = bpy.data.objects["WidgetChest"]
    bpy.context.object.pose.bones["Upper Chest"].custom_shape = bpy.data.objects["WidgetChest"]

    bpy.context.object.pose.bones["cf_d_bust00"].custom_shape = bpy.data.objects["WidgetBust"]
    bpy.context.object.pose.bones["cf_d_bust00"].use_custom_shape_bone_size = False
    bpy.context.object.pose.bones["cf_j_bust01_L"].custom_shape = bpy.data.objects["WidgetBreastL"]
    bpy.context.object.pose.bones["cf_j_bust01_L"].use_custom_shape_bone_size = False
    bpy.context.object.pose.bones["cf_j_bust01_R"].custom_shape = bpy.data.objects["WidgetBreastR"]
    bpy.context.object.pose.bones["cf_j_bust01_R"].use_custom_shape_bone_size = False

    bpy.context.object.pose.bones["Left shoulder"].custom_shape = bpy.data.objects["WidgetShoulderL"]
    bpy.context.object.pose.bones["Right shoulder"].custom_shape = bpy.data.objects["WidgetShoulderR"]
    bpy.context.object.pose.bones["cf_pv_hand_R"].custom_shape = bpy.data.objects["WidgetHandR"]
    bpy.context.object.pose.bones["cf_pv_hand_L"].custom_shape = bpy.data.objects["WidgetHandL"]

    bpy.context.object.pose.bones["Head"].custom_shape = bpy.data.objects["WidgetHead"]
    bpy.context.object.pose.bones["Eye Controller"].custom_shape = bpy.data.objects["WidgetEye"]
    bpy.context.object.pose.bones["Neck"].custom_shape = bpy.data.objects["WidgetNeck"]

    bpy.context.object.pose.bones["Hips"].custom_shape = bpy.data.objects["WidgetHips"]
    bpy.context.object.pose.bones["Pelvis"].custom_shape = bpy.data.objects["WidgetPelvis"]

    bpy.context.object.pose.bones["MasterFootIK.R"].custom_shape = bpy.data.objects["WidgetFoot"]
    bpy.context.object.pose.bones["MasterFootIK.L"].custom_shape = bpy.data.objects["WidgetFoot"]
    bpy.context.object.pose.bones["ToeRotator.R"].custom_shape = bpy.data.objects["WidgetToe"]
    bpy.context.object.pose.bones["ToeRotator.L"].custom_shape = bpy.data.objects["WidgetToe"]
    bpy.context.object.pose.bones["HeelIK.R"].custom_shape = bpy.data.objects["WidgetHeel"]
    bpy.context.object.pose.bones["HeelIK.L"].custom_shape = bpy.data.objects["WidgetHeel"]

    bpy.context.object.pose.bones["cf_pv_knee_R"].custom_shape = bpy.data.objects["WidgetKnee"]
    bpy.context.object.pose.bones["cf_pv_knee_L"].custom_shape = bpy.data.objects["WidgetKnee"]
    bpy.context.object.pose.bones["cf_pv_elbo_R"].custom_shape = bpy.data.objects["WidgetKnee"]
    bpy.context.object.pose.bones["cf_pv_elbo_L"].custom_shape = bpy.data.objects["WidgetKnee"]
    
    bpy.context.object.pose.bones["Center"].custom_shape = bpy.data.objects["WidgetRoot"]
    
    try:
        bpy.context.space_data.overlay.show_relationship_lines = False
    except:
        #the script was run in the text editor or console, so this won't work
        pass
    
    # apply eye bones, mouth bones, eyebrow bones
    eyebones = [1,2,3,4,5,6,7,8]
    for piece in eyebones:
        left = 'cf_J_Eye0'+str(piece)+'_s_L'
        right = 'cf_J_Eye0'+str(piece)+'_s_R'
        bpy.context.object.pose.bones[left].custom_shape  = bpy.data.objects['WidgetFace']
        bpy.context.object.pose.bones[right].custom_shape = bpy.data.objects['WidgetFace']
    
    restOfFace = [
    'cf_J_Mayu_R', 'cf_J_MayuMid_s_R', 'cf_J_MayuTip_s_R',
    'cf_J_Mayu_L', 'cf_J_MayuMid_s_L', 'cf_J_MayuTip_s_L',
    'cf_J_Mouth_R', 'cf_J_Mouth_L',
    'cf_J_Mouthup', 'cf_J_MouthLow', 'cf_J_MouthMove', 'cf_J_MouthCavity']
    for bone in restOfFace:
        bpy.context.object.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetFace']
    
    evenMoreOfFace = [
    'cf_J_EarUp_L', 'cf_J_EarBase_ry_L', 'cf_J_EarLow_L',
    'cf_J_CheekUp2_L', 'cf_J_Eye_rz_L', 'cf_J_Eye_rz_L', 
    'cf_J_CheekUp_s_L', 'cf_J_CheekLow_s_L', 

    'cf_J_EarUp_R', 'cf_J_EarBase_ry_R', 'cf_J_EarLow_R',
    'cf_J_CheekUp2_R', 'cf_J_Eye_rz_R', 'cf_J_Eye_rz_R', 
    'cf_J_CheekUp_s_R', 'cf_J_CheekLow_s_R',

    'cf_J_ChinLow', 'cf_J_Chin_s', 'cf_J_ChinTip_Base', 
    'cf_J_NoseBase', 'cf_J_NoseBridge_rx', 'cf_J_Nose_tip']
    
    for bone in evenMoreOfFace:
        bpy.context.object.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetSpine']
        
    
    fingerList = [
    'IndexFinger1_L', 'IndexFinger2_L', 'IndexFinger3_L',
    'MiddleFinger1_L', 'MiddleFinger2_L', 'MiddleFinger3_L',
    'RingFinger1_L', 'RingFinger2_L', 'RingFinger3_L',
    'LittleFinger1_L', 'LittleFinger2_L', 'LittleFinger3_L',
    'Thumb0_L', 'Thumb1_L', 'Thumb2_L',
    
    'IndexFinger1_R', 'IndexFinger2_R', 'IndexFinger3_R',
    'MiddleFinger1_R', 'MiddleFinger2_R', 'MiddleFinger3_R',
    'RingFinger1_R', 'RingFinger2_R', 'RingFinger3_R',
    'LittleFinger1_R', 'LittleFinger2_R', 'LittleFinger3_R',
    'Thumb0_R', 'Thumb1_R', 'Thumb2_R']
    
    for finger in fingerList:
        #print(armature.pose.bones[finger].name)
        if 'Thumb' in finger:
            armature.pose.bones[finger].custom_shape  = bpy.data.objects['WidgetFingerThumb']
        else:
            armature.pose.bones[finger].custom_shape  = bpy.data.objects['WidgetFinger']
        
    try:
        bp_list = get_bone_list('bp_list')
        toe_list = get_bone_list('toe_list')
        for bone in bp_list:
            armature.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetSpine']
            armature.pose.bones[bone].custom_shape_scale = 1.8
        for bone in toe_list:
            armature.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetSpine']
    except:
        #This isn't a BP armature
        pass
    
    #Make the body and clothes layers visible
    all_layers = [
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False,
    False, False, False, False, False, False, False, False]

    all_layers[0] = True
    all_layers[8] = True
    all_layers[9] = True
    bpy.ops.armature.armature_layers(layers=all_layers)
    bpy.context.object.data.display_type = 'STICK'
    
    bpy.ops.object.mode_set(mode='OBJECT')

def get_and_load_textures(directory):

    bpy.ops.object.mode_set(mode='OBJECT')
    if r"C:\Users" in directory:
        print_directory =  directory[directory.find('\\', 10):]
    else:
        print_directory = directory
    kklog('Getting textures from: ' + print_directory)

    #get images for body object
    fileList = Path(directory).glob('*.*')
    files = [file for file in fileList if file.is_file()]

    #get all images from all outfit directories
    outfit_objects = [obj for obj in bpy.data.objects if obj.name[:7] == 'Outfit ']
    for outfit in outfit_objects:
        fileList = Path(directory + r'\Outfit 0' + outfit.name[8]).glob('*.*')
        files_to_append = [file for file in fileList if file.is_file()]
        for outfit_file in files_to_append:
            files.append(outfit_file)

    for image in files:
        bpy.ops.image.open(filepath=str(image), use_udim_detecting=False)
        bpy.data.images[image.name].pack()
    
    #Get texture data for offset and scale
    for file in files:
        if 'KK_TextureData.json' in str(file):
            json_file_path = str(file)
            json_file = open(json_file_path)
            json_tex_data = json.load(json_file)
    
    #Add all textures to the correct places in the body template
    def image_load(mat, group, node, image, raw = False):
        if bpy.data.images.get(image):
            current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image]
            if raw:
                current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image.colorspace_settings.name = 'Raw'
            apply_texture_data_to_image(image, mat, group, node)
        elif 'MainCol' in image:
            if bpy.data.images[image[0:len(image)-4] + '.dds']:
                current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image[0:len(image)-4] + '.dds']
            kklog('.dds and .png files not found, skipping: ' + image[0:len(image)-4] + '.dds')
        else:
            kklog('File not found, skipping: ' + image)
    
    def set_uv_type(mat, group, uvnode, uvtype):
        current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[uvnode].uv_map = uvtype

    #Added node2 for the alpha masks
    def apply_texture_data_to_image(image, mat, group, node, node2 = ''):
        #kklog('Im in the texture function')
        for item in json_tex_data:
            if item["textureName"] == str(image):
                #Apply Offset and Scale
                if node2 == '':
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[0] = item["offset"]["x"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[1] = item["offset"]["y"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[0] = item["scale"]["x"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[1] = item["scale"]["y"]
                else:
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.translation[0] = item["offset"]["x"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.translation[1] = item["offset"]["y"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.scale[0] = item["scale"]["x"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.scale[1] = item["scale"]["y"]
                #kklog('I finished the texture function')
                break
    
    current_obj = bpy.data.objects['Body']
    image_load('KK Body', 'Gentex', 'BodyMain', 'cf_m_body_MT_CT.png')
    if not current_obj.material_slots['KK Body'].material.node_tree.nodes['Gentex'].node_tree.nodes['BodyMain'].image:
        current_obj.material_slots['KK Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['colorsLight'].inputs['Use maintex instead?'].default_value = 0
    image_load('KK Body', 'Gentex', 'BodyMC', 'cf_m_body_CM.png')
    image_load('KK Body', 'Gentex', 'BodyMD', 'cf_m_body_DM.png') #cfm female
    image_load('KK Body', 'Gentex', 'BodyLine', 'cf_m_body_LM.png')
    image_load('KK Body', 'Gentex', 'BodyNorm', 'cf_m_body_NMP_CNV.png')
    image_load('KK Body', 'Gentex', 'BodyNormDetail', 'cf_m_body_NMPD_CNV.png')

    image_load('KK Body', 'Gentex', 'BodyMD', 'cm_m_body_DM.png') #cmm male
    image_load('KK Body', 'Gentex', 'BodyLine', 'cm_m_body_LM.png')
    
    image_load('KK Body', 'NSFWTextures', 'Genital', 'cf_m_body_MT.png') #chara main texture
    image_load('KK Body', 'NSFWTextures', 'Underhair', 'cf_m_body_ot2.png') #pubic hair

    image_load('KK Body', 'NSFWTextures', 'NipR', 'cf_m_body_ot1.png') #cfm female
    image_load('KK Body', 'NSFWTextures', 'NipL', 'cf_m_body_ot1.png')
    image_load('KK Body', 'NSFWTextures', 'NipR', 'cm_m_body_ot1.png') #cmm male
    image_load('KK Body', 'NSFWTextures', 'NipL', 'cm_m_body_ot1.png')

    image_load('KK Body', 'Gentex', 'overone', 'cf_m_body_T3.png') #body overlays
    image_load('KK Body', 'Gentex', 'overtwo', 'cf_m_body_T4.png')
    
    set_uv_type('KK Body', 'NSFWpos', 'nippleuv', 'uv_nipple_and_shine')
    set_uv_type('KK Body', 'NSFWpos', 'underuv', 'uv_underhair')

    try:
        #add female alpha mask
        current_obj.material_slots['KK Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].node_tree.nodes['AlphaBody'].image = bpy.data.images['cf_m_body_AM.png'] #female
        apply_texture_data_to_image('KK Body', 'BodyShader', 'BodyTransp', 'AlphaBody')
    except:
        try:
            #maybe the character is male
            current_obj.material_slots['KK Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].node_tree.nodes['AlphaBody'].image = bpy.data.images['cm_m_body_AM.png'] #male
            apply_texture_data_to_image('KK Body', 'BodyShader', 'BodyTransp', 'AlphaBody')
        except:
            #An alpha mask for the clothing wasn't present in the Textures folder
            current_obj.material_slots['KK Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].inputs['Built in transparency toggle'].default_value = 0
    
    image_load('KK Face', 'Gentex', 'FaceMain', 'cf_m_face_00_MT_CT.png')
    #default to colors if there's no face maintex
    if not current_obj.material_slots['KK Face'].material.node_tree.nodes['Gentex'].node_tree.nodes['FaceMain'].image:
        current_obj.material_slots['KK Face'].material.node_tree.nodes['FaceShader'].node_tree.nodes['colorsLight'].inputs['Use maintex instead?'].default_value = 0
    image_load('KK Face', 'Gentex', 'FaceMC', 'cf_m_face_00_CM.png')
    image_load('KK Face', 'Gentex', 'FaceMD', 'cf_m_face_00_DM.png')
    image_load('KK Face', 'Gentex', 'BlushMask', 'cf_m_face_00_T4.png')
    image_load('KK Face', 'Gentex', 'FaceTongue', 'cf_m_face_00_MT.png') #face main texture
    
    image_load('KK Face', 'Gentex', 'linemask', 'cf_m_face_00_LM.png')
    image_load('KK Face', 'Gentex', 'overlay1', 'cf_m_face_00_T5.png')
    image_load('KK Face', 'Gentex', 'overlay2', 'cf_m_face_00_T6.png')
    image_load('KK Face', 'Gentex', 'overlay3', 'cf_m_face_00_T7.png')
    
    image_load('KK Eyebrows (mayuge)', 'Gentex', 'Eyebrow', 'cf_m_mayuge_00_MT_CT.png')
    image_load('KK Nose', 'Gentex', 'Nose', 'cf_m_noseline_00_MT_CT.png')
    image_load('KK Teeth (tooth)', 'Gentex', 'Teeth', 'cf_m_tooth_MT_CT.png')
    image_load('KK Eyewhites (sirome)', 'Gentex', 'Eyewhite', 'cf_m_sirome_00_MT_CT.png')
    
    image_load('KK Eyeline up', 'Gentex', 'EyelineUp', 'cf_m_eyeline_00_up_MT_CT.png')
    image_load('KK Eyeline up', 'Gentex', 'EyelineUp.001', 'cf_m_eyeline_00_up_MT_CT.png')
    image_load('KK Eyeline up', 'Gentex', 'EyelineDown', 'cf_m_eyeline_down_MT_CT.png')
    image_load('KK Eyeline up', 'Gentex', 'EyelineDown.001', 'cf_m_eyeline_down_MT_CT.png')
    image_load('KK Eyeline up', 'Gentex', 'EyelineKage', 'cf_m_eyeline_kage_MT.png')
    
    image_load('KK Eye (hitomi)', 'Gentex', 'eyeAlpha', 'cf_m_hitomi_00_MT_CT.png')
    image_load('KK Eye (hitomi)', 'Gentex', 'EyeHU', 'cf_m_hitomi_00_ot1.png')
    image_load('KK Eye (hitomi)', 'Gentex', 'EyeHD', 'cf_m_hitomi_00_ot2.png')

    image_load('KK Face', 'Gentex', 'EyeshadowMask', 'cf_m_face_00_ot3.png')
    set_uv_type('KK Face', 'Facepos', 'eyeshadowuv', 'uv_eyeshadow')
    
    image_load('KK Tongue', 'Gentex', 'Maintex', 'cf_m_tang_CM.png') #done on purpose
    image_load('KK Tongue', 'Gentex', 'MainCol', 'cf_m_tang_CM.png')
    image_load('KK Tongue', 'Gentex', 'MainDet', 'cf_m_tang_DM.png')
    image_load('KK Tongue', 'Gentex', 'MainNorm', 'cf_m_tang_NMP.png')
    image_load('KK Tongue', 'Gentex', 'MainNormDetail', 'cf_m_tang_NMP_CNV.png') #load regular map by default
    image_load('KK Tongue', 'Gentex', 'MainNormDetail', 'cf_m_tang_NMPD_CNV.png') #then the detail map if it's there

    #load the tears texture in
    if bpy.data.objects.get('Tears'):
        current_obj = bpy.data.objects['Tears']
        image_load('KK Tears', 'Gentex', 'Maintex', 'cf_m_namida_00_MT_CT.png')

    #for each material slot in each hair object, load in the hair detail mask, colormask
    hair_objects = [obj for obj in bpy.data.objects if 'Hair Outfit ' in obj.name]
    for current_obj  in hair_objects:
        for hairMat in current_obj.material_slots:
            hairType = hairMat.name.replace('KK ','')
            
            #make a copy of the node group, use it to replace the current node group and rename it so each piece of hair has it's own unique hair texture group
            newNode = hairMat.material.node_tree.nodes['Gentex'].node_tree.copy()
            hairMat.material.node_tree.nodes['Gentex'].node_tree = newNode
            newNode.name = hairType + ' Textures'
            
            image_load(hairMat.name, 'Gentex', 'hairMainTex',  hairType+'_MT_CT.png')
            image_load(hairMat.name, 'Gentex', 'hairDetail', hairType+'_DM.png')
            image_load(hairMat.name, 'Gentex', 'hairFade',   hairType+'_CM.png')
            image_load(hairMat.name, 'Gentex', 'hairShine',  hairType+'_HGLS.png')
            image_load(hairMat.name, 'Gentex', 'hairAlpha',  hairType+'_AM.png')
            set_uv_type(hairMat.name, 'Hairpos', 'hairuv', 'uv_nipple_and_shine')

            #If no alpha mask wasn't loaded in disconnect the hair alpha node to make sure this piece of hair is visible
            if hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image == None and hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image == None:
                getOut = hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Group Output'].inputs['Hair alpha'].links[0]
                hairMat.material.node_tree.nodes['Gentex'].node_tree.links.remove(getOut)
    
    # Loop through each material in the general object and load the textures, if any, into unique node groups
    # also make unique shader node groups so all materials are unique
    # make a copy of the node group, use it to replace the current node group
    outfit_objects = [obj for obj in bpy.data.objects if 'Outfit ' in obj.name and 'Hair Outfit ' not in obj.name and obj.type == 'MESH']
    for object in outfit_objects:
        current_obj = object
        for genMat in current_obj.material_slots:
            genType = genMat.name.replace('KK ','')
            
            #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique texture group
            newNode = genMat.material.node_tree.nodes['Gentex'].node_tree.copy()
            genMat.material.node_tree.nodes['Gentex'].node_tree = newNode
            newNode.name = genType + ' Textures'

            #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique position group
            posNode = genMat.material.node_tree.nodes['Genpos'].node_tree.copy()
            genMat.material.node_tree.nodes['Genpos'].node_tree = posNode
            posNode.name = genType + ' Position'

            image_load(genMat.name, 'Gentex', 'Maintexplain', genType+ '_MT.png')
            image_load(genMat.name, 'Gentex', 'Maintex', genType+ '_MT.png')
            image_load(genMat.name, 'Gentex', 'Maintex', genType+'_MT_CT.png')
            image_load(genMat.name, 'Gentex', 'MainCol', genType+'_CM.png')
            image_load(genMat.name, 'Gentex', 'MainDet', genType+'_DM.png')
            image_load(genMat.name, 'Gentex', 'MainNorm', genType+'_NMP.png')
            image_load(genMat.name, 'Gentex', 'MainNormDetail', genType+'_NMP_CNV.png') #load regular map by default
            image_load(genMat.name, 'Gentex', 'MainNormDetail', genType+'_NMPD_CNV.png') #then the detail map if it's there
            image_load(genMat.name, 'Gentex', 'Alphamask', genType+'_AM.png')

            # image_load(genMat.name, 'Gentex', 'PatBase', genType+'_PM1.png')
            
            image_load(genMat.name, 'Gentex', 'PatRed', genType+'_PM1.png')
            image_load(genMat.name, 'Gentex', 'PatGreen', genType+'_PM2.png')
            image_load(genMat.name, 'Gentex', 'PatBlue', genType+'_PM3.png')
            
            MainImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
            AlphaImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
                    
            #Also, make a copy of the General shader node group, as it's unlikely everything using it will be the same color
            newNode = genMat.material.node_tree.nodes['KKShader'].node_tree.copy()
            genMat.material.node_tree.nodes['KKShader'].node_tree = newNode
            newNode.name = genType + ' Shader'
            
            #If an alpha mask was loaded in, enable the alpha mask toggle in the KK shader
            if  AlphaImage != None:
                toggle = genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['Transparency toggle'].default_value = 1

            #If no main image was loaded in, there's no alpha channel being fed into the KK Shader.
            #Unlink the input node and make the alpha channel pure white
            if  not MainImage:
                getOut = genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].links[0]
                genMat.material.node_tree.nodes['KKShader'].node_tree.links.remove(getOut)
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].default_value = (1,1,1,1)
            
            #check maintex config
            plainMain = not genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintexplain'].image .name == 'Template: Maintex plain placeholder'
            if not MainImage and not plainMain:
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 0
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 0
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 0
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 0

            elif not MainImage and plainMain:
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Use colored maintex?'].default_value = 0
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 0
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Use colored maintex?'].default_value = 0
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 0
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 1

            elif MainImage and not plainMain:
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Use colored maintex?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Use colored maintex?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 1

            else: #MainImage and plainMain
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Use colored maintex?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Use colored maintex?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1
                genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 1

def add_outlines(single_outline_mode):
    #Add face and body outlines, then load in the clothes transparency mask to body outline
    ob = bpy.context.view_layer.objects['Body']
    bpy.context.view_layer.objects.active = ob
    mod = ob.modifiers.new(type='SOLIDIFY', name='Outline Modifier')
    mod.thickness = 0.0005
    mod.offset = 0
    mod.material_offset = len(ob.material_slots)
    mod.use_flip_normals = True
    mod.use_rim = False
    #mod.vertex_group = 'Body without Tears'
    #mod.invert_vertex_group = True
    mod.name = 'Outline Modifier'
    mod.show_expanded = False
    
    #body
    ob.data.materials.append(bpy.data.materials['KK Body Outline'])
    try:
        bpy.data.materials['KK Body Outline'].node_tree.nodes['BodyMask'].image = bpy.data.images['cf_m_body_AM.png'] #female
    except:
        try:
            bpy.data.materials['KK Body Outline'].node_tree.nodes['BodyMask'].image = bpy.data.images['cf_m_body_AM.png'] #male
        except:
            #An alpha mask for the clothing wasn't present in the Textures folder
            bpy.data.materials['KK Body Outline'].node_tree.nodes['Clipping prevention toggle'].inputs[0].default_value = 0            
    
    #face
    faceOutlineMat = bpy.data.materials['KK Outline'].copy()
    faceOutlineMat.name = 'KK Face Outline'
    ob.data.materials.append(faceOutlineMat)
    faceOutlineMat.blend_method = 'CLIP'

    #And give the body an inactive data transfer modifier for the shading proxy
    mod = ob.modifiers.new(type='DATA_TRANSFER', name = 'Shadowcast shading proxy')
    mod.show_expanded = False
    mod.show_viewport = False
    mod.show_render = False
    if bpy.data.objects.get('Shadowcast'):
        mod.object = bpy.data.objects['Shadowcast']
    mod.use_loop_data = True
    mod.data_types_loops = {'CUSTOM_NORMAL'}
    mod.loop_mapping = 'POLYINTERP_LNORPROJ'

    #Give each piece of hair with an alphamask on each hair object it's own outline group
    hair_objects = [obj for obj in bpy.data.objects if 'Hair Outfit ' in obj.name]
    for ob in hair_objects:
        bpy.context.view_layer.objects.active = ob

        #Get the length of the material list before starting
        outlineStart = len(ob.material_slots)

        for matindex in range(0, outlineStart, 1):
            #print(matindex)
            genMat = ob.material_slots[matindex]
            genType = genMat.name.replace('KK ','')
            
            AlphaImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image
            MainImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image

            if AlphaImage or MainImage:
                #set the material as active and move to the top of the material list
                ob.active_material_index = ob.data.materials.find(genMat.name)

                def moveUp():
                    return bpy.ops.object.material_slot_move(direction='UP')

                while moveUp() != {"CANCELLED"}:
                    pass

                OutlineMat = bpy.data.materials['KK Outline'].copy()
                OutlineMat.name = 'Outline ' + genType
                ob.data.materials.append(OutlineMat)

                #redraw UI with each material append to prevent crashing
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

                #Make the new outline the first outline in the material list
                ob.active_material_index = ob.data.materials.find(OutlineMat.name)
                while ob.active_material_index > outlineStart:
                    #print(AlphaImage)
                    #print(ob.active_material_index)
                    moveUp()

                #and after it's done moving...
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)      
            else:
                kklog(genType + ' had no alphamask or maintex')

        #separate hair outline loop to prevent crashing
        if not single_outline_mode:
            bpy.context.view_layer.objects.active = ob
            for OutlineMat in ob.material_slots:
                if 'Outline ' in OutlineMat.name:
                    genType = OutlineMat.name.replace('Outline ','')
                    #print(genType)
                    AlphaImage = ob.material_slots['KK ' + genType].material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image
                    MainImage = ob.material_slots['KK ' + genType].material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image
                    #print(genType)
                    #print(MainImage)
                    if AlphaImage:
                        OutlineMat.material.node_tree.nodes['outlinealpha'].image = AlphaImage
                        OutlineMat.material.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                        OutlineMat.material.node_tree.nodes['maintexoralpha'].blend_type = 'MULTIPLY'
                    elif MainImage:
                        OutlineMat.material.node_tree.nodes['outlinealpha'].image = MainImage
                        OutlineMat.material.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                    
                    OutlineMat.material.node_tree.nodes['outlinetransparency'].inputs[0].default_value = 1.0
        else:
            outlineStart = 200
    
        #Add a general outline that covers the rest of the materials on the hair object that don't need transparency
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        mod = ob.modifiers[1]
        mod.thickness = 0.0005
        mod.offset = 1
        mod.material_offset = outlineStart
        mod.use_flip_normals = True
        mod.use_rim = False
        mod.name = 'Outline Modifier'
        mod.show_expanded = False
        hairOutlineMat = bpy.data.materials['KK Outline'].copy()
        hairOutlineMat.name = 'KK Hair Outline'
        ob.data.materials.append(hairOutlineMat)

        #hide alts
        if ob.name[:12] == 'Hair Outfit ' and ob.name != 'Hair Outfit 00':
            ob.hide = True
            ob.hide_render = True

    #Add a standard outline to all other objects
    outfit_objects = [obj for obj in bpy.data.objects if 'Outfit ' in obj.name and 'Hair Outfit ' not in obj.name and obj.type == 'MESH']
    #If the material has a maintex or alphamask then give it it's own outline, mmdtools style
    #keep a dictionary of the material length list for the next loop
    outlineStart = {}
    for ob in outfit_objects:
        bpy.context.view_layer.objects.active = ob
        
        #Get the length of the material list before starting
        outlineStart[ob.name] = len(ob.material_slots)
        
        #done this way because the range changes length during the loop
        for matindex in range(0, outlineStart[ob.name],1):
            genMat = ob.material_slots[matindex]
            genType = genMat.name.replace('KK ','')
            #print(genType)
            
            try:
                MainImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                AlphaImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
                
                if MainImage != None or AlphaImage != None:
                    transpType = 'alpha'
                    if AlphaImage != None:
                        Image = AlphaImage
                    else:
                        transpType = 'main'
                        Image = MainImage
                    
                    #set the material as active and move to the top of the material list
                    ob.active_material_index = ob.data.materials.find(genMat.name)

                    def moveUp():
                        return bpy.ops.object.material_slot_move(direction='UP')

                    while moveUp() != {"CANCELLED"}:
                        pass

                    OutlineMat = bpy.data.materials['KK Outline'].copy()
                    OutlineMat.name = 'Outline ' + genType
                    ob.data.materials.append(OutlineMat)

                    #redraw UI with each material append to prevent crashing
                    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

                    #Make the new outline the first outline in the material list
                    ob.active_material_index = ob.data.materials.find(OutlineMat.name)
                    while ob.active_material_index > outlineStart[ob.name]:
                        moveUp()
                        #print(ob.active_material_index)

                    #and after it's done moving...
                        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                        
            except:
                kklog(genType + ' had a maintex image but no transparency')

    #print(outlineStart)
    #separate loop to prevent crashing
    for ob in outfit_objects:
        if not single_outline_mode:
            bpy.context.view_layer.objects.active = ob
            for OutlineMat in ob.material_slots:
                if 'Outline ' in OutlineMat.name:
                    genType = OutlineMat.name.replace('Outline ','')
                    MainImage = ob.material_slots['KK ' + genType].material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                    AlphaImage = ob.material_slots['KK ' + genType].material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
                    #print(genType)
                    #print(MainImage)
                    #print(AlphaImage)

                    if AlphaImage != None:
                        OutlineMat.material.node_tree.nodes['outlinealpha'].image = AlphaImage
                        OutlineMat.material.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 0.0
                    else:
                        OutlineMat.material.node_tree.nodes['outlinealpha'].image = MainImage
                        OutlineMat.material.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0

                    OutlineMat.material.node_tree.nodes['outlinetransparency'].inputs[0].default_value = 1.0
        else:
            outlineStart = 200
        
        #Add a general outline that covers the rest of the materials on the object that don't need transparency
        bpy.context.view_layer.objects.active = ob
        mod = ob.modifiers.new(
            type='SOLIDIFY',
            name='Outline Modifier')
        mod.thickness = 0.0005
        mod.offset = 1
        mod.material_offset = outlineStart[ob.name]
        mod.use_flip_normals = True
        mod.use_rim = False
        mod.show_expanded = False
        ob.data.materials.append(bpy.data.materials['KK Outline'])

        #hide alts
        if 'Indoor shoes Outfit ' in ob.name or ' alt ' in ob.name or (ob.name[:7] == 'Outfit ' and ob.name != 'Outfit 00') or (ob.name[:12] == 'Hair Outfit ' and ob.name != 'Hair Outfit 00'):
            ob.hide = True
            ob.hide_render = True

def hide_widgets():
    #automatically hide bone widgets collection if it's visible
    for widget_col in ['Bone Widgets', 'Bone Widgets fbx']:
        try:
            bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children[widget_col]
            bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
        except:
            try:
                #maybe the collection is in the Collection collection
                bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children['Collection'].children[widget_col]
                bpy.context.scene.view_layers[0].active_layer_collection.exclude = True
            except:
                #maybe the collection is already hidden
                pass

def clean_orphan_data():
    #clean up the oprhaned data
    for block in bpy.data.materials:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.textures.remove(block)
    
    for block in bpy.data.images:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.images.remove(block)
    
class import_everything(bpy.types.Operator):
    bl_idname = "kkb.importeverything"
    bl_label = "Finish separating objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            last_step = time.time()
            directory = context.scene.kkbp.import_dir
            
            kklog('\nApplying material templates and textures...')

            scene = context.scene.kkbp
            use_fake_user = scene.templates_bool
            single_outline_mode = scene.texture_outline_bool
            modify_armature = scene.armature_dropdown in ['A', 'B']

            #these methods will return true if an error was encountered to make sure the error popup shows
            template_error = get_templates_and_apply(directory, use_fake_user)
            if template_error:
                return {'FINISHED'}
            
            #redraw the UI after each operation to let the user know the plugin is actually doing something
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            texture_error = get_and_load_textures(directory)
            if texture_error:
                return {'FINISHED'}
            
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
            add_outlines(single_outline_mode)
            if modify_armature and bpy.data.objects['Armature'].pose.bones["Spine"].custom_shape == None:
                #kklog(str(time.time() - last_step))
                kklog('Adding bone widgets...')
                apply_bone_widgets()
            hide_widgets()

            bpy.data.objects['Armature'].hide = False
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            #clean data
            clean_orphan_data()

            kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            return {'FINISHED'}

        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_everything)

    # test call
    print((bpy.ops.kkb.importeverything('INVOKE_DEFAULT')))
