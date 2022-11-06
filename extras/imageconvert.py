from pathlib import Path
import bpy
from ..importing.finalizepmx import kklog
from ..importing.importcolors import image_to_KK, load_luts
from ..importing.darkcolors import create_darktex

class image_convert(bpy.types.Operator):
    bl_idname = "kkb.imageconvert"
    bl_label = "Convert image"
    bl_description = "Click this to convert the currently loaded image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        kklog("Converting image: ".format(context.space_data.image))
        
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
        load_luts(lut_choice, lut_choice)
        # Need to run image_to_KK twice for the first image due to a weird bug
        image_to_KK(image, lut_choice)

        new_pixels, width, height = image_to_KK(image, lut_choice)
        image.pixels = new_pixels
        #image.save()

        return {'FINISHED'}

class image_dark_convert(bpy.types.Operator):
    bl_idname = "kkb.imagedarkconvert"
    bl_label = "Convert image"
    bl_description = "(SLOW!) Click this to create a dark version of the currently loaded maintex image. The new image will end in 'MT_DT.png' The new image will be automatically loaded to the dark color node group"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        body = bpy.data.objects['Body']
        kklog("Converting image: ".format(context.space_data.image))

        image = context.space_data.image
        image.reload()

        material_name = image.name[:-10]
        #kklog(material_name)
        #kklog(body['KKBP shadow colors'])
        #kklog(body['KKBP shadow colors'][material_name])
        #kklog(body['KKBP shadow colors'][material_name]['r'])
        try:
            shadow_color = [body['KKBP shadow colors'][material_name]['r'], body['KKBP shadow colors'][material_name]['g'], body['KKBP shadow colors'][material_name]['b']]
            #kklog(shadow_color)
            darktex = create_darktex(bpy.data.images[image.name], shadow_color)
            material_name = 'KK ' + image.name[:-10]
            bpy.data.materials[material_name].node_tree.nodes['Gentex'].node_tree.nodes['Darktex'].image = darktex
            bpy.data.materials[material_name].node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use dark maintex?'].default_value = 1
            bpy.data.materials[material_name].node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1
        except:
            kklog('Tried to create a dark version of {} but there was no shadow color available. \nDark color conversion is only available for Koikatsu images that end in \'_MT_CT.png\''.format(image.name), type='error')
        
        return {'FINISHED'}

if __name__ == "__main__":
    bpy.utils.register_class(image_convert)

    # test call
    #print((bpy.ops.kkb.imageconvert('INVOKE_DEFAULT')))