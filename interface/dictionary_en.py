from bpy.app.translations import locale
from .dictionary_jp import translation_dictionary as jp_translation
from .dictionary_zh import translation_dictionary as zh_translation

translation_dictionary = {

    'seams'     : "Fix body seams",
    'seams_tt'  : 'This performs a "remove doubles" operation on the body materials. Removing doubles screws with the weights around certain areas and will mess with atlas creation. Disabling this will preserve the weights and allow you to create an atlas, but may cause seams to appear around the neck and down the chest when the outline modifier is on',
    
    'outline'     : 'Use single outline',
    'outline_tt'  : "Enable to use one generic outline material as opposed to using several unique ones. Checking this may cause outline transparency issues",
    
    'keep_templates'        : "Keep material templates",
    'keep_templates_tt'     : "Keep enabled to set the KKBP material templates to fake user. This will keep them from being deleted when blender is closed. Useful if you want to apply them to other objects after your character is finished",

    'sfw_mode'          : 'SFW mode',
    'sfw_mode_tt'       : 'Attempts to cover up some NSFW things',

    'arm_drop'          : "Armature type",
    'arm_drop_A'        : "Use KKBP Armature",
    'arm_drop_A_tt'     : "Use the KKBP armature. This will slightly modify the armature and give it basic IKs",
    'arm_drop_B'        : "Use Rigify Armature",
    'arm_drop_B_tt'     : "Use the Rigify armature. This is an advanced armature suitable for use in Blender",
    'arm_drop_C'        : "Use Koikatsu Armature",
    'arm_drop_C_tt'     : "Use the stock Koikatsu armature. This will match the bone naming and structure of the one in-game",
    'arm_drop_D'        : "Use PMX Armature",
    'arm_drop_D_tt'     : "Use the stock PMX armature. This is the armature you get from the KKBP exporter",

    'cat_drop'      : 'Run type',
    'cat_drop_A'    : "Single clothes object",
    'cat_drop_A_tt' : "Import everything and get a single object containing all your model's clothes. Hides any alternate clothes by default",
    'cat_drop_C'    : "Separate every object",
    'cat_drop_C_tt' : "Import everything and automatically separate every single piece of clothing into several objects",
    'cat_drop_D'    : "Separate by SMR Data",
    'cat_drop_D_tt' : "Import everyting and automatically separate every object by it's Skinned Mesh Renderer. Note: This option is only for exporting meshes so it will not apply any material templates or colors",

    'dark'      : "Dark colors",
    'dark_C'    : "Do not use dark colors",
    'dark_C_tt' : "Makes the dark colors the same as the light colors",
    'dark_F'    : 'Automatic dark colors',
    'dark_F_tt' : "Uses an automatic method to set the dark colors",

    'prep_drop'         : "Export type",
    'prep_drop_A'       : "Unity - VRM compatible",
    'prep_drop_A_tt'    : """Removes the outline and...
    removes duplicate Eyewhite material slot if present,
    edits bone hierarchy to allow Unity to automatically detect the right bones""",
    'prep_drop_B'       : "Generic FBX - No changes",
    'prep_drop_B_tt'    : """Removes the outline and...
    removes duplicate Eyewhite material slot if present""",
    'prep_drop_D'       : "Unity - VRChat compatible",
    'prep_drop_D_tt'    : """Removes the outline and...
    removes duplicate Eyewhite material slot if present,
    removes the "Upper Chest" bone,
    edits bone hierarchy to allow Unity to automatically detect the right bones""",

    'prep_drop_E'       : "Unreal Engine",
    'prep_drop_E_tt'    : """Removes the outline and...
    removes duplicate Eyewhite material slot if present,
    edits bone hierarchy to match Epic Mannequin skeleton""",

    'simp_drop'     : 'Armature simplification type',
    'simp_drop_A'   : 'Very simple (SLOW)',
    'simp_drop_A_tt': 'Use this option if you want a very low bone count. Moves the pupil bones to layer 1 and simplifies bones on armature layers 3-5, 11-12, and 17-19 (Leaves you with ~100 bones not counting the skirt bones)',
    'simp_drop_B'   : 'Simple',
    'simp_drop_B_tt': 'Moves the pupil bones to layer 1 and simplifies the useless bones on armature layer 11 (Leaves you with ~500 bones)',
    'simp_drop_C'   : 'No changes (FAST)',
    'simp_drop_C_tt': 'Does not simplify anything',

    'bake'          : 'Finalize materials',
    'bake_light'    : "Light",
    'bake_light_tt' : "Finalize light version of all textures",
    'bake_dark'     : "Dark",
    'bake_dark_tt'  : "Finalize dark version of all textures",
    'bake_norm'     : "Normal",
    'bake_norm_tt'  : "Finalize normal version of all textures",
    'bake_mult'     : 'Finalize multiplier',
    'bake_mult_tt'  : "Set this to 2 or 3 if the finalized texture is blurry",
    'old_bake'      : 'Use V4 baker',
    'old_bake_tt'   : 'Enable to use the old finalization system. This system will not bake any extra UV maps like hair shine or eyeshadow, but it may help if you are encountering corruption in the finalized images',

    'shape_A'       : 'Use KKBP shapekeys',
    'shape_A_tt'    : 'Rename and delete the old shapekeys. This will merge the shapekeys that are part of the same expression and delete the rest',
    'shape_B'       : "Save partial shapekeys",
    'shape_B_tt'    : "Save the partial shapekeys that are used to generate the KK shapekeys. These are useless on their own",
    'shape_C'       : "Skip modifying shapekeys",
    'shape_C_tt'    : "Use the stock Koikatsu shapekeys. This will not change the shapekeys in any way",

    'shader_A'       : 'Use Eevee',
    'shader_B'       : "Use Cycles (toon)",
    'shader_D'       : "Use Cycles (classic)",
    'shader_C'       : "Use Eevee mod",
    'shader_C_tt'    : "Uses a modified shader setup for Eevee",

    'import_export' : 'Importing and Exporting',
    'extras'        : 'KKBP Extras',
    'import_model'  : 'Import model',
    'prep'          : 'Prep for target application',

    'studio_object'             : 'Import studio object',
    'studio_object_tt'          : 'Open the folder containing the fbx files exported with SB3Utility',
    'convert_texture'           : 'Convert texture?',
    'convert_texture_tt'        : '''Enable this if you want the plugin to saturate the item's textures using the in-game LUT''',
    'single_animation'          : 'Import single animation file',
    'single_animation_tt'       : 'Only available for the Rigify armature. Imports an exported Koikatsu .fbx animation file and applies it to your character. Mixamo .fbx files are also supported if you use the toggle below',
    'animation_koi'             : 'Import Koikatsu animation',
    'animation_mix'             : 'Import Mixamo animation',
    'animation_type_tt'         : 'Disable this if you are importing a Koikatsu .fbx animation. Enable this if you are importing a Mixamo .fbx animation',
    'animation_library'         : 'Create animation library',
    'animation_library_tt'      : "Only available for the Rigify Armature. Creates an animation library using the current file and current character. Will not save over the current file in case you want to reuse it. Open the folder containing the animation files exported with SB3Utility",
    'animation_library_scale'   : 'Scale arms',
    'animation_library_scale_tt': 'Check this to scale the arms on the y axis by 5%. This will make certain poses more accurate to the in-game one',
    'map_library'               : 'Create map asset library',
    'map_library_tt'            : "Creates an asset library using ripped map data. Open the folder containing the map files exported with SB3Utility. Takes 40 to 500 seconds per map",

    'rigify_convert'            : "Convert for Rigify",
    'rigify_convert_tt'         : "Runs several scripts to convert a KKBP armature to be Rigify compatible",
    'sep_eye'                   : "Separate Eyes and Eyebrows",
    'sep_eye_tt'                : "Separates the Eyes and Eyebrows from the Body object and links the shapekeys to the Body object. Useful for when you want to make eyes or eyebrows appear through the hair using the Cryptomatte features in the compositor",
    'bone_visibility'           : "Show bones for current outfit",
    'bone_visibility_tt'        : "This will update visibility for all accessory bones. For example, if you have an Outfit 00 and an Outfit 01, both of them are visible then all accessory bones will be shown. If you hide Outfit 00 and click this button, only Outfit 01's accessory bones will be shown",
    'export_sep_meshes'         : "Export Seperate Meshes",
    'export_sep_meshes_tt'      : "Only available for the \"Separate by SMR data\" option. Choose where to export meshes",
    'link_hair'                 : 'Update hair materials',
    'link_hair_tt'              : 'Click to copy the current colors, detail intensity, etc to the other hair materials on this object',

    'kkbp_import_tt'    : "Imports a Koikatsu model (.pmx format) and applies fixes to it",
    'export_prep_tt'    : "Use the KKBP Armature for the best results. Check the dropdown for more info",
    'bake_mats_tt'      : "Finalize materials as .png files. These will be stored in the original .pmx folder",

    'delete_cache' : 'Delete cache',
    'delete_cache_tt' : 'Enable this to delete the cache files. Cache files are generated when you import a model or finalize materials. These are stored in the pmx folder as "atlas_files", "baked_files", "dark_files" and "saturated_files". Enabling this option will delete ALL files inside of these folders',

    'use_atlas' : 'Create atlas',
    'use_atlas_tt': 'Enable this to create a material atlas when finalizing materials',
    'dont_use_atlas' : 'Don\'t create Atlas',

    'mat_comb_tt' : 'KKBP uses parts of Shotariya\'s Material Combiner addon to automatically merge your materials into an atlas. Click this if you want to manually combine your materials instead of letting KKBP do it for you (requires you to download the Material Combiner addon. Also, make sure you have already clicked the Finalize Materials button in the KKBP panel or it will not work) ',
    'matcomb' : 'Setup materials for Material Combiner',
    'mat_comb_switch' : 'Toggle light / dark for Material Combiner',
    'mat_comb_switch_tt' : 'Click this to toggle texture state to get both a light and dark atlas from Material Combiner',

    'pillow' : 'Install PIL to use atlas feature',
    'pillow_tt':'Click to install Pillow. This could take a while and might require you to run Blender as Admin',
    'reset_mats' : 'Reset finalized materials',
    'reset_mats_tt' : 'Click this to reset ALL of your finalized materials back to the -ORG version. Handy if you want to refinalize everything',
    
    }

def t(text_entry):
    try:
        if locale == 'ja_JP':
            return jp_translation[text_entry]
        #Blender 4 changed the language code for Simplified Chinese from 'zh_CN' to 'zh_HANS'
        elif locale in ['zh_HANS', 'zh_CN']:
            return zh_translation[text_entry]
        else:
            return translation_dictionary[text_entry]
    except KeyError:
        if translation_dictionary.get(text_entry):
            return translation_dictionary[text_entry] 
        else:
            return text_entry

