'''
This file performs the following operations

·	Remove unused material slots on all objects
·	Remap duplicate slots on all objects

·	Replace all body materials with material templates from the KK Shader file
·	Replace all hair materials with KK Shader templates
·	Replace all outfit materials with KK Shader templates
·	Replace shadowcast materials
·	Replace tears and tongue and gag eye mats with templates
·	Remove all duplicate node groups after importing everything

·	Get shadow colors from MaterialData json and store on Body object
·	Import all textures from .pmx directory to blender and create dark variants of all maintex files
·	Saturate all maintexes using the in game LUTs
·	Load images to correct spot on the body template
·	Load images to correct spot on the face template
·	Load Eyes, eyeline, tongue, gag eyes, tears, all hairs, all outfits
·	Set materials correctly based on mainImage and plain mainImage presence
·	Import all colors from the json, saturate them and apply them to the shaders
·	Create dark colors for all colors, saturate them and apply them to the shaders

·	Sets up the gag eye material drivers using the values from the gag eye shapekeys
·	Adds an outline modifier and outline materials to the face, body, hair and outfit meshes (based on single outline mode choice)
·	Sets up the GFN empty

·	Autopack all files

Color and image saturation code taken from MediaMoots https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/ecad6a136e86aaf6c51194705157200797f91e5f/importing/importcolors.py
Dark color conversion code taken from Xukmi https://github.com/xukmi/KKShadersPlus/tree/main/Shaders
'''

import bpy, sys, os, bgl, gpu, numpy, math, time
from pathlib import Path
from .. import common as c

