'''
BAKE MATERIAL TO TEXTURE SCRIPT
- Bakes all materials of an object into image textures (to use in other programs)
- Will only bake a material if an image node is present in the green texture group
- If no image is present, a low resolution failsafe image will be baked to account for fully opaque or transparent materials that don't rely on texture files
- If multiple image files are present, only one texture will be created
    - If the multiple image files have different resolutions, a texture will be created for each resolution
- Export defaults to 8-bit PNG with an alpha channel.
--    Defaults can be changed by editing the exportType and exportColormode variables below.

Usage:
- Select the object you want to bake in the 3D viewport
- Press the button and choose the folder to dump the images into
- Textures are baked to that output folder

Notes:
- This script deletes all camera and light objects in the scene
- This script sets the world color in the World tab to black

fillerplane driver + shader code taken from https://blenderartists.org/t/scripts-create-camera-image-plane/580839
'''

import bpy, os, traceback
from pathlib import Path
from ..importing.importbuttons import kklog
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

def showError(self, context):
    self.layout.label(text="No object selected (make sure the body object is selected)")

def typeError(self, context):
    self.layout.label(text="The object to bake must be a mesh object (make sure the body object is selected)")

#returns None if an error is encountered
def setup_camera():
    #Stop if no object is selected
    try:
        #An object was set as the active object but is not selected
        if not bpy.context.active_object.select_get():
            bpy.context.window_manager.popup_menu(showError, title="Error", icon='ERROR')
            return None
    except:
        #No object is set as the active object
        bpy.context.window_manager.popup_menu(showError, title="Error", icon='ERROR')
        return None

    #Stop if the object is not a mesh object
    if bpy.context.active_object.type != 'MESH':
        bpy.context.window_manager.popup_menu(typeError, title="Error", icon='ERROR')
        return None

    #######################
    object_to_bake = bpy.context.active_object

    #Select all camera and light objects
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA' or obj.type == 'LIGHT':
            obj.select_set(True)
        else:
            obj.select_set(False)

    #Then delete them
    bpy.ops.object.delete()
    
    #Purge unused cameras and lights from orphan data
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)

    #and set the world color to black 
    bpy.data.worlds[0].node_tree.nodes['Background'].inputs[0].default_value = (0,0,0,1)
    #Add a new camera
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 1), rotation=(0, 0, 0))
    #save it for later
    camera = bpy.context.active_object
    #and set it as the active one
    bpy.context.scene.camera=camera
    #Set camera to orthographic
    bpy.data.cameras[camera.name].type='ORTHO'
    bpy.data.cameras[camera.name].ortho_scale=6
    bpy.context.scene.render.pixel_aspect_y=1
    bpy.context.scene.render.pixel_aspect_x=1

    #reset currently selected object
    bpy.context.view_layer.objects.active = object_to_bake
    object_to_bake.select_set(True)

    return camera

