from pathlib import Path
import bpy
from ..importing.finalizepmx import kklog
from ..importing.importcolors import image_to_KK, load_luts

class image_convert(bpy.types.Operator):
    bl_idname = "kkb.imageconvert"
    bl_label = "Convert image"
    bl_description = "Click this to convert the currently loaded image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        kklog("Converting image: ".format(context.space_data.image))
        
        scene = context.scene.placeholder
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

if __name__ == "__main__":
    bpy.utils.register_class(image_convert)

    # test call
    print((bpy.ops.kkb.imageconvert('INVOKE_DEFAULT')))