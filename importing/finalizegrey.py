#Finalize the accessory placements

import bpy, math
from mathutils import Vector

def finalize():
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
    bpy.context.view_layer.objects.active.name = 'Body'
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    
    #modify armature to match KK armature
    armature = bpy.data.objects['Armature']
    armature.select_set(True)
    bpy.context.view_layer.objects.active=armature
    bpy.ops.object.mode_set(mode='EDIT')

    #reparent these to match the KK armature
    armature.data.edit_bones['p_cf_body_bone'].parent = None
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1) #???
    armature.data.edit_bones.remove(armature.data.edit_bones['BodyTop'])
    armature.data.edit_bones['cf_j_foot_R'].parent = armature.data.edit_bones['cf_j_leg03_R']
    armature.data.edit_bones['cf_j_foot_L'].parent = armature.data.edit_bones['cf_j_leg03_L']

    #remove the cf_hit_head bone because the bone location isn't needed anymore
    armature.data.edit_bones.remove(armature.data.edit_bones['cf_hit_head'])

    #give the new eye bones the correct parents
    armature.data.edit_bones['Eyesx'].parent = armature.data.edit_bones['cf_j_head']
    armature.data.edit_bones['N_EyesLookTargetP'].parent = armature.data.edit_bones['cf_j_head']

    #unlock the armature and all bones
    armature.lock_location = [False, False, False]
    armature.lock_rotation = [False, False, False]
    armature.lock_scale = [False, False, False]
    
    for bone in armature.pose.bones:
        bone.lock_location = [False, False, False]

def modify_fbx_armature():
    armature = bpy.data.objects['Armature']
    armature.select_set(True)
    bpy.context.view_layer.objects.active=armature
    
    #move armature bones that didn't have animation data up a level
    bpy.ops.object.mode_set(mode='EDIT')
    armature.data.edit_bones['cf_n_height'].parent = None
    armature.data.edit_bones['cf_j_root'].parent = armature.data.edit_bones['cf_n_height']
    armature.data.edit_bones['cf_pv_root'].parent = armature.data.edit_bones['cf_n_height']
    
    #store unused bones under the pv_root bone
    armature.data.edit_bones['cf_j_root'].parent = armature.data.edit_bones['cf_pv_root']
    armature.data.edit_bones['p_cf_body_bone'].parent = armature.data.edit_bones['cf_pv_root']
    
    #relocate the tail of some bones to make IKs easier
    #this is different from the one in finalizepmx.py
    def relocate_tail(bone1, bone2, direction):
        if direction == 'leg':
            armature.data.edit_bones[bone1].tail.y = armature.data.edit_bones[bone2].head.y
            #move the bone forward a bit or the ik bones won't bend correctly
            armature.data.edit_bones[bone1].head.z += 0.002
            #armature.data.edit_bones[bone1].tail.z += -0.002
            armature.data.edit_bones[bone1].roll = 0
        elif direction == 'arm':
            armature.data.edit_bones[bone1].tail.x = armature.data.edit_bones[bone2].head.x
            armature.data.edit_bones[bone1].tail.y = armature.data.edit_bones[bone2].head.y
            #move the bone back a bit or the ik bones won't bend correctly
            armature.data.edit_bones[bone1].head.z += -0.002
            armature.data.edit_bones[bone1].roll = -math.pi/2
        elif direction == 'hand':
            armature.data.edit_bones[bone1].tail = armature.data.edit_bones[bone2].tail
            armature.data.edit_bones[bone1].tail.y += .01
            armature.data.edit_bones[bone1].head = armature.data.edit_bones[bone2].head
        else:
            armature.data.edit_bones[bone1].tail.z = armature.data.edit_bones[bone2].head.z
            armature.data.edit_bones[bone1].tail.y = armature.data.edit_bones[bone2].head.y
            armature.data.edit_bones[bone1].roll = 0
    
    relocate_tail('cf_j_leg01_R', 'cf_j_foot_R', 'leg')
    relocate_tail('cf_j_leg01_R', 'cf_j_toes_R', 'foot')
    relocate_tail('cf_j_forearm01_R', 'cf_j_hand_R', 'arm')
    relocate_tail('cf_pv_hand_R', 'cf_j_hand_R', 'hand')

    relocate_tail('cf_j_leg01_L', 'cf_j_foot_L', 'leg')
    relocate_tail('cf_j_leg01_L', 'cf_j_toes_L', 'foot')
    relocate_tail('cf_j_forearm01_L', 'cf_j_hand_L', 'arm')
    relocate_tail('cf_pv_hand_L', 'cf_j_hand_L', 'hand')
    
    bpy.ops.object.mode_set(mode='OBJECT')

class finalize_grey(bpy.types.Operator):
    bl_idname = "kkb.finalizegrey"
    bl_label = "Finalize .fbx file"
    bl_description = "Finalize accessory placements and .fbx file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context): 
        
        scene = context.scene.kkbp
        modify_armature = scene.armature_edit_bool

        finalize()
        if modify_armature:
            modify_fbx_armature()
        
        #redraw the UI after each operation to let the user know the plugin is actually doing something
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.kkb.shapekeys('INVOKE_DEFAULT')

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.kkb.separatebody('INVOKE_DEFAULT')

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.kkb.cleanarmature('INVOKE_DEFAULT')

        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        bpy.ops.kkb.bonedrivers('INVOKE_DEFAULT')
        
        #Set the view transform 
        bpy.context.scene.view_settings.view_transform = 'Standard'
        
        return {'FINISHED'}
        
if __name__ == "__main__":
    bpy.utils.register_class(finalize_grey)
    
    # test call
    print((bpy.ops.kkb.finalizegrey('INVOKE_DEFAULT')))