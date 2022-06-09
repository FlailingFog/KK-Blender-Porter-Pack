from .dictionary_en import translation_dictionary as fallback

translation_dictionary = {
    'bake_mult'     : 'ベーク乗数:',
    'bake_mult_tt'  : "不鮮明なテクスチャーがジェネレートされたら２，３にしてみて",
    
    'seams'     : "からだを縫合する",
    'seams_tt'  : '距離でからだに近い頂点をマージ。 この設定はRemoving doubles also screws with the weights around certain areas. Disabling this will preserve the weights but may cause seams to appear around the neck and down the chest',
    
    'outline'     : 'Use generic outline',
    'outline_tt'  : "Enable to use one generic outline material as opposed to using several unique ones. Checking this may cause outline transparency issues",
    
    'keep_templates'        : "Keep material templates",
    'keep_templates_tt'     : "Keep enabled to set the KKBP material templates to fake user. This will keep them from being deleted when blender is closed. Useful if you want to apply them to other objects after your character is finished",

    'arm_drop'          :"アーマチュアのタイプ",
    'arm_drop_A'        : "KKBPアーマチュアにする",
    'arm_drop_A_tt'     : "KKBPアーマチュアにする。この設定にはアーマチュアは改造されて、ベーシックなIKがジェネレートされる",
    'arm_drop_B'        : "Rigifyアーマチュアにする",
    'arm_drop_B_tt'     : "Rigifyアーマチュアにする。この設定にはBlenderでの使用アーマチュアがジェネレートされる",
    'arm_drop_C'        : "コイカツのアーマチュアにする",
    'arm_drop_C_tt'     : "コイカツのアーマチュアにする。この設定にはボーンの名前、アーマチュアの構造はコイカツのアーマチュアと一致される",
    'arm_drop_D'        : "PMXアーマチュアにする",
    'arm_drop_D_tt'     : "PMXアーマチュアにする。この設定にはアーマチュアが改造されない",

    'cat_drop'      : '操作タイプ',
    'cat_drop_A'    : "カテゴライズのために休止しない",
    'cat_drop_A_tt' : "Import everything and get a single object containing all your model's clothes. Hides any alternate clothes by default",
    'cat_drop_B'    : "カテゴライズのために休止する",
    'cat_drop_B_tt' : "Import everything, but pause to manually separate the clothes into groups of objects. When done separating, click the Finish categorization button to finish the import. Hides any alternate clothes by default",
    'cat_drop_C'    : "AUTOカテゴライズ",
    'cat_drop_C_tt' : "Import everyting and automatically separate every piece of clothing into several objects. This option disables the outline modifier shown in blender",
    'cat_drop_D'    : "SMRデータでカテゴライズ",
    'cat_drop_D_tt' : "Import everyting and automatically separate every object by it's Skinned Mesh Renderer. Note: This option is only for exporting meshes so it will not apply any material templates or colors",

    'dark'      : "ダークな色",
    'dark_A'    : "LUT 夜",
    'dark_A_tt' : "ダークな色青くする",
    'dark_B'    : "LUT 暮れ",
    'dark_B_tt' : "ダークな色赤にする",
    'dark_C'    : "LUT 昼",
    'dark_C_tt' : "ダークな色はライトな色と同じにする",
    'dark_D'    : "飽和",
    'dark_D_tt' : "ダークな色を飽和する",
    'dark_E'    : '明るさ',
    'dark_E_tt' : "ダークな色黒くする",

    'prep_drop'         : "エクスポートタイプ",
    'prep_drop_A'       : "Unity - VRMコンパチ",
    'prep_drop_A_tt'    : """すべてのオブジェクトを組み合わせて...
    輪郭を削除して,
    Eyeの複写、Eyewhiteの複写を削除して,
    瞳のボーンをアマチュアレイヤー１６に移って,
    アマチュアレイヤー 3 / 5 / 11 / 12 / 13 のボーンをシンプル化して,
    Unityがボーンを独りでに見つけられるためにアマチュアを改造して""",
    'prep_drop_C'       : '汎用 - シンプル',
    'prep_drop_C_tt'    : """すべてのオブジェクトを組み合わせて...
    輪郭を削除して,
    Eyeの複写、Eyewhiteの複写を削除して,
    瞳のボーンをアマチュアレイヤー１６に移って,
    アマチュアレイヤー 11 のボーンをシンプル化して""",
    'prep_drop_D'       : "汎用 - 変更なし",
    'prep_drop_D_tt'    : """すべてのオブジェクトを組み合わせて...
    輪郭を削除して,
    Eyeの複写、Eyewhiteの複写を削除して""",

    'bake'          : 'マテリアルテンプレートをベーク',
    'bake_light'    : "ライト",
    'bake_light_tt' : "ライトテクスチャーをベーク",
    'bake_dark'     : "ダーク",
    'bake_dark_tt'  : "ダークテクスチャーをベーク",
    'bake_norm'     : "ノーマル",
    'bake_norm_tt'  : "ノーマルテクスチャーをベーク",

    'shape_A'       : 'Use KKBP shapekeys',
    'shape_A_tt'    : 'Rename and delete the old shapekeys. This will merge the shapekeys that are part of the same expression and delete the rest',
    'shape_B'       : "Save partial shapekeys",
    'shape_B_tt'    : "Save the partial shapekeys that are used to generate the KK shapekeys. These are useless on their own",
    'shape_C'       : "Skip modifying shapekeys",
    'shape_C_tt'    : "Use the stock Koikatsu shapekeys. This will not change the shapekeys in any way",

    'atlas'         : 'アトラスタイプ',

    'import_export' : 'インポート ・ エクスポート',
    'import_model'  : 'モデルをインポート',
    'finish_cat'    : 'カテゴライズしまって',
    'recalc_dark'   : 'ダークな色を再計算する',
    'prep'          : 'ターゲットアップのために準備する',
    'apply_temp'    : 'ベークしたテンプレートをつけて',

    'rigify_convert': "Rigifyアーマチュアに変えて",
    'sep_eye'       : "EyesとEyebrowsを別々になって",

    'convert_image' : 'KKBPのLUTでイマージをコンヴァート'
    }

def t(text_entry):
    try:
        return translation_dictionary[text_entry]
    except:
        return fallback[text_entry]

