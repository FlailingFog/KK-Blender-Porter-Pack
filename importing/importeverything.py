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

import bpy, os, traceback, json
from pathlib import Path
from bpy.props import StringProperty
from .finalizepmx import kklog
from .cleanarmature import get_bone_list

#Stop if this is the wrong folder
def wrong_folder_error(self, context):
    self.layout.label(text="The PMX folder was not selected. (Hint: go into the .pmx folder before confirming)")

#Stop if no face mc or body mc files were found
def missing_texture_error(self, context):
    self.layout.label(text="The files cf_m_body_CM.png and cf_m_face_00_CM.png were not found in the folder.\nMake sure to open the exported folder. \nHit undo and try again")

#stop if no hair object was found
def hair_error(self, context):
    self.layout.label(text="""An object named \"Hair\" wasn't found. Separate this from the Clothes object and rename it.
    If your character doesn't have hair, disable the hair check option in the import options section below""")

def get_templates_and_apply(directory, use_fake_user):
    #if a single thing was separated but the user forgot to rename it, it's probably the hair object
    if bpy.data.objects.get('Clothes.001') and len(bpy.data.objects) == 6:
        bpy.data.objects['Clothes.001'].name = 'Hair'
    
    #Check if a hair object exists
    if not (bpy.data.objects.get('Hair') or bpy.data.objects.get('hair')):
        bpy.context.window_manager.popup_menu(hair_error, title="Error", icon='ERROR')
        return True
    
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
        if '.blend' in str(file) and '.blend1' not in str(file):
            filepath = str(file)
            blend_file_missing = False
    
    if blend_file_missing:
        #grab it from the plugin directory
        script_dir=Path(__file__).parent
        template_path=(script_dir / '../KK Shader V5.0.blend').resolve()
        filepath = str(template_path)
    
    innerpath = 'Material'
    templateList = ['Template Body',
    'Template Outline',
    'Template Body Outline',
    'Template Tears',
    'Template Eye (hitomi)',
    'Template Eyebrows (mayuge)',
    'Template Eyeline down',
    'Template Eyeline up',
    'Template Eyewhites (sirome)',
    'Template Face',
    'Template General',
    'Template Hair',
    'Template Mixed Metal or Shiny',
    'Template Nose',
    'Template Shadowcast',
    'Template Teeth (tooth)',
    'Template Fangs (tooth.001)']

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
    
    swap_body_material('cf_m_face_00','Template Face')
    swap_body_material('cf_m_mayuge_00','Template Eyebrows (mayuge)')
    swap_body_material('cf_m_noseline_00','Template Nose')
    swap_body_material('cf_m_eyeline_00_up','Template Eyeline up')
    swap_body_material('cf_m_eyeline_down','Template Eyeline down')
    swap_body_material('cf_m_sirome_00','Template Eyewhites (sirome)')
    swap_body_material('cf_m_sirome_00.001','Template Eyewhites (sirome)')
    swap_body_material('cf_m_hitomi_00','Template Eye (hitomi)')
    swap_body_material('cf_m_hitomi_00.001','Template Eye (hitomi)')
    swap_body_material('cf_m_body','Template Body') #female
    swap_body_material('cm_m_body','Template Body') #male
    swap_body_material('cf_m_tooth','Template Teeth (tooth)')
    swap_body_material('cf_m_tooth.001','Template Fangs (tooth.001)')
    swap_body_material('cf_m_tang','Template General')
    
    #Make the tongue material unique so parts of the General Template aren't overwritten
    tongueTemplate = bpy.data.materials['Template General'].copy()
    tongueTemplate.name = 'Template Tongue'
    body.material_slots['Template General'].material = tongueTemplate
    
    #Make the texture group unique
    newNode = tongueTemplate.node_tree.nodes['Gentex'].node_tree.copy()
    tongueTemplate.node_tree.nodes['Gentex'].node_tree = newNode
    newNode.name = 'Tongue Textures'
    
    #Make the shader group unique
    newNode = tongueTemplate.node_tree.nodes['KKShader'].node_tree.copy()
    tongueTemplate.node_tree.nodes['KKShader'].node_tree = newNode
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
    hair = bpy.data.objects['Hair']
    for original in hair.material_slots:
        template = bpy.data.materials['Template Hair'].copy()
        template.name = 'Template ' + original.name
        original.material = bpy.data.materials[template.name]
    
    #Replace all other materials with the general template and name accordingly
    for ob in bpy.context.view_layer.objects:
        if ob.type == 'MESH' and ('Body' not in ob.name and 'Hair' not in ob.name):
            for original in ob.material_slots:
                template = bpy.data.materials['Template General'].copy()
                template.name = 'Template ' + original.name
                original.material = bpy.data.materials[template.name]
    
    #give the shadowcast object a template as well
    shadowcast = bpy.data.objects['Shadowcast']
    template = bpy.data.materials['Template Shadowcast']
    shadowcast.material_slots[0].material = bpy.data.materials[template.name]

    #give the tears a material template
    if bpy.data.objects.get('Tears'):
        tears = bpy.data.objects['Tears']
        template = bpy.data.materials['Template Tears']
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
    kklog('Getting textures from: ' + directory)

    #lazy check to see if the user actually opened the Textures folder
    #this will false pass if the word "Texture" is anywhere else on the path but I don't care
    fileList = Path(directory).glob('*.*')
    files = [file for file in fileList if file.is_file()]

    body_missing = True
    face_missing = True
    for image in files:
        bpy.ops.image.open(filepath=str(image))
        bpy.data.images[image.name].pack()
        if 'cf_m_body_CM.png' in str(image):
            body_missing = False
        if 'cf_m_face_00_CM.png' in str(image):
            face_missing = False
    
    if body_missing or face_missing:
        bpy.context.window_manager.popup_menu(missing_texture_error, title="Error", icon='ERROR')
        return True
    
    #Get texture data for offset and scale
    for file in files:
        if 'KK_TextureData.json' in str(file):
            json_file_path = str(file)
            json_file = open(json_file_path)
            json_tex_data = json.load(json_file)
    
    #Add all textures to the correct places in the body template
    currentObj = bpy.data.objects['Body']
    def imageLoad(mat, group, node, image, raw = False):
        if bpy.data.images.get(image):
            currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image]
            if raw:
                currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image.colorspace_settings.name = 'Raw'
            applyTextureDataToImageNode(image, mat, group, node)
        elif 'MainCol' in image:
            if bpy.data.images[image[0:len(image)-4] + '.dds']:
                currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image[0:len(image)-4] + '.dds']
            kklog('.dds and .png files not found, skipping: ' + image[0:len(image)-4] + '.dds')
        else:
            kklog('File not found, skipping: ' + image)
    
    #Added node2 for the alpha masks
    def applyTextureDataToImageNode(image, mat, group, node, node2 = ''):
        for item in json_tex_data:
            if item["textureName"] == str(image):
                #Apply Offset and Scale
                if node2 == '':
                    currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[0] = item["offset"]["x"]
                    currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[1] = item["offset"]["y"]
                    currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[0] = item["scale"]["x"]
                    currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[1] = item["scale"]["y"]
                else:
                    currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.translation[0] = item["offset"]["x"]
                    currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.translation[1] = item["offset"]["y"]
                    currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.scale[0] = item["scale"]["x"]
                    currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.scale[1] = item["scale"]["y"]
                break
            
    imageLoad('Template Body', 'Gentex', 'BodyMain', 'cf_m_body_MT_CT.png')
    imageLoad('Template Body', 'Gentex', 'BodyMC', 'cf_m_body_CM.png')
    imageLoad('Template Body', 'Gentex', 'BodyMD', 'cf_m_body_DM.png') #cfm female
    imageLoad('Template Body', 'Gentex', 'BodyLine', 'cf_m_body_LM.png')
    imageLoad('Template Body', 'Gentex', 'BodyNorm', 'cf_m_body_NMP.png')

    imageLoad('Template Body', 'Gentex', 'BodyMD', 'cm_m_body_DM.png') #cmm male
    imageLoad('Template Body', 'Gentex', 'BodyLine', 'cm_m_body_LM.png')
    
    imageLoad('Template Body', 'NippleTextures', 'Genital', 'cf_m_body_MT.png') #chara main texture
    imageLoad('Template Body', 'NippleTextures', 'Underhair', 'cf_m_body_ot2.png') #pubic hair

    imageLoad('Template Body', 'NippleTextures', 'NipR', 'cf_m_body_ot1.png') #cfm female
    imageLoad('Template Body', 'NippleTextures', 'NipL', 'cf_m_body_ot1.png')
    imageLoad('Template Body', 'NippleTextures', 'NipR', 'cm_m_body_ot1.png') #cmm male
    imageLoad('Template Body', 'NippleTextures', 'NipL', 'cm_m_body_ot1.png')
    
    try:
        #add female alpha mask
        currentObj.material_slots['Template Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].node_tree.nodes['AlphaBody'].image = bpy.data.images['cf_m_body_AM.png'] #female
        applyTextureDataToImageNode('Template Body', 'BodyShader', 'BodyTransp', 'AlphaBody')
    except:
        try:
            #maybe the character is male
            currentObj.material_slots['Template Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].node_tree.nodes['AlphaBody'].image = bpy.data.images['cm_m_body_AM.png'] #male
            applyTextureDataToImageNode('Template Body', 'BodyShader', 'BodyTransp', 'AlphaBody')
        except:
            #An alpha mask for the clothing wasn't present in the Textures folder
            currentObj.material_slots['Template Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].inputs['Built in transparency toggle'].default_value = 0
    
    imageLoad('Template Face', 'Gentex', 'FaceMain', 'cf_m_face_00_MT_CT.png')
    imageLoad('Template Face', 'Gentex', 'FaceMC', 'cf_m_face_00_CM.png')
    imageLoad('Template Face', 'Gentex', 'FaceMD', 'cf_m_face_00_DM.png')
    imageLoad('Template Face', 'Gentex', 'BlushMask', 'cf_m_face_00_T4.png')
    imageLoad('Template Face', 'Gentex', 'FaceTongue', 'cf_m_face_00_MT.png') #face main texture

    imageLoad('Template Face', 'Gentex', 'BlushMask.001', 'cf_m_face_00_T5.png')

    
    imageLoad('Template Eyebrows (mayuge)', 'Gentex', 'Eyebrow', 'cf_m_mayuge_00_MT_CT.png')
    imageLoad('Template Nose', 'Gentex', 'Nose', 'cf_m_noseline_00_MT_CT.png')
    imageLoad('Template Teeth (tooth)', 'Gentex', 'Teeth', 'cf_m_tooth_MT_CT.png')
    imageLoad('Template Eyewhites (sirome)', 'Gentex', 'Eyewhite', 'cf_m_sirome_00_MT_CT.png')
    
    imageLoad('Template Eyeline up', 'Gentex', 'EyelineUp', 'cf_m_eyeline_00_up_MT_CT.png')
    imageLoad('Template Eyeline up', 'Gentex', 'EyelineUp.001', 'cf_m_eyeline_00_up_MT_CT.png')
    imageLoad('Template Eyeline up', 'Gentex', 'EyelineDown', 'cf_m_eyeline_down_MT_CT.png')
    imageLoad('Template Eyeline up', 'Gentex', 'EyelineDown.001', 'cf_m_eyeline_down_MT_CT.png')
    imageLoad('Template Eyeline up', 'Gentex', 'EyelineKage', 'cf_m_eyeline_kage_MT.png')
    
    
    imageLoad('Template Eye (hitomi)', 'Gentex', 'eyeAlpha', 'cf_m_hitomi_00_MT_CT.png')
    imageLoad('Template Eye (hitomi)', 'Gentex', 'EyeHU', 'cf_m_hitomi_00_ot1.png')
    imageLoad('Template Eye (hitomi)', 'Gentex', 'EyeHD', 'cf_m_hitomi_00_ot2.png')
    
    imageLoad('Template Tongue', 'Gentex', 'Maintex', 'cf_m_tang_CM.png') #done on purpose
    imageLoad('Template Tongue', 'Gentex', 'MainCol', 'cf_m_tang_CM.png')
    imageLoad('Template Tongue', 'Gentex', 'MainDet', 'cf_m_tang_DM.png')
    imageLoad('Template Tongue', 'Gentex', 'MainNorm', 'cf_m_tang_NMP.png', True)

    #load the tears texture in
    if bpy.data.objects.get('Tears'):
        currentObj = bpy.data.objects['Tears']
        imageLoad('Template Tears', 'Gentex', 'Maintex', 'cf_m_namida_00_MT_CT.png')

    #for each material slot in the hair object, load in the hair detail mask, colormask
    currentObj = bpy.data.objects['Hair']
 
    for hairMat in currentObj.material_slots:
        hairType = hairMat.name.replace('Template ','')
        
        #make a copy of the node group, use it to replace the current node group and rename it so each piece of hair has it's own unique hair texture group
        newNode = hairMat.material.node_tree.nodes['Gentex'].node_tree.copy()
        hairMat.material.node_tree.nodes['Gentex'].node_tree = newNode
        newNode.name = hairType + ' Textures'
        
        imageLoad(hairMat.name, 'Gentex', 'hairMainTex',  hairType+'_MT_CT.png')
        imageLoad(hairMat.name, 'Gentex', 'hairDetail', hairType+'_DM.png')
        imageLoad(hairMat.name, 'Gentex', 'hairFade',   hairType+'_CM.png')
        imageLoad(hairMat.name, 'Gentex', 'hairShine',  hairType+'_HGLS.png')
        imageLoad(hairMat.name, 'Gentex', 'hairAlpha',  hairType+'_AM.png')

        #If no alpha mask wasn't loaded in disconnect the hair alpha node to make sure this piece of hair is visible
        if hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image == None and hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image == None:
            getOut = hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Group Output'].inputs['Hair alpha'].links[0]
            hairMat.material.node_tree.nodes['Gentex'].node_tree.links.remove(getOut)
    
    # Loop through each material in the general object and load the textures, if any, into unique node groups
    # also make unique shader node groups so all materials are unique
    
    # make a copy of the node group, use it to replace the current node group
    not_clothes = ['Hair', 'Body', 'Tears']
    for object in bpy.context.view_layer.objects:
        if  object.type == 'MESH' and object.name not in not_clothes:
            
            currentObj = object
            for genMat in currentObj.material_slots:
                genType = genMat.name.replace('Template ','')
                
                #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique texture group
                newNode = genMat.material.node_tree.nodes['Gentex'].node_tree.copy()
                genMat.material.node_tree.nodes['Gentex'].node_tree = newNode
                newNode.name = genType + ' Textures'
                
                imageLoad(genMat.name, 'Gentex', 'Maintexplain', genType+ '_MT.png')
                imageLoad(genMat.name, 'Gentex', 'Maintex', genType+ '_MT.png')
                imageLoad(genMat.name, 'Gentex', 'Maintex', genType+'_MT_CT.png')
                imageLoad(genMat.name, 'Gentex', 'MainCol', genType+'_CM.png')
                imageLoad(genMat.name, 'Gentex', 'MainDet', genType+'_DM.png')
                imageLoad(genMat.name, 'Gentex', 'MainNorm', genType+'_NMP.png', True)
                imageLoad(genMat.name, 'Gentex', 'Alphamask', genType+'_AM.png')

                # imageLoad(genMat.name, 'Gentex', 'PatBase', genType+'_PM1.png')
                
                imageLoad(genMat.name, 'Gentex', 'PatRed', genType+'_PM1.png')
                imageLoad(genMat.name, 'Gentex', 'PatGreen', genType+'_PM2.png')
                imageLoad(genMat.name, 'Gentex', 'PatBlue', genType+'_PM3.png')
                
                MainImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                AlphaImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
                     
                #Also, make a copy of the General shader node group, as it's unlikely everything using it will be the same color
                newNode = genMat.material.node_tree.nodes['KKShader'].node_tree.copy()
                genMat.material.node_tree.nodes['KKShader'].node_tree = newNode
                newNode.name = genType + ' Shader'
                
                #If no main image was loaded in, there's no alpha channel being fed into the KK Shader.
                #Unlink the input node and make the alpha channel pure white
                #Also, change a slider to make sure the colormask doesn't screw up later
                if  MainImage == None:
                    getOut = genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].links[0]
                    genMat.material.node_tree.nodes['KKShader'].node_tree.links.remove(getOut)
                    genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].default_value = (1,1,1,1)
                    genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsLight'].inputs['Maintex is loaded?'].default_value = 0
                    genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['colorsDark'].inputs['Maintex is loaded?'].default_value = 0

                    
                #If an alpha mask was loaded in, enable the alpha mask toggle in the KK shader
                if  AlphaImage != None:
                    toggle = genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['Transparency toggle'].default_value = 1

def add_outlines(single_outline_mode):
    #Add face and body outlines, then load in the clothes transparency mask to body outline
    ob = bpy.context.view_layer.objects['Body']
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    mod_index = 1 if len(ob.modifiers) == 2 else 3
    mod = ob.modifiers[mod_index]
    mod.thickness = 0.0005
    mod.offset = 0
    mod.material_offset = len(ob.material_slots)
    mod.use_flip_normals = True
    mod.use_rim = False
    #mod.vertex_group = 'Body without Tears'
    #mod.invert_vertex_group = True
    mod.name = 'Outline Modifier'
    
    #body
    ob.data.materials.append(bpy.data.materials['Template Body Outline'])
    try:
        bpy.data.materials['Template Body Outline'].node_tree.nodes['BodyMask'].image = bpy.data.images['cf_m_body_AM.png'] #female
    except:
        try:
            bpy.data.materials['Template Body Outline'].node_tree.nodes['BodyMask'].image = bpy.data.images['cf_m_body_AM.png'] #male
        except:
            #An alpha mask for the clothing wasn't present in the Textures folder
            bpy.data.materials['Template Body Outline'].node_tree.nodes['Clipping prevention toggle'].inputs[0].default_value = 0            
    
    #face
    faceOutlineMat = bpy.data.materials['Template Outline'].copy()
    faceOutlineMat.name = 'Template Face Outline'
    ob.data.materials.append(faceOutlineMat)
    faceOutlineMat.blend_method = 'CLIP'

    #And give the body an inactive data transfer modifier for the shading proxy
    mod = ob.modifiers.new(type='DATA_TRANSFER', name = 'Shadowcast shading proxy')
    mod.show_viewport = False
    mod.show_render = False
    mod.object = bpy.data.objects['Shadowcast']
    mod.use_loop_data = True
    mod.data_types_loops = {'CUSTOM_NORMAL'}
    mod.loop_mapping = 'POLYINTERP_LNORPROJ'

    #Give each piece of hair with an alphamask it's own outline group
    ob = bpy.context.view_layer.objects['Hair']
    bpy.context.view_layer.objects.active = ob

    #Get the length of the material list before starting
    outlineStart = len(ob.material_slots)

    for matindex in range(0, outlineStart, 1):
        #print(matindex)
        genMat = ob.material_slots[matindex]
        genType = genMat.name.replace('Template ','')
        
        AlphaImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image
        MainImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image

        if AlphaImage or MainImage:
            #set the material as active and move to the top of the material list
            ob.active_material_index = ob.data.materials.find(genMat.name)

            def moveUp():
                return bpy.ops.object.material_slot_move(direction='UP')

            while moveUp() != {"CANCELLED"}:
                pass

            OutlineMat = bpy.data.materials['Template Outline'].copy()
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
                AlphaImage = ob.material_slots['Template ' + genType].material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image
                MainImage = ob.material_slots['Template ' + genType].material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image
                #print(genType)
                #print(MainImage)
                if AlphaImage:
                    OutlineMat.material.node_tree.nodes['outlinealpha'].image = AlphaImage
                    OutlineMat.material.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                elif MainImage:
                    OutlineMat.material.node_tree.nodes['outlinealpha'].image = MainImage
                    OutlineMat.material.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                
                OutlineMat.material.node_tree.nodes['outlinetransparency'].inputs[0].default_value = 1.0
    else:
        outlineStart = 200
    
    #Add a general outline that covers the rest of the materials on the hair object that don't need transparency

    ob = bpy.context.view_layer.objects['Hair']
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    mod = ob.modifiers[1]
    mod.thickness = 0.0005
    mod.offset = 1
    mod.material_offset = outlineStart
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.name = 'Outline Modifier'
    hairOutlineMat = bpy.data.materials['Template Outline'].copy()
    hairOutlineMat.name = 'Template Hair Outline'
    ob.data.materials.append(hairOutlineMat)
    
    #Add a standard outline to all other objects
    #If the material has a maintex or alphamask then give it it's own outline, mmdtools style
    #keep a dictionary of the material length list for the next loop
    outlineStart = {}
    for ob in bpy.context.view_layer.objects:
        if  ob.type == 'MESH' and ob.name != 'Body' and ob.name != 'Hair' and ob.name != 'Tears' and 'Widget' not in ob.name and not single_outline_mode:
            
            bpy.context.view_layer.objects.active = ob
            
            #Get the length of the material list before starting
            outlineStart[ob.name] = len(ob.material_slots)
            
            #done this way because the range changes length during the loop
            for matindex in range(0, outlineStart[ob.name],1):
                genMat = ob.material_slots[matindex]
                genType = genMat.name.replace('Template ','')
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

                        OutlineMat = bpy.data.materials['Template Outline'].copy()
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

    #separate loop to prevent crashing
    for ob in bpy.context.view_layer.objects:
        if  ob.type == 'MESH' and ob.name != 'Body' and ob.name != 'Hair' and ob.name != 'Tears' and 'Widget' not in ob.name:
            if not single_outline_mode:
                bpy.context.view_layer.objects.active = ob
                for OutlineMat in ob.material_slots:
                    if 'Outline ' in OutlineMat.name:
                        genType = OutlineMat.name.replace('Outline ','')
                        MainImage = ob.material_slots['Template ' + genType].material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                        AlphaImage = ob.material_slots['Template ' + genType].material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
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
            bpy.ops.object.modifier_add(type='SOLIDIFY')
            mod = ob.modifiers[1]
            mod.thickness = 0.0005
            mod.offset = 1
            mod.material_offset = outlineStart[ob.name]
            mod.use_flip_normals = True
            mod.use_rim = False
            mod.name = 'Outline Modifier'
            ob.data.materials.append(bpy.data.materials['Template Outline'])

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
    bl_label = "Open Export folder"
    bl_description = "Open the folder containing your model.pmx file"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None

    def execute(self, context):
        try:

            directory = self.directory
            
            kklog('\nApplying material templates and textures...')

            scene = context.scene.placeholder
            use_fake_user = scene.templates_bool
            single_outline_mode = scene.texture_outline_bool
            modify_armature = scene.armature_edit_bool
            bald_alert = not scene.haircheck_bool
            
            #create a cube that will act as a fake hair object, then delete at the end
            if bald_alert:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.mesh.primitive_cube_add(size=0.5)
                bpy.data.objects['Cube'].name = 'Hair'
                bpy.data.materials.new(name="hairdummymat")
                bpy.data.objects['Hair'].data.materials.append(bpy.data.materials['hairdummymat'])
                bpy.context.view_layer.objects.active = bpy.data.objects['Hair']
                bpy.ops.object.modifier_add(type='ARMATURE')

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
                kklog('Adding bone widgets...')
                apply_bone_widgets()
            hide_widgets()

            bpy.data.objects['Armature'].hide = False
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            #delete the fake hair object
            if bald_alert:
                bpy.data.objects.remove(bpy.data.objects['Hair'], do_unlink=True)

            #clean data
            clean_orphan_data()

            #set the viewport shading
            my_areas = bpy.context.workspace.screens[0].areas
            my_shading = 'MATERIAL'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'

            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading 

            return {'FINISHED'}

        except:
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_everything)

    # test call
    print((bpy.ops.kkb.importeverything('INVOKE_DEFAULT')))
