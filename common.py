import bpy, json, datetime, traceback
from pathlib import Path

def toggle_console():
    '''toggle the console. will do nothing on Linux or Mac'''
    try:
        bpy.ops.wm.console_toggle()
    except:
        return #only available on windows so it might error out for other platforms

def kklog(log_text: str, type = ''):
    '''Log to the KKBP Log text in the scripting tab. Also prints to console. type can be error or warn'''
    if not bpy.data.texts.get('KKBP Log'):
        bpy.data.texts.new(name='KKBP Log')
        if bpy.data.screens.get('Scripting'):
            for area in bpy.data.screens['Scripting'].areas:
                if area.type == 'TEXT_EDITOR':
                    area.spaces[0].text = bpy.data.texts['KKBP Log']
                    bpy.data.texts['KKBP Log'].write('====    KKBP Log    ====\n')
    if type == 'error':
        log_text = '\nError:          ' + str(log_text)
    elif type == 'warn':
        log_text = 'Warning:        ' + str(log_text)
    bpy.data.texts['KKBP Log'].write(str(log_text) + '\n')
    print(str(log_text))

def set_viewport_shading(type = 'MATERIAL'):
    '''set the viewport shading in the layout tab. Accepts 'WIREFRAME' 'SOLID' 'MATERIAL' or 'RENDERED' '''
    for area in bpy.context.workspace.screens[0].areas:
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = type

def get_json_file(filename: str) -> json:
    '''Returns the json file by filename. Include the .json in the filename argument'''
    files = [file for file in Path(bpy.context.scene.kkbp.import_dir).glob('*.json') if filename in str(file)]
    if files:
        json_file_path = str(files[0])
        json_file = open(json_file_path)
        json_data = json.load(json_file)
        return json_data

