##########################################
# BONE HIDE SCRIPT
##########################################
#Hide all bones except those in the wantlist

import bpy

wantlist = ['Eyes', 'cf_d_shoulder_L', 'cf_d_shoulder_R', '両目x', '両目ｘ', 'cf_d_bust01_R', 'cf_d_bust01_L','cf_d_siri_L', 'cf_d_siri_R','cf_d_ana','cf_j_spine03','全ての親', 'センター', 'グルーブ', '下半身', '足.L', 'ひざ.L', '足首.L', '足先EX.L', 'Toe_01_L', 'Toe_02_L', 'Toe_03_L', 'Toe_04_L', 'Toe_05_L', '足.R', 'ひざ.R', '足首.R', '足先EX.R', 'Toe_01_R', 'Toe_02_R', 'Toe_03_R', 'Toe_04_R', 'Toe_05_R', 'tail base', 'tail1', 'tail2', 'tail3', 'tail4', 'tail5', 'tail6', 'tail7', '上半身', '上半身2', '首', '頭', 'bow left', '両目', 'RightEarBase', '耳.R', 'LeftEarBase', '耳.L', '目.R', '目.L', '舌1', '舌2', '眉.L', '眉.R', '前髪＿1＿1', '髪＿1＿1.L', '髪＿1＿1.R', '後髪＿1＿1', '後髪＿1＿1.L', '後髪＿1＿1.R', '肩.R', '腕.R', '腕捩.R', 'ひじ.R', '手捩.R', '手首.R', '親指０.R', '親指１.R', '親指２.R', '人指１.R', '人指２.R', '人指３.R', '中指１.R', '中指２.R', '中指３.R', '薬指１.R', '薬指２.R', '薬指３.R', '小指１.R', '小指２.R', '小指３.R', 'の指.R', '肩.L', '腕.L', '腕捩.L', 'ひじ.L', '手捩.L', '手首.L', '親指０.L', '親指１.L', '親指２.L', '人指１.L', '人指２.L', '人指３.L', '中指１.L', '中指２.L', '中指３.L', '薬指１.L', '薬指２.L', '薬指３.L', '小指１.L', '小指２.L', '小指３.L', 'の指.L', 'Butterfly_L', 'Butterfly_R', 'ネクタイ1', 'ネクタイ2', 'ネクタイ3', 'ネクタイ4', '足ＩＫ.L', 'つま先ＩＫ.L', '足ＩＫ.R', 'つま先ＩＫ.R', 'cf_s_wrist_R', 'cf_d_wrist_R', 'cf_s_forearm02_R', 'cf_d_forearm02_R', 'cf_s_wrist_L', 'cf_d_wrist_L', 'cf_s_forearm02_L', 'cf_d_forearm02_L']

counter = 0

for armature in [ob for ob in bpy.data.objects if ob.type == 'ARMATURE']:
    for bone in armature.data.bones:
        bone.hide=True
        if bone.name in wantlist:
            print(bone.name)
            bone.hide = False
            counter=counter+1
