'''
IMPORT TEXTURES SCRIPT
- Loads the material templates from the KK shader .blend
- Loads in the textures received from Grey's Mesh Exporter
Usage:
- Click the button and choose the folder that contains the textures
'''

import bpy, os
from pathlib import Path
from bpy.props import StringProperty
from .cleanarmature import get_bone_list

#Stop if this is the wrong folder
def wrong_folder_error(self, context):
    self.layout.label(text="The PMX folder was not selected. (Hint: go into the .pmx folder before confirming)")

#Stop if no face mc or body mc files were found
def missing_texture_error(self, context):
    self.layout.label(text="The files cf_m_body_ColorMask.png and cf_m_face_00_ColorMask.png were not found in the folder.\nMake sure to open the exported folder. \nHit undo and try again")

#stop if no hair object was found
def hair_error(self, context):
    self.layout.label(text="An object named \"Hair\" wasn't found. Separate this from the Clothes object and rename it.")

def get_templates_and_apply(directory, useFakeUser):
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
    templateList = ['Template Body', 'Template Outline', 'Template Body Outline', 'Template Eye (hitomi)', 'Template Eyebrows (mayuge)', 'Template Eyeline down', 'Template Eyeline up', 'Template Eyewhites (sirome)', 'Template Face', 'Template General', 'Template Hair', 'Template Mixed Metal or Shiny', 'Template Nose', 'Template Shadowcast (Standard)', 'Template Teeth (tooth)']

    for template in templateList:
        bpy.ops.wm.append(
            filepath=os.path.join(filepath, innerpath, template),
            directory=os.path.join(filepath, innerpath),
            filename=template,
            set_fake=useFakeUser
            )
    
    #Replace all materials on the body with templates
    body = bpy.data.objects['Body']
    def swap_body_material(original, template):
        try:
            body.material_slots[original].material = bpy.data.materials[template]
        except:
            print('material or template wasn\'t found: ' + original + ' / ' + template)
    
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
    
    #Make sure the hair object's name is capitalized
    try:
        bpy.data.objects['hair'].name = 'Hair'
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
    
    #give the shadowcast object the general template as well
    shadowcast = bpy.data.objects['Shadowcast']
    template = bpy.data.materials['Template General'].copy()
    template.name = 'Template Shadowcast'
    shadmat = shadowcast.material_slots[0].material
    shadmat = bpy.data.materials[template.name]
    shadmat.node_tree.nodes['KKShader'].inputs
    getOut = shadmat.node_tree.nodes['KKShader'].inputs['Main Texture'].links[0]
    shadmat.node_tree.links.remove(getOut)
    getOut = shadmat.node_tree.nodes['KKShader'].inputs['Main Alpha'].links[0]
    shadmat.node_tree.links.remove(getOut)

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
    
    if bpy.data.objects['Armature'].data.bones.get('Greybone'):
        templateList = ['Bone Widgets fbx']
    else:
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
        print(armature.pose.bones[finger].name)
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
    print('Getting textures from: ' + directory)

    #lazy check to see if the user actually opened the Textures folder
    #this will false pass if the word "Texture" is anywhere else on the path but I don't care
    fileList = Path(directory).glob('*.*')
    files = [file for file in fileList if file.is_file()]

    body_missing = True
    face_missing = True
    for image in files:
        bpy.ops.image.open(filepath=str(image))
        bpy.data.images[image.name].pack()
        if 'cf_m_body_ColorMask.png' in str(image):
            body_missing = False
        if 'cf_m_face_00_ColorMask.png' in str(image):
            face_missing = False
    
    if body_missing or face_missing:
        bpy.context.window_manager.popup_menu(missing_texture_error, title="Error", icon='ERROR')
        return True
    
    #Add all textures to the correct places in the body template
    currentObj = bpy.data.objects['Body']
    def imageLoad(mat, group, node, image, raw = False):
        if bpy.data.images.get(image):
            currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image]
            if raw:
                currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image.colorspace_settings.name = 'Raw'
        elif 'MainCol' in image:
            if bpy.data.images[image[0:len(image)-4] + '.dds']:
                currentObj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image[0:len(image)-4] + '.dds']
            print('.dds and .png files not found, skipping: ' + image[0:len(image)-4] + '.dds')
        else:
            print('File not found, skipping: ' + image)
        
    imageLoad('Template Body', 'BodyTextures', 'BodyMC', 'cf_m_body_ColorMask.png')
    imageLoad('Template Body', 'BodyTextures', 'BodyMD', 'cf_m_body_DetailMask.png') #cfm female
    imageLoad('Template Body', 'BodyTextures', 'BodyLine', 'cf_m_body_LineMask.png')
    imageLoad('Template Body', 'BodyTextures', 'BodyNorm', 'cf_m_body_NormalMap.png')

    imageLoad('Template Body', 'BodyTextures', 'BodyMD', 'cm_m_body_DetailMask.png') #cmm male
    imageLoad('Template Body', 'BodyTextures', 'BodyLine', 'cm_m_body_LineMask.png')
    
    imageLoad('Template Body', 'NippleTextures', 'Genital', 'cf_m_body_MainTex.png') #chara main texture
    imageLoad('Template Body', 'NippleTextures', 'Underhair', 'cf_m_body_overtex2.png') #pubic hair

    imageLoad('Template Body', 'NippleTextures', 'NipR', 'cf_m_body_overtex1.png') #cfm female
    imageLoad('Template Body', 'NippleTextures', 'NipL', 'cf_m_body_overtex1.png')
    imageLoad('Template Body', 'NippleTextures', 'NipR', 'cm_m_body_overtex1.png') #cmm male
    imageLoad('Template Body', 'NippleTextures', 'NipL', 'cm_m_body_overtex1.png')
    
    try:
        #add female alpha mask
        currentObj.material_slots['Template Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].node_tree.nodes['AlphaBody'].image = bpy.data.images['cf_m_body_AlphaMask.png'] #female
    except:
        try:
            #maybe the character is male
            currentObj.material_slots['Template Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].node_tree.nodes['AlphaBody'].image = bpy.data.images['cm_m_body_AlphaMask.png'] #male
        except:
            #An alpha mask for the clothing wasn't present in the Textures folder
            currentObj.material_slots['Template Body'].material.node_tree.nodes['BodyShader'].node_tree.nodes['BodyTransp'].inputs['Built in transparency toggle'].default_value = 0
    
    imageLoad('Template Face', 'FaceTextures', 'FaceMC', 'cf_m_face_00_ColorMask.png')
    imageLoad('Template Face', 'FaceTextures', 'FaceMD', 'cf_m_face_00_DetailMask.png')
    imageLoad('Template Face', 'FaceTextures', 'BlushMask', 'cf_m_face_00_Texture4.png')
    imageLoad('Template Face', 'FaceTextures', 'FaceTongue', 'cf_m_face_00_MainTex.png') #face main texture

    imageLoad('Template Face', 'FaceTextures', 'BlushMask.001', 'cf_m_face_00_Texture5.png')


    
    imageLoad('Template Eyebrows (mayuge)', 'BrowTextures', 'Eyebrow', 'cf_m_mayuge_00_MainTex_CT.png')
    imageLoad('Template Nose', 'Nose', 'Nose', 'cf_m_noseline_00_MainTex_CT.png')
    imageLoad('Template Teeth (tooth)', 'Teeth', 'Teeth', 'cf_m_tooth_MainTex_CT.png')
    imageLoad('Template Eyewhites (sirome)', 'EyewhiteTex', 'Eyewhite', 'cf_m_sirome_00_MainTex_CT.png')
    
    imageLoad('Template Eyeline up', 'Eyeline', 'EyelineUp', 'cf_m_eyeline_00_up_MainTex_CT.png')
    imageLoad('Template Eyeline up', 'Eyeline', 'EyelineUp.001', 'cf_m_eyeline_00_up_MainTex_CT.png')
    imageLoad('Template Eyeline up', 'Eyeline', 'EyelineDown', 'cf_m_eyeline_down_MainTex_CT.png')
    imageLoad('Template Eyeline up', 'Eyeline', 'EyelineDown.001', 'cf_m_eyeline_down_MainTex_CT.png')
    imageLoad('Template Eyeline up', 'Eyeline', 'EyelineKage', 'cf_m_eyeline_kage_MainTex.png')
    
    
    imageLoad('Template Eye (hitomi)', 'EyeTex', 'eyeAlpha', 'cf_m_hitomi_00_MainTex_CT.png')
    imageLoad('Template Eye (hitomi)', 'EyeTex', 'EyeHU', 'cf_m_hitomi_00_overtex1.png')
    imageLoad('Template Eye (hitomi)', 'EyeTex', 'EyeHD', 'cf_m_hitomi_00_overtex2.png')
    
    imageLoad('Template Tongue', 'Gentex', 'Maintex', 'cf_m_tang_ColorMask.png') #done on purpose
    imageLoad('Template Tongue', 'Gentex', 'MainCol', 'cf_m_tang_ColorMask.png')
    imageLoad('Template Tongue', 'Gentex', 'MainDet', 'cf_m_tang_DetailMask.png')
    imageLoad('Template Tongue', 'Gentex', 'MainNorm', 'cf_m_tang_NormalMap.png', True)

    #for each material slot in the hair object, load in the hair detail mask, colormask
    currentObj = bpy.data.objects['Hair']
 
    for hairMat in currentObj.material_slots:
        hairType = hairMat.name.replace('Template ','')
        
        #make a copy of the node group, use it to replace the current node group and rename it so each piece of hair has it's own unique hair texture group
        newNode = hairMat.material.node_tree.nodes['HairTextures'].node_tree.copy()
        hairMat.material.node_tree.nodes['HairTextures'].node_tree = newNode
        newNode.name = hairType + ' Textures'
        
        imageLoad(hairMat.name, 'HairTextures', 'hairDetail', hairType+'_DetailMask.png')
        imageLoad(hairMat.name, 'HairTextures', 'hairFade',   hairType+'_ColorMask.png')
        imageLoad(hairMat.name, 'HairTextures', 'hairShine',  hairType+'_HairGloss.png')
        imageLoad(hairMat.name, 'HairTextures', 'hairAlpha',  hairType+'_AlphaMask.png')

        #If no alpha mask wasn't loaded in disconnect the hair alpha node to make sure this piece of hair is visible
        if hairMat.material.node_tree.nodes['HairTextures'].node_tree.nodes['hairAlpha'].image == None:
            getOut = hairMat.material.node_tree.nodes['HairTextures'].node_tree.nodes['Group Output'].inputs['Hair alpha'].links[0]
            hairMat.material.node_tree.nodes['HairTextures'].node_tree.links.remove(getOut)
    
    # Loop through each material in the general object and load the textures, if any, into unique node groups
    # also make unique shader node groups so all materials are unique
    
    # make a copy of the node group, use it to replace the current node group
    for object in bpy.context.view_layer.objects:
        if  object.type == 'MESH' and object.name != 'Hair' and object.name != 'Body':
            
            currentObj = object
            
            for genMat in currentObj.material_slots:
                genType = genMat.name.replace('Template ','')
                
                #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique texture group
                newNode = genMat.material.node_tree.nodes['Gentex'].node_tree.copy()
                genMat.material.node_tree.nodes['Gentex'].node_tree = newNode
                newNode.name = genType + ' Textures'
                
                imageLoad(genMat.name, 'Gentex', 'Maintex', genType+ '_MainTex.png')
                imageLoad(genMat.name, 'Gentex', 'Maintex', genType+'_MainTex_CT.png')
                imageLoad(genMat.name, 'Gentex', 'MainCol', genType+'_ColorMask.png')
                imageLoad(genMat.name, 'Gentex', 'MainDet', genType+'_DetailMask.png')
                imageLoad(genMat.name, 'Gentex', 'MainNorm', genType+'_NormalMap.png', True)
                imageLoad(genMat.name, 'Gentex', 'Alphamask', genType+'_AlphaMask.png')

                # imageLoad(genMat.name, 'Gentex', 'PatBase', genType+'_PatternMask1.png')
                
                imageLoad(genMat.name, 'Gentex', 'PatRed', genType+'_PatternMask1.png')
                imageLoad(genMat.name, 'Gentex', 'PatGreen', genType+'_PatternMask2.png')
                imageLoad(genMat.name, 'Gentex', 'PatBlue', genType+'_PatternMask3.png')
                
                MainImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                AlphaImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
                     
                #Also, make a copy of the General shader node group, as it's unlikely everything using it will be the same color
                newNode = genMat.material.node_tree.nodes['KKShader'].node_tree.copy()
                genMat.material.node_tree.nodes['KKShader'].node_tree = newNode
                newNode.name = genType + ' Shader'
                
                #If no main image was loaded in, there's no alpha channel being fed into the KK Shader.
                #Unlink the input node and make the alpha channel pure white
                if  MainImage == None:
                    getOut = genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].links[0]
                    genMat.material.node_tree.nodes['KKShader'].node_tree.links.remove(getOut)
                    genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].default_value = (1,1,1,1)   
                    
                #If an alpha mask was loaded in, enable the alpha mask toggle in the KK shader
                if  AlphaImage != None:
                    toggle = genMat.material.node_tree.nodes['KKShader'].node_tree.nodes['alphatoggle'].inputs['Transparency toggle'].default_value = 1

