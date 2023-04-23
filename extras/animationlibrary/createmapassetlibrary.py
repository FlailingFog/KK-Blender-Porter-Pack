#This will take a folder full of map files ripped from the game and create a blender asset library from them

#  Usage instructions:
#  Export koikatsu fbx animation files using https://www.youtube.com/watch?v=PeryYTsAN6E
#  put all the map folders you exported into one folder
#  any subfolder names in that folder will be used to tag them
#       (i.e. /Desktop/all maps/map1/map1 fbx files + textures, then /Desktop/all maps/map2/map2 fbx files + textures, etc )

#  Run this button from the kkbp extras section of the panel
#  You can also do it in small batches and rotate out the already imported fbx files for new ones
#  Or you can put a large list and kill blender when you want to pause the import process (it will resume from where it left off next time you run the script)
#  remember to save the library file when it's done

import bpy, os, time, pathlib
from bpy.props import StringProperty
from ..importstudio import import_studio_objects
from ...importing.importbuttons import kklog, toggle_console
from ...importing.importcolors import load_luts, image_to_KK
from ...importing.darkcolors import create_darktex
from ...interface.dictionary_en import t

def better_fbx_map_import(directory):
    already_loaded_images = [image.name for image in bpy.data.images]
    #import
    path = pathlib.Path(directory).rglob('*')
    obj_list = []
    for item in path:
        if '.fbx' in str(item):
            obj_list.append(str(item))
    for obj in obj_list:
        bpy.ops.better_import.fbx(filepath = obj, my_scale = 1.0)
    
    #if nothing was imported, skip
    if len(bpy.data.objects) < 2:
        return

    #delete duplicate objects and sky mesh
    objs_to_delete = [obj for obj in bpy.data.objects if '.001' in obj.name or '.002' in obj.name or '_koi_sky_' in obj.name]
    for obj in objs_to_delete:
        data_name = obj.data.name
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(bpy.data.meshes[data_name])
    
    #remove all unused slots
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active = bpy.data.objects[1]
    bpy.ops.object.material_slot_remove_unused()
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    
    #setup simple toon shader for all objects
    for obj in [mesh for mesh in bpy.data.objects if mesh.type == 'MESH' and mesh.material_slots[0].material]:
        #if the material already exists, use that, else create it
        try:
            obj.material_slots[0].material = bpy.data.materials['KK ' + obj.material_slots[0].material.name]
            kklog('Material already exists: ' + obj.material_slots[0].material.name)
        except:
            try:
                template = bpy.data.materials['KK Simple'].copy()
            except:
                script_dir=pathlib.Path(__file__).parent.parent
                template_path=(script_dir / '../KK Shader V6.0.blend').resolve()
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
                template = bpy.data.materials['KK Simple'].copy()
            if obj.material_slots[0].material:
                template.name = 'KK ' + obj.material_slots[0].material.name
                new_node = template.node_tree.nodes['Gentex'].node_tree.copy()
                template.node_tree.nodes['Gentex'].node_tree = new_node
                new_node.name = template.name
                main_image_link = [node for node in obj.material_slots[0].material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'][0].inputs[0]
                if main_image_link.is_linked:
                    main_image = main_image_link.links[0].from_node.image
                    #replace the dds image with a png version
                    new_path = main_image.filepath.replace(".dds", ".png").replace(".DDS", ".png")
                    new_image_name = main_image.name.replace(".dds", ".png").replace(".DDS", ".png")
                    main_image.save_render(bpy.path.abspath(new_path))
                    bpy.ops.image.open(filepath=bpy.path.abspath(new_path), use_udim_detecting=False)
                    bpy.data.images[new_image_name].pack()

                    #create darktex
                    bpy.context.scene.kkbp.import_dir = os.path.dirname(bpy.data.filepath) + '\\'
                    main_image = bpy.data.images[new_image_name]
                    dark_image = create_darktex(main_image, [.764, .880, 1])
                    bpy.context.scene.kkbp.import_dir = ''

                    #saturate both with color code
                    lut_light = 'Lut_TimeDay.png'
                    lut_dark = 'Lut_TimeDay.png'
                    load_luts(lut_light, lut_dark)

                    for image in [main_image, dark_image]:
                        print('converting ' + image.name)
                        image.save()
                        image.reload()
                        image.colorspace_settings.name = 'sRGB'
                        image_to_KK(image, lut_light) #run twice because of bug
                        new_pixels, width, height = image_to_KK(image, lut_light)
                        image.pixels = new_pixels
                    
                    #then load it in
                    new_node.nodes['MapMain'].image = main_image
                    new_node.nodes['Darktex'].image = dark_image
                
                norm_image_link = [node for node in obj.material_slots[0].material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'][0].inputs[22]

                if norm_image_link.is_linked:
                    norm_image = norm_image_link.links[0].from_node.inputs[2].links[0].from_node.image
                    new_node.nodes['MapNorm'].image == norm_image
                obj.material_slots[0].material = template

def main(folder):
    #Use the Better FBX importer addon if installed, else fallback to internal fbx importer
    use_better_fbx_importer = 'better_fbx' in [addon.module for addon in bpy.context.preferences.addons]

    toggle_console()
    start = time.time()

    #delete the default scene if present
    if len(bpy.data.objects) == 3:
        for obj in ['Camera', 'Light', 'Cube']:
            if bpy.data.objects.get(obj):
                bpy.data.objects.remove(bpy.data.objects[obj])

    #Set the view transform 
    bpy.context.scene.view_settings.view_transform = 'Standard'
    
    #import the fbx files
    fbx_folders = [(folder + sub) for sub in os.listdir(folder) if '.blend' not in sub] 
    print(fbx_folders)
    for map in fbx_folders:
        category = map.replace(folder, '')
        filename = map
        blend_filepath = map.replace(category,'') + category + '.blend'

        #if a .blend file already exists, don't process this fbx file
        if os.path.exists(blend_filepath):
            continue

        collection = bpy.data.collections.new(category)
        bpy.context.scene.collection.children.link(collection)
        layer_collection = bpy.context.view_layer.layer_collection
        #Recursivly transverse layer_collection for a particular name
        def recurLayerCollection(layerColl, collName):
            found = None
            if (layerColl.name == collName):
                return layerColl
            for layer in layerColl.children:
                found = recurLayerCollection(layer, collName)
                if found:
                    return found
                            
        layerColl = recurLayerCollection(layer_collection, collection.name)
        bpy.context.view_layer.active_layer_collection = layerColl

        #import map object based on Better FBX availability
        if use_better_fbx_importer:
            better_fbx_map_import(map)
        else:
            import_studio_objects(map)

        #skip if this was an empty folder
        if len(bpy.data.objects) < 2:
            bpy.data.collections.remove(collection)
            continue
        
        #apply all armature transforms
        arm = bpy.data.objects['Armature']
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
        #delete armature because the asset browser sucks
        bpy.data.objects.remove(arm)
        bpy.context.view_layer.objects.active = bpy.data.objects[1]
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        #mark the collection as an asset and mark each object as an asset as long as it's not a wall, floor, ceiling or sky mesh
        collection.asset_mark()
        collection.asset_data.description = filename
        collection.asset_data.tags.new(filename)
        collection.asset_data.tags.new(category)

        reject_list = [
            '_yuka',
            '_wall',
            '_kabe',
            '_ten',
            '_black',
            '_yuka',
            'Armature',
            '_sotokabe',
            '_yane',
            '_hana',
            '_kuki',
            '_kusa',
            '_enkei',
            'fensu',
            'gura',
            '_kage',
            '_kmichi',
            '_kmichi',
            '_ie0',
            '_seimon',
            '_shadow',
            'hana_0',
            'kuki_0',
            'kusa_0',
            '_kyusui',
            '_saku',
            '_kumo',
            '_kaidan',
            '_nav',
            'nob',
            '_bushitu',
            'map20_kk00',
            '_styuka00',
            '_ueki0',
            '_kousya',
            '_kanten',
            'map21_light',
            'sky_hoshi',
            '_over',
            '_suido',
            '_kagamiwaku',
            'o_koi_map100h_00_0',
            'o_koi_map100_shawer00_00_0',
            '_kar0',
            'm00_o_box1__0',
            '_reef_tga',
            '_sky_star',
            '_o_tree',
            'o_ikegaki_0',
            'i_stu_kiha',
            'kouen_kakiwari_',
            'kouen_road',
            'kouen_pole',
            'kouen_sibahu',
            'mob_swimclub_',
            'map34_kk0',
            'p34_pool',
            'ap36_kikai',
            '_shitugaiki0',
            '_tatemono',
            'o_koi_map36_03_0',
            'i_mizukri',
            'koi_map17_kk00',
            '_karten',
            'i_gabyou',
            '_pos0',
            '_highyuka',
            'map70_mob',
            '_tesuri',
            'o_soto_doa',
            'o_soto_glass',
            'o_soto_mado',
            'o_koi_map80_00_s_0',
        ]
        for obj in collection.all_objects:
            mark_it = True
            for item in reject_list:
                if item in obj.name:
                    mark_it = False
                    break
            if mark_it:
                #apply transform then mark as asset
                #bpy.ops.object.select_all(action='DESELECT')
                #obj.select_set(True)
                #bpy.context.view_layer.objects.active = obj
                #bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
                obj.asset_mark()
                obj.asset_data.description = filename
                obj.asset_data.tags.new(obj.name)
                obj.asset_data.tags.new(category)

        #hide the collection afterwards
        bpy.context.scene.view_layers[0].active_layer_collection.exclude = True

        #load a script into the layout tab
#         if bpy.data.screens.get('Layout'):
#             for area in bpy.data.screens['Layout'].areas:
#                 if area.type == 'DOPESHEET_EDITOR':
#                     area.ui_type = 'TEXT_EDITOR'
#                     area.spaces[0].text = bpy.data.texts.new(name='Generate previews, save and close')
#                     area.spaces[0].text.write(
# '''#stolen script to generate thumbnails for all objects
# import bpy, functools, time

# assets = [o for o in bpy.data.objects if o.asset_data]  # Select all object assets
# assets.extend([m for m in bpy.data.materials if m.asset_data])  # Select all material assets

# for asset in assets:
#     asset.asset_generate_preview()

# while bpy.app.is_job_running('RENDER_PREVIEW') == True:
#     time.sleep(5)

# bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
# time.sleep(3)
# bpy.ops.wm.quit_blender()

# ''')

        print(blend_filepath)
        bpy.ops.wm.save_as_mainfile(filepath = blend_filepath)
        bpy.data.collections.remove(collection)
        for block in bpy.data.objects:
            bpy.data.objects.remove(block)
        for block in bpy.data.meshes:
            bpy.data.meshes.remove(block)
        for block in bpy.data.materials:
            bpy.data.materials.remove(block)
        for block in bpy.data.armatures:
            bpy.data.armatures.remove(block)
        for block in bpy.data.images:
            bpy.data.images.remove(block)
        for block in bpy.data.node_groups:
            bpy.data.node_groups.remove(block)
        
    print(str(time.time() - start))
    toggle_console()


class map_asset_lib(bpy.types.Operator):
    bl_idname = "kkb.createmapassetlib"
    bl_label = "Create map asset library"
    bl_description = t('map_library_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context):        
        main(self.directory)
        return {'FINISHED'}
        
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
if __name__ == "__main__":
    bpy.utils.register_class(map_asset_lib)
    
    # test call
    print((bpy.ops.kkb.createmapassetlib('INVOKE_DEFAULT')))