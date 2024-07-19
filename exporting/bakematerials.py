'''
BAKE MATERIAL TO TEXTURE SCRIPT
- Bakes all materials of an object into image textures (to use in other programs)
- Will only bake a material if an image node is present in the green texture group
- If no image is present, a low resolution failsafe image will be baked to account for fully opaque or transparent materials that don't rely on texture files
- If multiple image files are present, only one texture will be created
    - If the multiple image files have different resolutions, a texture will be created for each resolution
- Export defaults to 8-bit PNG with an alpha channel.
--    Defaults can be changed by editing the exportType and exportColormode variables below.

Notes:
- This script deletes all camera objects in the scene
- fillerplane driver + shader code taken from https://blenderartists.org/t/scripts-create-camera-image-plane/580839
'''

import bpy, os, traceback, time, pathlib, numpy, mathutils, bmesh
from .. import common as c
from . import rpack

from ..interface.dictionary_en import t

def showError(self, context):
    self.layout.label(text="No object selected (make sure the body object is selected)")

def typeError(self, context):
    self.layout.label(text="The object to bake must be a mesh object (make sure the body object is selected)")

#setup and return a camera
def setup_camera():
    #Delete all cameras in the scene
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            obj.select_set(True)
        else:
            obj.select_set(False)
    bpy.ops.object.delete()
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
   
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
    # print(object_to_bake)
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
    #import the premade flattener node to unwrap the mesh into the UV structure
    script_dir=pathlib.Path(__file__).parent
    template_path=(script_dir / '../KK Shader V6.6.blend').resolve()
    filepath = str(template_path)
    innerpath = 'NodeTree'
    geonodename = 'Geometry Nodes'
    bpy.ops.wm.append(
            filepath=os.path.join(filepath, innerpath, geonodename),
            directory=os.path.join(filepath, innerpath),
            filename=geonodename
            )

    #give the object a geometry node modifier
    geonodes_mod = object_to_bake.modifiers.new('Flattener', 'NODES')
    geonodes_mod.node_group = bpy.data.node_groups['Geometry Nodes']
    identifier = [str(i) for i in geonodes_mod.keys()][0]
    geonodes_mod[identifier+'_attribute_name'] = 'uv_main'
    geonodes_mod[identifier+'_use_attribute'] = True

    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake

##############################
#Changes the material of the image plane to the material of the object,
# and then puts a render of the image plane into the specified folder

def sanitizeMaterialName(text):
    '''Mat names need to be sanitized else you can't delete the files with windows explorer'''
    for ch in ['\\','`','*','<','>','.',':','?','|','/','\"']:
        if ch in text:
            text = text.replace(ch,'')
    return text

