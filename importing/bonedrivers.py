# most of the joint driver corrections were taken from a blend file by
# johnbbob_la_petite on the koikatsu discord

'''
BONE DRIVERS SCRIPT
- Adds IKs to the arms and legs using the "Pv" bones
- Moves the Knee and Elbow IKs a little closer to the body
- Adds drivers for twist / joint correction bones for the arms, hands, legs, waist and butt
- Adds an "Eye Controller" bone to the top of the head and UV warp modifiers on the Body object to give eye controls
- Scales and repositions some bones
Usage:
- Run the script
'''

import bpy, math, time, json, traceback

from .. import common as c
from .cleanarmature import set_armature_layer


#selects all materials that are likely to be hair on each outfit object
def begin_hair_selections():
    json_file = open(bpy.context.scene.kkbp.import_dir + 'KK_MaterialData.json')
    material_data = json.load(json_file)
    json_file = open(bpy.context.scene.kkbp.import_dir + 'KK_TextureData.json')
    texture_data = json.load(json_file)
    #get all texture files
    texture_files = []
    for file in texture_data:
        texture_files.append(file['textureName'])

    for outfit in [obj for obj in bpy.data.objects if obj.name[:7] == 'Outfit ']:
        if bpy.context.scene.kkbp.categorize_dropdown in ['B']:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            outfit.select_set(True)
            bpy.context.view_layer.objects.active=outfit
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')

            #Select all materials that use the hair renderer and don't have a normal map then separate
            hair_mat_list = []
            for mat in material_data:
                if mat['ShaderName'] in ["Shader Forge/main_hair_front", "Shader Forge/main_hair", 'Koikano/hair_main_sun_front', 'Koikano/hair_main_sun', 'xukmi/HairPlus', 'xukmi/HairFrontPlus']:
                    if (mat['MaterialName'] + '_NMP.png') not in texture_files and (mat['MaterialName'] + '_MT_CT.png') not in texture_files and (mat['MaterialName'] + '_MT.png') not in texture_files:
                        hair_mat_list.append(mat['MaterialName'])
            if len(hair_mat_list):
                for index in range(len(outfit.data.materials)):
                    mat_name = outfit.data.materials[index].name
                    if mat_name in hair_mat_list:
                        outfit.active_material_index = index
                        bpy.ops.object.material_slot_select()
    
    #set to face select mode
    bpy.context.tool_settings.mesh_select_mode = (False, False, True)
    bpy.data.objects['Armature'].hide = True

class bone_drivers(bpy.types.Operator):
    bl_idname = "kkbp.bonedrivers"
    bl_label = "Bone Driver script"
    bl_description = "Add IKs, joint drivers and an eye bone"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            last_step = time.time()

            c.kklog('\nAdding bone drivers...')

            modify_armature = context.scene.kkbp.armature_dropdown in ['A', 'B']
            
            if modify_armature:
                c.kklog('Reparenting bones and setting up IKs...')
                reparent_bones()
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

                setup_iks()
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            c.kklog('Setting up joint bones...')
            setup_joints()
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
            if modify_armature:
                c.kklog('Creating eye controller and renaming bones...', 'timed')
                make_eye_controller()
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                scale_final_bones()
                categorize_bones()
                rename_bones_for_clarity()

                
            
            if context.scene.kkbp.categorize_dropdown in ['B']:
                begin_hair_selections()

            #set the viewport shading
            my_areas = bpy.context.workspace.screens[0].areas
            my_shading = 'SOLID'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'

            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading 
            
            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            
            return {'FINISHED'}
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(bone_drivers)

    # test call
    print((bpy.ops.kkbp.bonedrivers('INVOKE_DEFAULT')))