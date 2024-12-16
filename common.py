import bpy, json, datetime, traceback
from pathlib import Path

def toggle_console():
    '''toggle the console. will do nothing on Linux or Mac'''
    print('console toggled')
    try:
        bpy.ops.wm.console_toggle()
    except:
        return #only available on windows so it might error out for other platforms

def kklog(log_text, type = ''):
    '''Log to the KKBP Log text in the scripting tab. Also prints to console. optional types are error or warn'''
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

def get_json_file(filename:str):
    '''Returns the json file by filename'''
    files = [file for file in Path(bpy.context.scene.kkbp.import_dir).glob('*.json') if filename in str(file)]
    if files:
        json_file_path = str(files[0])
        json_file = open(json_file_path)
        json_data = json.load(json_file)
        return json_data

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

def switch(object:bpy.types.Object, mode = 'OBJECT'):
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
        print(error_out_here)

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
    the list_of_items is an array with all of the item names that you want to import'''
    # try to import the material templates from the KK Shader.blend file in the plugin directory.
    # If not available, default to the one that comes with the plugin
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
        filename = 'KK Shader V7.0.blend/'
    
    library_path=(Path(directory).parent / filename).resolve()
    template_list = [{'name':item} for item in list_of_items]
    bpy.ops.wm.append(
        filepath=str((library_path / category).resolve()),
        directory=str(library_path / category) + '/',
        files=template_list,
        set_fake=use_fake_user
        )
