import bpy, os, traceback, json, time, sys
from pathlib import Path
from .. import common as c
from .cleanarmature import get_bone_list
from .darkcolors import create_darktex

#Stop if this is the wrong folder
def wrong_folder_error(self, context):
    self.layout.label(text="The PMX folder was not selected. (Hint: go into the .pmx folder before confirming)")

#Stop if no face mc or body mc files were found
def missing_texture_error(self, context):
    self.layout.label(text="The files cf_m_body_CM.png and cf_m_face_00_CM.png were not found in the folder.\nMake sure to open the exported folder. \nHit undo and try again")

#Stop if lightning boy shader is not installed
def missing_lbs(self, context):
    text = "An error occured when adding a Lightning Boy Shader node. Make sure it's installed."
    c.kklog(text, 'error')
    self.layout.label(text=text)

def get_templates_and_apply(directory, use_fake_user):
    

    
    
    
    
    
    
    



def get_and_load_textures(directory):
    

    
    

    
    

def add_outlines(single_outline_mode):






        #hide alts
        if 'Indoor shoes Outfit ' in ob.name or ' shift Outfit ' in ob.name or ' hang Outfit ' in ob.name or (ob.name[:7] == 'Outfit ' and ob.name != 'Outfit 00') or (ob.name[:12] == 'Hair Outfit ' and ob.name != 'Hair Outfit 00'):
            ob.hide = True
            ob.hide_render = True
        
    #hide hair alts
    for obj in [obj for obj in bpy.data.objects if obj.get('KKBP outfit ID') != None and 'Hair Outfit ' in obj.name and obj.name != 'Hair Outfit 00']:
        obj.hide = True




def apply_cycles():
    c.import_from_library_file('NodeTree', ['Raw Shading (face)', 'Cycles', 'Cycles no shadows', 'LBS', 'LBS face normals'], bpy.context.scene.kkbp.use_material_fake_user)

    c.kklog('Applying Cycles adjustments...')
    #taken from https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/234
    #remove outline modifier
    for o in bpy.context.view_layer.objects:
        for m in o.modifiers:
            if(m.name == "Outline Modifier"):
                m.show_viewport = False
                m.show_render = False
                
    ####fix the eyelash mesh overlap
    # deselect everything and make body active object
    body = bpy.data.objects['Body']
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active=body
    bpy.ops.object.mode_set(mode = 'EDIT')
    # define some stuff
    ops = bpy.ops
    obj = ops.object
    mesh = ops.mesh
    context = bpy.context
    object = context.object
    # edit mode and deselect everything
    obj.mode_set(mode='EDIT')
    mesh.select_all(action='DESELECT')
    # delete eyeline down verts and kage faces
    object.active_material_index = 6
    obj.material_slot_select()
    mesh.delete(type='VERT')
    object.active_material_index = 5
    obj.material_slot_select()
    mesh.delete(type='ONLY_FACE')
    #delete nose if no texture loaded in
    if not bpy.data.node_groups['Nose'].nodes[1].image:
        object.active_material_index = 2
        obj.material_slot_select()
        mesh.delete(type='VERT')
    mesh.select_all(action='DESELECT')

    #add cycles node group
    for tree in [mat.node_tree for mat in bpy.data.materials if 'KK ' in mat.name]:
        nodes = tree.nodes
        links = tree.links
        if nodes.get('Rim') and nodes.get('Shader'):
            nodes['Rim'].node_tree = bpy.data.node_groups['Cycles']
            links.new(nodes['Shader'].outputs['Color out light'], nodes['Rim'].inputs[0])
            links.new(nodes['Shader'].outputs['Color out dark'], nodes['Rim'].inputs[1])
            links.new(nodes['Shader'].outputs[3], nodes['Rim'].inputs[2])
        #disable detail shine color too
        if nodes.get('Shader'):
            if nodes['Shader'].node_tree.nodes.get('colorsLight'):
                if nodes['Shader'].node_tree.nodes['colorsLight'].inputs.get('Detail intensity (shine)'):
                    nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Detail intensity (shine)'].default_value = 0
                    nodes['Shader'].node_tree.nodes['colorsDark']. inputs['Detail intensity (shine)'].default_value = 0
    #remove linemask and blush on face material
    for type in ['colorsLight', 'colorsDark']:
        bpy.data.node_groups['Face Shader'].nodes[type].inputs['Linemask intensity'].default_value = 0
        bpy.data.node_groups['Face Shader'].nodes[type].inputs['Blush intensity'].default_value = 0
    #set eyeline up and eyebrows as shadowless
    for mat in [bpy.data.materials['KK Eyebrows (mayuge)'], bpy.data.materials['KK Eyeline up']]:
        mat.node_tree.nodes['Rim'].node_tree = bpy.data.node_groups['Cycles no shadows']
    
    #put face's color out in a mix shader with the cycles face mask
    #mute shader to rgb nodes for clothing items
    for node in [n for n in bpy.data.node_groups['General overlays'].nodes if 'Shader to RGB' in n.name]:
        node.mute = True

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.preview_samples = 10
    mesh.select_all(action='DESELECT')
    obj.mode_set(mode='OBJECT')