def add_outlines(oneOutlineOnlyMode):
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
    mod.name = 'Outline Modifier'
    
    #face
    faceOutlineMat = bpy.data.materials['Template Outline'].copy()
    faceOutlineMat.name = 'Template Face Outline'
    ob.data.materials.append(faceOutlineMat)
    
    #body
    ob.data.materials.append(bpy.data.materials['Template Body Outline'])
    try:
        bpy.data.materials['Template Body Outline'].node_tree.nodes['BodyMask'].image = bpy.data.images['cf_m_body_AlphaMask.png'] #female
    except:
        try:
            bpy.data.materials['Template Body Outline'].node_tree.nodes['BodyMask'].image = bpy.data.images['cf_m_body_AlphaMask.png'] #male
        except:
            #An alpha mask for the clothing wasn't present in the Textures folder
            bpy.data.materials['Template Body Outline'].node_tree.nodes['Clipping prevention toggle'].inputs[0].default_value = 0            
        
    #Give each piece of hair with an alphamask it's own outline group
    ob = bpy.context.view_layer.objects['Hair']
    bpy.context.view_layer.objects.active = ob

    #Get the length of the material list before starting
    outlineStart = len(ob.material_slots)
    print(outlineStart)
    
    #done this way because the range changes length during the loop
    for matindex in range(0, outlineStart,1):
        genMat = ob.material_slots[matindex]
        genType = genMat.name.replace('Template ','')
        
        AlphaImage = genMat.material.node_tree.nodes['HairTextures'].node_tree.nodes['hairAlpha'].image
        if AlphaImage:
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
            print(genType + ' had no alphamask')

    #separate hair outline loop to prevent crashing
    if not oneOutlineOnlyMode:
        bpy.context.view_layer.objects.active = ob
        for OutlineMat in ob.material_slots:
            if 'Outline ' in OutlineMat.name:
                genType = OutlineMat.name.replace('Outline ','')
                print(genType)
                AlphaImage = genMat.material.node_tree.nodes['HairTextures'].node_tree.nodes['hairAlpha'].image      

                if AlphaImage:
                    OutlineMat.material.node_tree.nodes['outlinealpha'].image = AlphaImage
                    OutlineMat.material.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                
                OutlineMat.material.node_tree.nodes['outlinetransparency'].inputs[0].default_value = 1.0
    else:
        outlineStart = 200
    
    #Add a general outline that covers the rest of the materials on the object that don't need transparency

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
    for ob in bpy.context.view_layer.objects:
        if  ob.type == 'MESH' and ob.name != 'Body' and ob.name != 'Hair' and 'Widget' not in ob.name and not oneOutlineOnlyMode:
            
            bpy.context.view_layer.objects.active = ob
            
            #Get the length of the material list before starting
            outlineStart = len(ob.material_slots)
            
            #done this way because the range changes length during the loop
            for matindex in range(0, outlineStart,1):
                genMat = ob.material_slots[matindex]
                genType = genMat.name.replace('Template ','')
                print(genType)
                
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
                        while ob.active_material_index > outlineStart:
                            moveUp()
                            #print(ob.active_material_index)

                        #and after it's done moving...
                            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                            
                except:
                    print(genType + ' had a maintex image but no transparency')

    #separate loop to prevent crashing
    for ob in bpy.context.view_layer.objects:
        if  ob.type == 'MESH' and ob.name != 'Body' and ob.name != 'Hair' and 'Widget' not in ob.name:
            if not oneOutlineOnlyMode:
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
            mod.material_offset = outlineStart
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
    bl_label = "Import Textures folder"
    bl_description = "Open the folder containing the textures and the KK Shader.blend file"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None

    def execute(self, context):
        directory = self.directory
        
        scene = context.scene.placeholder
        useFakeUser = scene.templates_bool
        oneOutlineOnlyMode = scene.textureoutline_bool
        modify_armature = scene.armature_edit_bool
        
        #these methods will return true if an error was encountered
        template_error = get_templates_and_apply(directory, useFakeUser)
        if template_error:
            return {'FINISHED'}
        
        #redraw the UI after each operation to let the user know the plugin is actually doing something
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        texture_error = get_and_load_textures(directory)
        if texture_error:
            return {'FINISHED'}
        
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        add_outlines(oneOutlineOnlyMode)
        if modify_armature and bpy.data.objects['Armature'].pose.bones["Spine"].custom_shape == None:
            apply_bone_widgets()
        hide_widgets()

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

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

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_everything)

    # test call
    print((bpy.ops.kkb.importeverything('INVOKE_DEFAULT')))
