import bpy
import json
from pathlib import Path
from bpy.props import StringProperty

########## ERRORS ##########
def kk_folder_error(self, context):
    self.layout.label(text="Please make sure to open the folder that was exported. (Hint: go into the folder before confirming)")

########## FUNCTIONS ##########
def checks(directory):
    # "Borrowed" some logic from importeverything.py :P
    file_list = Path(directory).glob('*.*')
    files = [file for file in file_list if file.is_file()]
    filtered_files = []

    json_file_missing = True
    for file in files:
        if 'KK_SMRData.json' in str(file):
            json_file_path = str(file)
            json_file = open(json_file_path)
            json_file_missing = False
    
    if json_file_missing:
        bpy.context.window_manager.popup_menu(kk_folder_error, title="Error", icon='ERROR')
        return True

    return False

def load_smr_data(directory):
    # "Borrowed" some logic from importeverything.py :P
    file_list = Path(directory).glob('*.*')
    files = [file for file in file_list if file.is_file()]

    for file in files:
        if 'KK_SMRData.json' in str(file):
            json_file_path = str(file)
            json_file = open(json_file_path)
            json_smr_data = json.load(json_file)
            
    do_separate_meshes(json_smr_data)
            
def do_separate_meshes(json_smr_data): 
    #Get Clothes and it's object data
    clothes = bpy.data.objects['Clothes']
    clothes_data = clothes.data
    
    #Pass 1: To make sure each material has a mesh
    #Select the Clothes object and remove it's unused material slots
    clothes.select_set(True)
    bpy.ops.object.material_slot_remove_unused()
    
    #To keep track if a mesh has been separated already
    separated_meshes = []
    
    #Loop over each material in the Clothes object
    for mat in clothes_data.materials:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        
        if mat.name in separated_meshes:
            continue
        
        for row in json_smr_data:
            if mat.name in row['SMRMaterialNames']:
                separated_meshes.append(mat.name)
                
                #Find and select the material
                bpy.context.object.active_material_index = clothes_data.materials.find(mat.name)
                bpy.ops.object.material_slot_select()
                
                #Seperate to a new mesh
                bpy.ops.mesh.separate(type='SELECTED')
                
                #Remove unused materials from the new object and rename it to it's corresponding Renderer name
                bpy.ops.object.mode_set(mode = 'OBJECT')
                bpy.ops.object.material_slot_remove_unused()
                bpy.context.selected_objects[0].name = row['SMRName']
                break
    bpy.ops.object.select_all(action='DESELECT')
    
    #Pass 2: Clean up
    #Select the Clothes object and remove it's unused material slots
    clothes.select_set(True)
    bpy.ops.object.material_slot_remove_unused()
     
class separate_meshes(bpy.types.Operator):
    bl_idname = "kkb.separatemeshes"
    bl_label = "Open Export folder"
    bl_description = "Open the folder containing the KK_SMRData.json file"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})

    def execute(self, context):
        directory = self.directory
        error = checks(directory)
        
        if not error:
            load_smr_data(directory)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    