def setup_geometry_nodes_and_fillerplane(camera):
    object_to_bake = bpy.context.active_object

    #create fillerplane
    bpy.ops.mesh.primitive_plane_add()
    bpy.ops.object.material_slot_add()
    fillerplane = bpy.context.active_object
    fillerplane.data.uv_layers[0].name = 'uv_main'
    fillerplane.name = "fillerplane"
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(0.5,0.5,0.5))
    bpy.ops.uv.reset()
    bpy.ops.object.editmode_toggle()

    fillerplane.location = (0,0,-0.0001)

    def setup_driver_variables(driver, camera):
        cam_ortho_scale = driver.variables.new()
        cam_ortho_scale.name = 'cOS'
        cam_ortho_scale.type = 'SINGLE_PROP'
        cam_ortho_scale.targets[0].id_type = 'CAMERA'
        cam_ortho_scale.targets[0].id = bpy.data.cameras[camera.name]
        cam_ortho_scale.targets[0].data_path = 'ortho_scale'
        resolution_x = driver.variables.new()
        resolution_x.name = 'r_x'
        resolution_x.type = 'SINGLE_PROP'
        resolution_x.targets[0].id_type = 'SCENE'
        resolution_x.targets[0].id = bpy.context.scene
        resolution_x.targets[0].data_path = 'render.resolution_x'
        resolution_y = driver.variables.new()
        resolution_y.name = 'r_y'
        resolution_y.type = 'SINGLE_PROP'
        resolution_y.targets[0].id_type = 'SCENE'
        resolution_y.targets[0].id = bpy.context.scene
        resolution_y.targets[0].data_path = 'render.resolution_y'
    
    #setup X scale for bake object and plane
    driver = object_to_bake.driver_add('scale',0).driver
    driver.type = 'SCRIPTED'
    setup_driver_variables(driver, camera)
    driver.expression = "((r_x)/(r_y)*(cOS)) if (((r_x)/(r_y)) < 1) else (cOS)"

    driver = fillerplane.driver_add('scale',0).driver
    driver.type = 'SCRIPTED'
    setup_driver_variables(driver, camera)
    driver.expression = "((r_x)/(r_y)*(cOS)) if (((r_x)/(r_y)) < 1) else (cOS)"

    #setup drivers for object's Y scale
    driver = object_to_bake.driver_add('scale',1).driver
    driver.type = 'SCRIPTED'
    setup_driver_variables(driver, camera)
    driver.expression = "((r_y)/(r_x)*(cOS)) if (((r_y)/(r_x)) < 1) else (cOS)"

    driver = fillerplane.driver_add('scale',1).driver
    driver.type = 'SCRIPTED'
    setup_driver_variables(driver, camera)
    driver.expression = "((r_y)/(r_x)*(cOS)) if (((r_y)/(r_x)) < 1) else (cOS)"

    ###########################
    #give the object a geometry node modifier
    geonodes = object_to_bake.modifiers.new('Flattener', 'NODES')

    #import the premade flattener node to unwrap the mesh into the UV structure
    script_dir=Path(__file__).parent
    template_path=(script_dir / '../KK Shader V5.0.blend').resolve()
    filepath = str(template_path)
    innerpath = 'NodeTree'
    node = 'Flatten to UV map'
    bpy.ops.wm.append(
            filepath=os.path.join(filepath, innerpath, node),
            directory=os.path.join(filepath, innerpath),
            filename=node
            )
    
    #place group
    nodes = bpy.data.node_groups['Geometry Nodes'].nodes
    group = nodes.new('GeometryNodeGroup')
    group.node_tree = bpy.data.node_groups['Flatten to UV map']

    #connect group and make new input
    links = bpy.data.node_groups['Geometry Nodes'].links
    links.new(group.outputs[0], nodes['Group Output'].inputs[0])
    links.new(nodes['Group Input'].outputs[0], group.inputs[0])

    #connect new input to group
    bpy.data.node_groups['Geometry Nodes'].inputs.new('NodeSocketVector', 'UVMap input')
    links.new(nodes['Group Input'].outputs[1], group.inputs[1])
    identifier = geonodes.node_group.inputs[1].identifier
    geonodes[identifier+'_attribute_name'] = 'uv_main'
    geonodes[identifier+'_use_attribute'] = True

    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake

##############################
#Changes the material of the image plane to the material of the object,
# and then puts a render of the image plane into the specified folder

def sanitizeMaterialName(text):
    for ch in ['\\','`','*','<','>','.',':','?','|','/','\"']:
        if ch in text:
            text = text.replace(ch,'')
    return text

