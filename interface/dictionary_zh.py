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

    'cat_drop'      : '分类类型',
    'cat_drop_A'    : "单一服装",
    'cat_drop_A_tt' : "导入所有内容并获得包含所有衣服模型的单个对象。默认情况下隐藏任何备用衣服",
    'cat_drop_C'    : "分开所有对象",
    'cat_drop_C_tt' : "导入所有内容并自动将每件衣服分成多个对象",
    'cat_drop_D'    : "按SMR数据分类",
    'cat_drop_D_tt' : "导入所有内容并通过SMR（蒙皮网格渲染器）自动分离每个对象。注意：此选项仅用于导出网格，因此不会应用任何材质模板或颜色",

    'dark'      : "暗色",
    'dark_C'    : "不使用暗色",
    'dark_C_tt' : "使暗色与亮色相同",
    'dark_F'    : '自动',
    'dark_F_tt' : "使用自动方法设置暗色",

    'prep_drop'         : "导出类型",
    'prep_drop_A'       : "Unity - VRM兼容",
    'prep_drop_A_tt'    : """删除轮廓...
    移除重复的眼白材质槽（如果存在），
    编辑骨骼层级以允许Unity自动检测正确骨骼""",
    'prep_drop_B'       : "通用FBX-无更改",
    'prep_drop_B_tt'    : """删除轮廓...
    移除重复的眼白材质槽（如果存在）""",
    'prep_drop_D'       : "Unity-兼容VRChat",
    'prep_drop_D_tt'    : """删除轮廓...
    移除重复的眼白材质槽（如果存在）
    移除“Upper Chest”骨骼，
    编辑骨骼层级以允许Unity自动检测正确骨骼""",

    'simp_drop'     : '骨骼简化类型',
    'simp_drop_A'   : '非常简单（慢）',
    'simp_drop_A_tt': '如果希望骨骼数很少，请使用此选项。将瞳孔骨骼移动到第1层，并简化骨架层3-5、11-12和17-19上的骨骼（留下约110个骨骼，不包括裙子骨骼）',
    'simp_drop_B'   : '简单',
    'simp_drop_B_tt': '将瞳孔骨骼移动到层1并简化骨架层11上无用的骨骼（留下大约1000个骨骼）',
    'simp_drop_C'   : '无更改（快）',
    'simp_drop_C_tt': '不简化任何东西',

    'bake'          : '最终确定材质',
    'bake_light'    : "亮色",
    'bake_light_tt' : "烘焙所有纹理的亮色版本",
    'bake_dark'     : "暗色",
    'bake_dark_tt'  : "烘焙所有纹理的暗色版本",
    'bake_norm'     : "法线",
    'bake_norm_tt'  : "烘焙所有纹理的法线版本",
    'bake_mult'     : '烘焙乘数：',
    'bake_mult_tt'  : "如果烘焙纹理模糊，请将其设置为2或3",
    'old_bake'      : '使用旧版烘焙',
    'old_bake_tt'   : '启用以使用旧的烘焙系统。该系统不会烘焙任何额外的UV贴图，如头发光泽或眼影。但如果您发现烘培的材质损坏，这可能有帮助',
    
    'shape_A'       : '使用KKBP形态键',
    'shape_A_tt'    : '重命名并删除旧的形态键。这将合并属于同一表情的形态键，并删除其余部分',
    'shape_B'       : "保存部分形态键",
    'shape_B_tt'    : "保存用于生成恋活形态键的部分形态键。这些本身是无用的",
    'shape_C'       : "跳过修改形态键",
    'shape_C_tt'    : "使用恋活形态键。这不会以任何方式改变形态键",

    'shader_A'       : '使用Eevee',
    'shader_B'       : "使用Cycles",
    'shader_C'       : "使用修改的Eevee",
    'shader_C_tt'    : "使用为Eevee修改的着色器",
    
    'atlas'         : '图集类型',

    'export_fbx'    : '导出FBX',
    'export_fbx_tt' : '将所有可见对象导出为FBX文件。这与文件-菜单中的FBX导出功能相同',

    'import_export' : '导入导出',
    'extras'        : 'KKBP 杂项功能',
    'import_model'  : '导入模型',
    'prep'          : '为目标应用程序处理',

    'studio_object'             : '导入工作室物体',
    'studio_object_tt'          : '打开包含导出自SB3Utility的.fbx的目录',
    'convert_texture'           : '转换纹理？',
    'convert_texture_tt'        : '''如果您希望插件使用游戏中的LUT对物体纹理进行饱和处理，请启用此项''',
    'single_animation'          : '导入单一动画文件',
    'single_animation_tt'       : '只适用于Rigify骨架，导入一个来自恋活的.fbx文件并应用于您的角色。来自Mixamo的.fbx文件也受支持。',
    'animation_koi'             : '导入恋活动画',
    'animation_mix'             : '导入Mixamo动画',
    'animation_type_tt'         : '禁用此开关以从恋活导入动画，启用此选项以从Mixamo导入动画',
    'animation_library'         : '创建动画库',
    'animation_library_tt'      : "只适用于Rigify骨架，使用当前文件和角色创建一个动画库。不会保存当前文件，以防您需要再次使用它。打开包含用 SB3Utility 导出的动画文件的文件夹",
    'animation_library_scale'   : '缩放手臂',
    'animation_library_scale_tt': '勾选此项可将手臂的Y轴缩放5%，这将使某些姿势更接近游戏中的样子',
    'map_library'               : '创建一个地图资源库',
    'map_library_tt'            : "使用解包的地图资源创建地图库。使用SB3Utility打开包含地图的目录。每张地图将花费40-500秒打开",

    'rigify_convert'            : "转换为Rigify",
    'rigify_convert_tt'         : "运行几个脚本，将KKBP骨架转换为兼容Rigify的骨架",
    'sep_eye'                   : "分离眼睛和眉毛",
    'sep_eye_tt'                : "将眼睛和眉毛从身体对象中分离出来，并将形态键链接到身体对象。当您想让眼睛或眉毛通过头发透视时，该功能非常有用",
    'bone_visibility'           : "更新骨骼可见性",
    'bone_visibility_tt'        : "根据隐藏的服装更新骨骼的可见性",
    'export_sep_meshes'         : "导出分离的网格",
    'export_sep_meshes_tt'      : "仅适用于 “按SMR数据分类”选项。选择导出网格的位置",

    'kkbp_import_tt'   : "导入恋活模型（.pmx格式），并对其应用修复",
    'export_prep_tt'    : "只适用于KKBP骨架，查看下拉列表以了解更多信息",
    'bake_mats_tt'      : "打开要将材质模板烘焙到的文件夹",

    'install_dependency': "安装依赖",
    'install_dependency_tt': """ 单击此按钮自动下载 Blender 2.90。导入 KKBP 模型需要该版本的 Blender。
此过程将耗时几分钟，具体取决于您的网络速度，并将从 https://download.blender.org/release/ 下载 193MB 的数据。
安装后，它将占用 504MB 的空间，并存储在 KKBP 附加组件目录中。您可以卸载 KKBP 附加组件来收回空间。
如果您想使用 Blender 3.6，请点击下方的 3.6 按钮。该版本比 Blender 2.90 大很多，但硬件兼容性可能更好。
如果您希望使用自己的Blender 2.90可执行文件而不是让插件为您下载，请打开 KKBP 插件首选项窗口并在其中输入可执行文件的绝对路径。2.90 和 3.6 之间的任何版本都可以使用""",

    'delete_cache' : '删除缓存',
    'delete_cache_tt' : '启用此选项可删除缓存文件。缓存文件在导入模型或最终确定材质时生成。这些文件被命名为 “atlas_files”、“baked_files”、“dark_files ”和 “saturated_files ”存储在pmx文件夹中。启用此选项将删除这些文件夹中的所有文件',

    'split_objects' : '分离物体',
    'split_objects_tt' : '单击此按钮可将当前选中的对象一分为二。使用 “最终确定材质 ”按钮时，插件会为模型生成图集，但如果对象的材质过多，Blender可能会因内存不足而崩溃。此按钮可将对象一分为二，从而将模型上的材质数量减半，这样在低端硬件上崩溃的可能性就会降低。',

    'use_atlas' : '创建材质图集',
    'use_atlas_tt': '禁用此功能可在最终确定材质时节省大量时间，但不会创建材质图集。',
    'dont_use_atlas' : '不创建材质图集',
    }
