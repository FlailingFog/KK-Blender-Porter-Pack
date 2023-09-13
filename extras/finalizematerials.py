import bpy, pathlib, os
from ..interface.dictionary_en import t
from .. import common as c

class finalize_materials(bpy.types.Operator):
    bl_idname = "kkbp.finalizematerials"
    bl_label = "Optimize KKBP Materials"
    bl_description = t('finalize_materials_tt')
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #bake the light and dark versions of each material
        #bpy.context.scene.kkbp.bake_dark_bool = True
        #bpy.context.scene.kkbp.bake_light_bool = True
        #bpy.context.scene.kkbp.bake_norm_bool = False
        #bpy.context.scene.kkbp.atlas_dropdown = 'B'
        #bpy.ops.kkbp.applymaterials('INVOKE_DEFAULT')

        #now all needed images are loaded into the file. Match each material to it's image textures
        for mat in bpy.data.materials:
            finalize_this_mat = 'KK ' in mat.name and 'Outline ' not in mat.name and ' Outline' not in mat.name
            if finalize_this_mat:
                if mat.node_tree.nodes.get('Image Texture'):
                    if ' light.png' in mat.node_tree.nodes['Image Texture'].image.name:
                        light_image = mat.node_tree.nodes['Image Texture'].image.name
                        dark_image  = mat.node_tree.nodes['Image Texture'].image.name.replace('light', 'dark')
                    else:
                        dark_image = mat.node_tree.nodes['Image Texture'].image.name
                        light_image  = mat.node_tree.nodes['Image Texture'].image.name.replace('dark', 'light')
                    #mat_dict[mat.name] = [light_image, dark_image]

                    #rename material to -ORG, and replace it with a new material
                    mat.name += '-ORG'
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
                    new_node.nodes['MapMain'].image = bpy.data.images[light_image]
                    new_node.nodes['Darktex'].image = bpy.data.images[dark_image]
                    
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

        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(finalize_materials)