def bake_pass(resolutionMultiplier, directory, bake_type, sun_strength):
    exportType = 'PNG'
    exportColormode = 'RGBA'
    #get the most recently created light object
    sun = bpy.data.lights[len(bpy.data.lights)-1]
    #make sure shadows are turned off
    sun.use_shadow = False
    #set the sun strength
    sun.energy = sun_strength
    #print('the sun is ' + str(bake_type) + ' at ' + str(sun_strength))
    #preserve the filepath
    folderpath = directory
    #get the currently selected object as the active object
    object_to_bake = bpy.context.active_object
    #remember what order the materials are in for later
    original_material_order = []
    for matslot in object_to_bake.material_slots:
        original_material_order.append(matslot.name)
    #get the filler plane
    fillerplane = bpy.data.objects['fillerplane']
    #go through each material slot
    for currentmaterial in object_to_bake.data.materials:
        nodes = currentmaterial.node_tree.nodes
        links = currentmaterial.node_tree.links

        print(currentmaterial)

        #Don't bake this material if it's an outline material
        if 'Outline ' in currentmaterial.name or 'Template Outline' in currentmaterial.name or 'Template Body Outline' in currentmaterial.name:
            continue

        #Don't bake this material if the material already has the atlas nodes loaded in and the mix shader is set to 1
        if currentmaterial.node_tree.nodes.get('KK Mix'):
            if currentmaterial.node_tree.nodes['KK Mix'].inputs[0].default_value > 0.5:
                continue
        
        #Turn off the normals for the raw shading node group input if this isn't a normal pass
        if nodes.get('RawShade') and bake_type != 'normal':
            original_normal_state = nodes['RawShade'].inputs[1].default_value
            nodes['RawShade'].inputs[1].default_value = 1
        
        #if this is a normal pass, attach the normal passthrough to the output before baking
        if nodes.get('RawShade') and bake_type == 'normal':
            getOut = nodes['Material Output'].inputs[0].links[0]
            currentmaterial.node_tree.links.remove(getOut)
            links.new(nodes['RawShade'].outputs[1], nodes['Material Output'].inputs[0])

        rendered_something = False

        if nodes.get('Gentex'):
            #Go through each of the textures loaded into the Gentex group and get the highest resolution one
            highest_resolution = [0,0]
            for image_node in nodes['Gentex'].node_tree.nodes:
                if image_node.type == 'TEX_IMAGE' and image_node.image:
                    image_size = image_node.image.size[0] * image_node.image.size[1]
                    largest_so_far = highest_resolution[0] * highest_resolution[1]
                    if image_size > largest_so_far:
                        highest_resolution = [image_node.image.size[0], image_node.image.size[1]]
            
            #Render an image using the highest dimensions
            if highest_resolution != [0,0]:
                dimension = str(highest_resolution[0])+'x'+str(highest_resolution[1])
                bpy.context.scene.render.resolution_x=highest_resolution[0] * resolutionMultiplier
                bpy.context.scene.render.resolution_y=highest_resolution[1] * resolutionMultiplier

                #set every material slot except the current material to be transparent
                for matslot in object_to_bake.material_slots:
                    if matslot.material != currentmaterial:
                        matslot.material = bpy.data.materials['Template Eyeline down']
                
                #set the filler plane to the current material
                fillerplane.material_slots[0].material = currentmaterial

                #then render it
                bpy.context.scene.render.filepath = folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + bake_type
                bpy.context.scene.render.image_settings.file_format=exportType
                bpy.context.scene.render.image_settings.color_mode=exportColormode
                #bpy.context.scene.render.image_settings.color_depth='16'
                
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                print('rendering this file:' + bpy.context.scene.render.filepath)
                bpy.ops.render.render(write_still = True)
                
                #reset folderpath after render
                bpy.context.scene.render.filepath = folderpath

                rendered_something = True

                #redraw the UI to let the user know the plugin is doing something
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        #If no images were detected in a Gentex group, render a very small (64px) failsafe image
        #this will let the script catch fully transparent materials or materials that are solid colors without textures
        if not rendered_something:
            bpy.context.scene.render.resolution_x=64
            bpy.context.scene.render.resolution_y=64
            
            #set every material slot except the current material to be transparent
            for matslot in object_to_bake.material_slots:
                if matslot.material != currentmaterial:
                    #print("changed {} to {}".format(matslot.material, currentmaterial))
                    matslot.material = bpy.data.materials['Template Eyeline down']

            #set the filler plane to the current material
            fillerplane.material_slots[0].material = currentmaterial

            #then render it
            bpy.context.scene.render.filepath = folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + bake_type
            bpy.context.scene.render.image_settings.file_format=exportType
            bpy.context.scene.render.image_settings.color_mode=exportColormode
            #bpy.context.scene.render.image_settings.color_depth='16'
            
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            print('rendering this file:' + bpy.context.scene.render.filepath)
            bpy.ops.render.render(write_still = True)
            #print(fillerplane.data.materials[0])
            
            #reset folderpath after render
            bpy.context.scene.render.filepath = folderpath
        
        #Restore the value in the raw shading node group for the normals
        if currentmaterial.node_tree.nodes.get('RawShade') and bake_type != 'normal':
            currentmaterial.node_tree.nodes['RawShade'].inputs[1].default_value = original_normal_state
        
        #Restore the links if they were edited for the normal pass
        if currentmaterial.node_tree.nodes.get('RawShade') and bake_type == 'normal':
            getOut = nodes['Material Output'].inputs[0].links[0]
            currentmaterial.node_tree.links.remove(getOut)
            if nodes.get('KK Mix'):
                links.new(nodes['KK Mix'].outputs[0], nodes['Material Output'].inputs[0])
            else:
                links.new(nodes['Rim'].outputs[0], nodes['Material Output'].inputs[0])
        #reset material slots
        for material_index in range(len(original_material_order)):
            object_to_bake.material_slots[material_index].material = bpy.data.materials[original_material_order[material_index]]

