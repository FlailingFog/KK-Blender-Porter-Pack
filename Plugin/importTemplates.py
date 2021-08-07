'''
IMPORT KK TEMPLATES SCRIPT
- Appends the material templates from the KK Shader .blend file
Usage:
- Click the button and choose the KK shader .blend file
'''

import bpy
import os

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

class import_Templates(Operator, ImportHelper):
    bl_idname = "kkb.importtemplates"
    bl_label = "Open KK Shader .blend"
    bl_description = "Open the KK Shader .blend file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: StringProperty(
        default='*.blend',
        options={'HIDDEN'}
    )
    
    def execute(self, context):
        
        scene = context.scene.placeholder
        useFakeUser = scene.templates_bool
        
        #Clean material list
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
        filepath = self.filepath
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
        def bodySwap(original, template):
            try:
                body.material_slots[original].material = bpy.data.materials[template]
            except:
                print('material or template wasn\'t found: ' + original + ' / ' + template)

        bodySwap('cf_m_face_00','Template Face')
        bodySwap('cf_m_mayuge_00','Template Eyebrows (mayuge)')
        bodySwap('cf_m_noseline_00','Template Nose')
        bodySwap('cf_m_eyeline_00_up','Template Eyeline up')
        bodySwap('cf_m_eyeline_down','Template Eyeline down')
        bodySwap('cf_m_sirome_00','Template Eyewhites (sirome)')
        bodySwap('cf_m_sirome_00.001','Template Eyewhites (sirome)')
        bodySwap('cf_m_hitomi_00','Template Eye (hitomi)')
        bodySwap('cf_m_hitomi_00.001','Template Eye (hitomi)')
        bodySwap('cf_m_body','Template Body') #female
        bodySwap('cm_m_body','Template Body') #male
        bodySwap('cf_m_tooth','Template Teeth (tooth)')
        bodySwap('cf_m_tang','Template General')
        
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
        
        # Get rid of the duplicate node groups cause there's a lot
        #stolen from somwhere
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
        filepath = self.filepath
        innerpath = 'Collection'
        templateList = ['Bone Widgets']

        for template in templateList:
            bpy.ops.wm.append(
                filepath=os.path.join(filepath, innerpath, template),
                directory=os.path.join(filepath, innerpath),
                filename=template,
                #set_fake=True
                )
        
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

        bpy.context.object.pose.bones["Hips"].custom_shape = bpy.data.objects["WidgetHips"]
        bpy.context.object.pose.bones["Spine"].custom_shape = bpy.data.objects["WidgetChest"]
        bpy.context.object.pose.bones["Chest"].custom_shape = bpy.data.objects["WidgetChest"]
        bpy.context.object.pose.bones["Cf_D_Bust00"].custom_shape = bpy.data.objects["WidgetBust"]
        bpy.context.object.pose.bones["Left shoulder"].custom_shape = bpy.data.objects["WidgetShoulder"]
        bpy.context.object.pose.bones["Right shoulder"].custom_shape = bpy.data.objects["WidgetShoulder"]
        bpy.context.object.pose.bones["MasterFootIK.R"].custom_shape = bpy.data.objects["WidgetFoot"]
        bpy.context.object.pose.bones["MasterFootIK.L"].custom_shape = bpy.data.objects["WidgetFoot"]
        bpy.context.object.pose.bones["ToeRotator.R"].custom_shape = bpy.data.objects["WidgetToe"]
        bpy.context.object.pose.bones["ToeRotator.L"].custom_shape = bpy.data.objects["WidgetToe"]
        bpy.context.object.pose.bones["HeelIK.R"].custom_shape = bpy.data.objects["WidgetHeel"]
        bpy.context.object.pose.bones["HeelIK.L"].custom_shape = bpy.data.objects["WidgetHeel"]
        bpy.context.object.pose.bones["Cf_Pv_Knee_R"].custom_shape = bpy.data.objects["WidgetKnee"]
        bpy.context.object.pose.bones["Cf_Pv_Knee_L"].custom_shape = bpy.data.objects["WidgetKnee"]
        bpy.context.object.pose.bones["Cf_Pv_Elbo_R"].custom_shape = bpy.data.objects["WidgetKnee"]
        bpy.context.object.pose.bones["Cf_Pv_Elbo_L"].custom_shape = bpy.data.objects["WidgetKnee"]
        bpy.context.object.pose.bones["Neck"].custom_shape = bpy.data.objects["WidgetNeck"]
        bpy.context.object.pose.bones["Head"].custom_shape = bpy.data.objects["WidgetHead"]
        bpy.context.object.pose.bones["Cf_Pv_Hand_R"].custom_shape = bpy.data.objects["WidgetHandR"]
        bpy.context.object.pose.bones["Cf_Pv_Hand_L"].custom_shape = bpy.data.objects["WidgetHandL"]
        bpy.context.object.pose.bones["AH1_L"].custom_shape = bpy.data.objects["WidgetBreast"]
        bpy.context.object.pose.bones["AH1_R"].custom_shape = bpy.data.objects["WidgetBreast"]
        bpy.context.object.pose.bones["Eye Controller"].custom_shape = bpy.data.objects["WidgetEye"]
        bpy.context.object.pose.bones["Root"].custom_shape = bpy.data.objects["WidgetRoot"]
        bpy.context.object.pose.bones["Pelvis"].custom_shape = bpy.data.objects["WidgetPelvis"]
        bpy.context.object.pose.bones["Upper Chest"].custom_shape = bpy.data.objects["WidgetChest"]
        
        try:
            bpy.context.space_data.overlay.show_relationship_lines = False
        except:
            #the script was run in the text editor or console, so this won't work
            pass
        
        skirtbones = [0,1,2,3,4,5,6,7]
        for root in skirtbones:
            bpy.context.object.pose.bones['Cf_D_Sk_0'+str(root)+'_00'].custom_shape = bpy.data.objects['WidgetSkirt']
        
        #scale and apply eye bones, mouth bones, eyebrow bones
        eyebones = [1,2,3,4,5,6,7,8]
        for piece in eyebones:
            left = 'Eye0'+str(piece)+'_S_L'
            right = 'Eye0'+str(piece)+'_S_R'
            bpy.context.object.pose.bones[left].custom_shape  = bpy.data.objects['WidgetFace']
            bpy.context.object.pose.bones[right].custom_shape = bpy.data.objects['WidgetFace']
            
        restOfFace = ['Mayu_R', 'MayuMid_S_R', 'MayuTip_S_R', 'Mayu_L', 'MayuMid_S_L', 'MayuTip_S_L', 'Mouth_R', 'Mouth_L', 'Mouthup', 'MouthLow', 'MouthMove', 'MouthCavity']
        for bone in restOfFace:
            bpy.context.object.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetFace']
        
        try:
            BPList = ['Kokan', 'Ana', 'Vagina_Root', 'Vagina_B', 'Vagina_F', 'Vagina_001_L', 'Vagina_002_L', 'Vagina_003_L', 'Vagina_004_L', 'Vagina_005_L',  'Vagina_001_R', 'Vagina_002_R', 'Vagina_003_R', 'Vagina_004_R', 'Vagina_005_R']
            for bone in BPList:
                bpy.context.object.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetBP']
        except:
            #This isn't a BP armature
            pass
        
        #Make both bone layers visible
        firstTwoBoneLayers = (True, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
        bpy.ops.armature.armature_layers(layers=firstTwoBoneLayers)
        bpy.context.object.data.display_type = 'STICK'
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(import_Templates)

    # test call
    print((bpy.ops.kkb.importtemplates('INVOKE_DEFAULT')))
    