class modify_material(bpy.types.Operator):
    bl_idname = "kkbp.modifymaterial"
    bl_label = bl_idname
    bl_description = bl_idname
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            self.retreive_stored_tags()

            self.remove_unused_material_slots()
            self.remap_duplcate_material_slots()

            self.replace_materials_for_body()
            self.replace_materials_for_hair()
            self.replace_materials_for_outfits()
            self.replace_materials_for_shadowcast()
            self.replace_materials_for_tears_tongue_gageye()
            self.remove_duplicate_node_groups()

            self.load_images_and_shadow_colors()
            self.link_textures_for_body()
            self.link_textures_for_hair()
            self.link_textures_for_clothes()
            self.link_textures_for_tongue_tear_gag()

            self.import_and_setup_gfn()
            self.setup_gag_eye_material_drivers()

            self.add_outlines_to_body()
            self.add_outlines_to_hair()
            self.add_outlines_to_clothes()

            self.load_luts()
            self.convert_main_textures()
            self.load_json_colors()
            self.set_color_management()

            c.clean_orphaned_data()
            return {'FINISHED'}
        except Exception as error:
            c.handle_error(self, error)
            return {"CANCELLED"}

    # %% Main functions
    def retreive_stored_tags(self):
        '''Gets the tag from each object to repopulate the class variables below'''
        self.hairs = []
        self.outfits = []
        self.outfit_alternates = []
        self.hitboxes = []
        for object in [o for o in bpy.data.objects if o.type == 'MESH']:
            if object.get('KKBP tag'):
                if object['KKBP tag'] == 'body':
                    self.body = object
                elif object['KKBP tag'] == 'outfit':
                    self.outfits.append(object)
                elif object['KKBP tag'] == 'alt':
                    self.outfit_alternates.append(object)
                elif object['KKBP tag'] == 'hair':
                    self.hairs.append(object)
                elif object['KKBP tag'] == 'hitbox':
                    self.hitboxes.append(object)
        for object in [o for o in bpy.data.objects if o.type == 'ARMATURE']:
            if object.get('KKBP tag'):
                if object['KKBP tag'] == 'armature':
                    self.armature = object
            
    def remove_unused_material_slots(self):
        '''Remove unused mat slots on all visible objects'''
        for object in [o for o in bpy.data.objects if o.type == 'MESH']:
            try:
                c.switch(object, 'object')
                bpy.ops.object.material_slot_remove_unused()
            except:
                pass
    
    def remap_duplcate_material_slots(self):
        c.switch(self.body, 'object')
        for cat in [[self.body], self.hairs, self.outfit_alternates, self.outfits]:
            for obj in cat:
                #combine duplicated material slots
                c.switch(obj, 'object')
                bpy.ops.object.material_slot_remove_unused()
                c.switch(obj, 'edit')
                
                #remap duplicate materials to the base one
                material_list = obj.data.materials
                for mat in material_list:
                    mat_name_list = []
                    mat_name_list.extend(self.body['SMR materials']['cf_Ohitomi_L02'])
                    mat_name_list.extend(self.body['SMR materials']['cf_Ohitomi_R02'])
                    mat_name_list.extend(self.body['SMR materials']['cf_Ohitomi_L'])
                    mat_name_list.extend(self.body['SMR materials']['cf_Ohitomi_R'])
                    mat_name_list.extend(self.body['SMR materials']['cf_O_namida_L'])
                    mat_name_list.extend(self.body['SMR materials']['cf_O_namida_M'])
                    mat_name_list.extend(self.body['SMR materials']['cf_O_namida_S'])
                    mat_name_list.extend(self.body['SMR materials']['o_tang'])
                    mat_name_list.extend(self.body['SMR materials']['o_tang_rigged'])
                    #don't merge the above materials if categorize by SMR is chosen.
                    eye_flag = mat.name not in mat_name_list if bpy.context.scene.kkbp.categorize_dropdown == 'D' else True
                    
                    if '.' in mat.name[-4:] and eye_flag:
                        try:
                            #the material name is normal
                            base_name, dupe_number = mat.name.split('.',2)
                        except:
                            #someone (not naming names) left a .### in the material name
                            base_name, rest_of_base_name, dupe_number = mat.name.split('.',2)
                            base_name = base_name + rest_of_base_name
                        #remap material if it's a dupe, but don't touch the eye dupe
                        if material_list.get(base_name) and int(dupe_number) and 'cf_m_hitomi_00' not in base_name and self.body['SMR materials']['o_tang'][0] not in base_name:
                            mat.user_remap(material_list[base_name])
                            bpy.data.materials.remove(mat)
                        else:
                            c.kklog("Somehow found a false duplicate material but didn't merge: " + mat.name, 'warn')
                
                #then clean material slots by going through each slot and reassigning the slots that are repeated
                repeats = {}
                for index, mat in enumerate(material_list):
                    if mat.name not in repeats:
                        repeats[mat.name] = [index]
                        # print("First entry of {} in slot {}".format(mat.name, index))
                    else:
                        repeats[mat.name].append(index)
                        # print("Additional entry of {} in slot {}".format(mat.name, index))
                
                for material_name in list(repeats.keys()):
                    if len(repeats[material_name]) > 1:
                        for repeated_slot in repeats[material_name]:
                            #don't touch the first slot
                            if repeated_slot == repeats[material_name][0]:
                                continue
                            c.kklog("Moving duplicate material {} in slot {} to the original slot {}".format(material_name, repeated_slot, repeats[material_name][0]))
                            obj.active_material_index = repeated_slot
                            bpy.ops.object.material_slot_select()
                            obj.active_material_index = repeats[material_name][0]
                            bpy.ops.object.material_slot_assign()
                            bpy.ops.mesh.select_all(action='DESELECT')
                c.switch(obj, 'object')
                bpy.ops.object.material_slot_remove_unused()

    def replace_materials_for_body(self):
        c.switch(self.body, 'object')
        templateList = [
        'KK Body',
        'KK Outline',
        'KK Body Outline',
        'KK Tears',
        'KK Gag00',
        'KK Gag01',
        'KK Gag02',
        'KK EyeR (hitomi)',
        'KK EyeL (hitomi)',
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
        'KK Fangs (tooth.001)',
        'KK Simple'
        ]
        c.import_from_library_file(category='Material', list_of_items=templateList, use_fake_user=True)

        #Replace all materials on the body with templates
        def swap_body_material(original, template):
                for mat in original:
                    try:
                        self.body.material_slots[mat].material = bpy.data.materials[template]
                    except:
                        c.kklog('material or template wasn\'t found when replacing body materials: ' + str(mat) + ' / ' + template, 'warn')
        
        swap_body_material(self.body['SMR materials']['cf_O_face'],'KK Face')
        swap_body_material(self.body['SMR materials']['cf_O_mayuge'],'KK Eyebrows (mayuge)')
        swap_body_material(self.body['SMR materials']['cf_O_noseline'],'KK Nose')
        swap_body_material(self.body['SMR materials']['cf_O_eyeline'],'KK Eyeline up')
        swap_body_material(self.body['SMR materials']['cf_O_eyeline_low'],'KK Eyeline down')
        swap_body_material(['cf_m_eyeline_kage'],'KK Eyeline Kage')
        swap_body_material(['Eyeline_Over'],'KK Eyeline Kage')
        swap_body_material(self.body['SMR materials']['cf_Ohitomi_L'],'KK Eyewhites (sirome)')
        swap_body_material(self.body['SMR materials']['cf_Ohitomi_R'],'KK Eyewhites (sirome)')
        swap_body_material(self.body['SMR materials']['cf_Ohitomi_L02'],'KK EyeL (hitomi)')
        swap_body_material(self.body['SMR materials']['cf_Ohitomi_R02'],'KK EyeR (hitomi)')
        swap_body_material(self.body['SMR materials']['o_body_a'],'KK Body')
        swap_body_material(self.body['SMR materials']['cf_O_tooth'],'KK Teeth (tooth)')
        swap_body_material([self.body['SMR materials']['cf_O_tooth'][0] + '.001'],'KK Fangs (tooth.001)')
        swap_body_material(self.body['SMR materials']['o_tang'],'KK General')

    def replace_materials_for_hair(self):
        '''Replace all of the Hair materials with hair templates and name accordingly'''
        for hair in self.hairs:
            for original_material in hair.material_slots:
                template = bpy.data.materials['KK Hair'].copy()
                template.name = 'KK ' + original_material.name
                original_material.material = bpy.data.materials[template.name]

    def replace_materials_for_outfits(self):
        #Replace all other materials with the general template and name accordingly
        for cat in [self.outfits, self.outfit_alternates]:
            for ob in cat:
                for original_material in ob.material_slots:
                    template = bpy.data.materials['KK General'].copy()
                    template.name = 'KK ' + original_material.name
                    original_material.material = bpy.data.materials[template.name]

    def replace_materials_for_shadowcast(self):
        #give the shadowcast object a template as well
        if bpy.data.objects.get('Shadowcast'):
            shadowcast = bpy.data.objects['Shadowcast']
            template = bpy.data.materials['KK Shadowcast']
            shadowcast.material_slots[0].material = bpy.data.materials[template.name]

    def replace_materials_for_tears_tongue_gageye(self):
        #give the tears a material template
        if bpy.data.objects.get('Tears'):
            tears = bpy.data.objects['Tears']
            template = bpy.data.materials['KK Tears']
            tears.material_slots[0].material = bpy.data.materials[template.name]
        
        #Make the tongue material unique so parts of the General Template aren't overwritten
        tongue_template = bpy.data.materials['KK General'].copy()
        tongue_template.name = 'KK Tongue'
        self.body.material_slots['KK General'].material = tongue_template
        
        #Make the texture group unique
        newNode = tongue_template.node_tree.nodes['Gentex'].node_tree.copy()
        tongue_template.node_tree.nodes['Gentex'].node_tree = newNode
        newNode.name = 'Tongue Textures'
        
        #Make the tongue shader group unique
        newNode = tongue_template.node_tree.nodes['Shader'].node_tree.copy()
        tongue_template.node_tree.nodes['Shader'].node_tree = newNode
        newNode.name = 'Tongue Shader'

        #give the rigged tongue the existing material template
        if bpy.data.objects.get('Tongue (rigged)'):
            tongue = bpy.data.objects['Tongue (rigged)']
            tongue.material_slots[0].material = bpy.data.materials['KK Tongue']

        #give the gag eyes a material template if they exist and have shapekeys setup
        if bpy.data.objects.get('Gag Eyes'):
            gag = bpy.data.objects['Gag Eyes']
            gag.material_slots[self.body['SMR materials']['cf_O_gag_eye_00'][0]].material = bpy.data.materials['KK Gag00']
            gag.material_slots[self.body['SMR materials']['cf_O_gag_eye_01'][0]].material = bpy.data.materials['KK Gag01']
            gag.material_slots[self.body['SMR materials']['cf_O_gag_eye_02'][0]].material = bpy.data.materials['KK Gag02']

    def remove_duplicate_node_groups(self):
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

    def load_images_and_shadow_colors(self):
        '''Load all images from the pmx folder'''
        c.switch(self.body, 'object')

        #get images for body object
        directory = bpy.context.scene.kkbp.import_dir + ('/' if (sys.platform == 'linux' or sys.platform == 'darwin') else '\\')
        fileList = Path(directory).glob('*.*')
        files = [file for file in fileList if file.is_file()]
        #c.kklog('this is my directory')
        #c.kklog(directory)
        #c.kklog('gettin this filelist')
        #c.kklog(files)
        #get images from outfit directory based on outfit ID numbers
        id_list = []
        for obj in [obj for obj in bpy.data.objects if obj.get('KKBP outfit ID') != None and obj.type == 'MESH']:
            if obj['KKBP outfit ID'] not in id_list:
                id_list.append(obj['KKBP outfit ID'])
        #c.kklog(id_list)
        for outfit_id in id_list:
            #c.kklog(directory)
            #c.kklog(directory + 'Outfit ' + str(outfit_id))
            #c.kklog(Path(directory + 'Outfit ' + str(outfit_id)))

            fileList = Path(directory + 'Outfit ' + str(outfit_id)).glob('*.*')
            files_to_append = [file for file in fileList if file.is_file()]
            #c.kklog('gettin this additional clothes fileList')
            #c.kklog(files_to_append)
            for outfit_file in files_to_append:
                files.append(outfit_file)

        #get shadow colors for each material and store the dictionary on the body object
        json_material_data = c.get_json_file('KK_MaterialData.json')
        color_dict = {}
        supporting_entries = ['Shader Forge/create_body', 'Shader Forge/create_head', 'Shader Forge/create_eyewhite', 'Shader Forge/create_eye', 'Shader Forge/create_topN']
        for line in json_material_data:
            if line['MaterialName'] in supporting_entries:
                line['MaterialName'] = line['MaterialName'].replace('create_','').replace('_create','')
            labels = line['ShaderPropNames']
            data = line['ShaderPropTextures']
            data.extend(line['ShaderPropTextureValues'])
            data.extend(line['ShaderPropColorValues'])
            data.extend(line['ShaderPropFloatValues'])
            data = dict(zip(labels, data))
            for entry in data:
                if '_ShadowColor ' in entry:
                    color_dict[line['MaterialName']] = data[entry]
                    break
                #default to [.764, .880, 1] if shadow color is not available for the material
                color_dict[line['MaterialName']] = {"r":0.764,"g":0.880,"b":1,"a":1}
        self.body['KKBP shadow colors'] = color_dict

        #open all images into blender and create dark variants if the image is a maintex
        #c.kklog('gettin these files')
        #c.kklog(files)
        for image in files:
            bpy.ops.image.open(filepath=str(image), use_udim_detecting=False)
            try:
                bpy.data.images[image.name].pack()
            except:
                c.kklog('This image was not automatically loaded in because its name exceeds 64 characters: ' + image.name, type = 'error')
            try:
                skip_list = ['cf_m_gageye', 'cf_m_eyeline', 'cf_m_mayuge', 'cf_m_namida_00', 'cf_m_noseline_00', 'cf_m_sirome_00', 'cf_m_tooth', '_cf_Ohitomi_', 'cf_m_emblem']
                convert_this = True
                for item in skip_list:
                    if item in image.name:
                        convert_this = False
                if '_MT_CT' in image.name and convert_this:
                    material_name = image.name[:-10]
                    shadow_color = [self.body['KKBP shadow colors'][material_name]['r'], self.body['KKBP shadow colors'][material_name]['g'], self.body['KKBP shadow colors'][material_name]['b']]
                    darktex = self.create_darktex(bpy.data.images[image.name], shadow_color) #create the darktex now and load it in later
            except:
                c.kklog('Tried to create a dark version of {} but it was missing a shadow color. Defaulting to shadow color of [.764, .880, 1].'.format(image.name), type='warn')
                skip_list = ['cf_m_gageye', 'cf_m_eyeline', 'cf_m_mayuge', 'cf_m_namida_00', 'cf_m_noseline_00', 'cf_m_sirome_00', 'cf_m_tooth', '_cf_Ohitomi_', 'cf_m_emblem']
                convert_this = True
                for item in skip_list:
                    if item in image.name:
                        convert_this = False
                if '_MT_CT' in image.name and convert_this:
                    material_name = image.name[:-10]
                    darktex = self.create_darktex(bpy.data.images[image.name], [.764, .880, 1]) #create the darktex now and load it in later
        
    def link_textures_for_body(self):
        '''Load the textures for the body materials to the correct spot'''
        self.image_load('KK Body', 'Gentex', 'BodyMain', self.body['SMR materials']['o_body_a'][0] + '_MT_CT.png')
        self.image_load('KK Body', 'Gentex', 'Darktex', self.body['SMR materials']['o_body_a'][0] + '_MT_DT.png')
        #check there's a maintex, if not there fallback to colors
        if not self.body.material_slots['KK Body'].material.node_tree.nodes['Gentex'].node_tree.nodes['BodyMain'].image:
            self.body.material_slots['KK Body'].material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use maintex instead?'].default_value = 0
        #but if it is, make sure the body darktex is being used as default
        else:
            self.body.material_slots['KK Body'].material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use maintex instead?'].default_value = 1
        
        self.image_load('KK Body', 'Gentex', 'BodyMC', self.body['SMR materials']['o_body_a'][0] + '_CM.png')
        self.image_load('KK Body', 'Gentex', 'BodyMD', self.body['SMR materials']['o_body_a'][0] + '_DM.png') #cfm female
        self.image_load('KK Body', 'Gentex', 'BodyLine', self.body['SMR materials']['o_body_a'][0] + '_LM.png')
        self.image_load('KK Body', 'Gentex', 'BodyNorm', self.body['SMR materials']['o_body_a'][0] + '_NMP_CNV.png')
        self.image_load('KK Body', 'Gentex', 'BodyNormDetail', self.body['SMR materials']['o_body_a'][0] + '_NMPD_CNV.png')

        self.image_load('KK Body', 'Gentex', 'BodyMD', 'cm_m_body_DM.png') #cmm male
        self.image_load('KK Body', 'Gentex', 'BodyLine', 'cm_m_body_LM.png')
        
        self.image_load('KK Body', 'NSFWTextures', 'Genital', self.body['SMR materials']['o_body_a'][0] + '_MT.png') #chara main texture
        self.image_load('KK Body', 'NSFWTextures', 'Underhair', self.body['SMR materials']['o_body_a'][0] + '_ot2.png') #pubic hair

        self.image_load('KK Body', 'NSFWTextures', 'NipR', self.body['SMR materials']['o_body_a'][0] + '_ot1.png') #cfm female
        self.image_load('KK Body', 'NSFWTextures', 'NipL', self.body['SMR materials']['o_body_a'][0] + '_ot1.png')
        self.image_load('KK Body', 'NSFWTextures', 'NipR', 'cm_m_body_ot1.png') #cmm male
        self.image_load('KK Body', 'NSFWTextures', 'NipL', 'cm_m_body_ot1.png')

        self.image_load('KK Body', 'Gentex', 'overone', self.body['SMR materials']['o_body_a'][0] + '_T3.png') #body overlays
        self.image_load('KK Body', 'Gentex', 'overtwo', self.body['SMR materials']['o_body_a'][0] + '_T4.png')
        
        self.set_uv_type('KK Body', 'NSFWpos', 'nippleuv', 'uv_nipple_and_shine')
        self.set_uv_type('KK Body', 'NSFWpos', 'underuv', 'uv_underhair')

        #find the appropriate alpha mask
        alpha_mask = None
        if bpy.data.images.get(self.body['SMR materials']['o_body_a'][0] + '_AM.png'):
            alpha_mask = bpy.data.images.get(self.body['SMR materials']['o_body_a'][0] + '_AM.png')
        elif bpy.data.images.get(self.body['SMR materials']['o_body_a'][0] + '_AM_00.png'):
            alpha_mask = bpy.data.images.get(self.body['SMR materials']['o_body_a'][0] + '_AM_00.png')
        else:
            #check the other alpha mask numbers
            for image in bpy.data.images:
                if '_m_body_AM_' in image.name and image.name[-6:-4].isnumeric():
                    alpha_mask = image
                    break
        if alpha_mask:
            self.body.material_slots['KK Body'].material.node_tree.nodes['Gentex'].node_tree.nodes['Bodyalpha'].image = bpy.data.images[alpha_mask.name] #female
            self.apply_texture_data_to_image(alpha_mask.name, 'KK Body', 'Gentex', 'Bodyalpha')
        else:
            #disable transparency if no alpha mask is present
            self.body.material_slots['KK Body'].material.node_tree.nodes['Shader'].node_tree.nodes['BodyTransp'].inputs['Built in transparency toggle'].default_value = 0

        self.image_load('KK Face', 'Gentex', 'FaceMain', self.body['SMR materials']['cf_O_face'][0] + '_MT_CT.png')
        self.image_load('KK Face', 'Gentex', 'Darktex', self.body['SMR materials']['cf_O_face'][0] + '_MT_DT.png')
        #default to colors if there's no face maintex
        if not self.body.material_slots['KK Face'].material.node_tree.nodes['Gentex'].node_tree.nodes['FaceMain'].image:
            self.body.material_slots['KK Face'].material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use maintex instead?'].default_value = 0
        else:
            self.body.material_slots['KK Face'].material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use maintex instead?'].default_value = 1        
        self.image_load('KK Face', 'Gentex', 'FaceMC', self.body['SMR materials']['cf_O_face'][0] + '_CM.png')
        self.image_load('KK Face', 'Gentex', 'FaceMD', self.body['SMR materials']['cf_O_face'][0] + '_DM.png')
        self.image_load('KK Face', 'Gentex', 'BlushMask', self.body['SMR materials']['cf_O_face'][0] + '_T4.png')
        self.image_load('KK Face', 'Gentex', 'FaceTongue', self.body['SMR materials']['cf_O_face'][0] + '_MT.png') #face main texture
        
        self.image_load('KK Face', 'Gentex', 'linemask', self.body['SMR materials']['cf_O_face'][0] + '_LM.png')
        self.image_load('KK Face', 'Gentex', 'lowerlip', self.body['SMR materials']['cf_O_face'][0] + '_T5.png')

        self.image_load('KK Face', 'Gentex', 'lipstick', self.body['SMR materials']['cf_O_face'][0] + '_ot1.png')
        self.image_load('KK Face', 'Gentex', 'flush', self.body['SMR materials']['cf_O_face'][0] + '_ot2.png')
        self.image_load('KK Face', 'Gentex', 'overlay1', self.body['SMR materials']['cf_O_face'][0] + '_T6.png')
        self.image_load('KK Face', 'Gentex', 'overlay2', self.body['SMR materials']['cf_O_face'][0] + '_T7.png')
        self.image_load('KK Face', 'Gentex', 'overlay3', self.body['SMR materials']['cf_O_face'][0] + '_T8.png')
        self.image_load('KK Face', 'Gentex', 'EyeshadowMask', self.body['SMR materials']['cf_O_face'][0] + '_ot3.png')
        self.set_uv_type('KK Face', 'Facepos', 'eyeshadowuv', 'uv_eyeshadow')  #face extra texture
        
        self.image_load('KK Eyebrows (mayuge)', 'Gentex', 'Eyebrow', self.body['SMR materials']['cf_O_mayuge'][0] + '_MT_CT.png')
        self.image_load('KK Nose', 'Gentex', 'Nose', self.body['SMR materials']['cf_O_noseline'][0] + '_MT_CT.png')
        self.image_load('KK Teeth (tooth)', 'Gentex', 'Teeth', self.body['SMR materials']['cf_O_tooth'][0] + '_MT_CT.png')
        self.image_load('KK Eyewhites (sirome)', 'Gentex', 'Eyewhite', self.body['SMR materials']['cf_Ohitomi_R'][0] + '_MT_CT.png')
        
        self.image_load('KK Eyeline up', 'Gentex', 'EyelineUp', self.body['SMR materials']['cf_O_eyeline'][0] + '_MT_CT.png')
        self.image_load('KK Eyeline up', 'Gentex', 'EyelineUp.001', self.body['SMR materials']['cf_O_eyeline'][0] + '_MT_CT.png')
        self.image_load('KK Eyeline up', 'Gentex', 'EyelineDown', self.body['SMR materials']['cf_O_eyeline_low'][0] + '_MT_CT.png')
        self.image_load('KK Eyeline up', 'Gentex', 'EyelineDown.001', self.body['SMR materials']['cf_O_eyeline_low'][0] + '_MT_CT.png')
        self.image_load('KK Eyeline up', 'Gentex', 'EyelineKage', 'cf_m_eyeline_kage_MT.png')
        self.image_load('KK Eyeline up', 'Gentex', 'EyelineKage', 'Eyeline_Over_MT_CT.png')
        
        self.image_load('KK EyeR (hitomi)', 'Gentex', 'eyeAlpha', self.body['SMR materials']['cf_Ohitomi_R02'][0] + '_MT_CT.png')
        self.image_load('KK EyeR (hitomi)', 'Gentex', 'EyeHU', self.body['SMR materials']['cf_Ohitomi_R02'][0] + '_ot1.png')
        self.image_load('KK EyeR (hitomi)', 'Gentex', 'EyeHD', self.body['SMR materials']['cf_Ohitomi_R02'][0] + '_ot2.png')
        self.image_load('KK EyeR (hitomi)', 'Gentex', 'expression0', self.body['SMR materials']['cf_Ohitomi_R'][0] + '_cf_t_expression_00_EXPR.png')
        self.image_load('KK EyeR (hitomi)', 'Gentex', 'expression1', self.body['SMR materials']['cf_Ohitomi_R'][0] + '_cf_t_expression_01_EXPR.png')

        self.image_load('KK EyeL (hitomi)', 'Gentex', 'eyeAlpha', self.body['SMR materials']['cf_Ohitomi_L02'][0] + '_MT_CT.png')
        self.image_load('KK EyeL (hitomi)', 'Gentex', 'EyeHU', self.body['SMR materials']['cf_Ohitomi_L02'][0] + '_ot1.png')
        self.image_load('KK EyeL (hitomi)', 'Gentex', 'EyeHD', self.body['SMR materials']['cf_Ohitomi_L02'][0] + '_ot2.png')
        self.image_load('KK EyeL (hitomi)', 'Gentex', 'expression0', self.body['SMR materials']['cf_Ohitomi_L02'][0] + '_cf_t_expression_00_EXPR.png')
        self.image_load('KK EyeL (hitomi)', 'Gentex', 'expression1', self.body['SMR materials']['cf_Ohitomi_L02'][0] + '_cf_t_expression_01_EXPR.png')
    
    def link_textures_for_hair(self):
        #for each material slot in each hair object, load in the hair detail mask, colormask
        for current_obj  in self.hairs:
            for hairMat in current_obj.material_slots:
                hairType = hairMat.name.replace('KK ','')
                
                #make a copy of the node group, use it to replace the current node group and rename it so each piece of hair has it's own unique hair texture group
                newNode = hairMat.material.node_tree.nodes['Gentex'].node_tree.copy()
                hairMat.material.node_tree.nodes['Gentex'].node_tree = newNode
                newNode.name = hairType + ' Textures'
            
                self.image_load(hairMat.name, 'Gentex', 'hairMainTex',  hairType+'_MT_CT.png')
                self.image_load(hairMat.name, 'Gentex', 'hairDetail', hairType+'_DM.png')
                self.image_load(hairMat.name, 'Gentex', 'hairFade',   hairType+'_CM.png')
                self.image_load(hairMat.name, 'Gentex', 'hairShine',  hairType+'_HGLS.png')
                self.image_load(hairMat.name, 'Gentex', 'hairAlpha',  hairType+'_AM.png')
                self.set_uv_type(hairMat.name, 'Hairpos', 'hairuv', 'uv_nipple_and_shine')

                #If no alpha mask wasn't loaded in disconnect the hair alpha node to make sure this piece of hair is visible
                if hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image == None and hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image == None:
                    getOut = hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Group Output'].inputs['Hair alpha'].links[0]
                    hairMat.material.node_tree.nodes['Gentex'].node_tree.links.remove(getOut)
    
    def link_textures_for_clothes(self):
        '''Loop through each material in the general object and load the textures, if any, into unique node groups
        also make unique shader node groups so all materials are unique
        make a copy of the node group, use it to replace the current node group'''
        for cat in [self.outfits, self.outfit_alternates]:
            for outfit in cat:
                outfit = outfit
                for genMat in outfit.material_slots:
                    genType = genMat.name.replace('KK ','')
                    
                    #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique texture group
                    newNode = genMat.material.node_tree.nodes['Gentex'].node_tree.copy()
                    genMat.material.node_tree.nodes['Gentex'].node_tree = newNode
                    newNode.name = genType + ' Textures'

                    #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique position group
                    posNode = genMat.material.node_tree.nodes['Genpos'].node_tree.copy()
                    genMat.material.node_tree.nodes['Genpos'].node_tree = posNode
                    posNode.name = genType + ' Position'

                    self.image_load(genMat.name, 'Gentex', 'Maintexplain', genType+ '_MT.png')
                    self.image_load(genMat.name, 'Gentex', 'Maintex', genType+ '_MT.png')
                    self.image_load(genMat.name, 'Gentex', 'Maintex', genType+'_MT_CT.png')
                    self.image_load(genMat.name, 'Gentex', 'Darktex', genType+'_MT_DT.png')
                    self.image_load(genMat.name, 'Gentex', 'MainCol', genType+'_CM.png')
                    self.image_load(genMat.name, 'Gentex', 'MainDet', genType+'_DM.png')
                    self.image_load(genMat.name, 'Gentex', 'MainNorm', genType+'_NMP.png')
                    self.image_load(genMat.name, 'Gentex', 'MainNormDetail', genType+'_NMPD_CNV.png') #load detail map if it's there
                    self.image_load(genMat.name, 'Gentex', 'Alphamask', genType+'_AM.png')

                    # image_load(genMat.name, 'Gentex', 'PatBase', genType+'_PM1.png')
                    self.image_load(genMat.name, 'Gentex', 'PatRed', genType+'_PM1.png')
                    self.image_load(genMat.name, 'Gentex', 'PatGreen', genType+'_PM2.png')
                    self.image_load(genMat.name, 'Gentex', 'PatBlue', genType+'_PM3.png')
                    
                    MainImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                    DarkImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Darktex'].image
                    AlphaImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image

                    #set dark colors to use the maintex if there was a dark image loaded in
                    if DarkImage and 'Template: Pattern Placeholder' not in DarkImage.name:
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use dark maintex?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1

                    #Also, make a copy of the General shader node group, as it's unlikely everything using it will be the same color
                    newNode = genMat.material.node_tree.nodes['Shader'].node_tree.copy()
                    genMat.material.node_tree.nodes['Shader'].node_tree = newNode
                    newNode.name = genType + ' Shader'
                    
                    #If an alpha mask was loaded in, enable the alpha mask toggle in the KK shader
                    if  AlphaImage != None:
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['alphatoggle'].inputs['Transparency toggle'].default_value = 1

                    #If no main image was loaded in, there's no alpha channel being fed into the KK Shader.
                    #Unlink the input node and make the alpha channel pure white
                    if  not MainImage:
                        getOut = genMat.material.node_tree.nodes['Shader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].links[0]
                        genMat.material.node_tree.nodes['Shader'].node_tree.links.remove(getOut)
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].default_value = (1,1,1,1)
                    
                    #check maintex config
                    plainMain = not genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintexplain'].image.name == 'Template: Maintex plain placeholder'
                    if not MainImage and not plainMain:
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 0
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 0
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 0
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 0

                    elif not MainImage and plainMain:
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use colored maintex?'].default_value = 0
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 0
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use colored maintex?'].default_value = 0
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 0
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 1

                    elif MainImage and not plainMain:
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use colored maintex?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use colored maintex?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 1

                    else: #MainImage and plainMain
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use colored maintex?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use colored maintex?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1
                        genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 1
    
    def link_textures_for_tongue_tear_gag(self):
        self.image_load('KK Tongue', 'Gentex', 'Maintex',        self.body['SMR materials']['o_tang'][0] + '_CM.png') #done on purpose
        self.image_load('KK Tongue', 'Gentex', 'MainCol',        self.body['SMR materials']['o_tang'][0] + '_CM.png')
        self.image_load('KK Tongue', 'Gentex', 'MainDet',        self.body['SMR materials']['o_tang'][0] + '_DM.png')
        self.image_load('KK Tongue', 'Gentex', 'MainNorm',       self.body['SMR materials']['o_tang'][0] + '_NMP.png')
        self.image_load('KK Tongue', 'Gentex', 'MainNormDetail', self.body['SMR materials']['o_tang'][0] + '_NMP_CNV.png') #load regular map by default
        self.image_load('KK Tongue', 'Gentex', 'MainNormDetail', self.body['SMR materials']['o_tang'][0] + '_NMPD_CNV.png') #then the detail map if it's there

        #load all gag eyes in if it exists
        if bpy.data.objects.get('Gag Eyes'):
            self.image_load('KK Gag00', 'Gentex', '00gag00', self.body['SMR materials']['cf_O_gag_eye_00'][0] + '_cf_t_gageye_00_MT_CT.png')
            self.image_load('KK Gag00', 'Gentex', '00gag02', self.body['SMR materials']['cf_O_gag_eye_00'][0] + '_cf_t_gageye_02_MT_CT.png')
            self.image_load('KK Gag00', 'Gentex', '00gag04', self.body['SMR materials']['cf_O_gag_eye_00'][0] + '_cf_t_gageye_04_MT_CT.png')
            self.image_load('KK Gag00', 'Gentex', '00gag05', self.body['SMR materials']['cf_O_gag_eye_00'][0] + '_cf_t_gageye_05_MT_CT.png')
            self.image_load('KK Gag00', 'Gentex', '00gag06', self.body['SMR materials']['cf_O_gag_eye_00'][0] + '_cf_t_gageye_06_MT_CT.png')

            self.image_load('KK Gag01', 'Gentex', '01gag03', self.body['SMR materials']['cf_O_gag_eye_01'][0] + '_cf_t_gageye_03_MT_CT.png')
            self.image_load('KK Gag01', 'Gentex', '01gag01', self.body['SMR materials']['cf_O_gag_eye_01'][0] + '_cf_t_gageye_01_MT_CT.png')

            self.image_load('KK Gag02', 'Gentex', '02gag07', self.body['SMR materials']['cf_O_gag_eye_02'][0] + '_cf_t_gageye_07_MT_CT.png')
            self.image_load('KK Gag02', 'Gentex', '02gag08', self.body['SMR materials']['cf_O_gag_eye_02'][0] + '_cf_t_gageye_08_MT_CT.png')
            self.image_load('KK Gag02', 'Gentex', '02gag09', self.body['SMR materials']['cf_O_gag_eye_02'][0] + '_cf_t_gageye_09_MT_CT.png')

        #load the tears texture in
        if bpy.data.objects.get('Tears'):
            self.image_load('KK Tears', 'Gentex', 'Maintex', self.body['SMR materials']['cf_O_namida_L'][0] + '_MT_CT.png')

    def import_and_setup_gfn(self):
        '''Sets up the Generated Face Normals (GFN) empty for smooth face normals'''
        #setup face normals
        try:
            #import gfn face node group, cycles node groups as well
            c.import_from_library_file('NodeTree', ['Raw Shading (face)'], bpy.context.scene.kkbp.use_material_fake_user)
            c.switch(self.armature, 'edit')
            head_location = (self.armature.data.edit_bones['Head'].tail.x+1, self.armature.data.edit_bones['Head'].tail.y+1, self.armature.data.edit_bones['Head'].tail.z+1)
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=head_location)
            empty = bpy.context.view_layer.objects.active
            empty.location.x -= 1
            empty.location.y -= 1
            empty.location.z -= 1
            empty.scale = (0.15, 0.15, 0.15)
            empty.name = 'GFN Empty'
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = self.armature
            empty.select_set(True)
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')
            self.armature.data.bones['Head'].select = True
            self.armature.data.bones.active = self.armature.data.bones['Head']
            bpy.ops.object.parent_set(type='BONE')
            bpy.ops.pose.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.node_groups['Generated Face Normals'].nodes['GFNEmpty'].object = empty
            bpy.context.view_layer.objects.active = empty
            empty.select_set(True)
            bpy.ops.object.move_to_collection(collection_index=1)
            empty.hide = True
            empty.hide_render = True
        except:
            #i don't feel like dealing with any errors related to this
            c.kklog('The GFN empty wasnt setup correctly. Oh well.', 'warn')
            pass

    def setup_gag_eye_material_drivers(self):
        '''setup gag eye drivers'''
        if bpy.data.objects.get('Gag Eyes'):
            gag_keys = [
                'Circle Eyes 1',
                'Circle Eyes 2',
                'Spiral Eyes',
                'Heart Eyes',
                'Fiery Eyes',
                'Cartoony Wink',
                'Vertical Line',
                'Cartoony Closed',
                'Horizontal Line',
                'Cartoony Crying' 
            ]
            
            skey_driver = bpy.data.materials['KK Gag00'].node_tree.nodes['Parser'].inputs[0].driver_add('default_value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
            skey_driver.driver.expression = '0 if CircleEyes1 else 1 if CircleEyes2 else 2 if CartoonyClosed else 3 if VerticalLine else 4'
            skey_driver = bpy.data.materials['KK Gag00'].node_tree.nodes['hider'].inputs[0].driver_add('default_value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value'
            skey_driver.driver.expression = 'CircleEyes1 or CircleEyes2 or CartoonyClosed or VerticalLine or HorizontalLine'

            skey_driver = bpy.data.materials['KK Gag01'].node_tree.nodes['Parser'].inputs[0].driver_add('default_value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
            skey_driver.driver.expression = '0 if HeartEyes else 1'
            skey_driver = bpy.data.materials['KK Gag01'].node_tree.nodes['hider'].inputs[0].driver_add('default_value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
            skey_driver.driver.expression = 'HeartEyes or SpiralEyes'

            skey_driver = bpy.data.materials['KK Gag02'].node_tree.nodes['Parser'].inputs[0].driver_add('default_value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
            skey_driver.driver.expression = '0 if CartoonyCrying else 1 if CartoonyWink else 2'
            skey_driver = bpy.data.materials['KK Gag02'].node_tree.nodes['hider'].inputs[0].driver_add('default_value')
            skey_driver.driver.type = 'SCRIPTED'
            for key in gag_keys:
                newVar = skey_driver.driver.variables.new()
                newVar.name = key.replace(' ','')
                newVar.type = 'SINGLE_PROP'
                newVar.targets[0].id_type = 'KEY'
                newVar.targets[0].id = self.body.data.shape_keys
                newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
            skey_driver.driver.expression = 'CartoonyCrying or CartoonyWink or FieryEyes'

    def add_outlines_to_body(self):
        #Add face and body outlines, then load in the clothes transparency mask to body outline
        c.switch(self.body, 'object')
        mod = self.body.modifiers.new(type='SOLIDIFY', name='Outline Modifier')
        mod.thickness = 0.0005
        mod.offset = 0
        mod.material_offset = len(self.body.material_slots)
        mod.use_flip_normals = True
        mod.use_rim = False
        mod.name = 'Outline Modifier'
        mod.show_expanded = False
        #face first
        faceOutlineMat = bpy.data.materials['KK Outline'].copy()
        faceOutlineMat.name = 'KK Face Outline'
        self.body.data.materials.append(faceOutlineMat)
        faceOutlineMat.blend_method = 'CLIP'
        #body second
        self.body.data.materials.append(bpy.data.materials['KK Body Outline'])
        if not bpy.data.materials['KK Body Outline'].node_tree.nodes['Gentex'].node_tree.nodes['Bodyalpha'].image:
            #An alpha mask for the clothing wasn't present in the Textures folder
            bpy.data.materials['KK Body Outline'].node_tree.nodes['Clipping prevention toggle'].inputs[0].default_value = 0            

    def add_outlines_to_hair(self):
        #Give each piece of hair with an alphamask on each hair object it's own outline group
        if not bpy.context.scene.kkbp.use_single_outline:
            for ob in self.hairs:
                #Get the length of the material list before starting
                outlineStart = len(ob.material_slots)
                #link all polygons to material name
                mats_to_gons = {}
                for slot in ob.material_slots:
                    mats_to_gons[slot.material.name] = []
                for gon in ob.data.polygons:
                        mats_to_gons[ob.material_slots[gon.material_index].material.name].append(gon)
                #find all materials that use an alpha mask or maintex
                alpha_users = []
                for mat in ob.material_slots:
                    AlphaImage = mat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image
                    MainImage =  mat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image
                    if AlphaImage or MainImage:
                        alpha_users.append(mat.material.name)
                #reorder material_list to place alpha/maintex users first
                new_mat_list_order = [mat_slot.material.name for mat_slot in ob.material_slots if mat_slot.material.name not in alpha_users]
                new_mat_list_order = alpha_users + new_mat_list_order
                #reorder mat slot list
                for index, mat_slot in enumerate(ob.material_slots):
                    mat_slot.material = bpy.data.materials[new_mat_list_order[index]]
                #create empty slots for new alpha user outlines
                for mat in alpha_users:
                    ob.data.materials.append(None)
                #fill alpha user outline materials, and fill image node
                for index, mat in enumerate(alpha_users):
                    OutlineMat = bpy.data.materials['KK Outline'].copy()
                    OutlineMat.name = mat.replace('KK ', 'Outline ')
                    AlphaImage = ob.material_slots[mat].material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image
                    MainImage =  ob.material_slots[mat].material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image
                    if AlphaImage:
                        OutlineMat.node_tree.nodes['outlinealpha'].image = AlphaImage
                        OutlineMat.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                        OutlineMat.node_tree.nodes['maintexoralpha'].blend_type = 'MULTIPLY'
                    elif MainImage:
                        OutlineMat.node_tree.nodes['outlinealpha'].image = MainImage
                        OutlineMat.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                    OutlineMat.node_tree.nodes['outlinetransparency'].inputs[0].default_value = 1.0
                    ob.material_slots[index + outlineStart].material = OutlineMat
                #update polygon material indexes
                for mat in mats_to_gons:
                    for gon in mats_to_gons[mat]:
                        gon.material_index = new_mat_list_order.index(mat)

        #Add a general outline that covers the rest of the materials on the hair object that don't need transparency
        for ob in self.hairs:
            bpy.context.view_layer.objects.active = ob
            mod = ob.modifiers.new(
                type='SOLIDIFY',
                name='Outline Modifier')
            mod.thickness = 0.0005
            mod.offset = 1
            mod.material_offset = outlineStart if not bpy.context.scene.kkbp.use_single_outline else 200
            mod.use_flip_normals = True
            mod.use_rim = False
            mod.show_expanded = False
            hairOutlineMat = bpy.data.materials['KK Outline'].copy()
            hairOutlineMat.name = 'KK Hair Outline'
            ob.data.materials.append(hairOutlineMat)
            #hide alts
            if ob.name[:12] == 'Hair Outfit ' and ob.name != 'Hair Outfit 00':
                ob.hide = True
                ob.hide_render = True

    def add_outlines_to_clothes(self):
        #Add a standard outline to all other objects
        #keep a dictionary of the material length list for the next loop
        outlineStart = {}
        c.switch(self.body, 'object')
        if not bpy.context.scene.kkbp.use_single_outline:
            #If the material has a maintex or alphamask then give it it's own outline, mmdtools style
            for cat in [self.outfits, self.outfit_alternates]:
                for ob in cat:
                    #Get the length of the material list before starting
                    outlineStart[ob.name] = len(ob.material_slots)
                    #link all polygons to material name
                    mats_to_gons = {}
                    for slot in ob.material_slots:
                        mats_to_gons[slot.material.name] = []
                    for gon in ob.data.polygons:
                            mats_to_gons[ob.material_slots[gon.material_index].material.name].append(gon)
                    #find all materials that use an alpha mask or maintex
                    alpha_users = []
                    for mat in ob.material_slots:
                        AlphaImage = mat.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
                        MainImage = mat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                        if AlphaImage or MainImage:
                            alpha_users.append(mat.material.name)
                    #reorder material_list to place alpha/maintex users first
                    new_mat_list_order = [mat_slot.material.name for mat_slot in ob.material_slots if mat_slot.material.name not in alpha_users]
                    new_mat_list_order = alpha_users + new_mat_list_order
                    #reorder mat slot list
                    for index, mat_slot in enumerate(ob.material_slots):
                        mat_slot.material = bpy.data.materials[new_mat_list_order[index]]
                    #create empty slots for new alpha user outlines
                    for mat in alpha_users:
                        ob.data.materials.append(None)
                    #fill alpha user outline materials, and fill image node
                    for index, mat in enumerate(alpha_users):
                        OutlineMat = bpy.data.materials['KK Outline'].copy()
                        OutlineMat.name = mat.replace('KK ', 'Outline ')
                        AlphaImage = ob.material_slots[mat].material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
                        MainImage = ob.material_slots[mat].material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                        if AlphaImage:
                            OutlineMat.node_tree.nodes['outlinealpha'].image = AlphaImage
                            OutlineMat.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                            OutlineMat.node_tree.nodes['maintexoralpha'].blend_type = 'MULTIPLY'
                        elif MainImage:
                            OutlineMat.node_tree.nodes['outlinealpha'].image = MainImage
                            OutlineMat.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                        OutlineMat.node_tree.nodes['outlinetransparency'].inputs[0].default_value = 1.0
                        ob.material_slots[index + outlineStart[ob.name]].material = OutlineMat
                    #update polygon material indexes
                    for mat in mats_to_gons:
                        for gon in mats_to_gons[mat]:
                            gon.material_index = new_mat_list_order.index(mat)

        for cat in [self.outfits, self.outfit_alternates]:
            for ob in cat:    
                #Add a general outline that covers the rest of the materials on the object that don't need transparency
                mod = ob.modifiers.new(
                    type='SOLIDIFY',
                    name='Outline Modifier')
                mod.thickness = 0.0005
                mod.offset = 1
                mod.material_offset = outlineStart[ob.name] if not bpy.context.scene.kkbp.use_single_outline else 200
                mod.use_flip_normals = True
                mod.use_rim = False
                mod.show_expanded = False
                ob.data.materials.append(bpy.data.materials['KK Outline'])

    @classmethod
    def load_luts(cls):
        self = cls
        self.lut_selection = bpy.context.scene.kkbp.colors_dropdown
        if self.lut_selection == 'A':
            self.lut_dark = 'Lut_TimeNight.png'
        elif self.lut_selection == 'B':
            self.lut_dark = 'Lut_TimeSunset.png'
        else:
            self.lut_dark = 'Lut_TimeDay.png'
        self.lut_light = 'Lut_TimeDay.png'
        
        self.lut_path = os.path.dirname(os.path.abspath(__file__)) + '/luts/'
        day_lut = bpy.data.images.load(self.lut_path + self.lut_light, check_existing=True)
        day_lut.use_fake_user = True
        #day_lut.save()

        night_lut = bpy.data.images.load(self.lut_path + self.lut_dark, check_existing=True)
        night_lut.use_fake_user = True
        #night_lut.save()

    def convert_main_textures(self):
        ignore_list = [
            "cf_m_eyeline_00_up_MT_CT.png",
            "cf_m_eyeline_down_MT_CT.png",
            "cf_m_noseline_00_MT_CT.png",
            "cf_m_mayuge_00_MT_CT.png",
            "cf_m_eyeline_kage_MT.png",
        ]

        bpy.data.use_autopack = True #enable autopack on file save
        
        images = bpy.data.images
        first = True
        for image in images:
            if "_MT" in image.name and image.name not in ignore_list:
                image.reload()

                # Need to run image_to_KK twice for the first image due to a weird bug
                if first:
                    self.image_to_KK(image, self.lut_light)
                    first = False

                new_pixels, width, height = self.image_to_KK(image, self.lut_light)
                image.pixels = new_pixels
                #image.save()

    def load_json_colors(self):
        json_color_data = c.get_json_file('KK_MaterialData.json')
        self.update_shaders(json_color_data, self.lut_selection, self.lut_light, light = True) # Set light colors
        self.update_shaders(json_color_data, self.lut_selection, self.lut_dark, light = False) # Set dark colors

    def set_color_management(self):
        bpy.data.scenes[0].display_settings.display_device = 'sRGB'
        bpy.data.scenes[0].view_settings.view_transform = 'Standard'
        bpy.data.scenes[0].view_settings.look = 'None'

    # %% Supporting functions

    @staticmethod
    def apply_texture_data_to_image(image, mat, group, node, node2 = ''):
        '''Sets offset and scale of an image node using the TextureData.json '''
        json_tex_data = c.get_json_file('KK_TextureData.json')
        for item in json_tex_data:
            if item["textureName"] == str(image):
                if bpy.data.materials.get(mat):
                    #Apply Offset and Scale
                    if node2 == '': #Added node2 for the alpha masks
                        bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[0] = item["offset"]["x"]
                        bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[1] = item["offset"]["y"]
                        bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[0] = item["scale"]["x"]
                        bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[1] = item["scale"]["y"]
                    else:
                        bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.translation[0] = item["offset"]["x"]
                        bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.translation[1] = item["offset"]["y"]
                        bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.scale[0] = item["scale"]["x"]
                        bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.scale[1] = item["scale"]["y"]
                    break

    def image_load(self, mat, group, node, image, raw = False):
        '''load an image to a texture node'''
        if bpy.data.images.get(image):
            bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image]
            if raw:
                bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].image.colorspace_settings.name = 'Raw'
            self.apply_texture_data_to_image(image, mat, group, node)
        elif 'MainCol' in image:
            if bpy.data.images[image[0:len(image)-4] + '.dds']:
                bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image[0:len(image)-4] + '.dds']
            c.kklog('.dds and .png files not found, skipping: ' + image[0:len(image)-4] + '.dds')
        else:
            c.kklog('File not found, skipping: ' + image)

    @staticmethod
    def set_uv_type(mat, group, uvnode, uvtype):
            bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[uvnode].uv_map = uvtype

    @staticmethod
    def batch_for_shader(shader, type, content, *, indices=None):
        """
        The batch_for_shader function from Blender 3.3.2
        Return a batch already configured and compatible with the shader.

        :arg shader: shader for which a compatible format will be computed.
        :type shader: :class:`gpu.types.GPUShader`
        :arg type: "'POINTS', 'LINES', 'TRIS' or 'LINES_ADJ'".
        :type type: str
        :arg content: Maps the name of the shader attribute with the data to fill the vertex buffer.
        :type content: dict
        :return: compatible batch
        :rtype: :class:`gpu.types.Batch`
        """
        from gpu.types import (
            GPUBatch,
            GPUIndexBuf,
            GPUVertBuf,
        )

        for data in content.values():
            vbo_len = len(data)
            break
        else:
            raise ValueError("Empty 'content'")

        vbo_format = shader.format_calc()
        vbo = GPUVertBuf(vbo_format, vbo_len)

        for id, data in content.items():
            if len(data) != vbo_len:
                raise ValueError("Length mismatch for 'content' values")
            vbo.attr_fill(id, data)

        if indices is None:
            return GPUBatch(type=type, buf=vbo)
        else:
            ibo = GPUIndexBuf(type=type, seq=indices)
            return GPUBatch(type=type, buf=vbo, elem=ibo)

    @classmethod
    def image_to_KK(cls, image, lut_name):
        self = cls
        width = image.size[0]
        height = image.size[1]

        # Some Sauce
        vertex_default = '''
        in vec2 a_position;
        in vec2 a_texcoord;
        
        in vec4 color;
        out vec4 col;
        
        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
            col = color;
        }
        '''

        # The Secret Sauce
        current_code = '''
        uniform sampler2D tex0;
        uniform sampler2D lut;
        uniform vec2    u_resolution;
        
        in vec4 col;
        out vec4 out_Color;

        vec3 to_srgb(vec3 c){
            c.rgb = max( 1.055 * pow( c.rgb, vec3(0.416666667,0.416666667,0.416666667) ) - 0.055, 0 );
            return c;
        }
        
        vec3 apply_lut(vec3 color) {
            const vec3 coord_scale = vec3(0.0302734375, 0.96875, 31.0);
            const vec3 coord_offset = vec3( 0.5/1024, 0.5/32, 0.0);
            const vec2 texel_height_X0 = vec2( 0.03125, 0.0 );
            
            vec3 coord = color * coord_scale + coord_offset;
            
            vec3 coord_frac = fract( coord );
            vec3 coord_floor = coord - coord_frac;
            vec2 coord_bot = coord.xy + coord_floor.zz * texel_height_X0;
            vec2 coord_top = coord_bot + texel_height_X0;

            vec3 lutcol_bot = texture( lut, coord_bot ).rgb; //Changed from texture2D to texture just in case (apparently depreciated in opengl 3.1?)
            vec3 lutcol_top = texture( lut, coord_top ).rgb;
            
            vec3 lutColor = mix(lutcol_bot, lutcol_top, coord_frac.z);
            
            return lutColor;
        }

        void main() {
            vec4 texRGBA = texture(tex0, gl_FragCoord.xy / u_resolution);

            vec3 texColor = to_srgb(texRGBA.rgb);

            vec3 newColor = apply_lut(texColor);

            newColor = to_srgb(newColor);
            
            out_Color = vec4(newColor.rgb, texRGBA.a);
        }
        '''

        # This object gives access to off screen buffers.
        offscreen = gpu.types.GPUOffScreen(width, height)
        
        # Context manager to ensure balanced bind calls, even in the case of an error.
        # Only run if valid
        with offscreen.bind():
            
            # Clear buffers to preset values
            bgl.glClear(bgl.GL_COLOR_BUFFER_BIT)

            # Initialize the shader
            # GPUShader combines multiple GLSL shaders into a program used for drawing. 
            # It must contain a vertex and fragment shaders, with an optional geometry shader.
            shader = gpu.types.GPUShader(vertex_default, current_code)
            
            # Initialize the shader batch
            # It makes sure that all the vertex attributes necessary for a specific shader are provided.
            batch = modify_material.batch_for_shader(
                shader, 
                'TRI_STRIP', #https://wiki.blender.org/wiki/Reference/Release_Notes/3.2/Python_API for TRI_FAN depreciation
                {
                    'a_position': ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)),
                },
            )

            # Bind the shader object. Required to be able to change uniforms of this shader.
            shader.bind()
            
            bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "tex0"), 0)
            bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "lut"), 1)
                        
            try:
                # Make sure image has a bindcode
                if image.bindcode == 0:
                    for i in range(0, 20):
                        image.gl_load()
                        if image.bindcode != 0:
                            break

                # https://docs.blender.org/api/current/bgl.html
                bgl.glActiveTexture(bgl.GL_TEXTURE0)
                bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)
                bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_EDGE)
                bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_EDGE)
                bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
                bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
                
                # Specify the value of a uniform variable for the current program object. 
                # In this case, an image.
                shader.uniform_int("tex0", 0)
            except ValueError:
                pass
            
            try:
                lut_image = bpy.data.images[lut_name]

                # Make sure image has a bindcode
                if lut_image.bindcode == 0:
                    for i in range(0, 20):
                        lut_image.gl_load()
                        if lut_image.bindcode != 0:
                            break

                # https://docs.blender.org/api/current/bgl.html
                bgl.glActiveTexture(bgl.GL_TEXTURE1)
                bgl.glBindTexture(bgl.GL_TEXTURE_2D, lut_image.bindcode)
                bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_EDGE)
                bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_EDGE)
                bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
                bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
                
                # Specify the value of a uniform variable for the current program object. 
                # In this case, an image.
                shader.uniform_int("lut", 1)
            except ValueError: 
                pass

            try:
                shader.uniform_float('u_resolution', (width, height))
            except ValueError: 
                pass
            
            # Run the drawing program with the parameters assigned to the batch.
            batch.draw(shader)

            # The Buffer object is simply a block of memory that is delineated and initialized by the user.
            buffer = bgl.Buffer(bgl.GL_BYTE, width * height * 4)
            
            # Select a color buffer source for pixels.
            bgl.glReadBuffer(bgl.GL_BACK)
            
            # Read a block of pixels from the frame buffer.
            bgl.glReadPixels(0, 0, width, height, bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, buffer)

        # Free the offscreen object. The framebuffer, texture and render objects will no longer be accessible.
        offscreen.free()

        # Return the final buffer-pixels
        pixels = [v / 255 for v in buffer]
        return pixels, width, height

    def color_to_KK(self, color, lut_name):
        '''Accepts an 8bit int rgba color, returns a 1.0 float rgba'''
        #print(color)
        color = color[:3] #drop alpha
        width = 1
        height = 1

        # Some Sauce
        vertex_default = '''
        in vec2 a_position;
        
        in vec4 color;
        out vec4 col;

        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
            col = color;
        }
        '''

        # The Secret Sauce
        current_code = '''
        uniform vec3 inputColor;
        uniform sampler2D lut;
        
        in vec4 col;
        out vec4 out_Color;

        vec3 to_srgb(vec3 c){
            c.rgb = max( 1.055 * pow( c.rgb, vec3(0.416666667,0.416666667,0.416666667) ) - 0.055, 0 );
            return c;
        }

        void main() {
            vec3 color = inputColor / 255;
            
            const vec3 coord_scale = vec3(0.0302734375, 0.96875, 31.0);
            const vec3 coord_offset = vec3( 0.5/1024, 0.5/32, 0.0);
            const vec2 texel_height_X0 = vec2( 0.03125, 0.0 );
            
            vec3 coord = color * coord_scale + coord_offset;
            
            vec3 coord_frac = fract( coord );
            vec3 coord_floor = coord - coord_frac;
            vec2 coord_bot = coord.xy + coord_floor.zz * texel_height_X0;
            vec2 coord_top = coord_bot + texel_height_X0;

            vec3 lutcol_bot = texture( lut, coord_bot ).rgb;
            vec3 lutcol_top = texture( lut, coord_top ).rgb;
            
            vec3 lutColor = mix(lutcol_bot, lutcol_top, coord_frac.z);
            
            
            vec3 shaderColor = lutColor;
            
            out_Color = vec4(shaderColor.rgb, 1);
        }
        '''

        # This object gives access to off screen buffers.
        offscreen = gpu.types.GPUOffScreen(width, height)
        
        # Context manager to ensure balanced bind calls, even in the case of an error.
        # Only run if valid
        with offscreen.bind():
            
            # Clear buffers to preset values
            bgl.glClear(bgl.GL_COLOR_BUFFER_BIT)

            # Initialize the shader
            # GPUShader combines multiple GLSL shaders into a program used for drawing. 
            # It must contain a vertex and fragment shaders, with an optional geometry shader.
            shader = gpu.types.GPUShader(vertex_default, current_code)
            
            # Initialize the shader batch
            # It makes sure that all the vertex attributes necessary for a specific shader are provided.
            batch = modify_material.batch_for_shader(
                shader, 
                'TRI_STRIP', { #https://wiki.blender.org/wiki/Reference/Release_Notes/3.2/Python_API for TRI_FAN depreciation
                    'a_position': ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1))
                },
            )

            # Bind the shader object. Required to be able to change uniforms of this shader.
            shader.bind()
            
            try:
                # Specify the value of a uniform variable for the current program object. 
                # In this case, a color tuple.
                shader.uniform_float('inputColor', color)
            except ValueError:
                pass
            
            try:
                lut_image = bpy.data.images[lut_name]

                # Make sure image has a bindcode
                if lut_image.bindcode == 0:
                    for i in range(0, 20):
                        lut_image.gl_load()
                        if lut_image.bindcode != 0:
                            break

                # https://docs.blender.org/api/current/bgl.html
                bgl.glBindTexture(bgl.GL_TEXTURE_2D, lut_image.bindcode)
                bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_EDGE)
                bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_EDGE)
                bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
                bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
                
                # Specify the value of a uniform variable for the current program object. 
                # In this case, an image.
                shader.uniform_int("lut", 0)
            except ValueError: 
                pass
            
            # Run the drawing program with the parameters assigned to the batch.
            batch.draw(shader)

            # The Buffer object is simply a block of memory that is delineated and initialized by the user.
            buffer = bgl.Buffer(bgl.GL_BYTE, width * height * 3)
            
            # Select a color buffer source for pixels.
            bgl.glReadBuffer(bgl.GL_BACK)
            
            # Read a block of pixels from the frame buffer.
            bgl.glReadPixels(0, 0, width, height, bgl.GL_RGB, bgl.GL_UNSIGNED_BYTE, buffer)

        # Free the offscreen object. The framebuffer, texture and render objects will no longer be accessible.
        offscreen.free()

        # Get and return the pixels from the final buffer
        final_color = [v for v in buffer]
        final_color = numpy.array(final_color).reshape(width, height, -1)
        return [final_color[0][0][0] / 255, final_color[0][0][1]/ 255, final_color[0][0][2]/ 255, 1] #set alpha to 1, returning rgba

    def update_shaders(self, json, lut_selection, active_lut, light):
        def to_255(color):
            '''converts a 1.0 float rgba dict to a 8bit int rgb'''
            try:
                rgb = [color['r']*255, color['g']*255, color['b']*255]
            except:
                rgb = [color[0], color[1], color[2]] #rgb is already an 8bit int
            #print(color)
            return rgb

        node_groups = bpy.data.node_groups

        ## Body
        body_shader_node_group = node_groups['Body Shader']
        body_colors = []

        ## Face
        face_shader_node_group = node_groups['Face Shader']
        face_colors = []

        ## Eyebrows
        eyebrows_shader_node_group = node_groups['Eyebrows Shader']

        ## Eyeline
        eyeline_shader_node_group = node_groups['Eyeline Shader']
        kage_color = [1, 1, 1, 1]

        ## Tongue
        tongue_shader_node_group = node_groups['Tongue Shader']
        tongue_color1 = to_255({"r":1,"g":1,"b":1,"a":1})
        tongue_color2 = to_255({"r":1,"g":1,"b":1,"a":1})
        tongue_color3 = to_255({"r":1,"g":1,"b":1,"a":1})

        ## Hair
        hair_shader_node_group = node_groups['Hair Shader']
        hair_base_color   = {"r":1,"g":1,"b":1,"a":1}
        hair_root_color   = to_255({"r":1,"g":1,"b":1,"a":1})
        hair_tip_color    = to_255({"r":1,"g":1,"b":1,"a":1})
        hair_shadow_color = {"r":1,"g":1,"b":1,"a":1}
        
        ## All Other Items
        item_data = []
        item_shader_node_groups = []
        
        def entry_exists(material_name):
            for idx, line in enumerate(json):
                if line["MaterialName"] == material_name:
                    return idx
            return -1
        
        ### Get json groups based on shader type, and reformat them to work with the existing script
        supporting_entries = ['Shader Forge/create_body', 'Shader Forge/create_head', 'Shader Forge/create_eyewhite', 'Shader Forge/create_eye', 'Shader Forge/create_topN']
        body = bpy.data.objects['Body']
        body_material_name = body['SMR materials']['o_body_a'][0]
        face_material_name = body['SMR materials']['cf_O_face'][0]
        brow_material_name = body['SMR materials']['cf_O_mayuge'][0]
        eyeline_material_name = body['SMR materials']['cf_O_eyeline'][0]
        kage_material_name = 'cf_m_eyeline_kage'
        tongue_material_names = [body['SMR materials']['o_tang'][0], body['SMR materials']['o_tang_rigged'][0]]
        hair_material_names = []
        for ob in self.hairs:
            hair_material_names.extend([mat.material.name.replace('KK ','') for mat in ob.material_slots])
        
        for idx, line in enumerate(json):
            #Skip supporting entries for now
            if line['ShaderName'] in supporting_entries:
                continue
            
            labels = line['ShaderPropNames']
            data = line['ShaderPropTextures'].copy()
            data.extend(line['ShaderPropTextureValues'])
            data.extend(line['ShaderPropColorValues'])
            data.extend(line['ShaderPropFloatValues'])
            colors = dict(zip(labels, data))
            for entry in colors:
                if '_ShadowColor ' in entry:
                    shadow_color = colors[entry]
                    break
                shadow_color = {"r":0.764,"g":0.880,"b":1,"a":1}
            
            #This is a face entry
            if line['MaterialName'] == face_material_name:
                face_colors.append(self.color_to_KK(to_255(colors["_overcolor1 Color 1"]), active_lut)) #lipstick
                face_colors.append(self.color_to_KK(to_255(colors["_overcolor2 Color 2"]), active_lut)) #Light blush color
                #print('face colors: ' + str(face_colors))
                continue

            #This is a body entry
            if line['MaterialName'] == body_material_name:
                nip_base  = to_255(colors["_overcolor1 Color 1"])
                nip_1     = to_255(colors["_overcolor2 Color 2"])
                nip_2     = to_255(colors["_overcolor3 Color 3"])
                underhair = to_255({"r":0,"g":0,"b":0,"a":1})

                #if this entry has a "create" equivalent, get additional colors from it
                existing_index = entry_exists(line['MaterialName'] + '_create')
                if existing_index == -1:
                    body_light = {"r":1,"g":1,"b":1,"a":1}
                    skin_type  = to_255({"r":1,"g":1,"b":1,"a":1})
                    nail_color = to_255({"r":1,"g":1,"b":1,"a":1})
                else:
                    labels =    json[existing_index]['ShaderPropNames']
                    data   =    json[existing_index]['ShaderPropTextures'].copy()
                    data.extend(json[existing_index]['ShaderPropTextureValues'])
                    data.extend(json[existing_index]['ShaderPropColorValues'])
                    data.extend(json[existing_index]['ShaderPropFloatValues'])
                    colors = dict(zip(labels, data))
                    body_light = colors["_Color Color 0"]
                    skin_type  = to_255(colors["_Color2 Color 1"])
                    nail_color = to_255(colors["_Color5 Color 4"])

                body_colors.append(self.color_to_KK(to_255(body_light), active_lut))    # light body color
                body_colors.append(self.color_to_KK(skin_type,  active_lut))            # skin type color
                body_colors.append(self.color_to_KK(nail_color, active_lut))            # nail color
                body_colors.append(self.color_to_KK(nip_base,   active_lut))            # nip base
                body_colors.append(self.color_to_KK(underhair,  active_lut))            # under hair color
                body_colors.append(self.color_to_KK(to_255(self.skin_dark_color(body_light)), active_lut)) # dark body color
                #print('Body colors: ' + str(body_colors))
                continue

            #This is hair
            if line['MaterialName'] in hair_material_names:
                hair_base_color   = colors["_Color Color 0"]
                hair_shadow_color = shadow_color
                hair_root_color   = to_255(colors["_Color2 Color 1"])
                hair_tip_color    = to_255(colors["_Color3 Color 2"])
                #print('hair colors: ' + str(hair_base_color))
            
            #This is eyeline
            if line['MaterialName'] == eyeline_material_name:
                eyeline_color = to_255(colors["_Color Color 0"])
                continue

            #This is an eyebrow
            if line['MaterialName'] == brow_material_name:
                brow_color = to_255(colors["_Color Color 0"])
                continue
            
            #This is the tongue
            if line['MaterialName'] in tongue_material_names:
                try:
                    tongue_color1 = to_255(colors["_Color Color 0"])
                    tongue_color2 = to_255(colors["_Color2 Color 1"])
                    tongue_color3 = to_255(colors["_Color3 Color 2"])
                except:
                    c.kklog('Could not load tongue colors', 'error')
                    print(colors)
            
            #This is the kage
            if line['MaterialName'] == kage_material_name:
                kage_color = to_255(colors["_Color Color 0"])

            #This is an item
            shader_name = line['MaterialName']
            if (shader_name + ' Shader') in node_groups:
                
                #if this entry has a "create" equivalent, get the rgb colors from it
                existing_index = entry_exists('create_' + shader_name)
                if existing_index == -1:
                    color1 = {"r":0,"g":1,"b":1,"a":1}
                    color2 = {"r":0,"g":1,"b":1,"a":1}
                    color3 = {"r":0,"g":1,"b":1,"a":1}
                    pater1 = {"r":0,"g":1,"b":1,"a":1}
                    pater2 = {"r":0,"g":1,"b":1,"a":1}
                    pater3 = {"r":0,"g":1,"b":1,"a":1}
                else:
                    labels =    json[existing_index]['ShaderPropNames']
                    data   =    json[existing_index]['ShaderPropTextures'].copy()
                    data.extend(json[existing_index]['ShaderPropTextureValues'])
                    data.extend(json[existing_index]['ShaderPropColorValues'])
                    data.extend(json[existing_index]['ShaderPropFloatValues'])
                    colors = dict(zip(labels, data))
                    color1 = colors["_Color Color 0"]
                    color2 = colors["_Color2 Color 2"]
                    color3 = colors["_Color3 Color 4"]
                    pater1 = colors["_Color1_2 Color 1"]
                    pater2 = colors["_Color2_2 Color 3"]
                    pater3 = colors["_Color3_2 Color 5"]

                reformatted_data = {
                    "MaterialName":
                        shader_name,
                    "colorInfo":[
                        color1,
                        color2,
                        color3],
                    "patternColors":[
                        pater1,
                        pater2,
                        pater3],
                    'shadowColor':
                        shadow_color}
                #print(existing_index)
                #print(reformatted_data)
                item_data.append(reformatted_data)
                item_shader_node_groups.append(node_groups[(shader_name + ' Shader')])
                continue

        tongue_color1 = self.color_to_KK(tongue_color1, active_lut)
        tongue_color2 = self.color_to_KK(tongue_color2, active_lut)
        tongue_color3 = self.color_to_KK(tongue_color3, active_lut)

        hair_light      = self.color_to_KK(to_255(hair_base_color), active_lut)
        hair_dark       = self.color_to_KK(to_255(self.clothes_dark_color(color = hair_base_color, shadow_color = hair_shadow_color)), 'Lut_TimeDay.png')
        hair_root_color = self.color_to_KK(hair_root_color, active_lut)
        hair_tip_color  = self.color_to_KK(hair_tip_color, active_lut)

        ### Set shader colors
        ## Body Shader
        shader_inputs = body_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
        shader_inputs['Skin color'].default_value = body_colors[0] if light else body_colors[5]
        shader_inputs['Skin type color'].default_value = body_colors[1]
        shader_inputs['Skin type intensity (Base)'].default_value = 0.5
        shader_inputs['Skin type intensity'].default_value = 1
        shader_inputs['Skin detail color'].default_value = body_colors[1]
        shader_inputs['Skin detail intensity'].default_value = 0.5
        shader_inputs['Nail Color (multiplied)'].default_value = body_colors[2]
        shader_inputs['Skin gloss intensity'].default_value = 0.5

        if not bpy.context.scene.kkbp.sfw_mode:
            shader_inputs['Underhair color'].default_value = body_colors[4]
            shader_inputs['Nipple base'].default_value = body_colors[3]
            shader_inputs['Nipple base 2'].default_value = [1, 0, 0, 1] # Red
            shader_inputs['Nipple shine'].default_value = numpy.array(body_colors[3]) * 1.5
            shader_inputs['Nipple rim'].default_value = numpy.array(body_colors[3]) * 0.5

        ## Face Shader
        shader_inputs = face_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
        shader_inputs['Skin color'].default_value = body_colors[0] if light else body_colors[5]
        shader_inputs['Skin detail color'].default_value = body_colors[1]
        shader_inputs['Light blush color'].default_value = face_colors[1]
        shader_inputs['Mouth interior multiplier'].default_value = [1, 1, 1, 1]
        shader_inputs['Lipstick multiplier'].default_value = face_colors[0]

        ## Eyebrow Shader
        shader_inputs = eyebrows_shader_node_group.nodes['colorsLight'].inputs
        shader_inputs['Light Eyebrow color' if light else 'Dark Eyebrow color'].default_value =  self.color_to_KK(brow_color, active_lut)

        ## Eyeline Shader
        shader_inputs = eyeline_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
        shader_inputs['Eyeline base color'].default_value   = [0, 0, 0, 1]
        shader_inputs['Eyeline fade color'].default_value   = self.color_to_KK(eyeline_color, active_lut)
        shader_inputs['Eyeline shadow color'].default_value = self.color_to_KK(kage_color, active_lut)

        ## Tongue Shader
        shader_inputs = tongue_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
        #shader_inputs['Use Color mask instead? (1 = yes)'].default_value = 1
        shader_inputs['Manually set detail color? (1 = yes)'].default_value = 0
        shader_inputs['Maintex Saturation'].default_value = 0.6
        shader_inputs['Detail intensity (green)'].default_value = 0.01
        shader_inputs['Color mask color (base)'].default_value = [1, 1, 1, 1]
        shader_inputs['Color mask color (red)'].default_value = tongue_color1
        shader_inputs['Color mask color (green)'].default_value = tongue_color2
        shader_inputs['Color mask color (blue)'].default_value = tongue_color3

        ## Hair Shader
        shader_inputs = hair_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
        if lut_selection == 'F' and not light:
            shader_inputs['Dark Hair color'].default_value = hair_dark
        else:
            shader_inputs['Light Hair color' if light else 'Dark Hair color'].default_value = hair_light
        shader_inputs['Light Hair rim color' if light else 'Dark Hair rim color'].default_value = hair_root_color
        shader_inputs['Dark fade color'].default_value  = hair_root_color
        shader_inputs['Light fade color'].default_value = hair_tip_color
        shader_inputs['Manually set the hair color detail? (1 = yes)'].default_value = 0
        shader_inputs['Use fade mask? (1 = yes)'].default_value = 0.5

        ## Accessories/Items Shader
        uses_lut = lut_selection in ['A', 'B', 'C', 'F']
        for idx, item in enumerate(item_data):
            pattern_input_names = [
                'Pattern color (red)',
                'Pattern color (green)',
                'Pattern color (blue)'
            ]

            color_input_names = [
                'Color mask color (red)',
                'Color mask color (green)',
                'Color mask color (blue)'
            ]

            shader_inputs = item_shader_node_groups[idx].nodes['colorsLight' if light else 'colorsDark'].inputs
            if not light and uses_lut:
                shader_inputs['Automatically darken color?'].default_value = 0
            elif not light and lut_selection == 'D':
                shader_inputs['Automatically darken color?'].default_value = 1
                shader_inputs['Auto dark color (low sat.)'].default_value = [0.278491, 0.311221, 0.700000, 1.000000]
                shader_inputs['Auto dark color (high sat.)'].default_value = [0.531185, 0.544296, 0.700000, 1.000000]
            elif not light and lut_selection == 'E':
                shader_inputs['Automatically darken color?'].default_value = 0

            shader_inputs['Manually set detail color? (1 = yes)'].default_value = 0
            shader_inputs['Detail intensity (green)'].default_value = 0.1
            shader_inputs['Detail intensity (blue)'].default_value = 0.1
            #shader_inputs['Use Color mask instead? (1 = yes)'].default_value = 1

            if not light and lut_selection == 'E':
                shader_inputs['Color mask color (base)'].default_value = [0.3, 0.3, 0.3, 0.3]
            else:
                shader_inputs['Color mask color (base)'].default_value = [1, 1, 1, 1]
            
            if lut_selection == 'F' and not light: #automatic dark color replication
                for i, colorItem in enumerate(item['colorInfo']):
                    if i < len(color_input_names):
                        color = colorItem
                        shadow_color = item['shadowColor']
                        #print(color)
                        #print(shadow_color)
                        color_channel = self.color_to_KK(to_255(self.clothes_dark_color(color = color, shadow_color = shadow_color)), 'Lut_TimeDay.png')
                        shader_inputs[color_input_names[i]].default_value = color_channel
                shader_inputs['Use colored maintex?'].default_value = 0
                shader_inputs['Ignore colormask?'].default_value = shader_inputs['Use dark maintex?'].default_value #these should match up
                #doesn't work?
                #shader_inputs['Color mask color (base)'].default_value = [el/255 for el in self.color_to_KK([255*el for el in clothes_dark_color(color = [255, 255, 255], shadow_color = shadow_color)], 'Lut_TimeDay.png'))]
            else:
                for i, colorItem in enumerate(item['colorInfo']):
                    if i < len(color_input_names):
                        color_channel = self.color_to_KK(to_255(colorItem), active_lut)
                        if not light and lut_selection == 'E':
                            color_channel = [x * .3 for x in color_channel]
                        shader_inputs[color_input_names[i]].default_value = color_channel
                #shader_inputs['Ignore colormask?'].default_value = 1

            if not light and lut_selection == 'E':
                shader_inputs['Pattern (base)'].default_value = [0.3, 0.3, 0.3, 0.3]
            else:
                shader_inputs['Pattern (base)'].default_value =  [1, 1, 1, 1]

            for i, patternColor in enumerate(item['patternColors']):
                if i < len(pattern_input_names):
                    color_channel = self.color_to_KK(to_255(patternColor), active_lut)
                    if not light and lut_selection == 'E':
                        color_channel = [x * .3 for x in color_channel]
                    shader_inputs[pattern_input_names[i]].default_value = color_channel

    #something is wrong with this one, currently unused
    def hair_dark_color(self, color, shadow_color):
        diffuse = float4(color[0], color[1], color[2], 1)
        _ShadowColor = float4(shadow_color['r'], shadow_color['g'], shadow_color['b'], 1)

        finalAmbientShadow = 0.7225; #constant
        invertFinalAmbientShadow = finalAmbientShadow #this shouldn't be equal to this but it works so whatever

        finalAmbientShadow = finalAmbientShadow * _ShadowColor
        finalAmbientShadow += finalAmbientShadow;
        shadowCol = _ShadowColor - 0.5;
        shadowCol = -shadowCol * 2 + 1;

        invertFinalAmbientShadow = -shadowCol * invertFinalAmbientShadow + 1;
        shadeCheck = 0.5 < _ShadowColor;
        hlslcc_movcTemp = finalAmbientShadow;
        hlslcc_movcTemp.x = invertFinalAmbientShadow.x if (shadeCheck.x) else finalAmbientShadow.x; 
        hlslcc_movcTemp.y = invertFinalAmbientShadow.y if (shadeCheck.y) else finalAmbientShadow.y; 
        hlslcc_movcTemp.z = invertFinalAmbientShadow.z if (shadeCheck.z) else finalAmbientShadow.z; 
        finalAmbientShadow = (hlslcc_movcTemp).saturate();
        diffuse *= finalAmbientShadow;

        finalDiffuse  = diffuse.saturate();

        shading = 1 - finalAmbientShadow;
        shading = 1 * shading + finalAmbientShadow;
        finalDiffuse *= shading;
        shading = 1.0656;
        finalDiffuse *= shading;

        return [finalDiffuse.x, finalDiffuse.y, finalDiffuse.z];

    def MapValuesMain(self, color):
        '''#mapvaluesmain function is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Skin/KKPDiffuse.cginc'''
        t0 = color;
        tb30 = t0.y>=t0.z;
        t30 = 1 if tb30 else float(0.0);
        t1 = float4(t0.z, t0.y, t0.z, t0.w);
        t2 = float4(t0.y - t1.x,  t0.z - t1.y); 
        t1.z = float(-1.0);
        t1.w = float(0.666666687);
        t2.z = float(1.0);
        t2.w = float(-1.0);
        t1 = float4(t30, t30, t30, t30) * float4(t2.x, t2.y, t2.w, t2.z) + float4(t1.x, t1.y, t1.w, t1.z);
        tb30 = t0.x>=t1.x;
        t30 = 1 if tb30 else 0.0;
        t2.z = t1.w;
        t1.w = t0.x;
        t2 = float4(t1.w, t1.y, t2.z, t1.x)
        t2 = (-t1) + t2;
        t1 = float4(t30, t30, t30, t30) * t2 + t1;
        t30 = min(t1.y, t1.w);
        t30 = (-t30) + t1.x;
        t2.x = t30 * 6.0 + 1.00000001e-10;
        t11 = (-t1.y) + t1.w;
        t11 = t11 / t2.x;
        t11 = t11 + t1.z;
        t1.x = t1.x + 1.00000001e-10;
        t30 = t30 / t1.x;
        t30 = t30 * 0.660000026;
        #w component isn't used anymore so ignore
        t2 = float4(t11, t11, t11).abs() + float4(-0.0799999982, -0.413333356, 0.25333333)
        t2 = t2.frac()
        t2 = (-t2) * float4(2.0, 2.0, 2.0) + float4(1.0, 1.0, 1.0);
        t2 = t2.abs() * float4(3.0, 3.0, 3.0) + float4(-1.0, -1.0, -1.0);
        t2 = t2.clamp()
        t2 = t2 + float4(-1.0, -1.0, -1.0);
        t2 = float4(t30, t30, t30) * t2 + float4(1.0, 1.0, 1.0);
        return float4(t2.x, t2.y, t2.z, 1);

    def skin_dark_color(self, color, shadow_color = None):
        '''Takes a 1.0 max rgba dict and returns a 1.0 max rgba dict. #skin is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Skin/KKPSkinFrag.cginc '''
        diffuse = float4(color['r'], color['g'], color['b'], 1)
        shadingAdjustment = self.MapValuesMain(diffuse);

        diffuseShaded = shadingAdjustment * 0.899999976 - 0.5;
        diffuseShaded = -diffuseShaded * 2 + 1;
        
        compTest = 0.555555582 < shadingAdjustment;
        shadingAdjustment *= 1.79999995;
        diffuseShaded = -diffuseShaded * 0.7225 + 1;
        hlslcc_movcTemp = shadingAdjustment;
        hlslcc_movcTemp.x = diffuseShaded.x if (compTest.x) else shadingAdjustment.x; #370
        hlslcc_movcTemp.y = diffuseShaded.y if (compTest.y) else shadingAdjustment.y; #371
        hlslcc_movcTemp.z = diffuseShaded.z if (compTest.z) else shadingAdjustment.z; #372
        shadingAdjustment = (hlslcc_movcTemp).saturate(); #374 the lerp result (and shadowCol) is going to be this because shadowColor's alpha is always 1 making shadowCol 1

        finalDiffuse = diffuse * shadingAdjustment;
        
        bodyShine = float4(1.0656, 1.0656, 1.0656, 1);
        finalDiffuse *= bodyShine;
        fudge_factor = float4(0.02, 0.05, 0, 0) #result is slightly off but it looks consistently off so add a fudge factor
        finalDiffuse += fudge_factor

        return {'r':finalDiffuse.x, 'g':finalDiffuse.y, 'b':finalDiffuse.z, 'a':1}

    def ShadeAdjustItem(self, col, _ShadowColor):
        '''#shadeadjust function is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Item/KKPItemDiffuse.cginc
    #lines without comments at the end have been copied verbatim from the C# source'''
        #start at line 63
        t0 = col
        t1 = float4(t0.y, t0.z, None, t0.x) * float4(_ShadowColor.y, _ShadowColor.z, None, _ShadowColor.x) #line 65
        t2 = float4(t1.y, t1.x) #66
        t3 = float4(t0.y, t0.z) * float4(_ShadowColor.y, _ShadowColor.z) + (-float4(t2.x, t2.y)); #67
        tb30 = t2.y >= t1.y;
        t30 = 1 if tb30 else 0;
        t2 = float4(t2.x, t2.y, -1.0, 0.666666687); #70-71
        t3 = float4(t3.x, t3.y, 1.0, -1); #72-73
        t2 = (t30) * t3 + t2;
        tb30 = t1.w >= t2.x; 
        t30 = 1 if tb30 else float(0.0);
        t1 = float4(t2.x, t2.y, t2.w, t1.w) #77
        t2 = float4(t1.w, t1.y, t2.z, t1.x) #78
        t2 = (-t1) + t2;
        t1 = (t30) * t2 + t1;
        t30 = min(t1.y, t1.w);
        t30 = (-t30) + t1.x;
        t2.x = t30 * 6.0 + 1.00000001e-10;
        t11 = (-t1.y) + t1.w;
        t11 = t11 / t2.x;
        t11 = t11 + t1.z;
        t1.x = t1.x + 1.00000001e-10;
        t30 = t30 / t1.x;
        t30 = t30 * 0.5;
        #the w component of t1 is no longer used, so ignore it
        t1 = abs((t11)) + float4(0.0, -0.333333343, 0.333333343, 1); #90
        t1 = t1.frac(); #91
        t1 = -t1 * 2 + 1; #92
        t1 = t1.abs() * 3 + (-1) #93
        t1 = t1.clamp() #94
        t1 = t1 + (-1); #95
        t1 = (t30) * t1 + 1; #96
        return float4(t1.x, t1.y, t1.z, 1) #97

    def clothes_dark_color(self, color, shadow_color):
        '''Takes a 1.0 max rgba dict and returns a 1.0 max rgba dict.
        #clothes is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Item/MainItemPlus.shader
        #This was stripped down to just the shadow portion, and to remove all constants'''
        #print(color)
        #print(shadow_color)
        ################### variable setup
        _ambientshadowG = float4(0.15, 0.15, 0.15, 0.15) #constant from experimentation
        diffuse = float4(color['r'],color['g'],color['b'],1) #maintex color
        _ShadowColor = float4(shadow_color['r'],shadow_color['g'],shadow_color['b'],1) #the shadow color from material editor
        ##########################
        
        #start at line 344 because the other one is for outlines
        shadingAdjustment = self.ShadeAdjustItem(diffuse, _ShadowColor)

        #skip to line 352
        diffuseShaded = shadingAdjustment * 0.899999976 - 0.5;
        diffuseShaded = -diffuseShaded * 2 + 1;

        compTest = 0.555555582 < shadingAdjustment;
        shadingAdjustment *= 1.79999995;
        diffuseShaded = -diffuseShaded * 0.7225 + 1; #invertfinalambient shadow is a constant 0.7225, so don't calc it

        hlslcc_movcTemp = shadingAdjustment;
        hlslcc_movcTemp.x = diffuseShaded.x if (compTest.x) else shadingAdjustment.x; #370
        hlslcc_movcTemp.y = diffuseShaded.y if (compTest.y) else shadingAdjustment.y; #371
        hlslcc_movcTemp.z = diffuseShaded.z if (compTest.z) else shadingAdjustment.z; #372
        shadingAdjustment = (hlslcc_movcTemp).saturate(); #374 the lerp result (and shadowCol) is going to be this because shadowColor's alpha is always 1 making shadowCol 1

        diffuseShadow = diffuse * shadingAdjustment;

        # lightCol is constant 1.0656, 1.0656, 1.0656, 1 calculated from the custom ambient of 0.666, 0.666, 0.666, 1 and sun light color 0.666, 0.666, 0.666, 1,
        # so ambientCol always results in lightCol after the max function
        ambientCol = float4(1.0656, 1.0656, 1.0656, 1);
        diffuseShadow = diffuseShadow * ambientCol;
        
        return {'r':diffuseShadow.x, 'g':diffuseShadow.y, 'b':diffuseShadow.z, 'a':1}

    @staticmethod
    def create_darktex(maintex, shadow_color):
        '''    #accepts a bpy image and creates a dark alternate using a modified version of the darkening code above. Returns a new bpy image'''
        if not os.path.isfile(bpy.context.scene.kkbp.import_dir + '/dark_files/' + maintex.name[:-6] + 'DT.png'):
            ok = time.time()
            image_array = numpy.asarray(maintex.pixels)
            image_length = len(image_array)
            image_row_length = int(image_length/4)
            image_array = image_array.reshape((image_row_length, 4))

            ################### variable setup
            _ambientshadowG = numpy.asarray([0.15, 0.15, 0.15, .15]) #constant from experimentation
            diffuse = image_array #maintex color
            _ShadowColor = numpy.asarray([shadow_color[0],shadow_color[1],shadow_color[2], 1]) #the shadow color from material editor
            ##########################
            
            #start at line 344 because the other one is for outlines
            #shadingAdjustment = ShadeAdjustItemNumpy(diffuse, _ShadowColor)
            #start at line 63
            x=0;y=1;z=2;w=3;
            t0 = diffuse
            t1 = t0[:, [y, z, z, x]] * _ShadowColor[[y,z,z,x]]
            t2 = t1[:, [y,x]]
            t3 = t0[:, [y,z]] * _ShadowColor[[y,z]] + (-t2)
            tb30 = t2[:, [y]] >= t1[:, [y]]
            t30 = tb30.astype(int)
            t2 = numpy.hstack((t2[:, [x,y]], numpy.full((t2.shape[0], 1), -1, t2.dtype), numpy.full((t2.shape[0], 1), 0.666666687, t2.dtype))) 
            t3 = numpy.hstack((t3[:, [x,y]], numpy.full((t3.shape[0], 1),  1, t3.dtype), numpy.full((t3.shape[0], 1), -1,          t3.dtype))) 
            t2 = t30 * t3 + t2
            tb30 = t1[:, [w]] >= t1[:, [x]]
            t30 = tb30.astype(int)
            t1 = numpy.hstack((t2[:, [x, y, w]], t1[:, [w]]))
            t2 = numpy.hstack((t1[:, [w, y]], t2[:, [z]], t1[:, [x]]))
            t2 = -t1 + t2
            t1 = t30 * t2 + t1
            t30 = numpy.minimum(t1[:, [y]], t1[:, [w]])
            t30 = -t30 + t1[:, [x]]
            t2[:, [x]] = t30 * 6 + 1.00000001e-10
            t11 = -t1[:, [y]] + t1[:, [w]]
            t11 = t11 / t2[:, [x]];
            t11 = t11 + t1[:, [z]];
            t1[:, [x]] = t1[:, [x]] + 1.00000001e-10;
            t30 = t30 / t1[:, [x]];
            t30 = t30 * 0.5;
            #the w component of t1 is no longer used, so ignore it
            t1 = numpy.absolute(t11) + numpy.asarray([0.0, -0.333333343, 0.333333343, 1]); #90
            t1 = t1 - numpy.floor(t1)
            t1 = -t1 * 2 + 1
            t1 = numpy.absolute(t1) * 3 + (-1)
            t1 = numpy.clip(t1, 0, 1)
            t1 = t1 + (-1); #95
            t1 = (t30) * t1 + 1; #96

            shadingAdjustment = t1

            #skip to line 352
            diffuseShaded = shadingAdjustment * 0.899999976 - 0.5;
            diffuseShaded = -diffuseShaded * 2 + 1;

            compTest = 0.555555582 < shadingAdjustment;
            shadingAdjustment *= 1.79999995;
            diffuseShaded = -diffuseShaded * 0.7225 + 1; #invertfinalambient shadow is a constant 0.7225, so don't calc it

            hlslcc_movcTemp = shadingAdjustment;
            #reframe ifs as selects
            hlslcc_movcTemp[:, [x]] = numpy.select(condlist=[compTest[:, [x]], numpy.invert(compTest[:, [x]])], choicelist=[diffuseShaded[:, [x]], shadingAdjustment[:, [x]]])
            hlslcc_movcTemp[:, [y]] = numpy.select(condlist=[compTest[:, [y]], numpy.invert(compTest[:, [y]])], choicelist=[diffuseShaded[:, [y]], shadingAdjustment[:, [y]]])
            hlslcc_movcTemp[:, [z]] = numpy.select(condlist=[compTest[:, [z]], numpy.invert(compTest[:, [z]])], choicelist=[diffuseShaded[:, [z]], shadingAdjustment[:, [z]]])
            shadingAdjustment = numpy.clip(hlslcc_movcTemp, 0, 1) #374 the lerp result (and shadowCol) is going to be this because shadowColor's alpha is always 1 making shadowCol 1

            diffuseShadow = diffuse * shadingAdjustment;

            # lightCol is constant 1.0656, 1.0656, 1.0656, 1 calculated from the custom ambient of 0.666, 0.666, 0.666, 1 and sun light color 0.666, 0.666, 0.666, 1,
            # so ambientCol always results in lightCol after the max function
            ambientCol = numpy.asarray([1.0656, 1.0656, 1.0656, 1]);
            diffuseShadow = diffuseShadow * ambientCol;

            #make a new image and place the dark pixels into it
            dark_array = diffuseShadow
            darktex = bpy.data.images.new(maintex.name[:-7] + '_DT.png', width=maintex.size[0], height=maintex.size[1])
            darktex.file_format = 'PNG'
            darktex.pixels = dark_array.ravel()
            darktex.use_fake_user = True
            darktex_filename = maintex.filepath_raw[maintex.filepath_raw.find(maintex.name):][:-7]+ '_DT.png'
            darktex_filepath = bpy.context.scene.kkbp.import_dir + '/dark_files/' + darktex_filename
            darktex.filepath_raw = darktex_filepath
            darktex.pack()
            darktex.save()
            c.kklog('Created dark version of {} in {} seconds'.format(darktex.name, time.time() - ok))
            return darktex
        else:
            bpy.ops.image.open(filepath=str(bpy.context.scene.kkbp.import_dir + '/dark_files/' + maintex.name[:-6] + 'DT.png'), use_udim_detecting=False)
            darktex = bpy.data.images[maintex.name[:-6] + 'DT.png']
            c.kklog('A dark version of {} already exists'.format(darktex.name))
            try:
                darktex.pack()
                darktex.save()
            except:
                c.kklog('This image was not automatically loaded in because its name exceeds 64 characters: ' + darktex.name, type = 'error')
            return darktex

