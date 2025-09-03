
# This file performs the following operations

#	Remove unused material slots on all objects
#	Remap duplicate material slots on all objects

#	Replace all materials with templates from the KK Shader file
# 	Remove all duplicate node groups after importing everything

# 	Import all textures from .pmx directory
# 	Saturates all main textures and creates dark versions of all main textures
# 	Load all textures to correct spot on all materials
# 	Sets up the normal smoothing geometry nodes group
# 	Sets up drivers to make the gag eye shapekeys work correctly

# 	Load all colors from KK_MaterialDataComplete.json to correct spot on all materials
# 	Adds an outline modifier and outline materials to the face, body, hair and outfit meshes

# Color and image saturation code taken from MediaMoots https://github.com/FlailingFog/KK-Blender-Porter-Pack/blob/ecad6a136e86aaf6c51194705157200797f91e5f/importing/importcolors.py
# Dark color conversion code taken from Xukmi https://github.com/xukmi/KKShadersPlus/tree/main/Shaders


import bpy, os, numpy, math, time, concurrent.futures, threading, queue, bmesh
from pathlib import Path
from .. import common as c
from mathutils import Color

class modify_material(bpy.types.Operator):
    bl_idname = "kkbp.modifymaterial"
    bl_label = bl_idname
    bl_description = bl_idname
    bl_options = {'REGISTER', 'UNDO'}

    #  numpy's precision
    np_number_precision = numpy.float32

    # these three parameters should be exposed in the gui and decided by user

    # This is how many cpu cores you want to use to saturate the images. 
    # If you have a better CPU, you can set it higher.
    kkbp_package_name = __package__[:__package__.rindex('.')]
    max_thread_num = bpy.context.preferences.addons[kkbp_package_name].preferences.max_thread_num

    # this is related to memory usage.
    # Actually it's not perfect because the size of each image varies.
    # If loading four 4096 * 4096, the peak memory usage could reach 16000MB.
    # If the user doesn't have this much available memory, the program will crash.
    # In that case, the user should lower the value
    max_image_num = bpy.context.preferences.addons[kkbp_package_name].preferences.max_image_num

    # this is related to cpu and memory usage.
    # This is the number of rows of pixels to process in one batch (images are saturated in batches).
    # Simply separate images in rows, ignoring that the num of column usually increase as num of rows increasing
    # For a 1024 * 1024, a batch is 512 * 1024.But for 2048 * 2048, a batch is 512 * 2048
    batch_rows = bpy.context.preferences.addons[kkbp_package_name].preferences.batch_rows

    # constants for later
    lut_pixels = None
    coord_scale = None
    coord_offset = None
    texel_height_X0 = None
    # used to protect the data_queue
    queue_lock = threading.Lock()
    data_queue = queue.Queue()

    export_light_dark_material = False

    def execute(self, context):
        try:
            modify_material.export_light_dark_material = c.json_file_manager.get_json_file("KK_KKBPExporterConfig.json").get("exportLightDarkTexture")
            self.remove_unused_material_slots()
            self.remap_duplicate_material_slots()
            self.load_materials()

            if modify_material.export_light_dark_material:
                self.ELDT_load_images()
                self.ELDT_replace_materials_and_link_textures_adjust_UV()

            else:
                self.replace_materials_for_body()
                self.replace_materials_for_hair()
                self.replace_materials_for_outfits()

            self.replace_materials_for_tears_tongue_gageye()

            if not modify_material.export_light_dark_material:
                self.remove_duplicate_node_groups()

                self.load_images()
                self.link_textures_for_face_body()
                self.link_textures_for_hair()
                self.link_textures_for_clothes()
                self.link_textures_for_tongue_tear_gag()
                self.create_dark_textures()

            self.import_and_setup_smooth_normals()
            self.setup_gag_eye_material_drivers()

            self.add_outlines_to_body()
            self.add_outlines_to_hair()
            self.add_outlines_to_clothes()

            if not modify_material.export_light_dark_material:
                self.load_luts()
                self.load_json_colors()

                self.adjust_pupil_highlight()

            self.set_color_management()

            c.clean_orphaned_data()
            return {'FINISHED'}
        except Exception as error:
            c.handle_error(self, error)
            return {"CANCELLED"}

    def init_prefab_data(self):
        '''Initialize constants for saturating textures'''
        modify_material.lut_pixels = numpy.array(bpy.data.images['Lut_TimeDay.png'].pixels[:],dtype=modify_material.np_number_precision).reshape(bpy.data.images['Lut_TimeDay.png'].size[1], bpy.data.images['Lut_TimeDay.png'].size[0], 4)
        #constants to ensure bot and top are within the 32 x 1024 dimensions of the lut
        modify_material.coord_scale = numpy.array([0.0302734375, 0.96875, 31.0],dtype=modify_material.np_number_precision)
        modify_material.coord_offset = numpy.array([0.5 / 1024, 0.5 / 32, 0.0], dtype=modify_material.np_number_precision)
        modify_material.texel_height_X0 = numpy.array([1 / 32, 0], dtype=modify_material.np_number_precision)
        pass

    def load_materials(self):
        templateList = [
            'KK Body',
            'KK Tears',
            'KK Gag00',
            'KK Gag01',
            'KK Gag02',
            'KK EyeR (hitomi)',
            'KK EyeL (hitomi)',
            'KK Eyebrows (mayuge)',
            'KK Eyeline down',
            'KK Eyeline kage',
            'KK Eyeline up',
            'KK Eyewhites (sirome)',
            'KK Face',
            'KK General',
            'KK Hair',
            'KK Nose',
            'KK Teeth (tooth)',
            'KK Simple',
            'KK Glasses',
            'Outline General',
            'Outline Body',
            'KK Light Dark Texture',
            'KK Transparent',
            'KK Light Dark Texture Outline',
            'KK Light Dark Texture Body Outline'
        ]
        c.import_from_library_file(category='Material', list_of_items=templateList, use_fake_user=True)
    # %% Main functions
    def remove_unused_material_slots(self):
        '''Remove unused mat slots on all visible objects'''
        objects = c.get_outfits()
        objects.extend(c.get_alts())
        objects.append(c.get_body)
        objects.extend(c.get_hairs())
        for object in objects:
            try:
                c.switch(object, 'object')
                bpy.ops.object.material_slot_remove_unused()

                #If this is an outfit, and there's only one material slot, check if it's a duplicate material.
                #If it's a duplicate the object actually had no materials to begin with, but the material_slot_remove_unused function left a slot behind
                #This can happen if the outfit does not contain any clothes
                if len(object.material_slots) == 1 and object.get('outfit') and bpy.data.objects.get('Hair ' + object.name):
                    if object.material_slots[0].material.get('id') == bpy.data.objects.get(object.name.replace('Ouftit', 'Hair Outfit')).material_slots[0].material.get('id'):
                        c.kklog(f'No materials detected in outfit "{object.name}". Deleting...', 'warn')
                        bpy.data.objects.remove(object)
            except:
                pass
        c.print_timer('remove_unused_material_slots')

    def remap_duplicate_material_slots(self):
        c.switch(c.get_body(), 'object')
        objects = c.get_outfits()
        objects.extend(c.get_alts())
        objects.append(c.get_body())
        objects.extend(c.get_hairs())


        for obj in objects:
            c.switch(obj, 'object')
            bpy.ops.object.material_slot_remove_unused()
            c.switch(obj, 'edit')
            #combine duplicated material slots
            for mat_name in [o.name for o in obj.data.materials]:
                index = 1
                base_material = bpy.data.materials.get(mat_name)
                while redundant_material := bpy.data.materials.get(f'{mat_name}.{index:03d}'):
                    index += 1
                    redundant_material.user_remap(base_material)
                    bpy.data.materials.remove(redundant_material)

            #then clean material slots by going through each slot and reassigning the slots that are repeated
            repeats = {}
            material_list = obj.data.materials
            for index, mat in enumerate(material_list):
                if mat.name not in repeats:
                    repeats[mat.name] = [index]
                else:
                    repeats[mat.name].append(index)

            for material_name in repeats.keys():
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
        c.print_timer('remap_duplicate_material_slots')

    def replace_materials_for_body(self):
        c.switch(c.get_body(), 'object')
        if bpy.app.version[0] != 3:
            c.get_body().visible_shadow = False

        #Replace all materials on the body with templates
        def swap_body_material(original_materials: list[str], template_name: str):
            c_name = c.get_name()
            #remove dupes and check the material slot actually exists
            original_materials = list(set(original_materials))
            for original_material in original_materials:
                if c.get_body().material_slots.get(original_material):
                    template = bpy.data.materials[template_name].copy()
                    template['body'] = True

                    template['name'] = c_name
                    template['id'] = original_material
                    template['bake'] = True
                    template.name = bpy.data.materials[template_name].name + ' ' + c_name
                    c.get_body().material_slots[original_material].material = template
                    template_group = template.node_tree.nodes['textures'].node_tree.copy()
                    template_group.name = 'Tex ' + original_material + ' ' + c_name
                    template.node_tree.nodes['textures'].node_tree = template_group
                else:
                    c.kklog(f'material or template wasn\'t found when replacing body materials: {str(original_material)} / {str(template_name)}', 'warn')

        swap_body_material(c.get_material_names('cf_O_face'),'KK Face')  # However, some model has multiple textures on face, like nose material. Simply converting all of them to KK Face gets a white face(could be fixed by removing those material slots manually).Meanwhile, face's material name could change, getting face's material by its general name(cf_m_face_00) may fail under some circumstances
        swap_body_material(c.get_material_names('cf_O_mayuge'),'KK Eyebrows (mayuge)')
        swap_body_material(c.get_material_names('cf_O_noseline'),'KK Nose')
        swap_body_material(c.get_material_names('cf_O_eyeline_low'),'KK Eyeline down')
        swap_body_material(c.get_material_names('cf_Ohitomi_L'),'KK Eyewhites (sirome)')
        # swap_body_material(c.get_material_names('cf_Ohitomi_R'),'KK Eyewhites (sirome)')
        swap_body_material(c.get_material_names('cf_Ohitomi_L02'),'KK EyeL (hitomi)')
        swap_body_material(c.get_material_names('cf_Ohitomi_R02'),'KK EyeR (hitomi)')
        swap_body_material(c.get_material_names('o_body_a'),'KK Body')
        swap_body_material(c.get_material_names('cf_O_tooth'),'KK Teeth (tooth)')
        swap_body_material(c.get_material_names('o_tang'),'KK General')

        #Replace the eyeline materials separately
        if c.get_material_names('cf_O_eyeline'):
            swap_body_material([c.get_material_names('cf_O_eyeline')[0]],'KK Eyeline up')
        if len(c.get_material_names('cf_O_eyeline')) > 1:
            swap_body_material([c.get_material_names('cf_O_eyeline')[1]],'KK Eyeline kage')

        c.print_timer('replace_materials_for_body')

    def replace_materials_for_hair(self):
        '''Replace all of the Hair materials with hair templates and name accordingly'''
        c_name = c.get_name()
        for hair in c.get_hairs():
            if bpy.app.version[0] != 3:
                hair.visible_shadow = False
            for material_slot in hair.material_slots:
                original_name = material_slot.material.name
                template = bpy.data.materials['KK Hair'].copy()
                template['hair'] = True

                template['name'] = c_name
                template['bake'] = True
                #Some hair materials are repeated. The order goes 'hair_material', 'hair_material 00', 'hair_material 01', etc.
                #If this happens use the name without numbers or the color information from the json will not be loaded correctly
                if original_name[-2:].isnumeric() and original_name[-3] == ' ':
                    template['id'] = original_name[:-3]
                else:
                    template['id'] = original_name
                template.name = 'KK ' + original_name + ' ' + c_name
                material_slot.material = bpy.data.materials[template.name]

                template_group = template.node_tree.nodes['textures'].node_tree.copy()
                template_group.name = 'Tex ' + original_name + ' ' + c_name
                template.node_tree.nodes['textures'].node_tree = template_group

                template_group_pos = template.node_tree.nodes['textures'].node_tree.nodes['pospattern'].node_tree.copy()
                template_group_pos.name = 'Pos ' + original_name + ' ' + c_name
                template.node_tree.nodes['textures'].node_tree.nodes['pospattern'].node_tree = template_group_pos

        c.print_timer('replace_materials_for_hair')

    def replace_materials_for_outfits(self):
        #Replace all other materials with the general template and name accordingly
        outfits = c.get_outfits()
        outfits.extend(c.get_alts())
        c_name = c.get_name()
        for ob in outfits:
            if bpy.app.version[0] != 3:
                ob.visible_shadow = False
            for material_slot in ob.material_slots:
                original_name = material_slot.material.name
                template = bpy.data.materials['KK General'].copy()
                template['outfit'] = True

                template['name'] = c_name
                template['bake'] = True
                #Some outfit materials are repeated. The order goes 'outfit_material', 'outfit_material 00', 'outfit_material 01', etc.
                #If this happens use the name without numbers or the color information from the json will not be loaded correctly

                if original_name[-2:].isnumeric() and original_name[-3] == ' ':
                    template['id'] = original_name[:-3]
                else:
                    template['id'] = original_name
                template.name = 'KK ' + original_name + ' ' + c_name
                material_slot.material = bpy.data.materials[template.name]

                template_group = template.node_tree.nodes['textures'].node_tree.copy()
                template_group.name = 'Tex ' + original_name + ' ' + c_name
                template.node_tree.nodes['textures'].node_tree = template_group

                template_group_pos = template.node_tree.nodes['textures'].node_tree.nodes['pospattern'].node_tree.copy()
                template_group_pos.name = 'Pos ' + original_name + ' ' + c_name
                template.node_tree.nodes['textures'].node_tree.nodes['pospattern'].node_tree = template_group_pos

        c.print_timer('replace_materials_for_outfits')

    def replace_materials_for_tears_tongue_gageye(self):

        #give the tears a material template
        c_name = c.get_name()
        if tears := c.get_tears():
            template = bpy.data.materials['KK Tears'].copy()
            template.name = 'KK Tears ' + c_name
            template['tears'] = True
            template['id'] = c.get_material_names('cf_O_namida_L')[0]
            tears.material_slots[0].material = bpy.data.materials[template.name]
            template_group = template.node_tree.nodes['textures'].node_tree.copy()
            template.node_tree.nodes['textures'].node_tree = template_group
            template_group.name += ' ' + c_name

        #replace tongue material if it exists
        if c.get_body().material_slots.get('KK General ' + c_name):
            #Make the tongue material unique so parts of the General Template aren't overwritten
            template = bpy.data.materials['KK General'].copy()
            template.name = 'KK Tongue ' + c_name
            template['tongue'] = True
            template['bake'] = True
            # template['id'] = c.get_material_names('o_tang')[0]
            for material_name in c.get_material_names('o_tang'): # avoid getting the deleted material
                if bpy.data.materials.get(material_name):
                    template['id'] = material_name
                    break
            if template.get('id') is None:
                c.kklog('Failed to replace tongue material', 'warn')

            c.get_body().material_slots['KK General ' + c_name].material = template
            template_group = template.node_tree.nodes['textures'].node_tree.copy()
            template.node_tree.nodes['textures'].node_tree = template_group
            template_group.name = 'Tex Tongue ' + c_name
            template_group_pos = template.node_tree.nodes['textures'].node_tree.nodes['pospattern'].node_tree.copy()
            template.node_tree.nodes['textures'].node_tree.nodes['pospattern'].node_tree = template_group_pos
            template_group_pos.name = 'Position Tongue ' + c_name

            #give the rigged tongue the existing material template
            if c.get_tongue():
                c.get_tongue().material_slots[0].material = template

        #give the gag eyes a material template if they exist
        if gag := c.get_gags():
            for num in ['00', '01', '02']:
                template = bpy.data.materials['KK Gag'+num].copy()
                template['gag'] = True
                template['id'] = c.get_material_names('cf_O_gag_eye_'+num)[0]
                gag.material_slots['cf_m_gageye_'+num].material = template
                template.name = 'KK Gag' + num + ' ' + c_name
                template_group = template.node_tree.nodes['textures'].node_tree.copy()
                template.node_tree.nodes['textures'].node_tree = template_group
                template_group.name = 'Tex Gag' + num + ' ' + c_name
        c.print_timer('replace_materials_for_tears_tongue_gageye')

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
        c.print_timer('remove_duplicate_node_groups')

    def ELDT_load_images(self):
        c.switch(c.get_body(), 'object')
        file_dir = Path(bpy.context.scene.kkbp.import_dir)

        files = list(file_dir.rglob('**/pre_light/*'))
        files.extend(list(file_dir.rglob('**/pre_dark/*')))
        files.extend(list(file_dir.rglob('*_AM.png')))
        files.extend(list(file_dir.rglob('*_NMP_CNV.png')))
        files.extend(list(file_dir.rglob('*_NMPD_CNV.png')))

        for file in files:
            bpy.ops.image.open(filepath=str(file), use_udim_detecting=False)
            try:
                bpy.data.images[file.name].pack()
            except:
                c.kklog(
                    'This image was not automatically loaded in because its filename exceeds 64 characters: ' + file.name, type='error')

    def load_images(self):
        c.switch(c.get_body(), 'object')

        file_dir = os.path.dirname(__file__)
        lut_image = os.path.join(file_dir, 'Lut_TimeDay.png')
        lut_image = bpy.data.images.load(str(lut_image))
        self.init_prefab_data()

        fileList = Path(bpy.context.scene.kkbp.import_dir).rglob('*.png')
        files = [file for file in fileList if file.is_file() and "_MT" in file.name]
        unloaded = unprocessed = len(files) # unloaded: unloaded images to saturate, unprocessed: unfinished images that still need to be saturated
        last_miss_time = time.time()  # last time of accessing queue
        current_image_num = 0  # current num of concurrent processing images
        futures = []
        record = {}  # as each image is separated to several batches, this is to record each image's base info

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_thread_num) as executor:
            # the to-output data occupies a lot of memory, so we should save them timely before loading more images
            while unloaded > 0 or unprocessed > 0:
                if (current_time := time.time()) - last_miss_time > 0.3:  # accessing queue every 0.3s, because queue is empty most of the time, so is no need to access it every loop
                    with self.queue_lock:
                        try:
                            while True: # fetching all data from queue if not empty
                                result = self.data_queue.get(timeout=0.1)
                                (result := record[result])[0] -= 1  # data in tuple: (current_image's batch num, name that the image to be saved with, image, image_data in numpy array, start time to process this image)
                                # record[result][0] -= 1
                                if result[0] == 0:
                                    image = result[2]
                                    image_pixels = result[3]
                                    image.pixels.foreach_set(image_pixels.ravel())
                                    image.save_render(os.path.join(bpy.context.scene.kkbp.import_dir, "saturated_files", result[1]))

                                    del image_pixels
                                    unprocessed -= 1
                                    current_image_num -= 1
                                    c.kklog(f'Saturating image {result[1]} takes {round(time.time() - result[4], 1)}s')
                        except queue.Empty:
                            last_miss_time = current_time
                # if there has unloaded images and current num of image in processing is smaller than the max value, then load a image and submit it.This prevent loading too many images, which pushes memory usage to a high level
                if unloaded > 0 and current_image_num < self.max_image_num:
                    unloaded -= 1
                    # skip this file if it has already been converted
                    if os.path.isfile(os.path.join(bpy.context.scene.kkbp.import_dir, 'saturated_files', (save_file_name := files[unloaded].name.replace('_MT', '_ST')))):
                        c.kklog('File already saturated. Skipping {}'.format(files[unloaded].name))
                        unprocessed -= 1
                        continue

                    current_image_num += 1
                    # Load image
                    start_time = time.time()
                    image = bpy.data.images.load(str(files[unloaded]))

                    # Submit task
                    width, height = image.size
                    image_pixels = numpy.array(image.pixels[:], dtype=modify_material.np_number_precision).reshape(height, width, 4)

                    # separating an image to several batches to make full use of CPU
                    start_row = 0
                    while start_row < height:
                        end_row = start_row + self.batch_rows
                        if end_row > height:
                            end_row = height

                        future = executor.submit(
                            self.saturate_texture,
                            unloaded,
                            image_pixels[start_row:end_row - 1]
                        )
                        start_row = end_row

                        futures.append(future)

                    record[unloaded] = [math.ceil(height / self.batch_rows), save_file_name, image, image_pixels, start_time]


            bpy.data.use_autopack = True  # enable autopack on file save

            # Load all textures
            fileList = Path(bpy.context.scene.kkbp.import_dir).rglob('*.png')
            files = [file for file in fileList if file.is_file()]
            for image_file in files:
                bpy.ops.image.open(filepath=str(image_file), use_udim_detecting=False)
                try:
                    bpy.data.images[image_file.name].pack()
                except:
                    c.kklog('This image was not automatically loaded in because its filename exceeds 64 characters: ' + image_file.name, type = 'error')

            # Monitor completion
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    c.kklog(f'Processing failed: {str(e)}')

        c.print_timer('load_images')

    def saturate_texture(self, index, slice_image):
        '''The Secret Sauce. Accepts a bpy image and saturates it to match the in-game look.'''
        # Find the XY coordinates of the LUT image needed to saturate each pixel
        coord = slice_image[:, :, :3] * self.coord_scale + self.coord_offset
        coord_frac, coord_floor = numpy.modf(coord)
        coord_frac_z = coord_frac[:, :, 2:3]
        del coord_frac  # free temporary variables after they're used
        coord_bot = coord[:, :, :2] + coord_floor[:, :, 2:3] * self.texel_height_X0
        del coord
        del coord_floor

        #use those XY coordinates to find the saturated version of the color from the LUT image
        lutcol_bot = self.__bilinear_interpolation__(self.lut_pixels, coord_bot)

        lut_colors = lutcol_bot * (1 - coord_frac_z)
        del lutcol_bot
        coord_top = numpy.clip(coord_bot + self.texel_height_X0, 0, 1)
        lutcol_top = self.__bilinear_interpolation__(self.lut_pixels, coord_top)
        lut_colors += lutcol_top * coord_frac_z
        del lutcol_top
        del coord_top
        slice_image[:, :, :3] = lut_colors[:,:,:3]

        with self.queue_lock:
            self.data_queue.put(index)

    def ELDT_replace_materials_and_link_textures_adjust_UV(self):
        c.import_from_library_file(category='Material', list_of_items=["KK Light Dark Texture"], use_fake_user=True)
        textures = ["_light.png", "_dark.png", "_NMP_CNV.png", "_NMPD_CNV.png", "_AM.png"]

        UV_adjustments = c.json_file_manager.get_json_file("KK_UVAdjustments.json")
        meshes = [('body', c.get_body()), ('tongue', c.get_tongue())]

        def swap_mesh_material(original_material: str, target_material: str, mesh_type: str, mesh):
            c_name = c.get_name()
            # remove dupes and check the material slot actually exists
            if mesh.material_slots.get(original_material):
                template = bpy.data.materials[target_material].copy()
                template[mesh_type] = True

                template['name'] = c_name
                template['id'] = original_material
                template['bake'] = False
                template.name = 'KK ' + original_material
                mesh.material_slots[original_material].material = template
                # template_group = template.node_tree.nodes['textures'].node_tree.copy()
                # template_group.name = 'Tex ' + original_material + ' ' + c_name
                # template.node_tree.nodes['textures'].node_tree = template_group
            else:
                c.kklog(
                    f'material or template wasn\'t found when replacing body materials: {str(original_material)}, {target_material}', 'warn')


        for hair in c.get_hairs():
            meshes.append(('hair', hair))
        for outfit in c.get_outfits():
            meshes.append(('outfit', outfit))

        record = {}
        bm = bmesh.new()
        for mesh_type, mesh in meshes:
            c.switch(mesh, 'OBJECT')
            if mesh.data.uv_layers is None:
                continue
            bm.clear()
            bm.from_mesh(mesh.data)
            for entry in UV_adjustments:
                for index, material_name in enumerate(entry['materials']):
                    if (material_index := mesh.material_slots.find(material_name)) >= 0:
                        record[material_index] = (entry['xOffset'], entry['yOffset'], entry['xScale'], entry['yScale'])
                        # Update the shader

                        swap_mesh_material(material_name, 'KK Light Dark Texture', mesh_type, mesh)
                        material = mesh.material_slots[material_index].material
                        material.node_tree.nodes["UV Scale"].inputs[3].default_value[0] = entry['xScale']
                        material.node_tree.nodes["UV Scale"].inputs[3].default_value[1] = entry['yScale']
                        material.node_tree.nodes["AlphaMask Stage Switch"].outputs[0].default_value = 0 if entry['AlphaMaskAStage'][index] <= 0 else 2

                        for texture_name in textures:
                            if image := bpy.data.images.get(material_name + texture_name):
                                material.node_tree.nodes[texture_name].image = image
                        material.node_tree.update_tag()

            if not (uv_bm_layer := bm.loops.layers.uv.active):
                continue
            # UV transform
            for vert in bm.verts:
                for loop in vert.link_loops:
                    if adjustment_info := record.get(loop.face.material_index):
                        uv = loop[uv_bm_layer].uv
                        uv.x = (uv.x + adjustment_info[0]) / adjustment_info[2]
                        uv.y = (uv.y + adjustment_info[1]) / adjustment_info[3]
            record.clear()
            bm.to_mesh(mesh.data)
            mesh.data.update()

            #  Replace mesh's materials that do not show in the list to transparent
            for material_slot in mesh.material_slots:
                if not material_slot.material.name.startswith('KK '):
                    swap_mesh_material(material_slot.material.name, 'KK Transparent', mesh_type, mesh)

        # Do not forget tongue.001
        if (material_index := c.get_tongue().material_slots.find('cf_m_tang.001')) >= 0:
            swap_mesh_material('cf_m_tang.001', 'KK Light Dark Texture', 'tongue', c.get_tongue())
            for texture_name in textures:
                if image := bpy.data.images.get('cf_m_tang' + texture_name):
                    c.get_tongue().material_slots[material_index].material.node_tree.nodes[texture_name] = image

        # force to update
        bpy.context.view_layer.update()
        bpy.context.evaluated_depsgraph_get().update()

    def link_textures_for_face_body(self):
        '''Load all body textures into their texture slots'''
        self.image_load('Body', '_ST_CT.png')
        self.image_load('Body', '_ST_CT.png', node_override='_ST_DT.png') #attempt to default to light in case dark is not available later on
        #default to colors if there's no maintex
        if c.get_body().material_slots['KK Body ' + c.get_name()].material.node_tree.nodes['textures'].node_tree.nodes['_ST_CT.png'].image.name == 'Template: Placeholder':
            c.get_body().material_slots['KK Body ' + c.get_name()].material.node_tree.nodes['dark' ].inputs['Use main texture instead?'].default_value = 0
            c.get_body().material_slots['KK Body ' + c.get_name()].material.node_tree.nodes['light'].inputs['Use main texture instead?'].default_value = 0
        self.image_load('Body', '_CM.png') #color mask
        self.image_load('Body', '_DM.png') #cfm female
        self.image_load('Body', '_LM.png') #line mask for lips
        self.image_load('Body', '_NMP_CNV.png')
        self.image_load('Body', '_NMPD_CNV.png')
        self.image_load('Body', '_ST.png', group_override='texturesnsfw') #chara main texture
        self.image_load('Body', '_ot2.png', group_override='texturesnsfw') #pubic hair
        self.image_load('Body', '_ot1.png', group_override='texturesnsfw') #cfm female
        self.image_load('Body', '_ot1.png', group_override='texturesnsfw', node_override='_ot1.pngleft')
        self.image_load('Body', '_T3.png') #body overlays
        self.image_load('Body', '_T6.png')
        self.set_uv_type('Body', 'nippleuv', 'uv_nipple_and_shine', group= 'texturesnsfw')
        self.set_uv_type('Body', 'underuv', 'uv_underhair', group= 'texturesnsfw')
        #find the appropriate alpha mask
        alpha_mask = None
        if bpy.data.images.get('_AM.png'):
            alpha_mask = bpy.data.images.get('_AM.png')
        elif bpy.data.images.get('_AM_00.png'):
            alpha_mask = bpy.data.images.get('_AM_00.png')
        else:
            #check the other alpha mask numbers
            for image in bpy.data.images:
                if '_m_body_AM_' in image.name and image.name[-6:-4].isnumeric():
                    alpha_mask = image
                    break
        #if there was an alpha mask detected, load it in
        if alpha_mask:
            self.image_load('Body', image_override = alpha_mask.name, node_override='_AM.png')

        #load in face textures
        if c.get_material_names('cf_O_face'):
            self.image_load('Face', '_ST_CT.png')
            self.image_load('Face', '_ST_CT.png', node_override='_ST_DT.png') #attempt to default to light in case dark is not available
            #default to colors if there's no maintex
            if c.get_body().material_slots['KK Face ' + c.get_name()].material.node_tree.nodes['textures'].node_tree.nodes['_ST_CT.png'].image.name == 'Template: Placeholder':
                c.get_body().material_slots['KK Face ' + c.get_name()].material.node_tree.nodes['light'].inputs['Use main texture instead?'].default_value = 0
                c.get_body().material_slots['KK Face ' + c.get_name()].material.node_tree.nodes['dark' ].inputs['Use main texture instead?'].default_value = 0
            self.image_load('Face', '_CM.png')
            self.image_load('Face', '_DM.png')
            self.image_load('Face', '_T4.png') #blush
            self.image_load('Face', '_ST.png') #mouth interior
            self.image_load('Face', '_LM.png')
            self.image_load('Face', '_T5.png') #lower lip mask
            self.image_load('Face', '_ot1.png') #lipstick
            self.image_load('Face', '_ot2.png') #flush
            self.image_load('Face', '_T3.png')
            self.image_load('Face', '_T7.png')
            self.image_load('Face', '_ot3.png') #eyeshadow
            self.set_uv_type('Face', 'eyeshadowuv', 'uv_eyeshadow')

        #load in the remaining face materials if they exist
        if c.get_material_names('cf_O_mayuge'):
            self.image_load('Eyebrows (mayuge)', '_ST_CT.png')
            self.image_load('Eyebrows (mayuge)', '_ST_CT.png')

        if c.get_material_names('cf_O_noseline'):
            self.image_load('Nose', '_ST_CT.png')
        if c.get_material_names('cf_O_tooth'):
            self.image_load('Teeth (tooth)', '_ST_CT.png')
        if c.get_material_names('cf_Ohitomi_R'):
            self.image_load('Eyewhites (sirome)',  image_override = c.get_material_names('cf_Ohitomi_L')[0] + '_ST_CT.png', node_override = '_ST_CT.png')
            self.image_load('Eyewhites (sirome)',  image_override = c.get_material_names('cf_Ohitomi_R')[0] + '_ST_CT.png', node_override = '_ST_CT.png')

        if c.get_material_names('cf_O_eyeline'):
            self.image_load('Eyeline up', image_override= c.get_material_names('cf_O_eyeline')[0] + '_ST_CT.png', node_override='_ST_CT.png')
        if len(c.get_material_names('cf_O_eyeline')) > 1:
            self.image_load('Eyeline up', image_override=c.get_material_names('cf_O_eyeline')[1] + '_ST_CT.png', node_override='_ST_CT.pngkage')
        if c.get_material_names('cf_O_eyeline_low'):
            self.image_load('Eyeline up', image_override=c.get_material_names('cf_O_eyeline_low')[0] + '_ST_CT.png', node_override='_ST_CT.pngdown')

        #eyes
        for side in ['L', 'R']:
            if c.get_material_names(f'cf_Ohitomi_{side}02'):
                eye_mat = c.get_material_names(f'cf_Ohitomi_{side}02')[0]
                self.image_load(f'Eye{side} (hitomi)', '_ST_CT.png')
                self.image_load(f'Eye{side} (hitomi)', '_ST_CT.png', node_override='_ST_DT.png') #attempt to default to light in case dark is not available
                self.image_load(f'Eye{side} (hitomi)', '_ot1.png')
                self.image_load(f'Eye{side} (hitomi)', '_ot2.png')
                self.image_load(f'Eye{side} (hitomi)', image_override = eye_mat[:-15] + '_cf_t_expression_00_EXPR.png', node_override= '_cf_t_expression_00_EXPR.png')
                self.image_load(f'Eye{side} (hitomi)', image_override = eye_mat[:-15] + '_cf_t_expression_01_EXPR.png', node_override= '_cf_t_expression_01_EXPR.png')

        #correct the eye scaling using info from the KK_ChaFileCustomFace.json
        face_data = c.json_file_manager.get_json_file('KK_ChaFileCustomFace.json')
        bpy.data.node_groups['.Eye Textures positioning'].nodes['eye_scale'].inputs[1].default_value = 1/(float(face_data[18]['Value']) + 0.0001)
        bpy.data.node_groups['.Eye Textures positioning'].nodes['eye_scale'].inputs[2].default_value = 1/(float(face_data[19]['Value']) + 0.0001)

        c.print_timer('link_textures_for_face_body')

    def link_textures_for_hair(self):
        '''Load all hair textures into their texture slots'''
        for current_obj  in c.get_hairs():
            for hairMat in current_obj.material_slots:
                #use the material name instead of hairMat.material['id'] to catch any instances of 00 01 02 materials
                hairType = hairMat.name.replace('KK ','').replace(' ' + c.get_name(), '')

                self.image_load( hairType,  '_ST_CT.png')
                self.image_load( hairType,  '_ST_CT.png', node_override='_ST_DT.png') #attempt to default to light in case dark is not available
                self.image_load( hairType,  '_DM.png')
                self.image_load( hairType,  '_CM.png')
                self.image_load( hairType,  '_HGLS.png')
                self.image_load( hairType,  '_AM.png')
                self.set_uv_type(hairType, 'hairuv', 'uv_nipple_and_shine')

        c.print_timer('link_textures_for_hair')

    def link_textures_for_clothes(self):
        '''Load all clothes textures into their texture slots'''
        outfits = c.get_outfits()
        outfits.extend(c.get_alts())
        for outfit in outfits:
            for genMat in outfit.material_slots:
                #use the material name instead of genMat.material['id'] to catch any instances of 00 01 02 materials
                genType = genMat.name.replace('KK ','').replace(' ' + c.get_name(), '')

                #load these textures if they are present
                self.image_load(genType, '_ST.png')
                self.image_load(genType, '_ST_CT.png')
                self.image_load(genType, '_AM.png')
                self.image_load(genType, '_CM.png')
                self.image_load(genType, '_DM.png')
                self.image_load(genType, '_NMP.png')
                self.image_load(genType, '_NMPD_CNV.png')
                self.image_load(genType, '_PM1.png')
                self.image_load(genType, '_PM2.png')
                self.image_load(genType, '_PM3.png')

                #If there's a plain maintex loaded, but no colored maintex loaded, make the shader use the plain maintex
                plain_but_no_main = (
                    genMat.material.node_tree.nodes['textures'].node_tree.nodes['_ST_CT.png'].image.name == 'Template: Placeholder' and
                    genMat.material.node_tree.nodes['textures'].node_tree.nodes['_ST.png'].image.name != 'Template: Placeholder'
                    )
                if plain_but_no_main:
                    genMat.material.node_tree.nodes['combine'].inputs['Use plain main texture?'].default_value = 1

                #If there's an AnotherRamp (AR) texture present, the material is likely supposed to be metallic on the red parts of the detail mask
                #I don't have a template for this, so the material will just look pure white. Turn off the shine intensity to avoid this
                image_name = genMat.material['id'] + '_AR.png'
                if bpy.data.images.get(image_name):
                    genMat.material.node_tree.nodes['light'].inputs['Detail intensity (shine)'].default_value = 0
                    genMat.material.node_tree.nodes['dark' ].inputs['Detail intensity (shine)'].default_value = 0

                shader_name = c.get_shader_name(genMat.material['id'])

                #If the shader of this material is set to "main opaque" then there is NOT supposed to be a color mask, but the kkbp exporter exports one anyway
                #Move the colormask to the opaque slot if one was loaded in. This way it can still be used by the plain main texture
                if genMat.material.node_tree.nodes['textures'].node_tree.nodes['_CM.png'].image:
                    shaders = ['Koikano/main_clothes_opaque', 'Shader Forge/main_opaque', 'xukmi/MainOpaquePlus', 'xukmi/MainOpaquePlusTess', 'Shader Forge/main_opaque2', 'Shader Forge/main_opaque_low']
                    if shader_name in shaders:
                        c.kklog('Detected opaque shader. Moving color mask to color mask (plain) slot: {}'.format(genMat.material['id']))
                        genMat.material.node_tree.nodes['textures'].node_tree.nodes['_CM.pngopaque'].image = genMat.material.node_tree.nodes['textures'].node_tree.nodes['_CM.png'].image
                        genMat.material.node_tree.nodes['textures'].node_tree.nodes['_CM.png'].image = None

                #If the shader of this material is set to "main alpha", set the material to "blended" in blender
                shaders = ['Shader Forge/main_alpha', 'Koikano/main_clothes_alpha', 'xukmi/MainAlphaPlus', 'xukmi/MainAlphaPlusTess', 'xukmi/MainItemAlphaPlus', 'IBL_Shader_alpha', ]
                #find this material in the MaterialDataComplete.json and see if it's an alpha shader
                if shader_name in shaders:
                    c.kklog('Detected alpha shader. Setting render method to blended: {}'.format(genMat.material['id']))
                    if bpy.app.version[0] == 3:
                        genMat.material.blend_method = 'BLEND'
                    else:
                        genMat.material.surface_render_method = 'BLENDED'

                #If the shader of this material is set to "glasses", replace the entire shader with
                shaders = ['Shader Forge/toon_glasses_lod0', 'Koikano/main_clothes_item_glasses',]
                #find this material in the MaterialDataComplete.json and see if it's a glasses shader
                if shader_name in shaders:
                    c.kklog('Detected glasses shader. Replacing material with KK Glasses: {}'.format(genMat.material['id']))

                    original_textures_group = genMat.material.node_tree.nodes['textures'].node_tree
                    template = bpy.data.materials['KK Glasses'].copy()
                    template.node_tree.nodes['textures'].node_tree = original_textures_group
                    bpy.data.materials.remove(genMat.material)
                    template['bake'] = True
                    template['glasses'] = True
                    template.name = 'KK ' + genType + ' ' + c.get_name()
                    genMat.material = template

                #special exception to clip the emblem image because I am tired of seeing it repeat at the edges
                if 'KK cf_m_emblem ' in genMat.material.name:
                    genMat.material.node_tree.nodes['textures'].node_tree.nodes['_ST_CT.png'].extension = 'CLIP'

        c.print_timer('link_textures_for_clothes')

    def link_textures_for_tongue_tear_gag(self):
        if c.get_tongue() and not modify_material.export_light_dark_material:
            tongue_mat = c.get_material_names('o_tang')
            tongue_mat = tongue_mat if tongue_mat else ['cf_m_tang'] #check for bugged/missing SMR Tongue data
            self.image_load('Tongue', '_CM.png', node_override='_ST_CT.png') #done on purpose
            self.image_load('Tongue', '_CM.png', node_override='_ST_DT.png') #still done on purpose
            self.image_load('Tongue', '_CM.png')
            self.image_load('Tongue', '_DM.png')
            self.image_load('Tongue', '_NMP.png')
            self.image_load('Tongue', '_NMP_CNV.png', node_override = '_NMPD_CNV.png') #load regular map by default
            self.image_load('Tongue', '_NMPD_CNV.png') #then the detail map if it's there

        #load all gag eye textures if it exists
        if c.get_gags():
            self.image_load('Gag00', '_cf_t_gageye_00_ST_CT.png')
            self.image_load('Gag00', '_cf_t_gageye_02_ST_CT.png')
            self.image_load('Gag00', '_cf_t_gageye_04_ST_CT.png')
            self.image_load('Gag00', '_cf_t_gageye_05_ST_CT.png')
            self.image_load('Gag00', '_cf_t_gageye_06_ST_CT.png')
            self.image_load('Gag01', '_cf_t_gageye_03_ST_CT.png')
            self.image_load('Gag01', '_cf_t_gageye_01_ST_CT.png')
            self.image_load('Gag02', '_cf_t_gageye_07_ST_CT.png')
            self.image_load('Gag02', '_cf_t_gageye_08_ST_CT.png')
            self.image_load('Gag02', '_cf_t_gageye_09_ST_CT.png')

        #load the tears texture in
        if c.get_tears():
            self.image_load('Tears', '_ST_CT.png')

        c.print_timer('link_textures_for_tongue_tear_gag')

    def create_dark_textures(self):
        """
        Creates dark versions of textures for body, hair, and outfit materials.

        This method retrieves all body, hair, and outfit materials, and for each material,
        it checks if the material has a 'textures' node and if it contains a '_ST_DT.png' texture.
        If the texture is not a placeholder, it creates a dark version of the texture using the
        shadow color specific to the material and assigns it to the '_ST_DT.png' texture node.
        """
        materials = c.get_body_materials()
        materials.extend(c.get_hair_materials())
        materials.extend(c.get_outfit_materials())
        for material in materials:
            if material.node_tree.nodes.get('textures'):
                if material.node_tree.nodes['textures'].node_tree.nodes.get('_ST_DT.png'):
                    maintex = material.node_tree.nodes['textures'].node_tree.nodes['_ST_CT.png'].image
                    #if this isn't a placeholder image, create a dark version of it
                    if maintex.name != 'Template: Placeholder' and maintex.name != 'cf_m_tang_CM.png':
                        shadow_color = c.json_file_manager.get_shadow_color(material.name)
                        darktex = self.create_darktex(maintex, shadow_color)
                        material.node_tree.nodes['textures'].node_tree.nodes['_ST_DT.png'].image = darktex
        c.print_timer('create_dark_textures')

    def import_and_setup_smooth_normals(self):
        '''Sets up the Smooth Normals geo nodes setup for smoother face, body, hair and clothes normals'''
        try:
            #import all the node groups
            body = c.get_body()
            c.import_from_library_file('NodeTree', ['.Raw Shading (smooth normals)', '.Raw Shading (smooth body normals)', '.Smooth Normals', '.Other Smooth Normals'], bpy.context.scene.kkbp.use_material_fake_user)
            c.switch(body, 'object')
            geo_nodes = body.modifiers.new(name = 'Normal Smoothing', type = 'NODES')
            geo_nodes.node_group = bpy.data.node_groups['.Smooth Normals']
            geo_nodes.show_viewport = False
            geo_nodes.show_render = False
            for ob in c.get_hairs():
                geo_nodes = ob.modifiers.new(name = 'Normal Smoothing', type = 'NODES')
                geo_nodes.node_group = bpy.data.node_groups['.Other Smooth Normals']
                geo_nodes.show_viewport = False
                geo_nodes.show_render = False
            outfits = c.get_outfits()
            outfits.extend(c.get_alts())
            for ob in outfits:
                geo_nodes = ob.modifiers.new(name = 'Normal Smoothing', type = 'NODES')
                geo_nodes.node_group = bpy.data.node_groups['.Other Smooth Normals']
                geo_nodes.show_viewport = False
                geo_nodes.show_render = False
        except:
            #i don't feel like dealing with any errors related to this
            c.kklog('The normal smoothing wasnt setup correctly. Oh well.', 'warn')
        c.print_timer('import_and_setup_smooth_normals')

    def setup_gag_eye_material_drivers(self):
        '''setup gag eye drivers'''
        if c.get_gags():
            body = c.get_body()
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

            def create_driver(material, expression1, expression2):
                skey_driver = bpy.data.materials[material].node_tree.nodes['Parser'].inputs[0].driver_add('default_value')
                skey_driver.driver.type = 'SCRIPTED'
                for key in gag_keys:
                    newVar = skey_driver.driver.variables.new()
                    newVar.name = key.replace(' ','')
                    newVar.type = 'SINGLE_PROP'
                    newVar.targets[0].id_type = 'KEY'
                    newVar.targets[0].id = body.data.shape_keys
                    newVar.targets[0].data_path = 'key_blocks["' + key + '"].value'
                skey_driver.driver.expression = expression1
                skey_driver = bpy.data.materials[material].node_tree.nodes['hider'].inputs[0].driver_add('default_value')
                skey_driver.driver.type = 'SCRIPTED'
                for key in gag_keys:
                    newVar = skey_driver.driver.variables.new()
                    newVar.name = key.replace(' ','')
                    newVar.type = 'SINGLE_PROP'
                    newVar.targets[0].id_type = 'KEY'
                    newVar.targets[0].id = body.data.shape_keys
                    newVar.targets[0].data_path = 'key_blocks["' + key + '"].value'
                skey_driver.driver.expression = expression2

            create_driver (
                'KK Gag00 ' + c.get_name(),
                '0 if CircleEyes1 else 1 if CircleEyes2 else 2 if CartoonyClosed else 3 if VerticalLine else 4',
                'CircleEyes1 or CircleEyes2 or CartoonyClosed or VerticalLine or HorizontalLine'
                )

            create_driver (
                'KK Gag01 ' + c.get_name(),
                '0 if HeartEyes else 1',
                'HeartEyes or SpiralEyes'
                )

            create_driver (
                'KK Gag02 ' + c.get_name(),
                '0 if CartoonyCrying else 1 if CartoonyWink else 2',
                'CartoonyCrying or CartoonyWink or FieryEyes'
                )
        c.print_timer('setup_gag_eye_material_drivers')

    def add_outlines_to_body(self):
        #Add face and body outlines, then load in the clothes transparency mask to body outline
        body = c.get_body()
        c.switch(body, 'object')
        mod = body.modifiers.new(type='SOLIDIFY', name='Outline Modifier')
        mod.thickness = 0.0005
        mod.offset = 0
        mod.material_offset = len(body.material_slots)
        mod.use_flip_normals = True
        mod.use_rim = False
        mod.name = 'Outline Modifier'
        mod.show_expanded = False

        #face first
        if modify_material.export_light_dark_material:
            faceOutlineMat = bpy.data.materials['KK Light Dark Texture Outline'].copy()
            body_outline_mat = bpy.data.materials['KK Light Dark Texture Body Outline'].copy()
            body_material = bpy.data.materials['KK ' + c.get_material_names('cf_O_face')[0]]
            body_outline_mat.node_tree.nodes["_AM.png"].image = bpy.data.images[body_material.node_tree.nodes['_AM.png'].image.name]
            body_outline_mat.node_tree.nodes["UV Scale"].inputs[3].default_value[0] = body_material.node_tree.nodes["UV Scale"].inputs[3].default_value[0]
        else:
            faceOutlineMat = bpy.data.materials['Outline General'].copy()
            body_outline_mat = bpy.data.materials['Outline Body'].copy()
            body_outline_mat.node_tree.nodes['textures'].node_tree = bpy.data.materials['KK Body ' + c.get_name()].node_tree.nodes['textures'].node_tree

        faceOutlineMat.name = 'Outline Face ' + c.get_name()
        body.data.materials.append(faceOutlineMat)
        faceOutlineMat.blend_method = 'CLIP'
        body_outline_mat.name = 'Outline Body ' + c.get_name()
        body.data.materials.append(body_outline_mat)
        c.print_timer('add_outlines_to_body')

    def add_outlines_to_bonelyfans(self):
        # Add outlines to bonelyfans, used for alternative outline
        if bonely := c.get_bonelyfans():
            c.switch(bonely, 'object')
            mod = bonely.modifiers.new(type='SOLIDIFY', name='Outline Modifier')
            mod.thickness = 0.0005
            mod.offset = 0
            mod.material_offset = len(bonely.material_slots)
            mod.use_flip_normals = True
            mod.use_rim = False
            mod.name = 'Outline Modifier'
            mod.show_expanded = False

            if modify_material.export_light_dark_material:
                faceOutlineMat = bpy.data.materials['KK Light Dark Texture Outline'].copy()
                body_outline_mat = bpy.data.materials['KK Light Dark Texture Body Outline'].copy()
                body_material = bpy.data.materials['KK ' + c.get_material_names('cf_O_face')[0]]
                body_outline_mat.node_tree.nodes["_AM.png"].image = bpy.data.images[body_material.node_tree.nodes['_AM.png'].image.name]
                body_outline_mat.node_tree.nodes["UV Scale"].inputs[3].default_value[0] = body_material.node_tree.nodes["UV Scale"].inputs[3].default_value[0]
            else:
                faceOutlineMat = bpy.data.materials['Outline General'].copy()
                body_outline_mat = bpy.data.materials['Outline Body'].copy()
                body_outline_mat.node_tree.nodes['textures'].node_tree = bpy.data.materials['KK Body ' + c.get_name()].node_tree.nodes['textures'].node_tree

            faceOutlineMat.name = 'Outline Face ' + c.get_name() + 'Alternative'
            bonely.data.materials.append(faceOutlineMat)
            faceOutlineMat.blend_method = 'CLIP'
            body_outline_mat.name = 'Outline Body ' + c.get_name() + 'Alternative'
            bonely.data.materials.append(body_outline_mat)

            c.move_and_hide_collection([bonely], 'bonelyfans')
            c.print_timer('add_outlines_to_bonelyfans')

    def add_outlines_to_hair(self):
        #Give each piece of hair with an alphamask on each hair object it's own outline group
        if not bpy.context.scene.kkbp.use_single_outline:
            for ob in c.get_hairs():
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
                if modify_material.export_light_dark_material:
                    for mat in ob.material_slots:
                        AlphaImage = mat.material.node_tree.nodes['_AM.png'].image
                        MainImage = mat.material.node_tree.nodes['_light.png'].image
                        if AlphaImage or MainImage:
                            alpha_users.append(mat.material.name)
                else:
                    for mat in ob.material_slots:
                        AlphaImage = mat.material.node_tree.nodes['textures'].node_tree.nodes['_AM.png'].image
                        MainImage = mat.material.node_tree.nodes['textures'].node_tree.nodes['_ST_CT.png'].image
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

                if modify_material.export_light_dark_material:
                    for index, mat in enumerate(alpha_users):
                        material = bpy.data.materials[mat]
                        OutlineMat = bpy.data.materials['KK Light Dark Texture Outline'].copy()
                        OutlineMat.name = mat.replace('KK ', 'Outline ')
                        OutlineMat.node_tree.nodes["_AM.png"].image = bpy.data.images[material.node_tree.nodes['_AM.png'].image.name]
                        OutlineMat.node_tree.nodes["UV Scale"].inputs[3].default_value[0] = material.node_tree.nodes["UV Scale"].inputs[3].default_value[0]
                        OutlineMat.node_tree.nodes["_light.png"].image = bpy.data.images[material.node_tree.nodes['_light.png'].image.name]
                        ob.material_slots[index + outlineStart].material = OutlineMat
                else:
                    for index, mat in enumerate(alpha_users):
                        OutlineMat = bpy.data.materials['Outline General'].copy()
                        OutlineMat.name = mat.replace('KK ', 'Outline ')
                        OutlineMat.node_tree.nodes['textures'].node_tree = bpy.data.materials[mat].node_tree.nodes['textures'].node_tree
                        ob.material_slots[index + outlineStart].material = OutlineMat
                #update polygon material indexes
                for mat in mats_to_gons:
                    for gon in mats_to_gons[mat]:
                        gon.material_index = new_mat_list_order.index(mat)

        #Add a general outline that covers the rest of the materials on the hair object that don't need transparency
        for ob in c.get_hairs():
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
            hairOutlineMat = bpy.data.materials['Outline General'].copy()
            hairOutlineMat.name = 'Outline Hair ' + c.get_name()
            hairOutlineMat.node_tree.nodes['combine'].inputs['Force visibility'].default_value = 1
            ob.data.materials.append(hairOutlineMat)
        c.print_timer('add_outlines_to_hair')

    def add_outlines_to_clothes(self):
        #Add a standard outline to all other objects
        #keep a dictionary of the material length list for the next loop
        outlineStart = {}
        body = c.get_body()
        c.switch(body, 'object')
        outfits = c.get_outfits()
        outfits.extend(c.get_alts())
        if not bpy.context.scene.kkbp.use_single_outline:
            #If the material has a maintex or alphamask then give it it's own outline
            for ob in outfits:
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
                if modify_material.export_light_dark_material:
                    for mat in ob.material_slots:
                        AlphaImage = mat.material.node_tree.nodes['_AM.png'].image
                        MainImage = mat.material.node_tree.nodes['_light.png'].image
                        if AlphaImage or MainImage:
                            alpha_users.append(mat.material.name)
                else:
                    for mat in ob.material_slots:
                        AlphaImage = mat.material.node_tree.nodes['textures'].node_tree.nodes['_AM.png'].image
                        MainImage = mat.material.node_tree.nodes['textures'].node_tree.nodes['_ST_CT.png'].image
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
                pass
                if modify_material.export_light_dark_material:
                    for index, mat in enumerate(alpha_users):
                        material = bpy.data.materials[mat]
                        OutlineMat = bpy.data.materials['KK Light Dark Texture Outline'].copy()
                        OutlineMat.name = mat.replace('KK ', 'Outline ')
                        OutlineMat.node_tree.nodes["_AM.png"].image = bpy.data.images[material.node_tree.nodes['_AM.png'].image.name]
                        OutlineMat.node_tree.nodes["UV Scale"].inputs[3].default_value[0] = material.node_tree.nodes["UV Scale"].inputs[3].default_value[0]
                        OutlineMat.node_tree.nodes["_light.png"].image = bpy.data.images[material.node_tree.nodes['_light.png'].image.name]
                        ob.material_slots[index + outlineStart[ob.name]].material = OutlineMat

                        # if the outline material is for a glasses material, disable it
                        if bpy.data.materials[mat].get('glasses'):
                            nodes = OutlineMat.node_tree.nodes
                            links = OutlineMat.node_tree.links
                            links.remove(nodes['combine'].inputs['Main texture (alpha)'].links[0])
                else:
                    for index, mat in enumerate(alpha_users):
                        OutlineMat = bpy.data.materials['Outline General'].copy()
                        OutlineMat.name = mat.replace('KK ', 'Outline ')
                        OutlineMat.node_tree.nodes['textures'].node_tree = bpy.data.materials[mat].node_tree.nodes['textures'].node_tree
                        ob.material_slots[index + outlineStart[ob.name]].material = OutlineMat

                        # if the outline material is for a glasses material, disable it
                        if bpy.data.materials[mat].get('glasses'):
                            nodes = OutlineMat.node_tree.nodes
                            links = OutlineMat.node_tree.links
                            links.remove(nodes['combine'].inputs['Main texture (alpha)'].links[0])
                #update polygon material indexes
                for mat in mats_to_gons:
                    for gon in mats_to_gons[mat]:
                        gon.material_index = new_mat_list_order.index(mat)

        for ob in outfits:
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
            outline_mat = bpy.data.materials['Outline General'].copy()
            outline_mat.name = 'Outline ' + ob.name
            outline_mat.node_tree.nodes['combine'].inputs['Force visibility'].default_value = 1
            ob.data.materials.append(outline_mat)
        c.print_timer('add_outlines_to_clothes')

    @classmethod
    def load_luts(cls):
        self = cls
        self.lut_selection = bpy.context.scene.kkbp.colors_dropdown
        self.lut_light = 'Lut_TimeDay.png'

        self.lut_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.lut_light)
        day_lut = bpy.data.images.load(self.lut_path, check_existing=True)
        day_lut.use_fake_user = True


    def load_json_colors(self):
        self.update_shaders('light') # Set light colors
        self.update_shaders('dark') # Set dark colors
        self.make_bonelyfans_transparent() # Make Bonelyfans transparent
        c.print_timer('load_json_colors')

    def set_color_management(self):
        if bpy.app.version[0] != 3:
            #disable shadows in the scene. The toon shading in 4.2 is fucking broken but the broken-ness can be hidden with this setting
            bpy.data.scenes[0].eevee.use_shadows = False
        c.print_timer('set_color_management')

    # %% Supporting functions
    @staticmethod
    def apply_texture_data_to_image(mat: str, image: str, node:str, group = 'textures'):
        '''Sets offset and scale of an image node using the TextureData.json '''
        json_tex_data = c.json_file_manager.get_json_file('KK_TextureData.json')
        texture_data = [t for t in json_tex_data if t["textureName"] == image]
        if texture_data and bpy.data.materials.get(mat):
            #Apply Offset and Scale
            bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[0] = texture_data[0]["offset"]["x"]
            bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[1] = texture_data[0]["offset"]["y"]
            bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[0] = texture_data[0]["scale"]["x"]
            bpy.data.materials[mat].node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[1] = texture_data[0]["scale"]["y"]

    def image_load(self, material_name: str, image_suffix = '', image_override = None, node_override = None, group_override = None):
        '''Automatically load image into mat's texture slot'''
        #get the id from the material
        material_name = 'KK ' + material_name + ' ' + c.get_name()
        material = bpy.data.materials[material_name]
        #get the image name using the id and the suffix
        image_name = image_override if image_override else material['id'] + image_suffix
        #then load the image into the texture slot
        if bpy.data.images.get(image_name):
            node = node_override if node_override else image_name.replace(material['id'], '')
            group = group_override if group_override else 'textures'
            bpy.data.materials[material_name].node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image_name]
            #also apply scaling and offset data to the image
            self.apply_texture_data_to_image(material_name, image_name, node, group)
        else:
            c.kklog('File wasnt found, skipping: ' + image_name)

    @staticmethod
    def set_uv_type(mat: str, uvnode: str, uv_name: str, group = 'textures'):
        bpy.data.materials['KK ' + mat + ' ' + c.get_name()].node_tree.nodes[group].node_tree.nodes['pos'].node_tree.nodes[uvnode].uv_map = uv_name

    @staticmethod
    def __bilinear_interpolation__(lut_pixels, coords):
        h, w, _ = lut_pixels.shape
        x = coords[:, :, 0] * (w - 1)
        # Fudge x coordinates based on x position. subtract -0.5 if at x position 0 and add 0.5 if at x position 1024 of the LUT.
        # this helps with some kind of overflow / underflow issue where it reads from the next LUT square when it's not supposed to
        x = x + (x / 1024 - 0.5)
        y = coords[:, :, 1] * (h - 1)
        # Get integer and fractional parts of each coordinate.
        # Also make sure each coordinate is clipped to the LUT image bounds
        x0 = numpy.clip(numpy.floor(x).astype(int), 0, w - 1)
        x1 = numpy.clip(x0 + 1, 0, w - 1)
        y0 = numpy.clip(numpy.floor(y).astype(int), 0, h - 1)
        y1 = numpy.clip(y0 + 1, 0, h - 1)
        x_frac = x - x0
        y_frac = y - y0
        # Get the pixel values at four corners of this coordinate
        f00 = lut_pixels[y0, x0]
        f01 = lut_pixels[y1, x0]
        f10 = lut_pixels[y0, x1]
        f11 = lut_pixels[y1, x1]
        del x0
        del x1
        del y0
        del y1
        # Perform the bilinear interpolation using the fractional part of each coordinate
        # This will ensure the LUT can provide the correct color every single time, even if that color isn't found in the LUT itself
        # If this isn't performed, the resulting image will look very blocky because it will snap to colors only found in the LUT.
        lut_col_bot = f00 * (1 - y_frac)[:, :, numpy.newaxis] + f01 * y_frac[:, :, numpy.newaxis]
        lut_col_top = f10 * (1 - y_frac)[:, :, numpy.newaxis] + f11 * y_frac[:, :, numpy.newaxis]
        interpolated_colors = lut_col_bot * (1 - x_frac)[:, :, numpy.newaxis] + lut_col_top * x_frac[:, :, numpy.newaxis]
        return interpolated_colors

    def saturate_color(self, color: float, light_pass = 'light', shadow_color = {'r':0.764, 'g':0.880, 'b':1}) -> dict[str, float]:
        '''The Secret Sauce. Accepts a 0-1 float rgba color dict, saturates it to match the in-game look 
        and returns it in the form of a 0-1 float rgba array'''

        #fix the color if it does not have an alpha
        color['a'] = color.get('a', 1)

        #make the color a dark color if the light_pass is set to dark
        color = color if light_pass == 'light' else self.clothes_dark_color(color, shadow_color)
        width, height = 1,1

        # Load image and LUT image pixels into array
        image_pixels = numpy.array([color['r'], color['g'], color['b'], 1],dtype=modify_material.np_number_precision).reshape(height, width, 4)

        # Find the XY coordinates of the LUT image needed to saturate each pixel
        coord = image_pixels[:, :, :3] * self.coord_scale + self.coord_offset
        coord_frac, coord_floor = numpy.modf(coord)
        coord_bot = coord[:, :, :2] + numpy.tile(coord_floor[:, :, 2].reshape(height, width, 1), (1, 1, 2)) * self.texel_height_X0
        coord_top = numpy.clip(coord_bot + self.texel_height_X0, 0, 1)

        lutcol_bot = self.__bilinear_interpolation__(self.lut_pixels, coord_bot)
        lutcol_top = self.__bilinear_interpolation__(self.lut_pixels, coord_top)
        #After the older gpu code uses the texture lookup the colorspace is converted from srgb to linear,
        # so replicate that behavior here.
        def srgb_to_linear(srgb):
            linear_rgb = numpy.where(
                srgb <= 0.04045,
                srgb / 12.92,
                numpy.power((srgb + 0.055) / 1.055, 2.4))
            return linear_rgb
        lutcol_bot = srgb_to_linear(lutcol_bot)
        lutcol_top = srgb_to_linear(lutcol_top)
        lut_colors = lutcol_bot * (1 - coord_frac[:, :, 2].reshape(height, width, 1)) + lutcol_top * coord_frac[:, :, 2].reshape(height, width, 1)
        image_pixels[:, :, :3] = lut_colors[:,:,:3]

        return image_pixels.flatten().tolist()[0:4]


    def update_shaders(self, light_pass: str):
        '''Set the colors for everything. This is run once for the light colors and again for the dark colors'''
        #set the tongue colors if it exists
        #if c.get_material_names('o_tang') and (tongue := c.get_tongue()):
        if c.get_material_names('o_tang') and (tongue := c.get_tongue()):
            shader_inputs = tongue.material_slots[0].material.node_tree.nodes[light_pass].inputs
            shader_inputs['Maintex Saturation'].default_value = 0.6
            shader_inputs['Detail intensity (green)'].default_value = 0.01
            shader_inputs['Color mask (base)'].default_value = [1, 1, 1, 1]
            mat_name = tongue.material_slots[0].name
            shader_inputs['Color mask (red)'].default_value =   self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color "),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(mat_name))
            shader_inputs['Color mask (green)'].default_value = self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color2 "), light_pass, shadow_color = c.json_file_manager.get_shadow_color(mat_name))
            shader_inputs['Color mask (blue)'].default_value =  self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color3 "), light_pass, shadow_color = c.json_file_manager.get_shadow_color(mat_name))

        #set all of the hair colors
        hair_materials = [m for m in bpy.data.materials if m.get('hair') == True and m.get('name') == c.get_name()]
        for hair_material in hair_materials:
            shader_inputs = hair_material.node_tree.nodes[light_pass].inputs
            shader_inputs['Hair color'].default_value         = self.saturate_color(c.json_file_manager.get_color(hair_material.name, "_Color " ),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(hair_material.name))
            shader_inputs['Color mask (root)'].default_value  = self.saturate_color(c.json_file_manager.get_color(hair_material.name, "_Color2 "),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(hair_material.name))
            shader_inputs['Color mask (tip)'].default_value = self.saturate_color(c.json_file_manager.get_color(hair_material.name, "_Color3 "),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(hair_material.name))

        #set body colors
        if c.get_body():
            if c.get_material_names('o_body_a'):
                shader_inputs = c.get_body().material_slots['KK Body ' + c.get_name()].material.node_tree.nodes[light_pass].inputs
                mat_name = 'KK Body ' + c.get_name()
                if light_pass == 'light':
                    shader_inputs['Skin color'].default_value = self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color "), light_pass = 'light')
                else:
                    shader_inputs['Skin color'].default_value = self.saturate_color(self.skin_dark_color(c.json_file_manager.get_color(mat_name, "_Color ")), light_pass = 'light')
                shader_inputs['Detail color'].default_value =               self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color2 " ),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(mat_name))
                shader_inputs['Line mask color'].default_value =            self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color2 " ),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(mat_name)) #use same color for both detail and line
                shader_inputs['Nail color (multiplied)'].default_value =    self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color5 " ),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(mat_name))
                if not bpy.context.scene.kkbp.sfw_mode:
                    shader_inputs['Underhair color'].default_value =        [0, 0, 0, 1]
                    # shader_inputs['Nipple base'].default_value =            [1.0, 0.48, 0.48, 1.0] #these don't seem to be the correct colors. Just use hardcoded colors in .blend file
                    # shader_inputs['Nipple base 2'].default_value =          [0.9, 0.0, 0.1, 1.0]
                    # shader_inputs['Nipple shine'].default_value =           [1.0, 0.8, 0.8, 1.0]
                    # shader_inputs['Nipple rim'].default_value =             [1.0, 0.08, 0.09, 1.0]

            #face
            #Note that some headmods have multiple face materials. This will only replace the first one
            if c.get_material_names('cf_O_face'):
                #setup the face material
                mat_name = 'KK Face ' + c.get_name()
                shader_inputs = c.get_body().material_slots[mat_name].material.node_tree.nodes[light_pass].inputs
                shader_inputs['Skin color'].default_value =             c.get_body().material_slots['KK Body ' + c.get_name()].material.node_tree.nodes[light_pass].inputs['Skin color'].default_value
                shader_inputs['Detail color'].default_value =      self.saturate_color(c.json_file_manager.get_color('KK Body ' + c.get_name(), "_Color2 " ),         light_pass, shadow_color = c.json_file_manager.get_shadow_color('KK Body ' + c.get_name()))
                shader_inputs['Light blush color'].default_value =      self.saturate_color(c.json_file_manager.get_color(mat_name, "_overcolor2 "  ),                light_pass, shadow_color = c.json_file_manager.get_shadow_color(mat_name))
                shader_inputs['Lipstick multiplier'].default_value =    self.saturate_color(c.json_file_manager.get_color(mat_name, "_overcolor1 "  ),                light_pass, shadow_color = c.json_file_manager.get_shadow_color(mat_name))

            #eyebrows
            if c.get_material_names('cf_O_mayuge'):
                mat_name = 'KK Eyebrows (mayuge) ' + c.get_name()
                shader_inputs = c.get_body().material_slots[mat_name].material.node_tree.nodes['light'].inputs
                shader_inputs['Eyebrow color'].default_value =       self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color "))
                shader_inputs['Eyebrow color dark'].default_value =  self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color "),  'dark' , shadow_color = c.json_file_manager.get_shadow_color(mat_name))

            #eyeline
            if c.get_material_names('cf_O_eyeline'):
                mat_name = 'KK Eyeline up ' + c.get_name()
                shader_inputs = c.get_body().material_slots[mat_name].material.node_tree.nodes['light'].inputs
                shader_inputs['Eyeline fade color'].default_value = self.saturate_color(c.json_file_manager.get_color(mat_name, "_Color "),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(mat_name))
                #the below doesn't seem to be the correct color. Use the hardcoded one in the blend file for now
                # if len(c.get_material_names('cf_O_eyeline')) > 1:
                #     shader_inputs['Kage color'].default_value =  self.saturate_color(c.json_file_manager.get_color('KK Eyeline kage ' + c.get_name(), "_Color "),  light_pass, shadow_color = c.json_file_manager.get_shadow_color('KK Eyeline kage ' + c.get_name()))
                if c.get_material_names('cf_O_eyeline_low'):
                    shader_inputs = c.get_body().material_slots[mat_name].material.node_tree.nodes['light'].inputs
                    shader_inputs['Eyeline down fade color'].default_value = self.saturate_color(c.json_file_manager.get_color('KK Eyeline down ' + c.get_name(), "_Color "),  light_pass, shadow_color = c.json_file_manager.get_shadow_color('KK Eyeline down ' + c.get_name()))

        #set the clothes colors
        materials = [m for m in bpy.data.materials if m.get('outfit') == True and m.get('name') == c.get_name()]
        for material in materials:
            shader_inputs = material.node_tree.nodes[light_pass].inputs
            shader_inputs['Color mask (red)'].default_value =       self.saturate_color(c.json_file_manager.get_color(material.name, "_Color "),     light_pass, shadow_color = c.json_file_manager.get_shadow_color(material.name))
            shader_inputs['Color mask (green)'].default_value =     self.saturate_color(c.json_file_manager.get_color(material.name, "_Color2 "),    light_pass, shadow_color = c.json_file_manager.get_shadow_color(material.name))
            shader_inputs['Color mask (blue)'].default_value =      self.saturate_color(c.json_file_manager.get_color(material.name, "_Color3 "),    light_pass, shadow_color = c.json_file_manager.get_shadow_color(material.name))
            shader_inputs['Pattern color (red)'].default_value =    self.saturate_color(c.json_file_manager.get_color(material.name, "_Color1_2 "),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(material.name))
            shader_inputs['Pattern color (green)'].default_value =  self.saturate_color(c.json_file_manager.get_color(material.name, "_Color2_2 "),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(material.name))
            shader_inputs['Pattern color (blue)'].default_value =   self.saturate_color(c.json_file_manager.get_color(material.name, "_Color3_2 "),  light_pass, shadow_color = c.json_file_manager.get_shadow_color(material.name))

    def make_bonelyfans_transparent(self):
        if bonely := bpy.data.materials.get('Bonelyfans'):
            bonely.node_tree.nodes['mmd_shader'].inputs[12].default_value = 0.
        if bonely := bpy.data.materials.get('Bonelyfans.001'):
            bonely.node_tree.nodes['mmd_shader'].inputs[12].default_value = 0.
    #something is wrong with this one, currently unused
    # def hair_dark_color(self, color, shadow_color):
    #     diffuse = float4(color[0], color[1], color[2], 1)
    #     _ShadowColor = float4(shadow_color['r'], shadow_color['g'], shadow_color['b'], 1)

    #     finalAmbientShadow = 0.7225; #constant
    #     invertFinalAmbientShadow = finalAmbientShadow #this shouldn't be equal to this but it works so whatever

    #     finalAmbientShadow = finalAmbientShadow * _ShadowColor
    #     finalAmbientShadow += finalAmbientShadow;
    #     shadowCol = _ShadowColor - 0.5;
    #     shadowCol = -shadowCol * 2 + 1;

    #     invertFinalAmbientShadow = -shadowCol * invertFinalAmbientShadow + 1;
    #     shadeCheck = 0.5 < _ShadowColor;
    #     hlslcc_movcTemp = finalAmbientShadow;
    #     hlslcc_movcTemp.x = invertFinalAmbientShadow.x if (shadeCheck.x) else finalAmbientShadow.x; 
    #     hlslcc_movcTemp.y = invertFinalAmbientShadow.y if (shadeCheck.y) else finalAmbientShadow.y; 
    #     hlslcc_movcTemp.z = invertFinalAmbientShadow.z if (shadeCheck.z) else finalAmbientShadow.z; 
    #     finalAmbientShadow = (hlslcc_movcTemp).saturate();
    #     diffuse *= finalAmbientShadow;

    #     finalDiffuse  = diffuse.saturate();

    #     shading = 1 - finalAmbientShadow;
    #     shading = 1 * shading + finalAmbientShadow;
    #     finalDiffuse *= shading;
    #     shading = 1.0656;
    #     finalDiffuse *= shading;

    #     return [finalDiffuse.x, finalDiffuse.y, finalDiffuse.z];

    def MapValuesMain(self, color): #-> float4
        '''mapvaluesmain function is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Skin/KKPDiffuse.cginc'''
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

    def skin_dark_color(self, color) -> dict[str, float]:
        '''Takes a 1.0 max rgba dict and returns a 1.0 max rgba dict. skin is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Skin/KKPSkinFrag.cginc '''
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

    def ShadeAdjustItem(self, col, _ShadowColor): #-> float4
        '''#shadeadjust function is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Item/KKPItemDiffuse.cginc .
    lines with comments at the end have been translated from C# to python. lines without comments at the end have been copied verbatim from the C# source'''
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

    def clothes_dark_color(self, color: dict, shadow_color: dict) -> dict[str, float]:
        '''Takes a 1.0 max rgba dict and returns a 1.0 max rgba dict.
        clothes is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Item/MainItemPlus.shader
        This was stripped down to just the shadow portion, and to remove all constants'''
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

        # lightCol is constant [1.0656, 1.0656, 1.0656, 1] calculated from the custom ambient of [0.666, 0.666, 0.666, 1] and sun light color [0.666, 0.666, 0.666, 1],
        # so ambientCol always results in lightCol after the max function
        ambientCol = float4(1.0656, 1.0656, 1.0656, 1);
        diffuseShadow = diffuseShadow * ambientCol;

        return {'r':diffuseShadow.x, 'g':diffuseShadow.y, 'b':diffuseShadow.z, 'a':1}

    @staticmethod
    def create_darktex(maintex: bpy.types.Image, shadow_color: float) -> bpy.types.Image:
        '''#accepts a bpy image and creates a dark alternate using a modified version of the darkening code above. Returns a new bpy image'''
        if not os.path.isfile(bpy.context.scene.kkbp.import_dir + '/dark_files/' + maintex.name[:-6] + 'DT.png'):
            ok = time.time()
            image_array = numpy.asarray(maintex.pixels,dtype=modify_material.np_number_precision)
            image_length = len(image_array)
            image_row_length = int(image_length/4)
            image_array = image_array.reshape((image_row_length, 4))

            ################### variable setup
            _ambientshadowG = numpy.asarray([0.15, 0.15, 0.15, 0.15],dtype=modify_material.np_number_precision) #constant from experimentation
            diffuse = image_array #maintex color
            _ShadowColor = numpy.asarray([shadow_color['r'],shadow_color['g'],shadow_color['b'], 1],dtype=modify_material.np_number_precision) #the shadow color from material editor
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

            # lightCol is constant [1.0656, 1.0656, 1.0656, 1] calculated from the custom ambient of [0.666, 0.666, 0.666, 1] and sun light color [0.666, 0.666, 0.666, 1],
            # so ambientCol always results in lightCol after the max function
            ambientCol = numpy.asarray([1.0656, 1.0656, 1.0656, 1],dtype=modify_material.np_number_precision);
            diffuseShadow = diffuseShadow * ambientCol;

            #make a new image and place the dark pixels into it
            dark_array = diffuseShadow
            darktex = bpy.data.images.new(maintex.name[:-7] + '_DT.png', width=maintex.size[0], height=maintex.size[1], alpha = True)
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
            if bpy.app.version[0] == 3:
                bpy.ops.image.open(filepath=str(bpy.context.scene.kkbp.import_dir + '/dark_files/' + maintex.name[:-6] + 'DT.png'), use_udim_detecting=False)
            else:
                bpy.data.images.load(filepath=str(bpy.context.scene.kkbp.import_dir + '/dark_files/' + maintex.name[:-6] + 'DT.png'))
            darktex = bpy.data.images[maintex.name[:-6] + 'DT.png']
            c.kklog('Loading in existing dark version of {}'.format(darktex.name))
            try:
                darktex.pack()
                darktex.save()
            except:
                c.kklog('This image was not automatically loaded in because its name exceeds 64 characters: ' + darktex.name, type = 'error')
            return darktex

    def adjust_pupil_highlight(self):
        data = c.json_file_manager.get_json_file('KK_CharacterInfoData.json')[0]
        if vec0 := data.get('pupilOffset'):
            bpy.data.node_groups[".Eye Textures positioning"].nodes["eye_scale"].inputs[3].default_value = vec0[0] * 50 + 25
            bpy.data.node_groups[".Eye Textures positioning"].nodes["eye_scale"].inputs[4].default_value = vec0[1] * 50 + 25

            vec = data['pupilScale']
            bpy.data.node_groups[".Eye Textures positioning"].nodes["eye_scale"].inputs[1].default_value = vec[0]
            bpy.data.node_groups[".Eye Textures positioning"].nodes["eye_scale"].inputs[2].default_value = vec[1]

            vec = data['highlightUpOffset']
            bpy.data.node_groups[".Eye Textures positioning"].nodes["Group"].inputs[3].default_value = (vec[0] - vec0[0]) * 50 + 25
            bpy.data.node_groups[".Eye Textures positioning"].nodes["Group"].inputs[4].default_value = (vec[1] - vec0[1]) * 50 + 25

            # vec = data['highlightUpScale']
            bpy.data.node_groups[".Eye Textures positioning"].nodes["Group"].inputs[1].default_value = 1
            bpy.data.node_groups[".Eye Textures positioning"].nodes["Group"].inputs[2].default_value = 1

            vec = data['highlightDownOffset']
            bpy.data.node_groups[".Eye Textures positioning"].nodes["Group.001"].inputs[3].default_value = (vec[0] - vec0[0]) * 50 + 25
            bpy.data.node_groups[".Eye Textures positioning"].nodes["Group.001"].inputs[4].default_value = (vec[1] - vec0[1]) * 50 + 25

            # vec = data['highlightDownScale']
            bpy.data.node_groups[".Eye Textures positioning"].nodes["Group.001"].inputs[1].default_value = 1
            bpy.data.node_groups[".Eye Textures positioning"].nodes["Group.001"].inputs[2].default_value = 1

            # No need to set rotation
            # vec = data['eyeRotation']
            # bpy.data.node_groups[".Eye Textures positioning"].nodes["eye_scale"].inputs[5].default_value = math.degrees(vec[0])

            name = c.get_name()
            vec0 = tuple(data['highlightUpColor'])
            vec = tuple(data['highlightDownColor'])
            bpy.data.materials[f"KK EyeL (hitomi) {name}"].node_tree.nodes["light"].inputs[0].default_value = vec0
            bpy.data.materials[f"KK EyeL (hitomi) {name}"].node_tree.nodes["light"].inputs[1].default_value = vec
            bpy.data.materials[f"KK EyeL (hitomi) {name}"].node_tree.nodes["light"].inputs[2].default_value = vec0[3]
            bpy.data.materials[f"KK EyeL (hitomi) {name}"].node_tree.nodes["light"].inputs[3].default_value = vec[3]
            bpy.data.materials[f"KK EyeR (hitomi) {name}"].node_tree.nodes["light"].inputs[0].default_value = vec0
            bpy.data.materials[f"KK EyeR (hitomi) {name}"].node_tree.nodes["light"].inputs[1].default_value = vec
            bpy.data.materials[f"KK EyeR (hitomi) {name}"].node_tree.nodes["light"].inputs[2].default_value = vec0[3]
            bpy.data.materials[f"KK EyeR (hitomi) {name}"].node_tree.nodes["light"].inputs[3].default_value = vec[3]
        c.print_timer('adjust pupil and highlight')

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