def bake_pass(resolutionMultiplier, folderpath, bake_type):
    #get list of already baked files
    fileList = pathlib.Path(folderpath).glob('*.*')
    files = [file for file in fileList if file.is_file()]
    #print(files)
    exportType = 'PNG'
    exportColormode = 'RGBA'
    #get the currently selected object as the active object
    object_to_bake = bpy.context.active_object
    #remember what order the materials are in for later
    original_material_order = []
    for matslot in object_to_bake.material_slots:
        original_material_order.append(matslot.name)
    #get the filler plane
    fillerplane = bpy.data.objects['fillerplane']

    #if this is a light or dark pass, make sure the RawShade group is a constant light or dark
    if bake_type in ['light', 'dark']:
        raw = bpy.data.node_groups['Raw Shading']
        getOut = raw.nodes['breaknode'].inputs[6].links[0]
        raw.links.remove(getOut)
        raw.nodes['breaknode'].inputs[6].default_value = (1,1,1,1) if bake_type == 'light' else (0,0,0,1)

    #go through each material slot
    for currentmaterial in object_to_bake.data.materials:
        nodes = currentmaterial.node_tree.nodes
        links = currentmaterial.node_tree.links

        #print(currentmaterial)

        #Don't bake this material if it's an outline material
        if 'Outline ' in currentmaterial.name or 'KK Outline' in currentmaterial.name or 'KK Body Outline' in currentmaterial.name:
            continue

        #Don't bake this material if the material already has the atlas nodes loaded in and the mix shader is set to 1 and the image already exists (user is re-baking a mat)
        if currentmaterial.node_tree.nodes.get('KK Mix'):
            if currentmaterial.node_tree.nodes['KK Mix'].inputs[0].default_value > 0.5 and pathlib.Path(folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + bake_type + '.png') in files:
                continue
            else:
                currentmaterial.node_tree.nodes['KK Mix'].inputs[0].default_value = 0
        
        #Don't bake this material if the material does not have the atlas nodes loaded in yet and the image already exists (baking was interrupted)
        if not currentmaterial.node_tree.nodes.get('KK Mix') and pathlib.Path(folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + bake_type + '.png') in files:
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
                bpy.context.scene.render.resolution_x=highest_resolution[0] * resolutionMultiplier
                bpy.context.scene.render.resolution_y=highest_resolution[1] * resolutionMultiplier

                #manually set gag02 resolution
                if 'KK Gag02' in currentmaterial.name:
                    bpy.context.scene.render.resolution_x = 512 * resolutionMultiplier
                    bpy.context.scene.render.resolution_y = 512 * resolutionMultiplier

                #set every material slot except the current material to be transparent
                for matslot in object_to_bake.material_slots:
                    if matslot.material != currentmaterial:
                        matslot.material = bpy.data.materials['KK Eyeline down']
                
                #set the filler plane to the current material
                fillerplane.material_slots[0].material = currentmaterial

                #then render it
                bpy.context.scene.render.filepath = folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + bake_type
                bpy.context.scene.render.image_settings.file_format=exportType
                bpy.context.scene.render.image_settings.color_mode=exportColormode
                #bpy.context.scene.render.image_settings.color_depth='16'
                
                #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                # print('rendering this file:' + bpy.context.scene.render.filepath)
                bpy.ops.render.render(write_still = True)
                
                #reset folderpath after render
                bpy.context.scene.render.filepath = folderpath

                rendered_something = True

                #redraw the UI to let the user know the plugin is doing something
                #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        #If no images were detected in a Gentex group, render a very small (64px) failsafe image
        #this will let the script catch fully transparent materials or materials that are solid colors without textures
        if not rendered_something:
            bpy.context.scene.render.resolution_x=64
            bpy.context.scene.render.resolution_y=64
            
            #set every material slot except the current material to be transparent
            for matslot in object_to_bake.material_slots:
                if matslot.material != currentmaterial:
                    #print("changed {} to {}".format(matslot.material, currentmaterial))
                    matslot.material = bpy.data.materials['KK Eyeline down']

            #set the filler plane to the current material
            fillerplane.material_slots[0].material = currentmaterial

            #then render it
            bpy.context.scene.render.filepath = folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + bake_type
            bpy.context.scene.render.image_settings.file_format=exportType
            bpy.context.scene.render.image_settings.color_mode=exportColormode
            #bpy.context.scene.render.image_settings.color_depth='16'
            
            #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            # print('rendering failsafe for this file:' + bpy.context.scene.render.filepath)
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
    
    #reset raw shading group state
    if bake_type in ['light', 'dark']:
        raw.links.new(raw.nodes['breakreroute'].outputs[0], raw.nodes['breaknode'].inputs[6])

def start_baking(folderpath, resolutionMultiplier, light, dark, norm):
    #enable transparency
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.filter_size = 0.50
    
    object_to_bake = bpy.context.active_object
    #Purge unused lights
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)

    #Make a new sun object
    #bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=(0, 0, 0)) #no longer need the sun object

    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake

    if light:
        #bake the light versions of each material to the selected folder at sun intensity 5
        bake_pass(resolutionMultiplier, folderpath, 'light')
    
    if dark:
        #bake the dark versions of each material at sun intensity 0
        bake_pass(resolutionMultiplier, folderpath, 'dark')
    
    if norm:
        #bake the normal maps
        bake_pass(resolutionMultiplier, folderpath, 'normal')

    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake

def cleanup():
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    #Select the camera
    for camera in [o for o in bpy.data.objects if o.type == 'CAMERA']:
        bpy.data.objects.remove(camera)
    #Select fillerplane
    for fillerplane in [o for o in bpy.data.objects if 'fillerplane' in o.name]:
        bpy.data.objects.remove(fillerplane)
    #delete orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
    for ob in [obj for obj in bpy.context.view_layer.objects]:
        if ob: #getting a weird Nonetype error, so do it this way instead
            if ob.type == 'MESH':
                #delete the geometry modifier
                if ob.modifiers.get('Flattener'):
                    ob.modifiers.remove(ob.modifiers['Flattener'])
                    #delete the two scale drivers
                    ob.animation_data.drivers.remove(ob.animation_data.drivers[0])
                    ob.animation_data.drivers.remove(ob.animation_data.drivers[0])
                    ob.scale = (1,1,1)
    bpy.data.node_groups.remove(bpy.data.node_groups['Geometry Nodes'])
    #disable alpha on the output
    bpy.context.scene.render.film_transparent = False
    bpy.context.scene.render.filter_size = 1.5

def replace_all_baked_materials(folderpath):

    #load all baked images into blender
    fileList = pathlib.Path(folderpath).glob('*.*')
    files = [file for file in fileList if file.is_file()]

    for bake_type in ['light', 'dark', 'norm']:
        for mat in [m for m in bpy.data.materials if 'KK ' in m.name and 'Outline ' not in m.name and ' Outline' not in m.name]:
            image_path = pathlib.Path(folderpath + sanitizeMaterialName(mat.name) + ' ' + bake_type + '.png')
            if image_path in files:
                bpy.data.images.load(filepath=str(image_path))
                bpy.data.images[sanitizeMaterialName(mat.name) + ' ' + bake_type + '.png'].pack()
                
    #now all needed images are loaded into the file. Match each material to it's image textures
    for mat in bpy.data.materials:
        finalize_this_mat = 'KK ' in mat.name and 'Outline ' not in mat.name and ' Outline' not in mat.name
        if finalize_this_mat:
            # print('Finalizing {}'.format(mat))
            if mat.node_tree.nodes.get('baked_file'):
                if mat.node_tree.nodes['baked_file'].image:
                    if ' light.png' in mat.node_tree.nodes['baked_file'].image.name:
                        light_image = mat.node_tree.nodes['baked_file'].image.name
                        dark_image  = mat.node_tree.nodes['baked_file'].image.name.replace('light', 'dark')
                        normal_image  = mat.node_tree.nodes['baked_file'].image.name.replace('light', 'normal')
                    else:
                        dark_image = mat.node_tree.nodes['baked_file'].image.name
                        light_image  = mat.node_tree.nodes['baked_file'].image.name.replace('dark', 'light')
                        normal_image  = mat.node_tree.nodes['baked_file'].image.name.replace('dark', 'normal')
                    #mat_dict[mat.name] = [light_image, dark_image]

                    #rename material to -ORG, and replace it with a new material
                    mat.name += '-ORG' if '-ORG' not in mat.name else ''
                    try:
                        simple = bpy.data.materials['KK Simple'].copy()
                    except:
                        script_dir=pathlib.Path(__file__).parent
                        template_path=(script_dir / '../KK Shader V6.6.blend').resolve()
                        filepath = str(template_path)
                        innerpath = 'Material'
                        templateList = ['KK Simple']
                        for template in templateList:
                            bpy.ops.wm.append(
                                filepath=os.path.join(filepath, innerpath, template),
                                directory=os.path.join(filepath, innerpath),
                                filename=template,
                                set_fake=False
                                )
                        simple = bpy.data.materials['KK Simple'].copy()
                    simple.name = mat.name.replace('-ORG','')
                    new_node = simple.node_tree.nodes['Gentex'].node_tree.copy()
                    simple.node_tree.nodes['Gentex'].node_tree = new_node
                    new_node.name = simple.name
                    new_node.nodes['light'].image = bpy.data.images[light_image]
                    if bpy.data.images.get(dark_image):
                        new_node.nodes['dark'].image = bpy.data.images[dark_image]
                    if bpy.data.images.get(normal_image):
                        new_node.nodes['norm'].image = bpy.data.images[normal_image]
                    #replace instances of ORG material with new finalized one
                    mat.use_fake_user = True
                    alpha_blend_mats = [
                        'KK Nose',
                        'KK Eyebrows (mayuge)',
                        'KK Eyeline up',
                        'KK Eyeline Kage',
                        'KK Eyeline down',
                        'KK Eyewhites (sirome)',
                        'KK EyeL (hitomi)',
                        'KK EyeR (hitomi)',
                    ]
                    for obj in bpy.data.objects:
                        for mat_slot in obj.material_slots:
                            if mat_slot.name.replace('-ORG','') == simple.name:
                                mat_slot.material = simple
                                if simple.name in alpha_blend_mats:
                                    mat_slot.material.blend_method = 'BLEND'