def apply_lbs():
    c.import_from_library_file('NodeTree', ['Raw Shading (face)', 'Cycles', 'Cycles no shadows', 'LBS', 'LBS face normals'], bpy.context.scene.kkbp.use_material_fake_user)

    c.kklog('Applying Lightning Boy Shader adjustments...')
    #Import lbs node group and replace rim group with the lbs group
    keep_list = ['KK Eyebrows (mayuge)', 'KK EyeL (hitomi)', 'KK EyeR (hitomi)', 'KK Eyeline up']
    for tree in [mat.node_tree for mat in bpy.data.materials if ('KK ' in mat.name and mat.name not in keep_list)]:
        nodes = tree.nodes
        links = tree.links
        if nodes.get('Rim') and nodes.get('Shader'):
            nodes['Rim'].node_tree = bpy.data.node_groups['LBS']
            links.new(nodes['Shader'].outputs['Color out light'], nodes['Rim'].inputs['Color light'])
            links.new(nodes['Shader'].outputs['Color out dark'], nodes['Rim'].inputs['Color dark'])
            links.new(nodes['Shader'].outputs[3], nodes['Rim'].inputs[2])
            #if nodes['Shader'].node_tree.name != 'Body Shader':
            #    links.new(nodes['RawShade'].outputs['Normal passthrough'], nodes['Rim'].inputs[3])
    #construct LBS node group from scratch because it can't be included with the KK shader
    nodes = bpy.data.node_groups['LBS'].nodes
    links = bpy.data.node_groups['LBS'].links
    try:
        LBS = nodes.new('LBSShaderNode')
    except:
        bpy.context.window_manager.popup_menu(missing_lbs, title="Error", icon='ERROR')
        return
    def expand(node):
        node.hide = False
        for sock in node.inputs:
            sock.hide = False
    LBS.initialize_group = ".Lightning Boy Shader"
    LBS.inputs['.transparency'].default_value = 0.001
    LBS.inputs['.transparency'].enabled = False
    LBS.inputs[0].enabled = False
    LBS.layers = 4
    LBS.location = 444.6600, 61.8538
    expand(LBS)
    output = [out for out in nodes if out.type == 'GROUP_OUTPUT'][0]
    output.location = 694.6600, -10.6462
    input =  [out for out in nodes if out.type == 'GROUP_INPUT'][0]
    input.location = -538.7341, 24.3778
    reroute_alpha = nodes.new('NodeReroute')
    reroute_alpha.location = 121.4401, -429.1375
    links.new(input.outputs[2], reroute_alpha.inputs[0])
    links.new(reroute_alpha.outputs[0], LBS.inputs[-3]) #connect alpha through reroute
    reroute_dark = nodes.new('NodeReroute')
    reroute_dark.location = 121.4401, -398.1375
    links.new(input.outputs[1], reroute_dark.inputs[0])
    links.new(reroute_dark.outputs[0], LBS.inputs[-4]) #connect dark
    links.new(LBS.outputs[0], output.inputs[0]) #connect LBS out

    key = nodes.new('LBSBaseNode')
    key.initialize_group = '.Key Light*'
    key.location = 49.4401, -144.1374
    expand(key)
    links.new(input.outputs['Color light'], key.inputs[0])
    links.new(input.outputs['Normal'], key.inputs[5])
    links.new(key.outputs[0], LBS.inputs[-5]) #connect light

    ao = nodes.new('LBSBaseNode')
    ao.initialize_group = '.Ambient Occlusion (SS)'
    ao.location = 49.4401, 109.8626
    expand(ao)
    links.new(input.outputs['Color dark'], ao.inputs[0])
    links.new(ao.outputs[0], LBS.inputs[-6]) #connect light

    rim = nodes.new('LBSBaseNode')
    rim.initialize_group = '.2D Rim Light*'
    rim.location = 49.4401, 423.8625
    expand(rim)
    curves = [out for out in nodes if out.type == 'CURVE_RGB'][0]
    curves.location = -215.5599, 289.3625
    links.new(input.outputs['Color light'], curves.inputs[0])
    links.new(curves.outputs[0], rim.inputs[0])
    links.new(rim.outputs[0], LBS.inputs[-7]) #connect 2d rim

    #turn on ambient occlusion and bloom in render settings
    bpy.context.scene.eevee.use_gtao = True

    #turn on bloom in render settings
    bpy.context.scene.eevee.use_bloom = True

    #face has special normal setup to work with gfn. make a copy and add the normals inside of the copy
    #this group prevents Amb Occ issues around nose, and mouth interior
    face_nodes = bpy.data.node_groups['LBS'].copy()
    face_nodes.use_fake_user = True
    face_nodes.name = 'LBS (Face)'
    nodes = bpy.data.node_groups['LBS (Face)'].nodes
    links = bpy.data.node_groups['LBS (Face)'].links
    face_norms = nodes.new('ShaderNodeGroup')
    face_norms.node_tree = bpy.data.node_groups['LBS face normals']
    face_norms.location = 410, 190
    links.new(face_norms.outputs[0], rim.inputs[-1])
    links.new(face_norms.outputs[0], key.inputs[-1])

    #select entire face and body and reset vectors to prevent Amb Occ seam around the neck 
    body = bpy.data.objects['Body']
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active=body
    bpy.ops.object.mode_set(mode = 'EDIT')
    body.active_material_index = 1
    bpy.ops.object.material_slot_select()
    bpy.ops.mesh.normals_tools(mode='RESET')
    bpy.ops.object.mode_set(mode = 'OBJECT')

