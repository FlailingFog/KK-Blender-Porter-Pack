'''
This file can be run by any blender version between 2.90 and 3.6 to import and saturate all of the pmx textures
'''
import bpy, sys, os, numpy, datetime
from pathlib import Path

def saturate(image, lut_image):
    width, height = image.size

    # Load image and LUT image pixels into NumPy arrays
    image_pixels = numpy.array(image.pixels[:]).reshape(height, width, 4)
    lut_pixels = numpy.array(lut_image.pixels[:]).reshape(lut_image.size[1], lut_image.size[0], 4)

    # Apply LUT
    coord_scale = numpy.array([0.0302734375, 0.96875, 31.0])
    coord_offset = numpy.array([0.5/1024, 0.5/32, 0.0])
    texel_height_X0 = numpy.array([1/32, 0])

    coord = image_pixels[:, :, :3] * coord_scale + coord_offset

    coord_frac, coord_floor = numpy.modf(coord)
    coord_bot = coord[:, :, :2] + numpy.tile(coord_floor[:, :, 2].reshape(height, width, 1), (1, 1, 2)) * texel_height_X0
    coord_top = numpy.clip(coord_bot + texel_height_X0, 0, 1)

    def bilinear_interpolation(lut_pixels, coords):
        h, w, _ = lut_pixels.shape
        x = coords[:, :, 0] * (w - 1)
        #Fudge x coordinates based on x position. subtract -0.5 if at x position 0 and add 0.5 if at x position 1024 of the LUT. 
        #this helps with some kind of overflow / underflow issue where it reads from the next LUT square when it's not supposed to
        x = x + (x/1024  - 0.5)
        y = coords[:, :, 1] * (h - 1)
        # Get integer and fractional parts
        x0 = numpy.floor(x).astype(int)
        x1 = numpy.clip(x0 + 1, 0, w - 1)
        y0 = numpy.floor(y).astype(int)
        y1 = numpy.clip(y0 + 1, 0, h - 1)
        x_frac = x - x0
        y_frac = y - y0
        # Get the pixel values at four corners
        f00 = lut_pixels[y0, x0]
        f01 = lut_pixels[y1, x0]
        f10 = lut_pixels[y0, x1]
        f11 = lut_pixels[y1, x1]
        # Perform the bilinear interpolation
        lut_col_bot = f00 * (1 - y_frac)[:, :, numpy.newaxis] + f01 * y_frac[:, :, numpy.newaxis]
        lut_col_top = f10 * (1 - y_frac)[:, :, numpy.newaxis] + f11 * y_frac[:, :, numpy.newaxis]
        interpolated_colors = lut_col_bot * (1 - x_frac)[:, :, numpy.newaxis] + lut_col_top * x_frac[:, :, numpy.newaxis]
        return interpolated_colors

    lutcol_bot = bilinear_interpolation(lut_pixels, coord_bot)
    lutcol_top = bilinear_interpolation(lut_pixels, coord_top)

    lut_colors = lutcol_bot * (1 - coord_frac[:, :, 2].reshape(height, width, 1)) + lutcol_top * coord_frac[:, :, 2].reshape(height, width, 1)
    image_pixels[:, :, :3] = lut_colors[:,:,:3]

    # Update image pixels
    image.pixels = image_pixels.flatten().tolist()

    return image

if __name__ == '__main__':
    #use datetime instead of time() because the latter doesn't work 
    timer = datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6

    #Set the view transform or the files will not save correctly
    bpy.context.scene.view_settings.view_transform = 'Standard'

    filter = int(sys.argv[-1])
    pmx_import_dir = sys.argv[-2]
    addon_dir = sys.argv[-3]

    lut_image = os.path.join(addon_dir, 'luts', 'Lut_TimeDay.png')
    lut_image = bpy.data.images.load(str(lut_image))

    #collect all images in this folder and all subfolders into an array
    ignore_list = [
            "cf_m_eyeline_00_up_MT_CT.png",
            "cf_m_eyeline_down_MT_CT.png",
            "cf_m_noseline_00_MT_CT.png",
            "cf_m_mayuge_00_MT_CT.png",
            "cf_m_eyeline_kage_MT.png",
        ]

    directory = pmx_import_dir
    fileList = Path(directory).rglob('*.png')
    if filter:
        files = [file for file in fileList if file.is_file() and "_MT" in file.name and file.name not in ignore_list]
    else:
        files = [file for file in fileList if file.is_file()]
    # print('|', str(os.path.join(directory, "saturated_files")))
    first = True
    for image_file in files:
        #skip this file if it has already been converted
        if os.path.isfile(os.path.join(pmx_import_dir, 'saturated_files', str(image_file.name).replace('_MT','_ST'))):
            print('|File already converted. Skipping {}'.format(image_file.name))
        else:
            #Run the saturator twice the first time to avoid a weird bug
            print('|Converting image {}'.format(image_file.name))
            image = bpy.data.images.load(str(image_file))
            if first:
                saturate(image, lut_image)
                image.reload()
                first = False
            
            #saturate the image, save and remove the file
            saturate(image, lut_image)
            image.save_render(str(os.path.join(directory, "saturated_files", image_file.name.replace('_MT', '_ST'))))
            # print('|', str(os.path.join(directory, "saturated_files", image_file.name.replace('_MT', '_ST'))))
            bpy.data.images.remove(image)
    
    print('|Image conversion operation took {} seconds'.format(abs(round(((datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6) - timer), 3))))
    bpy.ops.wm.quit_blender()