translation_dictionary = {
    'bake_mult'     : 'Bake multiplier:',
    'bake_mult_tt'  : "Set this to 2 or 3 if the baked texture is blurry",
    
    'seams'     : "Fix body seams",
    'seams_tt'  : 'This performs a "remove doubles" operation on the body materials. Removing doubles also screws with the weights around certain areas. Disabling this will preserve the weights but may cause seams to appear around the neck and down the chest',
    
    'outline'     : 'Use generic outline',
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
    'cat_drop_A'    : "Don't pause to categorize",
    'cat_drop_A_tt' : "Import everything and get a single object containing all your model's clothes. Hides any alternate clothes by default",
    'cat_drop_B'    : "Pause to categorize",
    'cat_drop_B_tt' : "Import everything, but pause to manually separate the clothes into groups of objects. The hair must be separated and named \"Hair\" or \"hair\". When done separating, click the Finish categorization button to finish the import. Hides any alternate clothes by default",
    'cat_drop_C'    : "Automatically categorize",
    'cat_drop_C_tt' : "Import everyting and automatically separate every piece of clothing into several objects. This option disables the outline modifier shown in blender",
    'cat_drop_D'    : "Categorize by SMR Data",
    'cat_drop_D_tt' : "Import everyting and automatically separate every object by it's Skinned Mesh Renderer. Note: This option is only for exporting meshes so it will not apply any material templates or colors",

    'dark'      : "Dark colors",
    'dark_A'    : "LUT Night",
    'dark_A_tt' : "Makes the dark colors blue-ish",
    'dark_B'    : "LUT Sunset",
    'dark_B_tt' : "Makes the dark colors red-ish",
    'dark_C'    : "LUT Day",
    'dark_C_tt' : "Makes the dark colors the same as the light colors",
    'dark_D'    : "Saturation based",
    'dark_D_tt' : "Makes the dark colors more saturated than the light ones",
    'dark_E'    : 'Value reduction',
    'dark_E_tt' : "Makes the dark colors darker than the light ones",

    'prep_drop'         : "Export type",
    'prep_drop_A'       : "Unity - VRM compatible",
    'prep_drop_A_tt'    : """Removes the outline and...
    removes duplicate Eyewhite material slot if present,
    edits bone hierarchy to allow Unity to automatically detect the right bones""",
    'prep_drop_B'       : "Generic FBX - No changes",
    'prep_drop_B_tt'    : """Removes the outline and...
    removes duplicate Eyewhite material slot if present""",

    'simp_drop'     : 'Armature simplification type',
    'simp_drop_A'   : 'Very simple (SLOW)',
    'simp_drop_A_tt': 'Use this option if you want a very low bone count. Moves the pupil bones to layer 1 and simplifies bones on armature layers 3-5, 11-12, and 17-19 (Leaves you with ~110 bones not counting the skirt bones)',
    'simp_drop_B'   : 'Simple',
    'simp_drop_B_tt': 'Moves the pupil bones to layer 1 and simplifies the useless bones on armature layer 11 (Leaves you with ~1000 bones)',
    'simp_drop_C'   : 'No changes (FAST)',
    'simp_drop_C_tt': 'Does not simplify anything',

    'bake'          : 'Bake material templates',
    'bake_light'    : "Light",
    'bake_light_tt' : "Bake light version of all textures",
    'bake_dark'     : "Dark",
    'bake_dark_tt'  : "Bake dark version of all textures",
    'bake_norm'     : "Normal",
    'bake_norm_tt'  : "Bake normal version of all textures",

    'shape_A'       : 'Use KKBP shapekeys',
    'shape_A_tt'    : 'Rename and delete the old shapekeys. This will merge the shapekeys that are part of the same expression and delete the rest',
    'shape_B'       : "Save partial shapekeys",
    'shape_B_tt'    : "Save the partial shapekeys that are used to generate the KK shapekeys. These are useless on their own",
    'shape_C'       : "Skip modifying shapekeys",
    'shape_C_tt'    : "Use the stock Koikatsu shapekeys. This will not change the shapekeys in any way",

    'atlas'         : 'Atlas type',

    'import_export' : 'Importing and Exporting',
    'import_model'  : 'Import model',
    'finish_cat'    : 'Finish categorization',
    'recalc_dark'   : 'Recalculate dark colors',
    'prep'          : 'Prep for target application',
    'apply_temp'    : 'Apply baked templates',

    'rigify_convert': "Convert for Rigify",
    'sep_eye'       : "Separate Eyes and Eyebrows",

    'convert_image' : 'Convert image with KKBP',

    'quick_import_tt'   : "Imports a Koikatsu model (.pmx format) and applies fixes to it",
    'mat_import_tt'     : "Finish separating objects, apply the textures and colors",
    'export_prep_tt'    : "Check the dropdown for more info",
    'bake_mats_tt'      : "Open the folder you want to bake the material templates to",
    'apply_mats_tt'     : "Open the folder that contains the baked materials. Use the menu to load the Light / Dark / Normal passes",
    'import_colors_tt'  : "Open the folder containing your model.pmx file to recalculate the dark colors",

    }

def t(text_entry):
    try:
        return translation_dictionary[text_entry]
    except:
        return '???'