def apply_sfw():
    #delete nsfw parts of the mesh
    body = bpy.data.objects['Body']
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active=body
    bpy.ops.object.mode_set(mode = 'EDIT')
    def mark_group_as_freestyle(group_list):
        for group in group_list:
            group_found = body.vertex_groups.find(group)      
            if group_found > -1:
                bpy.context.object.active_material_index = group_found
                bpy.ops.object.vertex_group_select()
            else:
                c.kklog('Group wasn\'t found when freestyling vertex groups: ' + group, 'warn')
        bpy.ops.mesh.mark_freestyle_face(clear=False)
    freestyle_list = [
        'cf_j_bnip02_L', 'cf_j_bnip02_R',
        'cf_s_bust03_L', 'cf_s_bust03_R']
    mark_group_as_freestyle(freestyle_list)
    bpy.ops.mesh.select_all(action = 'DESELECT')

    def delete_group_and_bone(group_list):
        #delete vertex groups
        bpy.ops.mesh.select_all(action = 'DESELECT')
        for group in group_list:
            group_found = body.vertex_groups.find(group)      
            if group_found > -1:
                bpy.context.object.vertex_groups.active_index = group_found
                bpy.ops.object.vertex_group_select()
            else:
                c.kklog('Group wasn\'t found when deleting vertex groups: ' + group, 'warn')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

    delete_list = ['cf_s_bnip025_L', 'cf_s_bnip025_R',
    'cf_j_kokan', 'cf_j_ana', 'cf_d_ana', 'cf_d_kokan', 'cf_s_ana',
    'Vagina_Root', 'Vagina_B', 'Vagina_F', 'Vagina_001_L', 'Vagina_002_L',
    'Vagina_003_L', 'Vagina_004_L', 'Vagina_005_L',  'Vagina_001_R', 'Vagina_002_R',
    'Vagina_003_R', 'Vagina_004_R', 'Vagina_005_R']
    delete_group_and_bone(delete_list)

    #reload the sfw alpha mask
    body_material = bpy.data.objects['Body'].material_slots['KK Body'].material
    body_material.node_tree.nodes['Gentex'].node_tree.nodes['Bodyalphacustom'].image = bpy.data.images['Template: SFW alpha mask.png']
    bpy.data.node_groups["Body Shader"].nodes["BodyTransp"].inputs[0].default_value = 1 #why do i have to do it this way
    bpy.data.node_groups["Body Shader"].nodes["BodyTransp"].inputs[1].default_value = 1
    body_material.node_tree.nodes['Shader'].node_tree.nodes['BodyTransp'].node_tree.inputs[0].hide_value = True
    body_material.node_tree.nodes['Shader'].node_tree.nodes['BodyTransp'].node_tree.inputs[1].hide_value = True

    #get rid of the nsfw groups on the body
    body_material.node_tree.nodes.remove(body_material.node_tree.nodes['NSFWTextures'])
    body_material.node_tree.nodes.remove(body_material.node_tree.nodes['NSFWpos'])

    body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Nipple mask'])
    body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Nipple alpha'])
    body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Genital mask'])
    body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Underhair mask'])

    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital intensity'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital saturation'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital hue'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Underhair color'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Underhair intensity'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple base'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple base 2'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple shine'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple rim'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple alpha'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple texture'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital mask'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Underhair mask'])

    bpy.data.materials['KK Body'].node_tree.nodes['Gentex'].node_tree.nodes['Bodyalphacustom'].image = bpy.data.images['Template: SFW alpha mask.png']
    bpy.data.materials['KK Body Outline'].node_tree.nodes['customToggle'].inputs[0].default_value = 1
    bpy.data.materials['KK Body Outline'].node_tree.nodes['customToggle'].inputs[0].hide = True

