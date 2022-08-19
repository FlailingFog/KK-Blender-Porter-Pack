from .dictionary_en import translation_dictionary as english_fallback

translation_dictionary = {
    'bake_mult'     : 'ベーク乗数:',
    'bake_mult_tt'  : "ベークしたテクスチャーがぼやけている場合は２，３にしてみて",
    
    'seams'     : "体を縫合する",
    'seams_tt'  : '体に近い頂点をマージ。 このマージには首のウエイトが台無しになる可能性がある。 このオプションを無効にしたらウエイトが保存されるけど体に縫い目が見えるかも',
    
    'outline'     : '一つのアウトラインモード',
    'outline_tt'  : "このオプションにしたらシングルのアウトラインを使われる。 このオプションにしたらアウトライン透明の問題が起こるかも",
    
    'keep_templates'        : "マテリアルテンプレートを保存",
    'keep_templates_tt'     : "KKBPマテリアルテンプレートをフェイクユーザーに設定する",

    'sfw_mode'          : 'エロ無しモード',
    'sfw_mode_tt'       : 'プラグインがエロの部分を隠してみる',

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
    'cat_drop_A_tt' : "すべてをインポートして一つの服オブジェクトにする。別の服はひとりでに隠される",
    'cat_drop_B'    : "カテゴライズのために休止する",
    'cat_drop_B_tt' : "すべてをインポートしてインポートを休止する。休止の状態に手動で服を別々になれる。髪の毛は別のオブジェクトに別々にされてから新しいオブジェクトは「Hair」か「hair」に名前を変更しないと。服を手動でカテゴライズしたら「カテゴライズしまって」ボタンをクリックして。別の服はひとりでに隠される",
    'cat_drop_C'    : "AUTOカテゴライズ",
    'cat_drop_C_tt' : "すべてをインポートして個々の服オブジェクトにする。この設定にはアウトラインを削除される",
    'cat_drop_D'    : "SMRデータでカテゴライズ",
    'cat_drop_D_tt' : "すべてをインポートしてSMR(Skinned Mesh Renderer)データで服を別々にする。この設定にはマテリアルテンプレートや色データや使われないからモデルはテクスチャーなしで見える",

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
    'prep_drop_A_tt'    : """アウトラインを削除して...
    Eyewhiteの複写を削除して,
    Unityがボーンをひとりでに見つけられるためにアーマチュアを改造して""",
    'prep_drop_B'       : "汎用FBX - 変更なし",
    'prep_drop_B_tt'    : """アウトラインを削除して...
    Eyewhiteの複写を削除して""",

    'simp_drop'     : 'アーマチュアの簡略化',
    'simp_drop_A'   : '超シンプル (遅い)',
    'simp_drop_A_tt': 'この設定には骨の数が減る。瞳の骨をアーマチュアレイヤー１に移って, アーマチュアレイヤー3,4,5,11,12,17,18,19の骨が簡略化される (約110骨が残る)',
    'simp_drop_B'   : 'シンプル',
    'simp_drop_B_tt': 'この設定には骨の数が減る。瞳の骨をアーマチュアレイヤー１に移って, アーマチュアレイヤー11の骨が簡略化される (約1000骨が残る)',
    'simp_drop_C'   : '簡略化してない (早い)',
    'simp_drop_C_tt': 'アーマチュアが簡略化されない',
    
    'bake'          : 'マテリアルテンプレートをベーク',
    'bake_light'    : "ライト",
    'bake_light_tt' : "ライトテクスチャーをベーク",
    'bake_dark'     : "ダーク",
    'bake_dark_tt'  : "ダークテクスチャーをベーク",
    'bake_norm'     : "ノーマル",
    'bake_norm_tt'  : "ノーマルテクスチャーをベーク",

    'shape_A'       : 'KKBPシェイプキーにする',
    'shape_A_tt'    : 'シェイプキーを変更して部分的なシェイプキーを削除する',
    'shape_B'       : "部分的なシェイプキーを保存",
    'shape_B_tt'    : "シェイプキーを変更して部分的なシェイプキーを保存する",
    'shape_C'       : "シェイプキー変更しない",
    'shape_C_tt'    : "コイカツのシェイプキーにする。シェイプキーが変更されない",

    'atlas'         : 'アトラスタイプ',

    'import_export' : 'インポート ・ エクスポート',
    'import_model'  : 'モデルをインポート',
    'finish_cat'    : 'カテゴライズしまって',
    'recalc_dark'   : 'ダークな色を再計算する',
    'prep'          : 'ターゲットアプリのために準備する',
    'apply_temp'    : 'ベークしたテンプレートをつけて',

    'rigify_convert': "Rigifyアーマチュアに変えて",
    'sep_eye'       : "EyesやEyebrowsやBodyのオブジェクトから別々になって",

    'convert_image' : 'KKBPのLUTでイマージをコンヴァート',

    'quick_import_tt'   : "コイカツモデル(.PMXフォーマット)をインポートして改造して",
    'mat_import_tt'     : "カテゴライズしまってテクスチャーや色データつけて",
    'export_prep_tt'    : "メニューの情報をチェックして",
    'bake_mats_tt'      : "フォルダにマテリアルテンプレートをベークして",
    'apply_mats_tt'     : "ベークしたマテリアルテンプレートをフォルダから読み取る。メニューからライト・ダーク・ノーマルバージョンを選択できる",
    'import_colors_tt'  : ".PMXフォルダを選択したらダークな色を再計算できる",

    }

def t(text_entry):
    try:
        return translation_dictionary[text_entry]
    except:
        return english_fallback[text_entry]

