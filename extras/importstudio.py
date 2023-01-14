import bpy, os
from pathlib import Path
from bpy.props import StringProperty
from ..importing.importcolors import load_luts, image_to_KK
from ..importing.darkcolors import create_darktex

def import_studio_objects(directory):
    #Stop if no files were detected
    def fileError(self, context):
        self.layout.label(text="No fbx files were detected in the folder you selected (including subfolders)")
    
    #Stop if no custom studio node group was detected
    def nodeError(self, context):
        self.layout.label(text="You need a node group named \"Custom_studio\" with at least three inputs and one output to use the Custom shader.")
        self.layout.label(text="Input 1: Maintex || Input 2: Image Alpha || Input 3: Normal || Input 4 (optional): Detailmask || Input 5 (optional): Colormask")
    
    #Stop if the KK shader was not detected
    def kkError(self, context):
        self.layout.label(text="You need to append the KK Shader from the KK Shader.blend file to use this shader.")
        self.layout.label(text="Go to File > Append > choose the KK shader.blend > go into the materials folder > choose \"KK General\" ")
    
    scene = bpy.context.scene.kkbp
    shader_type = scene.dropdown_box 
    shadow_type = scene.shadows_dropdown 
    blend_type = scene.blend_dropdown 
    use_lut = scene.studio_lut_bool
    
    #shader_dict = {"A": "principled", "B": "emission", "C": "kkshader", "D": "custom"}
    shadow_dict = {"A": "NONE", "B": "OPAQUE", "C": "CLIP", "D": "HASHED"}
    blend_dict = {"A": "OPAQUE", "B": "CLIP", "C": "HASHED", "D": "BLEND"}

    path = Path(directory).rglob('*')
    fbx_list = []
    image_list = []
    for item in path:
        if '.fbx' in str(item):
            fbx_list.append(item)
        if '.dds' in str(item) or '.tga' in str(item):
            image_list.append(item)
    
    #attempt to detect detail masks, color masks and main tex files from the selected folder/subfolders
    #normal map will always be attached on import if it's present

    conversion_image_list = []
    for image in image_list:
        if '_md-DXT' in str(image):
            detected_detailmask = image.name
        if '_mc-DXT' in str(image):
            detected_colormask = image.name
        if '_t-DXT' in str(image):
            detected_maintex = image.name
        
        #pack certain images for later
        if '_md-DXT' in str(image) or '_mc-DXT' in str(image) or '_t-DXT' in str(image):
            bpy.ops.image.open(filepath=str(image), use_udim_detecting=False)
            bpy.data.images[image.name].pack()
        
        #save the images in this directory for later
        conversion_image_list.append(image.name)

    if len(fbx_list) == 0:
        bpy.context.window_manager.popup_menu(fileError, title="Error", icon='ERROR')
        return
    
    #get the images currently loaded into the file
    already_loaded_images = [image.name for image in bpy.data.images]

    for fbx in fbx_list:
        bpy.ops.import_scene.fbx(filepath=str(fbx))
        bpy.ops.object.mode_set(mode='OBJECT')
        for object in bpy.context.selected_objects:
            if object.type == 'ARMATURE':
                object.scale = [1, 1, 1]
                if len(object.data.bones) == 1:
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                    bpy.data.objects.remove(object)
                    
            elif object.type == 'MESH':
                #set scale and rename the first UV map
                object.scale = [1, 1, 1]
                if object.data.uv_layers[0]:
                    object.data.uv_layers[0].name = 'UVMap'
                
                for material_slot in object.material_slots:
                    material = material_slot.material
                    nodes = material.node_tree.nodes
                    
                    material.use_backface_culling = True
                    material.show_transparent_back = False
                    material.blend_method = blend_dict[blend_type]
                    material.shadow_method = shadow_dict[shadow_type]
                    
                    #rename all principled BSDF nodes to 'Principled BSDF' just in case
                    for node in nodes:
                        if node.type == 'BSDF_PRINCIPLED':
                            node.name = 'Principled BSDF'
                    
                    #rename all Material Output nodes to 'Material Output' just in case
                    for node in nodes:
                        if node.type == 'OUTPUT_MATERIAL':
                            node.name = 'Material Output'

                    #Remove duplicate images if they exist
                    for node in nodes:
                        if node.type == 'TEX_IMAGE':
                            (base, sep, ext) = node.image.name.rpartition('.')
                            if ext.isnumeric():
                                if bpy.data.images.get(base):
                                    node.image = bpy.data.images.get(base)
                                    #print("replaced {} with {}".format(node.image.name, base_name + filetype))

                    #DDS files need to be converted to pngs or tgas or the color conversion scripts won't work
                    #also set images to srgb
                    for node in nodes:
                        if node.type == 'TEX_IMAGE':
                            bpy.data.images[node.image.name].colorspace_settings.name = 'sRGB'
                            image = bpy.data.images[node.image.name]
                            print(already_loaded_images)
                            print(image.name.replace('.dds', '.png'))
                            if ('.dds' in image.name or '.DDS' in image.name) and image.name.replace('.dds', '.png') not in already_loaded_images:
                                new_path = image.filepath.replace(".dds", ".png").replace(".DDS", ".png")
                                new_image_name = image.name.replace(".dds", ".png").replace(".DDS", ".png")
                                image.save_render(bpy.path.abspath(new_path))
                                bpy.ops.image.open(filepath=bpy.path.abspath(new_path), use_udim_detecting=False)
                                bpy.data.images[new_image_name].pack()
                                node.image = bpy.data.images[new_image_name]

                    #if two objects have the same material, and the material was already operated on, skip it
                    if nodes.get('Principled BSDF') == None:
                        continue
                    
                    emission_input = 19 if bpy.app.version[0] > 2 else 17
                    metallic_input = 6 if bpy.app.version[0] > 2 else 4
                    normal_input = 22 if bpy.app.version[0] > 2 else 20
                    alpha_input = 21 if bpy.app.version[0] > 2 else 19

                    #standardize dist and subsurf because the number of nodes on the principled bsdf changes with these choices
                    nodes['Principled BSDF'].distribution = 'GGX'
                    nodes['Principled BSDF'].subsurface_method = 'RANDOM_WALK'

                    #set emission to black
                    nodes['Principled BSDF'].inputs[emission_input].default_value = (0, 0, 0, 1)

                    #set metallic value to zero
                    nodes['Principled BSDF'].inputs[metallic_input].default_value = 0.0
                    
                    try:
                        image_alpha = nodes['Principled BSDF'].inputs[alpha_input].links[0].from_node
                    except:
                        #there was no image attached to the alpha node
                        image_alpha = 'noalpha'
                    
                    try:
                        image = nodes['Principled BSDF'].inputs[0].links[0].from_node
                    except:
                        image = 'noimage'
                    
                    if image_alpha != 'noalpha':
                        material.node_tree.links.new(image_alpha.outputs[1], nodes['Principled BSDF'].inputs[alpha_input])
                    
                    #if set to emission
                    if shader_type == 'B': 
                        nodes.remove(nodes['Principled BSDF'])
                        output_node = nodes['Material Output']
                        transparency_mix = nodes.new('ShaderNodeMixShader')
                        transparency_mix.location = output_node.location[0], output_node.location[1] - 300
                        transparency_node = nodes.new('ShaderNodeBsdfTransparent')
                        transparency_node.location = transparency_mix.location[0] - 300, transparency_mix.location[1]
                        emissive_node = nodes.new('ShaderNodeEmission')
                        emissive_node.location = transparency_node.location[0], transparency_node.location[1] + 300
                        output_node.location = transparency_mix.location[0] + 300, transparency_mix.location[1]
                        
                        if image != 'noimage':
                            material.node_tree.links.new(image.outputs[0], emissive_node.inputs[0])
                        else:
                            #if there's no image, try falling back to the colormask
                            try:
                                color_node = nodes.new('ShaderNodeTexImage')
                                color_node.image = bpy.data.images[detected_colormask]
                                color_node.location = emissive_node.location[0] - 300, emissive_node.location[1]
                                material.node_tree.links.new(color_node.outputs[0], emissive_node.inputs[0])
                            except:
                                nodes.remove(color_node)
                        
                        material.node_tree.links.new(emissive_node.outputs[0], transparency_mix.inputs[2])
                        material.node_tree.links.new(transparency_node.outputs[0], transparency_mix.inputs[1])
                        if image_alpha != 'noalpha':
                            material.node_tree.links.new(image_alpha.outputs[1], transparency_mix.inputs[0])
                        elif image != 'noimage':
                            material.node_tree.links.new(image.outputs[1], transparency_mix.inputs[0])
                                                            
                        material.node_tree.links.new(output_node.inputs[0], transparency_mix.outputs[0])
                    
                    elif shader_type == 'C':
                    #if set to KK shader
                        if image_alpha != 'noalpha':
                            #print('i got no alpha')
                            image_alpha = image_alpha.image
                        if image != 'noimage':
                            #print('i got no image')
                            image = image.image
                        else:
                            #if there's no image, try to fallback to the maintex
                            try:
                                #print('i fell into this')
                                image = bpy.data.images.get(detected_maintex)
                            except:
                                pass
                        
                        #get normal image
                        if nodes['Principled BSDF'].inputs[normal_input].links[0].from_node.inputs[1].links != ():
                            normal = nodes['Principled BSDF'].inputs[normal_input].links[0].from_node.inputs[1].links[0].from_node.image
                        else:
                            normal = 'nonormal'
                        
                        try:
                            template = bpy.data.materials['KK General'].copy()
                        except:
                            script_dir=Path(__file__).parent
                            template_path=(script_dir / '../KK Shader V6.0.blend').resolve()
                            filepath = str(template_path)

                            innerpath = 'Material'
                            templateList = ['KK General']

                            for template in templateList:
                                bpy.ops.wm.append(
                                    filepath=os.path.join(filepath, innerpath, template),
                                    directory=os.path.join(filepath, innerpath),
                                    filename=template,
                                    set_fake=False
                                    )
                            template = bpy.data.materials['KK General'].copy()
                        
                        template.name = 'KK ' + material.name
                        material_slot.material = bpy.data.materials[template.name]
                        material = material_slot.material
                        nodes = material.node_tree.nodes

                        def image_load(group, node, image, raw = False):
                            try:
                                nodes[group].node_tree.nodes[node].image = bpy.data.images[image]
                                if raw:
                                    nodes[group].node_tree.nodes[node].image.colorspace_settings.name = 'Raw'
                            except:
                                print('Image not found, skipping: ' + str(image))

                        gen_type = material_slot.name.replace('KK ','')

                        #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique texture group
                        new_node = material_slot.material.node_tree.nodes['Gentex'].node_tree.copy()
                        material_slot.material.node_tree.nodes['Gentex'].node_tree = new_node
                        new_node.name = gen_type + ' Textures'
                        
                        if image != 'noimage':
                            #print(image)
                            image_load('Gentex', 'Maintex', image.name)#, True)
                        else:
                            #if there's no image, fallback to the detected maintex
                            try:
                                image_load('Gentex', 'Maintex', detected_maintex)#, True)
                            except:
                                #oh well
                                pass
                        
                        if normal != 'nonormal':
                            image_load('Gentex', 'MainNorm', normal.name, True)
                        
                        #try importing the detail mask if there is one
                        try:
                            image_load('Gentex', 'MainDet', detected_detailmask)#, True)
                        except:
                            #or not
                            pass
                        
                        try:
                            image_load('Gentex', 'MainCol', detected_colormask)#, True)
                        except:
                            #or not
                            pass
                        
                        #Also, make a copy of the General shader node group, as it's unlikely everything using it will be the same color
                        new_node = material_slot.material.node_tree.nodes['Shader'].node_tree.copy()
                        material_slot.material.node_tree.nodes['Shader'].node_tree = new_node
                        new_node.name = gen_type + ' Shader'
                        
                        main_image = material_slot.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                        alpha_image = material_slot.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image

                        #If no main image was loaded in, there's no alpha channel being fed into the KK Shader.
                        #Unlink the input node and make the alpha channel pure white
                        if  main_image == None:
                            getOut = material_slot.material.node_tree.nodes['Shader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].links[0]
                            material_slot.material.node_tree.nodes['Shader'].node_tree.links.remove(getOut)
                            material_slot.material.node_tree.nodes['Shader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].default_value = (1,1,1,1)   
                        else:
                            #but if there is a main image, load in the darktex and enable it
                            #then create a darktex too
                            bpy.context.scene.kkbp.import_dir = os.path.dirname(bpy.data.filepath)
                            darktex = create_darktex(bpy.data.images[image.name], [.764, .880, 1]) #create the darktex now and load it in later
                            bpy.context.scene.kkbp.import_dir = ''

                            image_load('Gentex', 'Darktex', darktex.name)
                            material_slot.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use dark maintex?'].default_value = 1
                            material_slot.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1
                            
                        material.use_backface_culling = True
                        material.show_transparent_back = False
                        material.blend_method = blend_dict[blend_type]
                        material.shadow_method = shadow_dict[shadow_type]
                    
                    elif shader_type == 'D':
                        
                        if nodes['Principled BSDF'].inputs[20].links[0].from_node.inputs[1].links != ():
                            normal = nodes['Principled BSDF'].inputs[20].links[0].from_node.inputs[1].links[0].from_node
                        else:
                            normal = 'nonormal'
                            
                        nodes.remove(nodes['Principled BSDF'])
                        output_node = nodes['Material Output']
                        custom_group = nodes.new('ShaderNodeGroup')
                        try:
                            custom_group.node_tree = bpy.data.node_groups['Custom_studio']
                        except: 
                            try:
                                custom_group.node_tree = bpy.data.node_groups['custom_studio']
                            except:
                                #no custom studio node group was detected
                                bpy.context.window_manager.popup_menu(nodeError, title="Error", icon='ERROR')
                                return
                        
                        custom_group.location = output_node.location[0], output_node.location[1] - 300
                        
                        if image != 'noimage':
                            material.node_tree.links.new(image.outputs[0], custom_group.inputs[0])
                        if image_alpha != 'noalpha':
                            material.node_tree.links.new(image_alpha.outputs[1], custom_group.inputs[1])
                        if normal != 'nonormal':
                            material.node_tree.links.new(normal.outputs[0], custom_group.inputs[2])
                        
                        #if the custom studio node group has a fourth input, and a detail mask is available, put the detail mask in there
                        try:
                            detail_node = nodes.new('ShaderNodeTexImage')
                            detail_node.image = bpy.data.images[detected_detailmask]
                            detail_node.location = custom_group.location[0] - 300, custom_group.location[1] - 300
                            material.node_tree.links.new(detail_node.outputs[0], custom_group.inputs[3])
                        except:
                            nodes.remove(detail_node)
                        
                        #if the custom studio node group has a fifth input, and a color mask is available, put the color mask in there
                        try:
                            color_node = nodes.new('ShaderNodeTexImage')
                            color_node.image = bpy.data.images[detected_colormask]
                            color_node.location = custom_group.location[0] - 300, custom_group.location[1] - 600
                            material.node_tree.links.new(color_node.outputs[0], custom_group.inputs[4])
                        except:
                            nodes.remove(color_node)
                        
                        material.node_tree.links.new(output_node.inputs[0], custom_group.outputs[0])

    #convert newly imported textures using code from importcolors.py
    if use_lut:
        image_list = [image for image in bpy.data.images if image.name not in already_loaded_images]
        lut_light = 'Lut_TimeDay.png'
        lut_dark = 'Lut_TimeDay.png'
        load_luts(lut_light, lut_dark)

        first = True
        for image in image_list:
            image_name = image.name

            if ('.0' not in image_name) and ('_md-DXT' not in image_name) and ('_mc-DXT' not in image_name) and (image_name in conversion_image_list):
                image_name = image_name.replace(".dds", ".png").replace(".DDS", ".png")
                image = bpy.data.images[image_name]
                print('converting ' + image_name)
                image.reload()
                image.colorspace_settings.name = 'sRGB'

                # Need to run image_to_KK twice for the first image due to a weird bug
                #if first:
                image_to_KK(image, lut_light)
                #    first = False

                new_pixels, width, height = image_to_KK(image, lut_light)
                image.pixels = new_pixels
                #image.save()


class import_studio(bpy.types.Operator):
    bl_idname = "kkb.importstudio"
    bl_label = "Import studio object"
    bl_description = "Open the folder containing the fbx files exported with SB3Utility"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context):        
        import_studio_objects(self.directory)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_studio)
    
    # test call
    print((bpy.ops.kkb.importstudio('INVOKE_DEFAULT')))
