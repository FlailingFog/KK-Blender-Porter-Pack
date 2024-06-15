'''
This file can be run by any blender version between 2.80 and 3.6 to import and saturate all of the pmx textures
'''
import bpy, sys, os, bgl, gpu, numpy, datetime
from gpu_extras.batch import batch_for_shader
from pathlib import Path

def saturate(image, lut_image):

    width = image.size[0]
    height = image.size[1]

    # Some Sauce
    vertex_default = '''
    in vec2 a_position;
    in vec2 a_texcoord;

    in vec4 color;
    out vec4 col;

    void main() {
        gl_Position = vec4(a_position, 0.0, 1.0);
        col = color;
    }
    '''

    # The Secret Sauce
    current_code = '''
    uniform sampler2D tex0;
    uniform sampler2D lut;
    uniform vec2    u_resolution;

    in vec4 col;
    out vec4 out_Color;

    vec3 to_srgb(vec3 c){
        c.rgb = max( 1.055 * pow( c.rgb, vec3(0.416666667,0.416666667,0.416666667) ) - 0.055, 0 );
        return c;
    }

    vec3 apply_lut(vec3 color) {
        const vec3 coord_scale = vec3(0.0302734375, 0.96875, 31.0);
        const vec3 coord_offset = vec3( 0.5/1024, 0.5/32, 0.0);
        const vec2 texel_height_X0 = vec2( 0.03125, 0.0 );
        
        vec3 coord = color * coord_scale + coord_offset;
        
        vec3 coord_frac = fract( coord );
        vec3 coord_floor = coord - coord_frac;
        vec2 coord_bot = coord.xy + coord_floor.zz * texel_height_X0;
        vec2 coord_top = coord_bot + texel_height_X0;

        vec3 lutcol_bot = texture( lut, coord_bot ).rgb; //Changed from texture2D to texture just in case (apparently depreciated in opengl 3.1?)
        vec3 lutcol_top = texture( lut, coord_top ).rgb;
        
        vec3 lutColor = mix(lutcol_bot, lutcol_top, coord_frac.z);
        
        return lutcol_bot;
    }

    void main() {
        vec4 texRGBA = texture(tex0, gl_FragCoord.xy / u_resolution);

        vec3 texColor = to_srgb(texRGBA.rgb);

        vec3 newColor = apply_lut(texColor);

        newColor = to_srgb(newColor);
        
        out_Color = vec4(newColor.rgb, texRGBA.a);
    }
    '''

    # This object gives access to off screen buffers.
    offscreen = gpu.types.GPUOffScreen(width, height)

    # Context manager to ensure balanced bind calls, even in the case of an error.
    # Only run if valid
    with offscreen.bind():
        # Clear buffers to preset values
        bgl.glClear(bgl.GL_COLOR_BUFFER_BIT)
        # Initialize the shader
        # GPUShader combines multiple GLSL shaders into a program used for drawing. 
        # It must contain a vertex and fragment shaders, with an optional geometry shader.
        shader = gpu.types.GPUShader(vertex_default, current_code)
        # Initialize the shader batch
        # It makes sure that all the vertex attributes necessary for a specific shader are provided.
        batch = batch_for_shader(
            shader, 
            'TRI_STRIP', #https://wiki.blender.org/wiki/Reference/Release_Notes/3.2/Python_API for TRI_FAN depreciation
            {
                'a_position': ((-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)),
            },
        )
        # Bind the shader object. Required to be able to change uniforms of this shader.
        shader.bind()
        bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "tex0"), 0)
        bgl.glUniform1i(bgl.glGetUniformLocation(shader.program, "lut"), 1)
        try:
            # Make sure image has a bindcode
            if image.bindcode == 0:
                for i in range(0, 20):
                    image.gl_load()
                    if image.bindcode != 0:
                        break
            # https://docs.blender.org/api/current/bgl.html
            bgl.glActiveTexture(bgl.GL_TEXTURE0)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, image.bindcode)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_EDGE)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_EDGE)
            bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
            bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
            # Specify the value of a uniform variable for the current program object. 
            # In this case, an image.
            shader.uniform_int("tex0", 0)
        except ValueError:
            pass
        try:
            # Make sure image has a bindcode
            if lut_image.bindcode == 0:
                for i in range(0, 20):
                    lut_image.gl_load()
                    if lut_image.bindcode != 0:
                        break
            # https://docs.blender.org/api/current/bgl.html
            bgl.glActiveTexture(bgl.GL_TEXTURE1)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, lut_image.bindcode)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_EDGE)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_EDGE)
            bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
            bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
            # Specify the value of a uniform variable for the current program object. 
            # In this case, an image.
            shader.uniform_int("lut", 1)
        except ValueError: 
            pass
        try:
            shader.uniform_float('u_resolution', (width, height))
        except ValueError: 
            pass
        # Run the drawing program with the parameters assigned to the batch.
        batch.draw(shader)
        # The Buffer object is simply a block of memory that is delineated and initialized by the user.
        buffer = bgl.Buffer(bgl.GL_BYTE, width * height * 4)
        # # Select a color buffer source for pixels.
        bgl.glReadBuffer(bgl.GL_BACK)
        # # Read a block of pixels from the frame buffer.
        bgl.glReadPixels(0, 0, width, height, bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, buffer)

    # Free the offscreen object. The framebuffer, texture and render objects will no longer be accessible.
    offscreen.free()
    # Return the final buffer-pixels
    pixels = numpy.array([v / 255 for v in buffer])
    image.pixels = pixels.tolist()
    return image

if __name__ == '__main__':
    timer = datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6

    #Set the view transform or the files will not save correctly
    bpy.context.scene.view_settings.view_transform = 'Standard'

    pmx_import_dir = sys.argv[-1]
    addon_dir = sys.argv[-2]

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
    files = [file for file in fileList if file.is_file() and "_MT" in file.name and file.name not in ignore_list]

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
            bpy.data.images.remove(image)
    
    print('|Image conversion operation took {} seconds'.format(abs(round(((datetime.datetime.now().minute * 60 + datetime.datetime.now().second + datetime.datetime.now().microsecond / 1e6) - timer), 3))))
    bpy.ops.wm.quit_blender()