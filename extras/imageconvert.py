from pathlib import Path
import bpy
from .. import common as c
from ..importing.modifymaterial import modify_material

class image_convert(bpy.types.Operator):
    bl_idname = "kkbp.imageconvert"
    bl_label = "Convert light image"
    bl_description = "Click this to saturate the currently loaded image using the selected Koikatsu LUT"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        c.kklog("Converting image: ".format(context.space_data.image))
        
        scene = context.scene.kkbp
        lut_selection = scene.image_dropdown
        
        if lut_selection == 'A':
            lut_choice = 'Lut_TimeDay.png'
        elif lut_selection == 'B':
            lut_choice = 'Lut_TimeNight.png'
        else:
            lut_choice = 'Lut_TimeSunset.png'

        image = context.space_data.image
        image.reload()
        image.colorspace_settings.name = 'sRGB'
        
        # Use code from importcolors to convert the current image
        modify_material.load_luts(lut_choice, lut_choice)
        # Need to run image_to_KK twice for the first image due to a weird bug
        modify_material.image_to_KK(image, lut_choice)

        new_pixels, width, height = modify_material.image_to_KK(image, lut_choice)
        image.pixels = new_pixels
        #image.save()

        return {'FINISHED'}

class image_dark_convert(bpy.types.Operator):
    bl_idname = "kkbp.imagedarkconvert"
    bl_label = "Convert dark image"
    bl_description = "Click this to create a dark version of the currently loaded maintex image. The new image will end in 'MT_DT.png' The new image will be automatically loaded to the dark color node group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        body = bpy.data.objects['Body']
        c.kklog("Converting image: ".format(context.space_data.image))

        image = context.space_data.image
        material_name = image.name[:-10]
        try:
            shadow_color = [body['KKBP shadow colors'][material_name]['r'], body['KKBP shadow colors'][material_name]['g'], body['KKBP shadow colors'][material_name]['b']]
            darktex = modify_material.create_darktex(bpy.data.images[image.name], shadow_color)
            material_name = 'KK ' + image.name[:-10]
            bpy.data.materials[material_name].node_tree.nodes['Gentex'].node_tree.nodes['Darktex'].image = darktex
            bpy.data.materials[material_name].node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use dark maintex?'].default_value = 1
            bpy.data.materials[material_name].node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1
        except:
            c.kklog('Tried to create a dark version of {} but there was no shadow color available. \nDark color conversion is only available for Koikatsu images that end in \'_MT_CT.png\''.format(image.name), type='error')
        
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(image_convert)

    # test call
    #print((bpy.ops.kkbp.imageconvert('INVOKE_DEFAULT')))