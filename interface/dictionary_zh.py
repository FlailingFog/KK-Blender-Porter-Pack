translation_dictionary = {

    'seams'     : "修复身体接缝",
    'seams_tt'  : '合并靠近身体的顶点。这种合并可能会破坏颈部权重。如果禁用此选项，将保存权重，但可能会在身体上看到接缝',
    
    'outline'     : '使用通用轮廓线',
    'outline_tt'  : "启用来使用一种通用轮廓材质而不是几个单独的轮廓材质。选中此选项可能会导致轮廓线透明度问题",
    
     'keep_templates'        : "保留材质模板",
    'keep_templates_tt'     : "保持启用以将KKBP材质模板设置为假用户。这将防止它们在blender关闭时被删除。如果要在角色完成后将其应用于其他对象，则此选项非常有用",

    'sfw_mode'          : '和谐模式',
    'sfw_mode_tt'       : '试图掩盖一些少儿不宜的东西',

    'arm_drop'          :"骨架类型",
    'arm_drop_A'        : "使用KKBP骨架",
    'arm_drop_A_tt'     : "使用KKBP骨架。这将稍微修改骨架，使其具有基本的IK骨骼",
    'arm_drop_B'        : "使用Rigify骨架",
    'arm_drop_B_tt'     : "使用Rigify骨架。这是一种先进的骨架，适用于blender",
    'arm_drop_C'        : "使用恋活骨架",
    'arm_drop_C_tt'     : "使用恋活骨架。这将与游戏中的骨骼命名和结构相匹配",
    'arm_drop_D'        : "使用pmx骨架",
    'arm_drop_D_tt'     : "使用pmx骨架。这是你从KKBP导出时得到的骨架",

    'cat_drop'      : '运行类型',
    'cat_drop_A'    : "不要暂停分类",
    'cat_drop_A_tt' : "导入所有内容并获得包含所有模型衣服的单个对象。默认情况下隐藏任何备用衣服",
    'cat_drop_B'    : "暂停来分类",
    'cat_drop_B_tt' : "导入所有内容，但暂停以手动将衣服分成多组对象。头发必须分开并命名为 Hair 或 hair 分离完成后，单击“完成分类”按钮以完成导入。默认情况下隐藏任何备用衣服",
    'cat_drop_C'    : "自动分类",
    'cat_drop_C_tt' : "导入所有内容并自动将每件衣服分成多个对象。此选项禁用blender中显示的轮廓修改器",
    'cat_drop_D'    : "按SMR数据分类",
    'cat_drop_D_tt' : "导入所有内容并通过SMR（蒙皮网格渲染器）自动分离每个对象。注意：此选项仅用于导出网格，因此不会应用任何材质模板或颜色",

    'dark'      : "暗色",
    'dark_A'    : "LUT 夜晚",
    'dark_A_tt' : "使深色偏蓝色",
    'dark_B'    : "LUT 黄昏",
    'dark_B_tt' : "使深色偏红色",
    'dark_C'    : "LUT 白天",
    'dark_C_tt' : "使深色与浅色相同",
    'dark_D'    : "饱和",
    'dark_D_tt' : "使深色比浅色更饱和",
    'dark_E'    : '亮度',
    'dark_E_tt' : "使深色比浅色暗",
    'dark_F'    : '实验性',
    'dark_F_tt' : "使用实验方法设置深色",

     'prep_drop'         : "导出类型",
    'prep_drop_A'       : "Unity - VRM兼容",
    'prep_drop_A_tt'    : """删除轮廓...
移除重复的眼白材质槽（如果存在），
编辑骨骼层次以允许Unity自动检测正确骨骼""",
    'prep_drop_B'       : "通用FBX-无更改",
    'prep_drop_B_tt'    : """删除轮廓...
移除重复的眼白材质槽（如果存在）""",
    'prep_drop_D'       : "Unity-兼容VRChat",
    'prep_drop_D_tt'    : """删除轮廓...
移除重复的眼白材质槽（如果存在）
移除“Upper Chest”骨骼，
编辑骨骼层次以允许Unity自动检测正确骨骼""",

    'simp_drop'     : '骨架简化型',
    'simp_drop_A'   : '非常简单（慢）',
    'simp_drop_A_tt': '如果希望骨骼数很少，请使用此选项。将瞳孔骨骼移动到第1层，并简化骨架层3-5、11-12和17-19上的骨骼（留下约110个骨骼，不包括裙子骨骼）',
    'simp_drop_B'   : '简单',
    'simp_drop_B_tt': '将瞳孔骨骼移动到层1并简化骨架层11上无用的骨骼（留下大约1000个骨骼）',
    'simp_drop_C'   : '无更改（快）',
    'simp_drop_C_tt': '不简化任何东西',

    'bake'          : '烘焙材质模板',
    'bake_light'    : "亮色",
    'bake_light_tt' : "烘焙所有纹理的亮色版本",
    'bake_dark'     : "暗色",
    'bake_dark_tt'  : "烘焙所有纹理的暗色版本",
    'bake_norm'     : "法线",
    'bake_norm_tt'  : "烘焙所有纹理的法线版本",
    'bake_mult'     : '烘焙乘数：',
    'bake_mult_tt'  : "如果烘焙纹理模糊，请将其设置为2或3",
    'old_bake'      : '使用旧版烘焙',
    'old_bake_tt'   : '启用以使用旧的烘焙系统。该系统不会烘焙任何额外的UV贴图，如头发光泽或眼影',
    
    'shape_A'       : '使用KKBP形态键',
    'shape_A_tt'    : '重命名并删除旧的形态键。这将合并属于同一表情的形态键，并删除其余部分',
    'shape_B'       : "保存部分形态键",
    'shape_B_tt'    : "保存用于生成恋活形态键的部分形态键。这些本身是无用的",
    'shape_C'       : "跳过修改形态键",
    'shape_C_tt'    : "使用恋活形态键。这不会以任何方式改变形态键",
    'shader_A'       : '使用Eevee',
    'shader_B'       : "使用Cycles",
    'shader_C'       : "使用LBS",
    'shader_C_tt'    : "为Lightning Boy shader 2.1.3使用修改的着色器设置",
    
     'atlas'         : '图集类型',

    'export_fbx'    : '导出FBX',
    'export_fbx_tt' : '将所有可见对象导出为FBX文件。这与文件-菜单中的FBX导出功能相同',

    'import_export' : '导入导出',
    'import_model'  : '导入模型',
    'finish_cat'    : '完成分类',
    'recalc_dark'   : '重新计算暗色',
    'prep'          : '准备目标应用程序',
    'apply_temp'    : '应用烘焙模板',

    'rigify_convert': "转换为Rigify",
    'sep_eye'       : "分离眼睛和眉毛",

    'convert_image' : '使用KKBP转换图像',

    'kkbp_import_tt'   : "导入恋活模型（.pmx格式），并对其应用修复",
    'mat_import_tt'     : "完成对象分离，应用纹理和颜色",
    'export_prep_tt'    : "查看下拉列表以了解更多信息",
    'bake_mats_tt'      : "打开要将材质模板烘焙到的文件夹",
    'apply_mats_tt'     : "打开包含烘焙材质的文件夹。使用菜单加载亮/暗/法线材质",
    'import_colors_tt'  : "打开包括.pmx模型文件的文件夹以重新计算暗色",

    }