class float4:
    '''class to mimic part of float4 class in Unity
    multiplying things per element according to https://github.com/Unity-Technologies/Unity.Mathematics/blob/master/src/Unity.Mathematics/float4.gen.cs#L330
    returning things like float.XZW as [Xposition = X, Yposition = Z, Zposition = W] according to https://github.com/Unity-Technologies/Unity.Mathematics/blob/master/src/Unity.Mathematics/float4.gen.cs#L3056
    using the variable order x, y, z, w according to https://github.com/Unity-Technologies/Unity.Mathematics/blob/master/src/Unity.Mathematics/float4.gen.cs#L42'''
    def __init__(self, x = None, y = None, z = None, w = None):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
    def __mul__ (self, vector):
        #if a float4, multiply piece by piece, else multiply full vector
        if type(vector) in [float, int]:
            vector = float4(vector, vector, vector, vector)
        x = self.x * vector.x if self.get('x') != None else None
        y = self.y * vector.y if self.get('y') != None else None
        z = self.z * vector.z if self.get('z') != None else None
        w = self.w * vector.w if self.get('w') != None else None
        return float4(x,y,z,w)
    __rmul__ = __mul__
    def __add__ (self, vector):
        #if a float4, add piece by piece, else add full vector
        if type(vector) in [float, int]:
            vector = float4(vector, vector, vector, vector)
        x = self.x + vector.x if self.get('x') != None else None
        y = self.y + vector.y if self.get('y') != None else None
        z = self.z + vector.z if self.get('z') != None else None
        w = self.w + vector.w if self.get('w') != None else None
        return float4(x,y,z,w)
    __radd__ = __add__
    def __sub__ (self, vector):
        #if a float4, subtract piece by piece, else subtract full vector
        if type(vector) in [float, int]:
            vector = float4(vector, vector, vector, vector)
        x = self.x - vector.x if self.get('x') != None else None
        y = self.y - vector.y if self.get('y') != None else None
        z = self.z - vector.z if self.get('z') != None else None
        w = self.w - vector.w if self.get('w') != None else None
        return float4(x,y,z,w)
    __rsub__ = __sub__
    def __gt__ (self, vector):
        #if a float4, compare piece by piece, else compare full vector
        if type(vector) in [float, int]:
            vector = float4(vector, vector, vector, vector)
        x = self.x > vector.x if self.get('x') != None else None
        y = self.y > vector.y if self.get('y') != None else None
        z = self.z > vector.z if self.get('z') != None else None
        w = self.w > vector.w if self.get('w') != None else None
        return float4(x,y,z,w)
    def __neg__ (self):
        x = -self.x if self.get('x') != None else None
        y = -self.y if self.get('y') != None else None
        z = -self.z if self.get('z') != None else None
        w = -self.w if self.get('w') != None else None
        return float4(x,y,z,w)
    def frac(self):
        x = self.x - math.floor (self.x) if self.get('x') != None else None
        y = self.y - math.floor (self.y) if self.get('y') != None else None
        z = self.z - math.floor (self.z) if self.get('z') != None else None
        w = self.w - math.floor (self.w) if self.get('w') != None else None
        return float4(x,y,z,w)
    def abs(self):
        x = abs(self.x) if self.get('x') != None else None
        y = abs(self.y) if self.get('y') != None else None
        z = abs(self.z) if self.get('z') != None else None
        w = abs(self.w) if self.get('w') != None else None
        return float4(x,y,z,w)
    def clamp(self):
        x = (0 if self.x < 0 else 1 if self.x > 1 else self.x) if self.get('x') != None else None
        y = (0 if self.y < 0 else 1 if self.y > 1 else self.y) if self.get('y') != None else None
        z = (0 if self.z < 0 else 1 if self.z > 1 else self.z) if self.get('z') != None else None
        w = (0 if self.w < 0 else 1 if self.w > 1 else self.w) if self.get('w') != None else None
        return float4(x,y,z,w)
    saturate = clamp
    def clamphalf(self):
        x = (0 if self.x < 0 else .5 if self.x > .5 else self.x) if self.get('x') != None else None
        y = (0 if self.y < 0 else .5 if self.y > .5 else self.y) if self.get('y') != None else None
        z = (0 if self.z < 0 else .5 if self.z > .5 else self.z) if self.get('z') != None else None
        w = (0 if self.w < 0 else .5 if self.w > .5 else self.w) if self.get('w') != None else None
        return float4(x,y,z,w)
    def get(self, var):
        if hasattr(self, var):
            return getattr(self, var)
        else:
            return None
    def __str__(self):
        return str([self.x, self.y, self.z, self.w])
    __repr__ = __str__

if __name__ == "__main__":
    bpy.utils.register_class(modify_material)

    # test call
    print((bpy.ops.kkbp.modifymaterial('INVOKE_DEFAULT')))