def create_material_atlas():
    '''Merges all the finalized material png files into a single atlas file, copies the current model and applies the atlas to the copy'''

    # https://blender.stackexchange.com/questions/127403/change-active-collection
    #Recursivly transverse layer_collection for a particular name
    def recurLayerCollection(layerColl, collName):
        found = None
        if (layerColl.name == collName):
            return layerColl
        for layer in layerColl.children:
            found = recurLayerCollection(layer, collName)
            if found:
                return found
    
    def remove_orphan_data():
        #delete orphan data
        for cat in [bpy.data.armatures, bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.node_groups]:
            for block in cat:
                if block.users == 0:
                    cat.remove(block)
        #revert the image back from the atlas file to the baked file   
        for mat in bpy.data.materials:
            if mat.name[-4:] == '-ORG':
                simplified_name = mat.name[:-4]
                simplified_mat = bpy.data.materials[simplified_name]
                for bake_type in ['light', 'dark', 'norm']:
                    simplified_mat.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image = bpy.data.images.get(simplified_name + ' ' + bake_type + '.png')

    #TODO delete collection and materials if already exists and recreate fresh each time
    if bpy.data.collections.get('Model with atlas'):
        print('deleting previous collection "Model with atlas" and regenerating atlas model...')
        def del_collection(coll):
            for c in coll.children:
                del_collection(c)
            bpy.data.collections.remove(coll,do_unlink=True)
        del_collection(bpy.data.collections["Model with atlas"])
        remove_orphan_data()
        #show the original collection again
        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection, 'Scene Collection')
        bpy.context.view_layer.active_layer_collection = layerColl
        bpy.context.scene.view_layers[0].active_layer_collection.children[0].exclude = False

    #Change the Active LayerCollection to 'My Collection'
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection, 'Collection')
    bpy.context.view_layer.active_layer_collection = layerColl

    # https://blender.stackexchange.com/questions/157828/how-to-duplicate-a-certain-collection-using-python
    from collections import  defaultdict
    def copy_objects(from_col, to_col, linked, dupe_lut):
        for o in from_col.objects:
            dupe = o.copy()
            if not linked and o.data:
                dupe.data = dupe.data.copy()
            to_col.objects.link(dupe)
            dupe_lut[o] = dupe
    def copy(parent, collection, linked=False):
        dupe_lut = defaultdict(lambda : None)
        def _copy(parent, collection, linked=False):
            cc = bpy.data.collections.new(collection.name)
            copy_objects(collection, cc, linked, dupe_lut)
            for c in collection.children:
                _copy(cc, c, linked)
            parent.children.link(cc)
        _copy(parent, collection, linked)
        # print(dupe_lut)
        for o, dupe in tuple(dupe_lut.items()):
            parent = dupe_lut[o.parent]
            if parent:
                dupe.parent = parent
    context = bpy.context
    scene = context.scene
    col = context.collection
    # print(col, scene.collection)
    assert(col is not scene.collection)
    copy(scene.collection, col)

    def update_uvs(object_name, material_name, x, y, type = '+'):
        object = bpy.data.objects[object_name]
        c.switch(object, 'EDIT')
        object.active_material_index = object.data.materials.find(material_name)
        bpy.ops.object.material_slot_select()
        me = object.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.verify()
        # adjust uv coordinates
        for face in bm.faces:
            for loop in face.loops:
                if loop.vert.select:
                    loop_uv = loop[uv_layer]
                    if type == '+':
                        loop_uv.uv[0] += x
                        loop_uv.uv[1] += y
                    elif type == '*':
                        loop_uv.uv[0] *= x
                        loop_uv.uv[1] *= y
                    elif type == '/':
                        loop_uv.uv[0] /= x
                        loop_uv.uv[1] /= y
                    elif type == '-':
                        loop_uv.uv[0] -= x
                        loop_uv.uv[1] -= y
        bmesh.update_edit_mesh(me)
        c.switch(object, 'OBJECT')
    
    def get_max_min_uvs(object_name, material_name):
        object = bpy.data.objects[object_name]
        c.switch(object, 'EDIT')
        bpy.context.object.active_material_index = object.data.materials.find(material_name)
        bpy.ops.object.material_slot_select()
        bm = bmesh.from_edit_mesh(object.data)
        uv_layer = bm.loops.layers.uv.verify()
        x_max_uv = 0
        y_max_uv = 0
        x_min_uv = 0
        y_min_uv = 0
        for face in bm.faces:
            for loop in face.loops:
                if loop.vert.select:
                    loop_uv = loop[uv_layer]
                    x_max_uv = loop_uv.uv[0] if x_max_uv < loop_uv.uv[0] else x_max_uv
                    y_max_uv = loop_uv.uv[1] if y_max_uv < loop_uv.uv[1] else y_max_uv
                    x_min_uv = loop_uv.uv[0] if x_min_uv > loop_uv.uv[0] else x_min_uv
                    y_min_uv = loop_uv.uv[1] if y_min_uv > loop_uv.uv[1] else y_min_uv
        c.switch(object, 'OBJECT')
        return  x_max_uv, y_max_uv, x_min_uv, y_min_uv

    #first correct the tongue uv locations because easily fixable for every model
    update_uvs('Body.001', 'KK Tongue', 0, 1, '+')

    for object in [o for o in bpy.data.objects if (bpy.data.collections['Collection.001'] in o.users_collection and o.type == 'MESH')]:
        x_total_length = 0
        y_max_length = 0
        for mat_slot in [m for m in object.material_slots if ('KK ' in m.name and 'Outline ' not in m.name and ' Outline' not in m.name)]:
            material = mat_slot.material
            #TODO do something to create two atlases for the body
            
            print('')
            print(material)
            for bake_type in ['light', 'dark', 'norm']:
                try:
                    image = material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image
                    break
                except:
                    # print('no baked1')
                    image = None
            if not image:
                print('no image found for {} skipping'.format(material.name))
                continue
            else:
                print('found image for {}'.format(material.name))
            #some uvs are absolutely fucked. The baked image will need to grow to expand to whatever the UV limits go to if they are higher than 1.
            x_max_uv, y_max_uv, x_min_uv, y_min_uv = get_max_min_uvs(object.name, material.name)
            #if any uvs are less than 0, shift everything to at least 0, 0
            if x_min_uv < 0 or y_min_uv < 0:
                print('fixing negative uv irregularities {}'.format(bake_type))
                #do this for all three images
                uv_shift_flag = True
                for bake_type in ['light', 'dark', 'norm']:
                    image = material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image
                    if not image:
                        print('no image for {} {}'.format(material.name, bake_type))
                        continue
                    if uv_shift_flag:
                        print('shifting uvs for {} {}'.format(material.name, bake_type))
                        update_uvs(object.name, material.name, x_min_uv, y_min_uv, '-')
                    else:
                        print('NOT shifting uvs for {} {}'.format(material.name, bake_type))
                    #pad left and bottom
                    x_new_length = int(image.size[0] - x_min_uv * image.size[0])
                    y_new_length = int(image.size[1] - y_min_uv * image.size[1])
                    #make sure dimensions are divisble by 2
                    if x_new_length % 2:
                        x_new_length +=1
                    if y_new_length % 2:
                        y_new_length +=1
                    #also scale the uvs to the new length
                    if uv_shift_flag:
                        print('shifting uvs for {} {}'.format(material.name, bake_type))
                        update_uvs(object.name, material.name, image.size[0]/x_new_length, image.size[1]/y_new_length, '*')
                    else:
                        print('NOT shifting uvs for {} {}'.format(material.name, bake_type))
                    #get the pixels of the current image, then create the padding needed
                    new_image_pixels = numpy.reshape(image.pixels, (-1, image.size[0] * 4))
                    x_current_dimension = image.size[0]
                    y_current_dimension = image.size[1]
                    vertical_padding = list(numpy.zeros((y_new_length - y_current_dimension) * x_current_dimension * 4))
                    vertical_padding = numpy.reshape(vertical_padding, (-1, x_current_dimension * 4))
                    new_image_pixels = numpy.vstack((vertical_padding, new_image_pixels)) #put padding before image to appear on the bottom
                    #create the horizontal padding needed
                    x_current_dimension = image.size[0]
                    y_current_dimension = y_new_length
                    horizontal_padding = list(numpy.zeros((y_current_dimension) * (x_new_length - x_current_dimension) * 4))
                    horizontal_padding = numpy.reshape(horizontal_padding, (y_current_dimension, -1))
                    new_image_pixels = numpy.hstack((horizontal_padding, new_image_pixels)) #put padding before image to appear on the left
                    x_current_dimension = x_new_length
                    new_image = bpy.data.images.new(image.name.replace('.png', 'n.png'), x_current_dimension, y_current_dimension)
                    new_image.pixels = new_image_pixels.flatten()
                    material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image = new_image
                    uv_shift_flag = False
            #try looking at the positive uvs now
            if x_max_uv > 1 or y_max_uv > 1:
                #do this for all three images
                uv_shift_flag = True
                for bake_type in ['light', 'dark', 'norm']:
                    print('fixing positive uv irregularities {}'.format(bake_type))
                    image = material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image
                    if not image:
                        print('no image for {} {}'.format(material.name, bake_type))
                        continue
                    if uv_shift_flag:
                        print('shifting uvs for {} {}'.format(material.name, bake_type))
                        update_uvs(object.name, material.name, x_max_uv if x_max_uv > 1 else 1, y_max_uv if y_max_uv > 1 else 1, '/')
                    else:
                        print('NOT shifting uvs for {} {}'.format(material.name, bake_type))
                    #get the pixels of the current image, then create the padding needed
                    new_image_pixels = numpy.reshape(image.pixels, (-1, image.size[0] * 4))
                    x_new_length = int(image.size[0] * (x_max_uv if x_max_uv > 1 else 1))
                    y_new_length = int(image.size[1] * (y_max_uv if y_max_uv > 1 else 1))
                    #make sure dimensions are divisble by 2
                    if x_new_length % 2:
                        x_new_length +=1
                    if y_new_length % 2:
                        y_new_length +=1
                    x_current_dimension = image.size[0]
                    y_current_dimension = image.size[1]
                    #create the vertical padding needed
                    vertical_padding = list(numpy.zeros((y_new_length - y_current_dimension) * x_current_dimension * 4))
                    vertical_padding = numpy.reshape(vertical_padding, (-1, x_current_dimension * 4))
                    new_image_pixels = numpy.vstack((new_image_pixels, vertical_padding))
                    #create the horizontal padding needed
                    x_current_dimension = image.size[0]
                    y_current_dimension = y_new_length
                    if x_new_length > x_current_dimension:
                        horizontal_padding = list(numpy.zeros((y_current_dimension) * (x_new_length - x_current_dimension) * 4))
                        horizontal_padding = numpy.reshape(horizontal_padding, (-1, (x_new_length - x_current_dimension) * 4))
                        new_image_pixels = numpy.hstack((new_image_pixels, horizontal_padding))
                        x_current_dimension = x_new_length
                    new_image = bpy.data.images.new(image.name.replace('.png', 'p.png'), x_current_dimension, y_current_dimension)
                    new_image.pixels = new_image_pixels.flatten()
                    material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image = new_image
                    uv_shift_flag = False
            
            for bake_type in ['light', 'dark', 'norm']:
                try:
                    image = material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image
                    break
                except:
                    # print('no baked1')
                    image = None
            #get the image length
            x_length = image.size[0]
            x_total_length += x_length
            y_length = image.size[1]
            y_max_length = y_length if y_length > y_max_length else y_max_length

        #skip if this object had no images to atlas
        if y_max_length == 0:
            print('no max length for {}'.format(object.name))
            continue

        #give each image an index before stacking them
        uv_shift_flag = True
        for bake_type in ['light', 'dark', 'norm']:
            indexed_images = {}
            for mat_slot in [m for m in object.material_slots if ('KK ' in m.name and 'Outline ' not in m.name and ' Outline' not in m.name)]:
                material = mat_slot.material
                # print(material)
                try:
                    image = material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image
                except:
                    # print('no baked2')
                    image = None
                if not image:
                    continue
                indexed_images[image.name] = [object.name, material.name]

            #use rectangle-packer to find the best locations for each image, then store it into the indexed dict
            print('{}, {}'.format(bake_type, indexed_images))
            if not indexed_images:
                print('No images found for ' + bake_type)
                continue
            sizes = []
            for image_name in indexed_images:
                image = bpy.data.images[image_name]
                sizes.append((image.size[0] * 4, image.size[1]))
            positions = rpack.pack(sizes)
            for index, image_name in enumerate(indexed_images):
                # print(image_name)
                indexed_images[image_name].append(positions[index])

            #create a new numpy array the size of the bounding box
            bounding_box = rpack.bbox_size(sizes, positions)
            atlas_array = numpy.zeros(bounding_box[0] * bounding_box[1])
            atlas_array = numpy.reshape(atlas_array, (-1, bounding_box[0]))

            #insert each individual image into the final image at the correct coordinates
            for index, image_name in enumerate(indexed_images):
                image = bpy.data.images[image_name]
                reshaped_pixels = numpy.reshape(image.pixels, (-1, image.size[0] * 4))
                # print(image)
                a1,a0=indexed_images[image_name][2]
                atlas_array[a0:a0+reshaped_pixels.shape[0],a1:a1+reshaped_pixels.shape[1]] = reshaped_pixels

            atlas = bpy.data.images.new('{} Atlas {}'.format(object.name, bake_type), int(atlas_array.shape[1]/4), atlas_array.shape[0])
            atlas.pixels = atlas_array.flatten()
            
            #replace all images with the atlas
            for mat_slot in [m for m in object.material_slots if ('KK ' in m.name and 'Outline ' not in m.name and ' Outline' not in m.name)]:
                material = mat_slot.material
                # print(material)
                try:
                    image = material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image
                except:
                    # print('no baked3')
                    image = None
                if not image:
                    continue
                else:
                    mat_slot.material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image = bpy.data.images['{} Atlas {}'.format(object.name, bake_type)]

            #scale and translate all of the uvs based on the image's index and dimensions
            if uv_shift_flag:
                for index, image_name in enumerate(indexed_images):
                    object_name = indexed_images[image_name][0]
                    material_name = indexed_images[image_name][1]
                    image = bpy.data.images[image_name]
                    #scale the uvs to bring them to the atlas scale
                    x_length = image.size[0]
                    y_length = image.size[1]
                    x_scale = x_length / atlas.size[0]
                    y_scale = y_length / atlas.size[1]
                    update_uvs(object_name, material_name, x_scale, y_scale, '*')
                    #now that the uvs are in atlas scale, move them around if they need to
                    x_location = (indexed_images[image_name][2][0] / 4) / atlas.size[0]
                    y_location = indexed_images[image_name][2][1] / atlas.size[1]
                    update_uvs(object_name, material_name, x_location, y_location, '+')
            uv_shift_flag = False

    #rename the new collection and hide original
    bpy.data.collections['Collection.001'].name = 'Model with atlas'
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection, 'Scene Collection')
    bpy.context.view_layer.active_layer_collection = layerColl
    bpy.context.scene.view_layers[0].active_layer_collection.children[0].exclude = True