def get_hairs() -> list[bpy.types.Object]:
    '''Returns a list of all the hair objects for this import'''
    hairs = [o for o in bpy.data.objects if o.type == 'MESH' and o.get('hair') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return hairs

def get_outfits() -> list[bpy.types.Object]:
    '''Returns a list of all the outfit objects for this import'''
    outfits = [o for o in bpy.data.objects if o.type == 'MESH' and o.get('outfit') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return outfits

def get_alts() -> list[bpy.types.Object]:
    '''Returns a list of all the alternate outfit objects for this import'''
    alts = [o for o in bpy.data.objects if o.type == 'MESH' and o.get('alt') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return alts

def get_hitboxes() -> list[bpy.types.Object]:
    '''Returns a list of all the hitbox objects for this import'''
    hits = [o for o in bpy.data.objects if o.type == 'MESH' and o.get('hitbox') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return hits

def get_body() -> bpy.types.Object:
    '''Returns the body object for this import'''
    bodies = [o for o in bpy.data.objects if o.get('body') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return bodies[0] if bodies else None

def get_armature() -> bpy.types.Object:
    '''Returns the armature object for this import'''
    arms = [o for o in bpy.data.objects if o.get('armature') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return arms[0] if arms else None

def get_rig() -> bpy.types.Object:
    '''Returns the rigify armature object for this import'''
    arms = [o for o in bpy.data.objects if o.get('rig') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return arms[0] if arms else None

def get_empties() -> list[bpy.types.Object]:
    '''Returns a list of all empty objects for this import'''
    empties = [o for o in bpy.data.objects if o.type == 'EMPTY' and o.get('name') == bpy.context.scene.kkbp.character_name]
    return empties

def get_tears() -> bpy.types.Object:
    '''Returns the tears object for this import'''
    tears = [o for o in bpy.data.objects if o.get('tears') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return tears[0] if tears else None

def get_gags() -> bpy.types.Object:
    '''Returns the gag eyes object for this import'''
    gags = [o for o in bpy.data.objects if o.get('gag') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return gags[0] if gags else None

def get_tongue() -> bpy.types.Object:
    '''Returns the rigged tongue object for this import'''
    tongues = [o for o in bpy.data.objects if o.get('tongue') and o.get('name') == bpy.context.scene.kkbp.character_name]
    return tongues[0] if tongues else None

def get_all_objects() -> list[bpy.types.Object]:
    '''Returns all objects associated with this import'''
    everything = get_outfits()
    everything.extend(get_alts())
    everything.append(get_body())
    everything.extend(get_hairs())
    everything.append(get_tears())
    everything.append(get_gags())
    everything.append(get_tongue())
    return everything

def get_all_bakeable_objects() -> list[bpy.types.Object]:
    '''Returns all objects associated with this import that can be baked'''
    everything = get_outfits()
    everything.extend(get_alts())
    everything.append(get_body())
    everything.extend(get_hairs())
    return everything

def get_name() -> str:
    '''Returns the character name'''
    return bpy.context.scene.kkbp.character_name

def get_import_path() -> str:
    '''Returns the import path'''
    return bpy.context.scene.kkbp.import_dir

def get_material_names(smr_name: str) -> list[str]:
    '''Returns a list of the material names this smr object is using'''
    material_data = get_json_file('KK_MaterialDataComplete.json')
    material_infos = [m['MaterialInformation'] for m in material_data if m.get('MaterialInformation') and m.get('SMRName') == smr_name]
    materials = []
    for material_info in material_infos:
        materials.extend([m['MaterialName'] for m in material_info if m.get('MaterialName')])
    #remove dupes and sort
    materials = list(set(materials))
    return sorted(materials)

def get_shader_name(material_name: str) -> str:
    '''Returns the shader name for this material'''
    material_data = get_json_file('KK_MaterialDataComplete.json')
    material_infos = [m['MaterialInformation'] for m in material_data if m.get('MaterialInformation')]
    shaders = []
    for material_info in material_infos:
        shaders.extend([m.get('ShaderName') for m in material_info if m.get('MaterialName') == material_name])
    return shaders[0] if shaders else None

def get_color(material_name: str, color: str) -> dict[float]:
    '''Find the material material_name and return an RGBA dict list of the specified color ranging from 0-1. If material_name contains a space and the character name, it will be filtered out.'''
    material_name = bpy.data.materials[material_name].get('id')
    if material_name:
        material_data = get_json_file('KK_MaterialDataComplete.json')
        material_infos = [m['MaterialInformation'] for m in material_data if m.get('MaterialInformation')]
        #get all the colors
        material_colors = []
        for material_info in material_infos:
            material_colors.extend([m for m in material_info if m.get('MaterialName') == material_name])
        for material_color in material_colors:
            #then zip them and find the shadow color
            color_dict = zip(material_color['ShaderPropNames'], material_color['ShaderPropColorValues'])
            #key names are not consistent, so look through all of them
            for pair in color_dict:
                if color in pair[0]:
                    return pair[1]
    kklog(f"Couldn't find {color} for {material_name}", 'warn')
    return {'r':1, 'g':1, 'b':1, 'a':1}

def get_shadow_color(material_name: str) -> dict[float]:
    '''Find the material material_name and return an RGBA float list ranging from 0-1'''
    #get original name
    material_name = bpy.data.materials[material_name].get('id')
    if material_name:
        material_data = get_json_file('KK_MaterialDataComplete.json')
        material_infos = [m['MaterialInformation'] for m in material_data if m.get('MaterialInformation')]
        #get all the shadow colors
        material_colors = []
        for material_info in material_infos:
            material_colors.extend([m for m in material_info if m.get('MaterialName') == material_name])
        for material_color in material_colors:
            #then zip them and find the shadow color
            color_dict = zip(material_color['ShaderPropNames'], material_color['ShaderPropColorValues'])
            #key names are not consistent, so look through all of them
            for pair in color_dict:
                if '_shadowcolor' in pair[0].lower():
                    return pair[1]
    #return a default color if not found
    kklog(f'Couldn\'t find shadow color for {material_name}', 'warn')
    return {'r':0.764, 'g':0.880, 'b':1}

def get_body_materials() -> list[bpy.types.Material]:
    '''Returns a list of all the body materials'''
    materials = [m for m in bpy.data.materials if m.get('body') and m.get('name') == bpy.context.scene.kkbp.character_name]
    return materials

def get_hair_materials() -> list[bpy.types.Material]:
    '''Returns a list of all the body materials'''
    materials = [m for m in bpy.data.materials if m.get('hair') and m.get('name') == bpy.context.scene.kkbp.character_name]
    return materials

def get_outfit_materials() -> list[bpy.types.Material]:
    '''Returns a list of all the outfit materials'''
    materials = [m for m in bpy.data.materials if m.get('outfit') and m.get('name') == bpy.context.scene.kkbp.character_name]
    return materials

def initialize_timer():
    bpy.context.scene.kkbp.total_timer = datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6
    bpy.context.scene.kkbp.timer = datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6

def reset_timer():
    bpy.context.scene.kkbp.timer = datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6

def print_timer(operation_name:str):
    '''Prints the time between now and the last operation that was timed'''
    kklog('{} operation took {} seconds'.format(operation_name, abs(round(((datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6) - bpy.context.scene.kkbp.timer), 3))))
    reset_timer()

def handle_error(error_causer:bpy.types.Operator, error:Exception):
    kklog('Unknown python error occurred. \n          Make sure the default model imports correctly before troubleshooting on this model!\n\n\n', type = 'error')
    kklog(traceback.format_exc())
    error_causer.report({'ERROR'}, traceback.format_exc())

def switch(object: bpy.types.Object, mode = 'OBJECT'):
    '''Switches blender mode on a blender object. Valid modes are 'object', 'edit' and 'pose' '''
    bpy.context.view_layer.objects.active = object 
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    object.select_set(True)
    bpy.context.view_layer.objects.active = object  
    
    mode = mode.upper()
    bpy.ops.object.mode_set(mode=mode)

    if mode == 'POSE':
        bpy.ops.pose.select_all(action='DESELECT')
    elif mode == 'EDIT':
        if object.type == 'MESH':
            bpy.ops.mesh.select_all(action='DESELECT')
        else:
            bpy.ops.armature.select_all(action='DESELECT')                
    elif mode == 'OBJECT':
        pass
    else:
        kklog('INVALID MODE CHOICE', type = 'error')
        raise('INVALID MODE CHOICE')

def move_and_hide_collection(objects: bpy.types.Object, new_collection: str, hide = True):
    '''Move the objects into a new collection called "new_collection" and hide the new collection'''
    if not objects:
        return
    switch(objects[0], 'object')
    #move
    object_collection = bpy.data.collections.new(new_collection)
    for object in objects:
        object_collection.objects.link(object)
    bpy.context.scene.collection.children[get_name()].children.link(object_collection)
    #then hide the new collection
    try:
        bpy.context.scene.view_layers[0].active_layer_collection = bpy.context.view_layer.layer_collection.children[-1].children[new_collection]
        bpy.context.scene.view_layers[0].active_layer_collection.exclude = hide
    except:
        kklog(f'Failed to move and hide collection: {new_collection}', type = 'error')
    
def clean_orphaned_data():
    '''clean data that is no longer being used'''
    bpy.ops.object.mode_set(mode='OBJECT')
    for block in bpy.data.meshes:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.meshes.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.cameras.remove(block)
    for block in bpy.data.lights:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.lights.remove(block)
    for block in bpy.data.materials:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.materials.remove(block)

def import_from_library_file(category, list_of_items, use_fake_user = False):
    '''Import items from the KKBP library file. The category is 'Armature', 'Brush', 'Collection' etc and
    the list_of_items is an array with all of the item names that you want to import.
    This will try to import the material templates from the KK Shader.blend file in the PMX import folder.
    If there's no KK Shader.blend file in the PMX folder, it will default to the one that comes with the plugin'''
    fileList = Path(bpy.context.scene.kkbp.import_dir).glob('*.*')
    files = [file for file in fileList if file.is_file()]
    blend_file_missing = True
    for file in files:
        if '.blend' in str(file) and '.blend1' not in str(file) and 'KK Shader' in str(file):
            directory = Path(file).resolve()
            blend_file_missing = False
    if blend_file_missing:
        #grab it from the plugin directory
        directory = Path(__file__)
        filename = 'KK Shader V8.0.blend/'
    
    library_path=(Path(directory).parent / filename).resolve()
    template_list = [{'name':item} for item in list_of_items]
    bpy.ops.wm.append(
        filepath=str((library_path / category).resolve()),
        directory=str(library_path / category) + '/',
        files=template_list,
        set_fake=use_fake_user
        )
