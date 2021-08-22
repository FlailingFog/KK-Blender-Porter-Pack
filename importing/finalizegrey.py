#Finalize the accessory placements

import bpy
from mathutils import Vector

class finalize_grey(bpy.types.Operator):
    bl_idname = "kkb.finalizegrey"
    bl_label = "Finalize accessory placements"
    bl_description = "Finalize accessory placements"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context): 
        def runIt():
            
            bpy.ops.object.mode_set(mode='OBJECT')
            armature = bpy.data.objects['Armature']
            
            def return_child(parent):
                try:
                    new_parent = parent.children[0]
                    return return_child(new_parent)
                except:
                    return parent
                
            #go through the empties that have children
            for empty in [ob for ob in bpy.data.objects if ob.type == 'EMPTY' and len(ob.children) > 0]:
                #get the last child of the empty and check if it's a mesh (accessory object)
                if empty.parent_bone != None and empty.parent_bone != '':
                    empty_name = empty.name
                    empty_parent = bpy.data.objects[empty_name].parent_bone
                    last_child = return_child(empty)
                    if last_child.type == 'MESH':
                        
                        #unparent the mesh (accessory) and keep location
                        bpy.ops.object.select_all(action='DESELECT')
                        bpy.context.view_layer.objects.active = last_child
                        last_child.select_set(True)
                        #empty.select_set(True)
                        bone_location = empty.location
                        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
                        
                        #create a bone on the armature for this accessory
                        bpy.context.view_layer.objects.active = armature
                        bpy.ops.object.mode_set(mode='EDIT')
                        
                        height_adder = Vector((0,0.1,0))
                        
                        new_bone = armature.data.edit_bones.new(last_child.name)
                        new_bone.head = armature.data.edit_bones[empty_parent].head + bone_location
                        new_bone.tail = armature.data.edit_bones[empty_parent].head + bone_location + height_adder
                        new_bone.parent = armature.data.edit_bones[empty_parent]
                        
                        #parent the accessory to the new armature bone
                        bone = new_bone.name
                        bpy.ops.object.mode_set(mode='POSE')
                        
                        bpy.ops.pose.select_all(action='DESELECT')
                        armature.data.bones.active = armature.data.bones[bone]
                        armature.data.bones[bone].select = True
                        armature.data.bones[bone].select_head = True
                        armature.data.bones[bone].select_tail = True
                        bpy.ops.object.parent_set(type='BONE_RELATIVE')
                        bpy.ops.object.mode_set(mode='OBJECT')
                        
                        #make sure the accessory has a vertex group for the bone when it's merged
                        vertex_group = last_child.vertex_groups.new(name=bone)
                        verticesToAdd = []
                        for vertex in last_child.data.vertices:
                            verticesToAdd.append(vertex.index)
                        vertex_group.add(verticesToAdd, 1.0, 'ADD')
                        
                        #delete the empty
                        bpy.ops.object.select_all(action='DESELECT')
                        empty.select_set(True)
                        bpy.ops.object.delete(use_global=False, confirm=False)
                        
                else:
                    #delete the empty
                    bpy.ops.object.select_all(action='DESELECT')
                    empty.select_set(True)
                    bpy.ops.object.delete(use_global=False, confirm=False)
            
            #delete the rest of the empties
            bpy.ops.object.select_all(action='DESELECT')
            for empty in [ob for ob in bpy.data.objects if ob.type == 'EMPTY']:
                empty.select_set(True)
            bpy.ops.object.delete(use_global=False, confirm=False)
            
            #then merge all objects to the face object since that one seems to work
            bpy.ops.object.select_all(action='DESELECT')
            for mesh in [ob for ob in bpy.data.objects if ob.type == 'MESH']:
                mesh.select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects['cf_O_face']
            bpy.ops.object.join()
            bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
            
            
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active = armature
            #rename core bones to match unity bone names
            unity_rename_dict = {
            'cf_j_root':'Center',
            'cf_j_hips':'Hips',
            'cf_j_waist01':'Pelvis',
            'cf_j_spine01':'Spine',
            'cf_j_spine02':'Chest',
            'cf_j_spine03':'Upper Chest',
            'cf_j_neck':'Neck',
            'cf_j_head':'Head',
            'cf_j_shoulder_L':'Left shoulder',
            'cf_j_shoulder_R':'Right shoulder',
            'cf_j_arm00_L':'Left arm',
            'cf_j_arm00_R':'Right arm',
            'cf_j_forearm01_L':'Left elbow',
            'cf_j_forearm01_R':'Right elbow',
            'cf_j_hand_R':'Right wrist',
            'cf_j_hand_L':'Left wrist',

            'cf_j_thumb01_L':'Thumb0_L',
            'cf_j_thumb02_L':'Thumb1_L',
            'cf_j_thumb03_L':'Thumb2_L',
            'cf_j_ring01_L':'RingFinger1_L',
            'cf_j_ring02_L':'RingFinger2_L',
            'cf_j_ring03_L':'RingFinger3_L',
            'cf_j_middle01_L':'MiddleFinger1_L',
            'cf_j_middle02_L':'MiddleFinger2_L',
            'cf_j_middle03_L':'MiddleFinger3_L',
            'cf_j_little01_L':'LittleFinger1_L',
            'cf_j_little02_L':'LittleFinger2_L',
            'cf_j_little03_L':'LittleFinger3_L',
            'cf_j_index01_L':'IndexFinger1_L',
            'cf_j_index02_L':'IndexFinger2_L',
            'cf_j_index03_L':'IndexFinger3_L',

            'cf_j_thumb01_R':'Thumb0_R',
            'cf_j_thumb02_R':'Thumb1_R',
            'cf_j_thumb03_R':'Thumb2_R',
            'cf_j_ring01_R':'RingFinger1_R',
            'cf_j_ring02_R':'RingFinger2_R',
            'cf_j_ring03_R':'RingFinger3_R',
            'cf_j_middle01_R':'MiddleFinger1_R',
            'cf_j_middle02_R':'MiddleFinger2_R',
            'cf_j_middle03_R':'MiddleFinger3_R',
            'cf_j_little01_R':'LittleFinger1_R',
            'cf_j_little02_R':'LittleFinger2_R',
            'cf_j_little03_R':'LittleFinger3_R',
            'cf_j_index01_R':'IndexFinger1_R',
            'cf_j_index02_R':'IndexFinger2_R',
            'cf_j_index03_R':'IndexFinger3_R',

            'cf_j_thigh00_L':'Left leg',
            'cf_j_thigh00_R':'Right leg',
            'cf_j_leg01_L':'Left knee',
            'cf_j_leg01_R':'Right knee',
            'cf_j_foot_L':'Left ankle',
            'cf_j_foot_R':'Right ankle',
            'cf_j_toes_L':'Left toe',
            'cf_j_toes_R':'Right toe'
            }
            
            for bone in armature.data.bones:
                if bone.name in unity_rename_dict:
                    bone.name = unity_rename_dict[bone.name]
            
            #move armature bones that didn't have animation data up a level
            bpy.ops.object.mode_set(mode='EDIT')
            armature.data.edit_bones['Hips'].parent = armature.data.edit_bones['Center']
            #armature.data.edit_bones['cf_pv_root'].parent = armature.data.edit_bones['Center']
            armature.data.edit_bones['Center'].parent = None
            
            bpy.ops.armature.select_all(action='DESELECT')
                
            bpy.ops.object.mode_set(mode='OBJECT')


        #I need a better way to do this
        runIt()
        
        return {'FINISHED'}
    
if __name__ == "__main__":
    bpy.utils.register_class(finalize_grey)
    
    # test call
    print((bpy.ops.kkb.finalizegrey('INVOKE_DEFAULT')))