class bake_materials(bpy.types.Operator):
    bl_idname = "kkbp.bakematerials"
    bl_label = "Bake and generate atlased model"
    bl_description = t('bake_mats_tt')
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        try:
            #just use the pmx folder for the baked files
            scene = context.scene.kkbp
            folderpath = os.path.join(context.scene.kkbp.import_dir, 'baked_files', '')
            last_step = time.time()
            c.toggle_console()
            c.kklog('Switching to EEVEE for material baking...')
            bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'
            bpy.ops.object.mode_set(mode='OBJECT')

            #set viewport shading to solid for better performance
            my_areas = bpy.context.workspace.screens[0].areas
            my_shading = 'SOLID'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading
            #reset LBS node group to "Rim: None" if used
            for mat in bpy.data.materials:
                if mat.node_tree:
                    if mat.node_tree.nodes.get('Rim') and mat.node_tree.nodes.get('LBS'):
                        if mat.node_tree.nodes['Rim'].node_tree == bpy.data.node_groups['LBS']:
                            mat.node_tree.nodes['Rim'].node_tree = bpy.data.node_groups['Rim: None']
                            links = mat.node_tree.links
                            links.new(mat.node_tree.nodes['Shader'].outputs[0], mat.node_tree.nodes['Rim'].inputs[0]) #connect color out to rim input

            resolutionMultiplier = scene.bake_mult
            for ob in [obj for obj in bpy.context.view_layer.objects if obj.type == 'MESH']:
                camera = setup_camera()
                if camera == None:
                    return {'FINISHED'}
                for obj in [obj for obj in bpy.context.view_layer.objects if obj != ob]:
                    obj.hide_render = True
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = ob
                ob.select_set(True)
                setup_geometry_nodes_and_fillerplane(camera)
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                #remove the object itself for the old baking system
                if bpy.context.scene.kkbp.old_bake_bool:
                    ob.hide_render = True
                    ob.hide_viewport = True
                start_baking(folderpath, resolutionMultiplier, scene.bake_light_bool, scene.bake_dark_bool, scene.bake_norm_bool)
                for obj in bpy.context.view_layer.objects:
                    obj.hide_render = False
                    ob.hide_viewport = False
                cleanup()
            replace_all_baked_materials(folderpath)
            create_material_atlas()
            c.toggle_console()

            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            #reset viewport shading back to material preview
            my_areas = bpy.context.workspace.screens[0].areas
            my_shading = 'SOLID'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading 
            return {'FINISHED'}
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            #reset viewport shading back to solid
            my_areas = bpy.context.workspace.screens[0].areas
            my_shading = 'SOLID'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading 
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(bake_materials)

    # test call
    print((bpy.ops.kkbp.bakematerials('INVOKE_DEFAULT')))
