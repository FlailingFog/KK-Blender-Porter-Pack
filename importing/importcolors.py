import bpy, os, traceback
import bgl
import gpu
import json
from .importbuttons import kklog
import numpy as np
from pathlib import Path
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from gpu_extras.batch import batch_for_shader
from bpy.props import StringProperty, BoolProperty

#load plugin language
from bpy.app.translations import locale
if locale == 'ja_JP':
    from ..interface.dictionary_jp import t
else:
    from ..interface.dictionary_en import t

########## ERRORS ##########
def kk_folder_error(self, context):
    self.layout.label(text="Please make sure to open the folder that was exported. (Hint: go into the folder before confirming)")


########## FUNCTIONS ##########
def image_to_KK(image, lut_name):
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

        vec3 lutcol_bot = texture2D( lut, coord_bot ).rgb;
        vec3 lutcol_top = texture2D( lut, coord_top ).rgb;
        
        vec3 lutColor = mix(lutcol_bot, lutcol_top, coord_frac.z);
        
        return lutColor;
    }

    void main() {
        vec4 texRGBA = texture2D(tex0, gl_FragCoord.xy / u_resolution);

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
            'TRI_FAN', {
                'a_position': ((-1, -1), (1, -1), (1, 1), (-1, 1))
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
            lut_image = bpy.data.images[lut_name]

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
        
        # Select a color buffer source for pixels.
        bgl.glReadBuffer(bgl.GL_BACK)
        
        # Read a block of pixels from the frame buffer.
        bgl.glReadPixels(0, 0, width, height, bgl.GL_RGBA, bgl.GL_UNSIGNED_BYTE, buffer)

    # Free the offscreen object. The framebuffer, texture and render objects will no longer be accessible.
    offscreen.free()

    # Return the final buffer-pixels
    pixels = [v / 255 for v in buffer]
    return pixels, width, height

def color_to_KK(color, lut_name):
    width = 1
    height = 1

    # Some Sauce
    vertex_default = '''
    in vec2 a_position;
    
    in vec4 color;
    out vec4 col;

    void main() {
        gl_Position = vec4(a_position, 0.0, 1.0);
        col = color;
    }
    '''

    # The Secret Sauce
    current_code = '''
    uniform vec3 inputColor;
    uniform sampler2D lut;
    
    in vec4 col;
    out vec4 out_Color;

    vec3 to_srgb(vec3 c){
        c.rgb = max( 1.055 * pow( c.rgb, vec3(0.416666667,0.416666667,0.416666667) ) - 0.055, 0 );
        return c;
    }

    void main() {
        vec3 color = inputColor / 255;
        
        const vec3 coord_scale = vec3(0.0302734375, 0.96875, 31.0);
        const vec3 coord_offset = vec3( 0.5/1024, 0.5/32, 0.0);
        const vec2 texel_height_X0 = vec2( 0.03125, 0.0 );
        
        vec3 coord = color * coord_scale + coord_offset;
        
        vec3 coord_frac = fract( coord );
        vec3 coord_floor = coord - coord_frac;
        vec2 coord_bot = coord.xy + coord_floor.zz * texel_height_X0;
        vec2 coord_top = coord_bot + texel_height_X0;

        vec3 lutcol_bot = texture( lut, coord_bot ).rgb;
        vec3 lutcol_top = texture( lut, coord_top ).rgb;
        
        vec3 lutColor = mix(lutcol_bot, lutcol_top, coord_frac.z);
        
        
        vec3 shaderColor = lutColor;
        
        out_Color = vec4(shaderColor.rgb, 1);
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
            'TRI_FAN', {
                'a_position': ((-1, -1), (1, -1), (1, 1), (-1, 1))
            },
        )

        # Bind the shader object. Required to be able to change uniforms of this shader.
        shader.bind()
        
        
        try:
            # Specify the value of a uniform variable for the current program object. 
            # In this case, a color tuple.
            shader.uniform_float('inputColor', color)
        except ValueError:
            pass
        
        try:
            lut_image = bpy.data.images[lut_name]

            # Make sure image has a bindcode
            if lut_image.bindcode == 0:
                for i in range(0, 20):
                    lut_image.gl_load()
                    if lut_image.bindcode != 0:
                        break

            # https://docs.blender.org/api/current/bgl.html
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, lut_image.bindcode)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_S, bgl.GL_CLAMP_TO_EDGE)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_WRAP_T, bgl.GL_CLAMP_TO_EDGE)
            bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_LINEAR)
            bgl.glTexParameterf(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_LINEAR)
            
            # Specify the value of a uniform variable for the current program object. 
            # In this case, an image.
            shader.uniform_int("lut", 0)
        except ValueError: 
            pass
        
        
        # Run the drawing program with the parameters assigned to the batch.
        batch.draw(shader)

        # The Buffer object is simply a block of memory that is delineated and initialized by the user.
        buffer = bgl.Buffer(bgl.GL_BYTE, width * height * 3)
        
        # Select a color buffer source for pixels.
        bgl.glReadBuffer(bgl.GL_BACK)
        
        # Read a block of pixels from the frame buffer.
        bgl.glReadPixels(0, 0, width, height, bgl.GL_RGB, bgl.GL_UNSIGNED_BYTE, buffer)

    # Free the offscreen object. The framebuffer, texture and render objects will no longer be accessible.
    offscreen.free()

    # Get and return the pixels from the final buffer
    final_color = [v for v in buffer]
    final_color = np.array(final_color).reshape(width, height, -1)
    return final_color[0][0]


    
    # RGBA (1, 1, 1, 1) to RGB as int (255, 255, 255)
    def RGBA_to_RGB_int(rgba):
        rgba = np.round(rgba * 255).astype('int')
        rgba = np.delete(rgba, 3)
        return rgba
    
    # Make sure not to select a transparent pixel
    def filter_pixel(index_list, image):
        for i in index_list:
            if image[i][3] == 1:
                index = i
                break
        return index

    ########## SETUP ##########

    exposure = np.array([exposure[0], exposure[1], exposure[2], 1])

    # Init MC Texture
    mc_mask_data = np.array(mc_mask.pixels).reshape(-1, 4)
    mc_mask_data = mc_mask_data * exposure
    mc_mask_data = np.clip(mc_mask_data, 0, 1)
    
    # Init Main Texture
    bpy.data.images[texture.name].scale(mc_mask.size[0], mc_mask.size[1])
    texture_data = np.array(texture.pixels).reshape(-1, 4)
    
    # Init MC Color indexes
    red_index = -1
    green_index = -1
    blue_index = -1
    
    # Init MainTex Colors
    red_color = -1
    green_color = -1
    blue_color = -1
    
    # Init converted colors (light)
    red_converted_color_light = np.array([255, 0, 0, 255])
    green_converted_color_light = np.array([0, 255, 0, 255])
    blue_converted_color_light = np.array([0, 0, 255, 255])
    
    
    ########## FIND MC INDEXES ##########
    r, g, b = mc_mask_data[:, 0], mc_mask_data[:, 1], mc_mask_data[:, 2]
    r = r.max()
    g = g.max()
    b = b.max()
    
    # Red
    pixel_list = np.where(np.all(mc_mask_data == (r, 0, 0, 1), axis=-1))[0]
    if len(pixel_list) > 0:
        red_index = filter_pixel(pixel_list, texture_data)
    
    # Green
    pixel_list = np.where(np.all(mc_mask_data >= (0, g, 0, 1), axis=-1))[0]
    if len(pixel_list) > 0:
        green_index = filter_pixel(pixel_list, texture_data)
    else:
        # Green (Yellow)
        pixel_list = np.where(np.all(mc_mask_data == (r, g, 0, 1), axis=-1))[0]
        if len(pixel_list) > 0:
            green_index = filter_pixel(pixel_list, texture_data)

    # Blue
    pixel_list = np.where(np.all(mc_mask_data == (0, 0, b, 1), axis=-1))[0]
    if len(pixel_list) > 0:
        blue_index = filter_pixel(pixel_list, texture_data)
    else:
        # Blue (Cyan)
        pixel_list = np.where(np.all(mc_mask_data == (0, g, b, 1), axis=-1))[0]
        if len(pixel_list) > 0:
            blue_index = filter_pixel(pixel_list, texture_data)
        else:
            # Blue (Magenta)
            pixel_list = np.where(np.all(mc_mask_data == (r, 0, b, 1), axis=-1))[0]
            if len(pixel_list) > 0:
                blue_index = filter_pixel(pixel_list, texture_data)
            else:
                # Blue (White)
                pixel_list = np.where(np.all(mc_mask_data == (r, g, b, 1), axis=-1))[0]
                if len(pixel_list) > 0:
                    blue_index = filter_pixel(pixel_list, texture_data)


    ########## SCALE INDEXES ##########

    # mc_w, mc_h = mc_mask.size
    # tex_w, tex_h = texture.size

    # scale = int((tex_w * tex_h) / (mc_w * mc_h))

    # red_index = red_index * scale
    # green_index = green_index * scale
    # blue_index = blue_index * scale

    ########## GET AND CONVERT COLORS FROM MAIN TEXTURE ##########
    
    if red_index >= 0:
        red_color = texture_data[red_index]
        red_color = RGBA_to_RGB_int(red_color)
        
        red_converted_color_light = color_to_KK(red_color, lut)
        
    if green_index >= 0:  
        green_color = texture_data[green_index]
        green_color = RGBA_to_RGB_int(green_color)
        
        green_converted_color_light = color_to_KK(green_color, lut)
        
    if blue_index >= 0:
        blue_color = texture_data[blue_index]
        blue_color = RGBA_to_RGB_int(blue_color)
        
        blue_converted_color_light = color_to_KK(blue_color, lut)
    
    # print(red_index)
    # print(green_index)
    # print(blue_index)

    # print(red_converted_color_light)
    # print(green_converted_color_light)
    # print(blue_converted_color_light)

    return red_converted_color_light / 255, green_converted_color_light / 255, blue_converted_color_light / 255

def checks(directory):
    # "Borrowed" some logic from importeverything.py :P
    file_list = Path(directory).glob('*.*')
    files = [file for file in file_list if file.is_file()]
    filtered_files = []

    json_file_missing = True
    for file in files:
        if 'KK_CharacterColors.json' in str(file):
            json_file_path = str(file)
            json_file = open(json_file_path)
            json_file_missing = False
    
    if json_file_missing:
        bpy.context.window_manager.popup_menu(kk_folder_error, title="Error", icon='ERROR')
        return True

    return False

def load_luts(lut_light, lut_dark):
    lut_path = os.path.dirname(os.path.abspath(__file__)) + '/luts/'
    day_lut = bpy.data.images.load(lut_path + lut_light, check_existing=True)
    day_lut.use_fake_user = True
    day_lut.save()

    night_lut = bpy.data.images.load(lut_path + lut_dark, check_existing=True)
    night_lut.use_fake_user = True
    night_lut.save()

def convert_main_textures(lut_light):
    ignore_list = [
        "cf_m_eyeline_00_up_MT_CT.png",
        "cf_m_eyeline_down_MT_CT.png",
        "cf_m_noseline_00_MT_CT.png",
        "cf_m_mayuge_00_MT_CT.png",
        "cf_m_eyeline_kage_MT.png",
    ]

    images = bpy.data.images
    first = True
    for image in images:
        if "_MT" in image.name and image.name not in ignore_list:
            image.reload()

            # Need to run image_to_KK twice for the first image due to a weird bug
            if first:
                image_to_KK(image, lut_light)
                first = False

            new_pixels, width, height = image_to_KK(image, lut_light)
            image.pixels = new_pixels
            # image.save()

def load_json_colors(directory, lut_light, lut_dark, lut_selection):

    # "Borrowed" some logic from importeverything.py :P
    file_list = Path(directory).glob('*.*')
    files = [file for file in file_list if file.is_file()]
    filtered_files = []

    for file in files:
        if 'KK_CharacterColors.json' in str(file):
            json_file_path = str(file)
            json_file = open(json_file_path)
            json_color_data = json.load(json_file)

    update_shaders(json_color_data, lut_selection, lut_light, light = True) # Set light colors
    update_shaders(json_color_data, lut_selection, lut_dark, light = False) # Set dark colors

    set_color_management()

def update_shaders(json, lut_selection, active_lut, light):

    def to_rgba(rgb):
        rgba = [rgb[0], rgb[1], rgb[2], 1]
        return rgba

    def json_to_color(color):
        rgb = [color['r'], color['g'], color['b']]
        return rgb

    node_groups = bpy.data.node_groups

    ## Body
    body_shader_node_group = node_groups['Body Shader']
    body_colors = []

    ## Face
    face_shader_node_group = node_groups['Face Shader']
    face_colors = []

    ## Eyebrows
    eyebrows_shader_node_group = node_groups['Eyebrows Shader']

    ## Eyeline
    eyeline_shader_node_group = node_groups['Eyeline Shader']

    ## Tongue
    tongue_shader_node_group = node_groups['Tongue Shader']
    tongue_color = []

    ## Hair
    hair_shader_node_group = node_groups['Hair Shader']
    hair_base_color = [1, 1, 1, 1]
    hair_root_color = [1, 1, 1, 1]
    hair_tip_color = [1, 1, 1, 1]
    
    ## All Other Items
    item_data = []
    item_shader_node_groups = []
    

    ### Get json groups
    for idx, item in enumerate(json):
        if idx > 4:
            shader_name = item['materialName'] + ' Shader'
            if shader_name in node_groups:
                item_data.append(item)
                item_shader_node_groups.append(node_groups[shader_name])


    ### Get body/face/hair colors
    body_colors.append(to_rgba(color_to_KK(json_to_color(json[0]['colorInfo'][0]), active_lut) / 255))
    body_colors.append(to_rgba(color_to_KK(json_to_color(json[0]['colorInfo'][1]), active_lut) / 255))
    body_colors.append(to_rgba(color_to_KK(json_to_color(json[0]['colorInfo'][2]), active_lut) / 255))
    body_colors.append(to_rgba(color_to_KK(json_to_color(json[0]['colorInfo'][3]), active_lut) / 255))
    body_colors.append(to_rgba(color_to_KK(json_to_color(json[0]['colorInfo'][4]), active_lut) / 255))
    body_colors.append(to_rgba(color_to_KK(json_to_color(json[0]['colorInfo'][5]), active_lut) / 255))

    face_colors.append(to_rgba(color_to_KK(json_to_color(json[1]['colorInfo'][0]), active_lut) / 255))
    face_colors.append(to_rgba(color_to_KK(json_to_color(json[1]['colorInfo'][1]), active_lut) / 255))
    face_colors.append(to_rgba(color_to_KK(json_to_color(json[1]['colorInfo'][2]), active_lut) / 255))
    face_colors.append(to_rgba(color_to_KK(json_to_color(json[1]['colorInfo'][3]), active_lut) / 255))
    face_colors.append(to_rgba(color_to_KK(json_to_color(json[1]['colorInfo'][4]), active_lut) / 255))
    face_colors.append(to_rgba(color_to_KK(json_to_color(json[1]['colorInfo'][5]), active_lut) / 255))
    face_colors.append(to_rgba(color_to_KK(json_to_color(json[1]['colorInfo'][6]), active_lut) / 255))

    kage_color = to_rgba(color_to_KK(json_to_color(json[2]['colorInfo'][0]), active_lut) / 255)

    tongue_color = to_rgba(color_to_KK(json_to_color(json[4]['colorInfo'][0]), active_lut) / 255)

    hair_base_color = to_rgba(color_to_KK(json_to_color(json[5]['colorInfo'][0]), active_lut) / 255)
    hair_root_color = to_rgba(color_to_KK(json_to_color(json[5]['colorInfo'][1]), active_lut) / 255)
    hair_tip_color = to_rgba(color_to_KK(json_to_color(json[5]['colorInfo'][2]), active_lut) / 255)
    #hair_outline_color = to_rgba(color_to_KK(json_to_color(json[5]['colorInfo'][3]), active_lut) / 255)

    ### Set shader colors
    ## Body Shader
    shader_inputs = body_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
    shader_inputs['Skin color'].default_value = body_colors[0]
    shader_inputs['Skin type color'].default_value = body_colors[1]
    shader_inputs['Skin type intensity (Base)'].default_value = 0.5
    shader_inputs['Skin type intensity'].default_value = 1
    shader_inputs['Skin detail color'].default_value = body_colors[1]
    shader_inputs['Skin detail intensity'].default_value = 0.5
    shader_inputs['Nail Color (multiplied)'].default_value = body_colors[2]
    shader_inputs['Skin gloss intensity'].default_value = 1
    shader_inputs['Underhair color'].default_value = body_colors[4]

    shader_inputs['Nipple base'].default_value = body_colors[3]
    shader_inputs['Nipple base 2'].default_value = [1, 0, 0, 1] # Red
    shader_inputs['Nipple shine'].default_value = np.array(body_colors[3]) * 1.5
    shader_inputs['Nipple rim'].default_value = np.array(body_colors[3]) * 0.5


    ## Face Shader
    shader_inputs = face_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
    shader_inputs['Skin color'].default_value = body_colors[0]
    shader_inputs['Skin detail color'].default_value = body_colors[1]
    shader_inputs['Light blush color'].default_value = face_colors[5]
    shader_inputs['Mouth interior multiplier'].default_value = [1, 1, 1, 1]
    
    shader_inputs['Overlay 1 color'].default_value = face_colors[6]


    ## Eyebrow Shader
    shader_inputs = eyebrows_shader_node_group.nodes['colorsLight'].inputs
    shader_inputs['Light Eyebrow color' if light else 'Dark Eyebrow color'].default_value = face_colors[0]

    ## Eyeline Shader
    shader_inputs = eyeline_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
    shader_inputs['Eyeline base color'].default_value = [0, 0, 0, 1]
    shader_inputs['Eyeline fade color'].default_value = face_colors[1]
    shader_inputs['Eyeline shadow color'].default_value = kage_color

    ## Tongue Shader
    shader_inputs = tongue_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
    #shader_inputs['Use Color mask instead? (1 = yes)'].default_value = 1
    shader_inputs['Manually set detail color? (1 = yes)'].default_value = 0
    shader_inputs['Detail intensity (green)'].default_value = 0.01
    shader_inputs['Color mask color (base)'].default_value = [1, 1, 1, 1]
    shader_inputs['Color mask color (red)'].default_value = tongue_color
    shader_inputs['Color mask color (green)'].default_value = tongue_color
    shader_inputs['Color mask color (blue)'].default_value = tongue_color

    ## Hair Shader
    shader_inputs = hair_shader_node_group.nodes['colorsLight' if light else 'colorsDark'].inputs
    shader_inputs['Light Hair color' if light else 'Dark Hair color'].default_value = hair_base_color
    shader_inputs['Light Hair rim color' if light else 'Dark Hair rim color'].default_value = hair_root_color
    shader_inputs['Dark fade color'].default_value = hair_root_color
    shader_inputs['Light fade color'].default_value = hair_tip_color
    shader_inputs['Manually set the hair color detail? (1 = yes)'].default_value = 0
    shader_inputs['Use fade mask? (1 = yes)'].default_value = 0.5

    ## Accessories/Items Shader
    uses_lut = any([lut_selection == 'A', lut_selection == 'B', lut_selection == 'C'])
    for idx, item in enumerate(item_data):
        pattern_input_names = [
            'Pattern color (red)',
            'Pattern color (green)',
            'Pattern color (blue)'
        ]

        color_input_names = [
            'Color mask color (red)',
            'Color mask color (green)',
            'Color mask color (blue)'
        ]

        shader_inputs = item_shader_node_groups[idx].nodes['colorsLight' if light else 'colorsDark'].inputs
        if not light and uses_lut:
            shader_inputs['Automatically darken color?'].default_value = 0
        elif not light and lut_selection == 'D':
            shader_inputs['Automatically darken color?'].default_value = 1
            shader_inputs['Auto dark color (low sat.)'].default_value = [0.278491, 0.311221, 0.700000, 1.000000]
            shader_inputs['Auto dark color (high sat.)'].default_value = [0.531185, 0.544296, 0.700000, 1.000000]
        elif not light and lut_selection == 'E':
            shader_inputs['Automatically darken color?'].default_value = 0

        shader_inputs['Manually set detail color? (1 = yes)'].default_value = 0
        shader_inputs['Detail intensity (green)'].default_value = 0.1
        shader_inputs['Detail intensity (blue)'].default_value = 0.1
        #shader_inputs['Use Color mask instead? (1 = yes)'].default_value = 1

        if not light and lut_selection == 'E':
            shader_inputs['Color mask color (base)'].default_value = [0.3, 0.3, 0.3, 0.3]
        else:
            shader_inputs['Color mask color (base)'].default_value = [1, 1, 1, 1]

        for i, colorItem in enumerate(item['colorInfo']):
            if i < len(color_input_names):
                color_channel = to_rgba(color_to_KK(json_to_color(colorItem), active_lut) / 255)
                if not light and lut_selection == 'E':
                    color_channel = [x * .3 for x in color_channel]
                shader_inputs[color_input_names[i]].default_value = color_channel

        if not light and lut_selection == 'E':
            shader_inputs['Pattern (base)'].default_value = [0.3, 0.3, 0.3, 0.3]
        else:
            shader_inputs['Pattern (base)'].default_value =  [1, 1, 1, 1]

        for i, patternColor in enumerate(item['patternColors']):
            if i < len(pattern_input_names):
                color_channel = to_rgba(color_to_KK(json_to_color(patternColor), active_lut) / 255)
                if not light and lut_selection == 'E':
                    color_channel = [x * .3 for x in color_channel]
                shader_inputs[pattern_input_names[i]].default_value = color_channel
        

def set_color_management():
    bpy.data.scenes[0].display_settings.display_device = 'sRGB'
    bpy.data.scenes[0].view_settings.view_transform = 'Standard'
    bpy.data.scenes[0].view_settings.look = 'None'

class import_colors(bpy.types.Operator):
    bl_idname = "kkb.importcolors"
    bl_label = "Open Export folder"
    bl_description = t('import_colors_tt')
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None

    def execute(self, context):
        kklog('\nConverting Colors...')
        print(context.scene.kkbp.import_dir)
        try:
            if self.directory == '':
                directory = context.scene.kkbp.import_dir[:-9]
            else:
                directory = self.directory

            error = checks(directory)

            scene = context.scene.kkbp
            lut_selection = scene.colors_dropdown
            
            if lut_selection == 'A':
                lut_dark = 'Lut_TimeNight.png'
            elif lut_selection == 'B':
                lut_dark = 'Lut_TimeSunset.png'
            else:
                lut_dark = 'Lut_TimeDay.png'
            lut_light = 'Lut_TimeDay.png'

            if not error:
                load_luts(lut_light, lut_dark)
                convert_main_textures(lut_light)
                load_json_colors(directory, lut_light, lut_dark, lut_selection)

            context.scene.kkbp.import_dir = ''
            bpy.data.objects['Armature'].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects['Armature']

            return {'FINISHED'}
        
        except:
            print('waht the fuck excepted')
            kklog('Unknown python error occurred', type = 'error')
            kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

if __name__ == "__main__":
    bpy.utils.register_class(import_colors)
    print((bpy.ops.kkb.importcolors('INVOKE_DEFAULT')))

