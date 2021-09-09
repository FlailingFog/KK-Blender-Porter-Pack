import bpy, os
import bgl
import gpu
import json
import numpy as np
from pathlib import Path
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from gpu_extras.batch import batch_for_shader
from bpy.props import StringProperty, BoolProperty


lut_light = 'Lut_TimeDay.png'
lut_dark = 'Lut_TimeNight.png'
# lut_dark = 'Lut_TimeSunset.png'

########## ERRORS ##########

#Stop if no KK_Colors.json file was detected
def kk_json_error(self, context):
    self.layout.label(text="The KK_Colors.json file wasn't found. Please make sure it's in the selected \"PMX\" folder.")

#Stop if lut was detected
def kk_lut_error(self, context):
    self.layout.label(text="The LUT file wasn't found. Please make sure it's imported")


########## FUNCTIONS ##########

def color_to_KK(color, lut_name):
    width = 1
    height = 1

    # Some Sauce
    vertex_default = '''
    in vec2 a_position;

    void main() {
        gl_Position = vec4(a_position, 0.0, 1.0);
    }
    '''

    # The Secret Sauce
    current_code = '''
    uniform vec3 inputColor;
    uniform sampler2D lut;

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
        
        lutColor = to_srgb(lutColor);
        
        
        vec3 shaderColor = lutColor;
        
        gl_FragColor = vec4(shaderColor.rgb, 1);
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

def sample_and_convert_colors(mc_mask, texture, lut, exposure = (1, 1, 1)): 
    
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
    
    # Red
    pixel_list = np.where(np.all(mc_mask_data == (1, 0, 0, 1), axis=-1))[0]
    if len(pixel_list) > 0:
        red_index = filter_pixel(pixel_list, texture_data)
    
    # Green
    pixel_list = np.where(np.all(mc_mask_data >= (0, 1, 0, 1), axis=-1))[0]
    if len(pixel_list) > 0:
        green_index = filter_pixel(pixel_list, texture_data)
    else:
        # Green (Yellow)
        pixel_list = np.where(np.all(mc_mask_data == (1, 1, 0, 1), axis=-1))[0]
        if len(pixel_list) > 0:
            green_index = filter_pixel(pixel_list, texture_data)

    # Blue
    pixel_list = np.where(np.all(mc_mask_data == (0, 0, 1, 1), axis=-1))[0]
    if len(pixel_list) > 0:
        blue_index = filter_pixel(pixel_list, texture_data)
    else:
        # Blue (Cyan)
        pixel_list = np.where(np.all(mc_mask_data == (0, 1, 1, 1), axis=-1))[0]
        if len(pixel_list) > 0:
            blue_index = filter_pixel(pixel_list, texture_data)
        else:
            # Blue (Magenta)
            pixel_list = np.where(np.all(mc_mask_data == (1, 0, 1, 1), axis=-1))[0]
            if len(pixel_list) > 0:
                blue_index = filter_pixel(pixel_list, texture_data)
            else:
                # Blue (White)
                pixel_list = np.where(np.all(mc_mask_data == (1, 1, 1, 1), axis=-1))[0]
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

def init_import_colors(directory):
    print('Getting PMX textures from: ' + directory)

    # "Borrowed" some logic from importeverything.py :P
    file_list = Path(directory).glob('*.*')
    files = [file for file in file_list if file.is_file()]
    filtered_files = []

    # Checks
    json_file_missing = True
    for file in files:
        if 'KK_Colors.json' in str(file):
            json_file_path = str(file)
            json_file = open(json_file_path)
            json_color_data = json.load(json_file)
            json_file_missing = False
    
    if json_file_missing:
        bpy.context.window_manager.popup_menu(kk_json_error, title="Error", icon='ERROR')
        return True

    lut_missing = True
    if lut_light in bpy.data.images and lut_dark in bpy.data.images:
        lut_missing = False
    
    if lut_missing:
        bpy.context.window_manager.popup_menu(kk_lut_error, title="Error", icon='ERROR')
        return True

    
    # Remove unused files from the array
    excluded_texture_names = ['cf_m_eyeline', 'cf_m_hitomi_00', 'cf_m_mayuge', 'cf_m_noseline', 'cf_m_sirome', 'cf_m_tooth']
    for texture in files:
        if not any(name in texture.name for name in excluded_texture_names):
            filtered_files.append(texture)
    
    # Load and rename textures
    loaded_textures = []
    for texture in filtered_files:
        if '.png' in texture.name:
            bpy.ops.image.open(filepath=str(texture))
            bpy.data.images[texture.name].pack()
            # Correct image name
            new_name = texture.name.split('.')[0]
            new_name = new_name.split(' ')[0]

            new_texture = bpy.data.images[texture.name]
            new_texture.name = new_name
            loaded_textures.append(new_texture)

    update_shaders(loaded_textures, json_color_data, light = True) # Set light colors
    update_shaders(loaded_textures, json_color_data, light = False) # Set dark colors
    final_cleanup(loaded_textures)
    set_color_management()
    return True

def update_shaders(textures, json, light):

    def to_rgba(rgb):
        rgba = [rgb[0], rgb[1], rgb[2], 1]
        return rgba

    def json_to_color(color):
        rgb = [color['r'], color['g'], color['b']]
        return rgb

    node_groups = bpy.data.node_groups
    bpy_images = bpy.data.images
    excluded_shader_names = ['body', 'face']
    active_lut = lut_light if light else lut_dark

    ## Body
    body_mc_mask = None
    body_texture = None
    body_texture_node_group = None
    body_shader_node_group = None
    body_nipple_color = [1, 1, 1, 1]

    ## Face
    face_mc_mask = None
    face_texture = None
    face_texture_node_group = None
    face_shader_node_group = None
    face_blush_color = [1, 1, 1, 1]
    ## Eyebrows
    eyebrows_shader_node_group = None
    eyebrows_color = [1, 1, 1, 1]
    ## Eyeline
    eyeline_shader_node_group = None
    eyeliner_color = [1, 1, 1, 1]
    ## Tongue
    tongue_shader_node_group = None
    tongue_color = [1, 1, 1, 1]

    ## Hair
    hair_base_color = [1, 1, 1, 1]
    hair_root_color = [1, 1, 1, 1]
    hair_tip_color = [1, 1, 1, 1]

    ## Clothes & Other
    clothes_mc_masks = []
    clothes_textures = []
    clothes_texture_node_groups = []
    clothes_shader_node_groups = []

    ## Items
    item_data = []
    item_shader_node_groups = []

    ### Get shaders/texture groups and MC masks

    for texture in textures:
        if 'cf_m_body' in texture.name:
            body_texture_node_group = node_groups['Body textures']
            body_shader_node_group = node_groups['Body Shader']
            body_mc_mask = body_texture_node_group.nodes['BodyMC'].image
            body_texture = texture
            continue

        if 'cf_m_face' in texture.name:
            face_texture_node_group = node_groups['Face Textures']
            face_shader_node_group = node_groups['Face Shader']
            face_mc_mask = face_texture_node_group.nodes['FaceMC'].image
            face_texture = texture
            continue

        if not any(name in texture.name for name in excluded_shader_names):
            texture_name = texture.name + ' Textures'
            shader_name = texture.name + ' Shader'
            if texture_name in node_groups and shader_name in node_groups:
                temp_texture_node_group = node_groups[texture_name]
                temp_shader_node_group = node_groups[shader_name]
                temp_mc_mask = temp_texture_node_group.nodes['MainCol'].image

                clothes_texture_node_groups.append(temp_texture_node_group)
                clothes_shader_node_groups.append(temp_shader_node_group)
                clothes_mc_masks.append(temp_mc_mask)
                clothes_textures.append(texture)
            continue
    eyebrows_shader_node_group = node_groups['Eyebrows Shader']
    eyeline_shader_node_group = node_groups['Eyeline Shader']
    tongue_shader_node_group = node_groups['Tongue Shader']
    hair_shader_node_group = node_groups['Hair Shader']
    
    for idx, item in enumerate(json):
        if idx > 5:
            shader_name = item['materialName'] + ' Shader'
            if shader_name in node_groups:
                item_data.append(item)
                item_shader_node_groups.append(node_groups[shader_name])

    ### Set single colors

    face_blush_color = color_to_KK(json_to_color(json[0]['color1']), active_lut) / 255
    face_blush_color = to_rgba(face_blush_color)

    eyebrows_color = color_to_KK(json_to_color(json[1]['color1']), active_lut) / 255
    eyebrows_color = to_rgba(eyebrows_color)

    eyeliner_color = color_to_KK(json_to_color(json[2]['color1']), active_lut) / 255
    eyeliner_color = to_rgba(eyeliner_color)

    tongue_color = color_to_KK(json_to_color(json[3]['color1']), active_lut) / 255
    tongue_color = to_rgba(tongue_color)

    body_nipple_color = color_to_KK(json_to_color(json[4]['color1']), active_lut) / 255
    body_nipple_color = to_rgba(body_nipple_color)

    hair_base_color = color_to_KK(json_to_color(json[5]['color1']), active_lut) / 255
    hair_base_color = to_rgba(hair_base_color)

    hair_root_color = color_to_KK(json_to_color(json[5]['color2']), active_lut) / 255
    hair_root_color = to_rgba(hair_root_color)

    hair_tip_color = color_to_KK(json_to_color(json[5]['color3']), active_lut) / 255
    hair_tip_color = to_rgba(hair_tip_color)

    ### Set shader colors

    ## Body Shader
    r, g, b = sample_and_convert_colors(body_mc_mask, body_texture, active_lut, (1, 1.1, 1))
    shader_inputs = body_shader_node_group.nodes['Group.003' if light else 'Group.002'].inputs
    shader_inputs['Skin color' if light else 'Dark skin color'].default_value = to_rgba(r)
    shader_inputs['Skin detail color' if light else 'Skin detail multiplier'].default_value = to_rgba(g)
    shader_inputs['Nail Color'].default_value = to_rgba(b)
    shader_inputs['Nipple 1'].default_value = body_nipple_color
    shader_inputs['Nipple 2'].default_value = [1, 0, 0, 1] # Red
    shader_inputs['Nipple 3'].default_value = [0.9, 0.9, 0.9, 1] # Almost White
    shader_inputs['Nipple 4'].default_value = [1, 1, 1, 1] # White

    ## Face Shader
    r, g, b = sample_and_convert_colors(face_mc_mask, face_texture, active_lut)
    shader_inputs = face_shader_node_group.nodes['Group.003' if light else 'Group.006'].inputs
    shader_inputs['Skin color' if light else 'Dark skin color'].default_value = to_rgba(r)
    shader_inputs['Skin detail color'].default_value = to_rgba(g)
    shader_inputs['Mouth interior color'].default_value = to_rgba(b)
    shader_inputs['Light blush color'].default_value = face_blush_color

    ## Eyebrow Shader
    shader_inputs = eyebrows_shader_node_group.nodes['Group'].inputs
    shader_inputs['Light Eyebrow color' if light else 'Dark Eyebrow color'].default_value = eyebrows_color

    ## Eyeline Shader
    shader_inputs = eyeline_shader_node_group.nodes['Group.005' if light else 'Group.006'].inputs
    shader_inputs['Eyeline color'].default_value = eyeliner_color

    ## Tongue Shader
    shader_inputs = tongue_shader_node_group.nodes['Group.003' if light else 'Group.004'].inputs
    shader_inputs['Use Color mask instead? (1 = yes)'].default_value = 1
    shader_inputs['Manually set detail color? (1 = yes)'].default_value = 0
    shader_inputs['Color mask color (base)'].default_value = tongue_color
    shader_inputs['Color mask color (red)'].default_value = tongue_color
    shader_inputs['Color mask color (green)'].default_value = tongue_color
    shader_inputs['Color mask color (blue)'].default_value = tongue_color

    ## Hair Shader
    shader_inputs = hair_shader_node_group.nodes['Group.023' if light else 'Group.024'].inputs
    shader_inputs['Light Hair color' if light else 'Dark Hair color'].default_value = hair_base_color
    shader_inputs['Light Hair rim color' if light else 'Dark Hair rim color'].default_value = hair_root_color
    shader_inputs['Dark fade color'].default_value = hair_root_color
    shader_inputs['Light fade color'].default_value = hair_tip_color
    shader_inputs['Manually set the hair color detail? (1 = yes)'].default_value = 0

    ## Clothes/Other Shader
    for idx, texture in enumerate(clothes_textures):
        r, g, b = sample_and_convert_colors(clothes_mc_masks[idx], texture, active_lut)
        shader_inputs = clothes_shader_node_groups[idx].nodes['Group.003' if light else 'Group.004'].inputs
        shader_inputs['Use Color mask instead? (1 = yes)'].default_value = 1
        shader_inputs['Manually set detail color? (1 = yes)'].default_value = 0
        shader_inputs['Color mask color (base)'].default_value = [1, 1, 1, 1]
        shader_inputs['Color mask color (red)'].default_value = to_rgba(r)
        shader_inputs['Color mask color (green)'].default_value = to_rgba(g)
        shader_inputs['Color mask color (blue)'].default_value = to_rgba(b)

    ## Accessories/Items Shader
    for idx, item in enumerate(item_data):
        r = color_to_KK(json_to_color(item['color1']), active_lut) / 255
        g = color_to_KK(json_to_color(item['color2']), active_lut) / 255
        b = color_to_KK(json_to_color(item['color3']), active_lut) / 255
        shader_inputs = item_shader_node_groups[idx].nodes['Group.003' if light else 'Group.004'].inputs
        shader_inputs['Use Color mask instead? (1 = yes)'].default_value = 1
        shader_inputs['Manually set detail color? (1 = yes)'].default_value = 0
        shader_inputs['Color mask color (base)'].default_value = [1, 1, 1, 1]
        shader_inputs['Color mask color (red)'].default_value = to_rgba(r)
        shader_inputs['Color mask color (green)'].default_value = to_rgba(g)
        shader_inputs['Color mask color (blue)'].default_value = to_rgba(b)

def final_cleanup(textures):
    for texture in textures:
        bpy.data.images.remove(texture)
    return True

def set_color_management():
    bpy.data.scenes[0].display_settings.display_device = 'sRGB'
    bpy.data.scenes[0].view_settings.view_transform = 'Raw'
    bpy.data.scenes[0].view_settings.look = 'None'

class import_colors(bpy.types.Operator):
    bl_idname = "kkb.importcolors"
    bl_label = "Open PMX Textures folder"
    bl_description = "Open the folder containing the textures from the PMX export"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None

    def execute(self, context):
        directory = self.directory

        init_import_colors(directory)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

if __name__ == "__main__":
    bpy.utils.register_class(import_colors)
    print((bpy.ops.kkb.importcolors('INVOKE_DEFAULT')))