def start_baking(folderpath, resolutionMultiplier):
    #enable transparency
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.filter_size = 0.50
    
    object_to_bake = bpy.context.active_object
    #Purge unused lights
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)

    #Make a new sun object
    bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=(0, 0, 0))

    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake

    #remove the outline materials because they won't be baked
    bpy.ops.object.material_slot_remove_unused()

    #bake the light versions of each material to the selected folder at sun intensity 5
    bake_pass(resolutionMultiplier, folderpath, 'light' , 5)
    
    #bake the dark versions of each material at sun intensity 0
    bake_pass(resolutionMultiplier, folderpath, 'dark' , 0)
    
    #bake the normal maps
    bake_pass(resolutionMultiplier, folderpath, 'normal' , 0)

    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake

def cleanup():
    #save the originally selected object
    object_to_bake = bpy.context.active_object
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    #Select the sun
    sun = [o for o in bpy.data.objects if o.type == 'LIGHT'][0]
    sun.select_set(True)
    #Select the camera
    camera = [o for o in bpy.data.objects if o.type == 'CAMERA'][0]
    camera.select_set(True)
    #Select fillerplane
    bpy.data.objects['fillerplane'].select_set(True)
    #delete them
    bpy.ops.object.delete()
    #delete the geometry modifier
    object_to_bake.modifiers.remove(object_to_bake.modifiers['Flattener'])
    bpy.data.node_groups.remove(bpy.data.node_groups['Geometry Nodes'])
    #delete the two scale drivers
    object_to_bake.animation_data.drivers.remove(object_to_bake.animation_data.drivers[0])
    object_to_bake.animation_data.drivers.remove(object_to_bake.animation_data.drivers[0])
    object_to_bake.scale = (1,1,1)
    #disable alpha on the output
    bpy.context.scene.render.film_transparent = False
    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake
    bpy.context.scene.render.filter_size = 1.5

class bake_materials(bpy.types.Operator):
    bl_idname = "kkb.bakematerials"
    bl_label = "Store images here"
    bl_description = "Open the folder you want to bake the material templates to"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context):
        try:
            print(self.directory)
            folderpath =  self.directory
            scene = context.scene.kkbp
            resolutionMultiplier = scene.inc_dec_int
            camera = setup_camera()
            if camera == None:
                return {'FINISHED'}
            setup_geometry_nodes_and_fillerplane(camera)
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            start_baking(folderpath, resolutionMultiplier)
            cleanup()
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
    bpy.utils.register_class(bake_materials)

    # test call
    print((bpy.ops.kkb.bakematerials('INVOKE_DEFAULT')))
