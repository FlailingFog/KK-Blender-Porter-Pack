#This will take a folder full of map files ripped from the game and create a blender asset library from them

#  Usage instructions:
#  Export koikatsu fbx animation files using https://www.youtube.com/watch?v=PeryYTsAN6E
#  put all the map folders you exported into one folder
#  any subfolder names in that folder will be used to tag them (i.e. /Desktop/your main directory/map1/map1 fbx files + textures, then /Desktop/your main directory/map2/map2 fbx files + textures, etc )

#  Run this button from the kkbp extras section of the panel
#  You can also do it in small batches and rotate out the already imported fbx files for new ones
#  remember to save the library file when it's done
#  remember to purge orphan data when it's done

import bpy, os, time
from bpy.props import StringProperty
from ..importstudio import import_studio_objects
def main(folder):
    start = time.time()
    #bpy.ops.object.mode_set(mode = 'OBJECT')

    #import the fbx files
    fbx_folders = [(folder + sub) for sub in os.listdir(folder)] 
    for map in fbx_folders:
        category = map.replace(folder, '')
        filename = map
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
        import_studio_objects(map)

        #apply map armature rotation
        obj = bpy.context.object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)

        #translate names
        name = filename.replace('-p_cf_body_bone-0.fbx', '')
        translation_dict = {
            '_eda':'Chair_',
            'suwari':'Sit',
            'syagami':'Squat',
            'sadou':'Tea',
            'undou':'Excercise',
            'suiei':'Swim',
            'tachi':'Stand',
            'manken':'Read',
            'soine':'Lie',
            'kasa':'Umbrella',
            'konbou':'Club',
            'aruki':'Walk',
            'haruki':'Run',
            'ne_0':'Lie_0',
            'nugi':'Undress',
        }
        for item in translation_dict:
            name = name.replace(item, translation_dict[item])

        #mark the collection as an asset and mark each object as an asset as long as it's not a wall, floor or ceiling
        collection.asset_mark()
        collection.asset_data.description = filename
        collection.asset_data.tags.new(name)
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
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=False)
                obj.asset_mark()
                obj.asset_data.description = filename
                obj.asset_data.tags.new(obj.name)
                obj.asset_data.tags.new(name)
                obj.asset_data.tags.new(category)

        #hide the collection afterwards
        bpy.context.scene.view_layers[0].active_layer_collection.exclude = True

        #save the file for crashes or pausing the imports
        #bpy.ops.wm.save_mainfile()

    print(str(time.time() - start))


class map_asset_lib(bpy.types.Operator):
    bl_idname = "kkb.createmapassetlib"
    bl_label = "Create map asset library"
    bl_description = "Creates an asset library using ripped map data. Open the folder containing the map files exported with SB3Utility. Takes 40 to 500 seconds per map"
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
    print((bpy.ops.kkb.importstudio('INVOKE_DEFAULT')))