class import_everything(bpy.types.Operator):
    bl_idname = "kkbp.importeverything"
    bl_label = "Finish separating objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            last_step = time.time()
            directory = context.scene.kkbp.import_dir
            
            c.kklog('\nApplying material templates and textures...')

            scene = context.scene.kkbp
            use_fake_user = scene.use_material_fake_user
            single_outline_mode = scene.use_single_outline
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
                #c.kklog(str(time.time() - last_step))
                c.kklog('Adding bone widgets...')
                apply_bone_widgets()
            hide_widgets()

            if bpy.context.scene.kkbp.sfw_mode:
                apply_sfw()
            if bpy.context.scene.kkbp.shader_dropdown == 'B':
                apply_cycles()
            elif bpy.context.scene.kkbp.shader_dropdown == 'C':
                apply_lbs()

            #unhide first found outfit if outfit 00 is not present
            #find the appropriate outfit
            outfit = None
            if bpy.data.objects.get('Outfit 00'):
                outfit = bpy.data.objects.get('Outfit 00')
            else:
                #check the other outfit numbers
                for ob in bpy.data.objects:
                    if ob.name[0:8] == 'Outfit 0' and 'Outfit 00' not in ob.name:
                        outfit = ob
                        break
            if outfit:
                outfit.hide = False
                for child in outfit.children:
                    child.hide = True
                    if 'Hair Outfit 0' in child.name:
                        child.hide = False

            bpy.data.objects['Armature'].hide = False
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
            #clean data
            clean_orphan_data()

            #set to face select mode for easy material switching
            bpy.context.tool_settings.mesh_select_mode = (False, False, True)
            
            if context.scene.kkbp.categorize_dropdown in ['A', 'B', 'C']:
                c.set_viewport_shading('MATERIAL')

            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            return {'FINISHED'}

        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_everything)

    # test call
    print((bpy.ops.kkbp.importeverything('INVOKE_DEFAULT')))
