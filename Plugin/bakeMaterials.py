'''
BAKE MATERIAL TO TEXTURE SCRIPT
- Bakes all materials of an object into image textures (to use in other programs)
- Will only bake a material if an image node is present in the node tree
- If multiple image files are present, only one texture will be created
- If the multiple image files have different resolutions, a texture will be created for each resolution
- Export defaults to 8-bit PNG with an alpha channel.
--    Defaults can be changed by editing the exportType and exportColormode variables below this comment.

Usage:
- Enter the folder you want to export the textures to in the Output Properties tab
- Select the object you want to bake in the 3D viewport
- Run the script
- Textures are baked to the output folder

Notes:
- This script deletes all camera and light objects in the scene
- This script sets the world color in the World tab to black

Limitations:
- Does not (cannot?) account for multiple UV maps. Only the default map named "UVMap" is used.

imageplane driver + shader code taken from https://blenderartists.org/t/scripts-create-camera-image-plane/580839
Tested on Blender 2.91 and 2.83 LTS
'''

import bpy
import os
from pathlib import Path

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

class bake_Materials(bpy.types.Operator):
    bl_idname = "kkb.bakematerials"
    bl_label = "Store baked materials here"
    bl_description = "Open the folder you want to bake the material templates to"
    bl_options = {'REGISTER', 'UNDO'}
    
    directory : StringProperty(maxlen=1024, default='', subtype='FILE_PATH', options={'HIDDEN'})
    filter_glob : StringProperty(default='', options={'HIDDEN'})
    data = None
    mats_uv = None
    structure = None
    
    def execute(self, context):
        def runIt():
            scene = context.scene.placeholder
            exportType = 'PNG'
            exportColormode = 'RGBA'
            resolutionMultiplier = scene.inc_dec_int
            
            print(self.directory)
            #Stop if no object is selected
            def showError(self, context):
                self.layout.label(text="No object selected")

            try:
                #An object was set as the active object but is not selected
                if not bpy.context.active_object.select_get():
                    bpy.context.window_manager.popup_menu(showError, title="Error", icon='ERROR')
                    return
            except:
                #No object is set as the active object
                bpy.context.window_manager.popup_menu(showError, title="Error", icon='ERROR')
                return

            #######################
            #Select all camera and light objects

            currentlySelected = bpy.context.active_object

            for lightcam in bpy.context.scene.objects:
                if lightcam.type == 'CAMERA' or lightcam.type == 'LIGHT':
                    lightcam.select_set(True)
                else:
                    lightcam.select_set(False)

            #Then delete them
            bpy.ops.object.delete()

            #and set the world color to black 
            bpy.data.worlds[0].node_tree.nodes['Background'].inputs[0].default_value = (0,0,0,1)
            
            #reset currently selected object
            bpy.context.view_layer.objects.active = currentlySelected
            currentlySelected.select_set(True)

            #########################
            #Create a camera and an image plane that will fit to the camera's dimensions using drivers

            def SetupDriverVariables(driver, imageplane, camera):
                cam_ortho_scale = driver.variables.new()
                cam_ortho_scale.name = 'cOS'
                cam_ortho_scale.type = 'SINGLE_PROP'
                cam_ortho_scale.targets[0].id_type = 'CAMERA'
                cam_ortho_scale.targets[0].id = bpy.data.cameras[camera.name]
                cam_ortho_scale.targets[0].data_path = 'ortho_scale'
                resolution_x = driver.variables.new()
                resolution_x.name = 'r_x'
                resolution_x.type = 'SINGLE_PROP'
                resolution_x.targets[0].id_type = 'SCENE'
                resolution_x.targets[0].id = bpy.context.scene
                resolution_x.targets[0].data_path = 'render.resolution_x'
                resolution_y = driver.variables.new()
                resolution_y.name = 'r_y'
                resolution_y.type = 'SINGLE_PROP'
                resolution_y.targets[0].id_type = 'SCENE'
                resolution_y.targets[0].id = bpy.context.scene
                resolution_y.targets[0].data_path = 'render.resolution_y'

            #Purge unused cameras and lights from orphan data
            for block in bpy.data.cameras:
                if block.users == 0:
                    bpy.data.cameras.remove(block)
            for block in bpy.data.lights:
                if block.users == 0:
                    bpy.data.lights.remove(block)

            #save the currently selected object
            currentlySelected = bpy.context.active_object

            #Add a new camera
            try:
                #Blender 2.91
                bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, -1), rotation=(0, 0, 0), scale=(1, 1, 1))
            except:
                #Blender 2.83
                bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, -1), rotation=(0, 0, 0))

            #save it for later
            camera = bpy.context.active_object

            #and set it as the active one
            bpy.context.scene.camera=camera

            #create imageplane
            bpy.ops.mesh.primitive_plane_add()#radius = 0.5)
            imageplane = bpy.context.active_object
            imageplane.name = "imageplane"
            imageplane.lock_location[0] = True
            imageplane.lock_location[1] = True
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.transform.resize( value=(1.0,1.0,1.0))
            bpy.ops.uv.smart_project(angle_limit=66,island_margin=0)
            bpy.ops.uv.select_all(action='TOGGLE')
            bpy.ops.transform.rotate(value=1.5708, orient_axis='Z')
            bpy.ops.object.editmode_toggle()

            imageplane.location = (0,0,-3)
            imageplane.parent = camera

            #Set camera to orthographic
            bpy.data.cameras[camera.name].type='ORTHO'
            bpy.data.cameras[camera.name].ortho_scale=3
            bpy.context.scene.render.pixel_aspect_y=1
            bpy.context.scene.render.pixel_aspect_x=1

            #setup drivers for plane's Y scale
            driver = imageplane.driver_add('scale',1).driver
            driver.type = 'SCRIPTED'
            SetupDriverVariables(driver, imageplane, camera)
            driver.expression = "((r_y)/(r_x)*(cOS/2)) if (((r_y)/(r_x)) < 1) else (cOS/2)"

            #setup X scale
            driver = imageplane.driver_add('scale',0).driver
            driver.type = 'SCRIPTED'
            SetupDriverVariables(driver, imageplane, camera)
            driver.expression = "((r_x)/(r_y)*(cOS/2)) if (((r_x)/(r_y)) < 1) else (cOS/2)"

            ###########################
            #setup the material for the image plane

            imageplane = bpy.context.active_object
            if( len( imageplane.material_slots) == 0 ):
                bpy.ops.object.material_slot_add()

            imagemat = bpy.data.materials.new(name='dummyMat')
            imageplane.material_slots[0].material = bpy.data.materials['dummyMat']
            planematerial =  imageplane.material_slots[0].material
            planematerial.use_nodes = True

            #enable alpha on the output
            bpy.context.scene.render.film_transparent = True

            #Make the originally selected object active again
            bpy.ops.object.select_all(action='DESELECT')
            currentlySelected.select_set(True)
            bpy.context.view_layer.objects.active=currentlySelected

            ##############################
            #Changes the material of the image plane to the material of the object,
            # and then puts a render of the image plane into the specified folder

            def sanitizeMaterialName(text):
                for ch in ['\\','`','*','<','>','.',':','?','|','/','\"']:
                    if ch in text:
                        text = text.replace(ch,'')
                return text
            
            def bakeMaterials(sunstate, sunstrength):
                #get the most recently created light object
                sun = bpy.data.lights[len(bpy.data.lights)-1]

                #make sure shadows are turned off
                sun.use_shadow = False
                
                #set the sun strength
                sun.energy = sunstrength
                #print('the sun is ' + str(sunstate) + ' at ' + str(sunstrength))
                
                #prepare a blank array to use for detecting duplicate image dimensions
                dupedetect = []

                #preserve the filepath
                folderpath =  self.directory
                
                #go through each material slot
                for matslot in objectToBake.material_slots:
                    currentmaterial = matslot.material
                    #print(currentmaterial)
                    renderedSomething = False
                    
                    #Turn off the normals for the raw shading node group input
                    for matnode in matslot.material.node_tree.nodes:
                        try:
                            if 'Raw Shading' in matnode.node_tree.name:
                                shadingset = matnode.inputs[1].default_value
                                matnode.inputs[1].default_value=1
                        except:
                            #this slot doesn't have a node tree
                            pass
                    
                    for matnode in matslot.material.node_tree.nodes:
                        #print(matnode)
                        #print('each node in this node group')
                        try:
                            for matnodeingroup in matnode.node_tree.nodes:
                                print(matnodeingroup)
                                if matnodeingroup.type == 'TEX_IMAGE':
                                    try:
                                        currentImageX = matnodeingroup.image.size[0]
                                        currentImageY = matnodeingroup.image.size[1]
                                        dimension = str(currentImageX)+'x'+str(currentImageY)
                                        
                                        #check if a render has been done at these dimensions for this material
                                        if dimension not in dupedetect:
                                            #if it hasn't, render this one
                                            bpy.context.scene.render.resolution_x=currentImageX * resolutionMultiplier
                                            bpy.context.scene.render.resolution_y=currentImageY * resolutionMultiplier
                                            dupedetect.append(dimension)
                                            #print('rendering a ' + dimension + ' sized file')
                                            
                                            #set the material
                                            bpy.data.objects['imageplane'].data.materials[0] = currentmaterial
                                            
                                            #then render it
                                            bpy.context.scene.render.filepath = folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + dimension + ' ' + sunstate
                                            bpy.context.scene.render.image_settings.file_format=exportType
                                            bpy.context.scene.render.image_settings.color_mode=exportColormode
                                            #bpy.context.scene.render.image_settings.color_depth='16'
                                            
                                            print('rendering this file:' + bpy.context.scene.render.filepath)
                                            bpy.ops.render.render(write_still = True)
                                            #print(imageplane.data.materials[0])
                                            
                                            #reset folderpath after render
                                            bpy.context.scene.render.filepath = folderpath
                                            
                                            renderedSomething = True
                                            
                                        else:
                                            print('already did this dimension for this material: ' + dimension + ' || ' + currentmaterial)
                                    except:
                                        #An image node was present but there was no image loaded
                                        pass
                        except:
                            #this node doesn't have a node tree
                            pass
                    
                    #if nothing was rendered at all for this material, render a very small (64px) failsafe image
                    #this will let the script catch fully transparent materials or materials that are solid colors
                    if not renderedSomething:
                        bpy.context.scene.render.resolution_x=64
                        bpy.context.scene.render.resolution_y=64
                        
                        #set the material
                        bpy.data.objects['imageplane'].data.materials[0] = currentmaterial
                        
                        #then render it
                        bpy.context.scene.render.filepath = folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + '64x64' + ' ' + sunstate
                        bpy.context.scene.render.image_settings.file_format=exportType
                        bpy.context.scene.render.image_settings.color_mode=exportColormode
                        #bpy.context.scene.render.image_settings.color_depth='16'
                        
                        print('rendering this file:' + bpy.context.scene.render.filepath)
                        bpy.ops.render.render(write_still = True)
                        #print(imageplane.data.materials[0])
                        
                        #reset folderpath after render
                        bpy.context.scene.render.filepath = folderpath
                    
                    #reset dupedetect array for the next material
                    dupedetect = []
                    
                    #Restore the value in the raw shading node group for the normals
                    for matnode in matslot.material.node_tree.nodes:
                        try:
                            if 'Raw Shading' in matnode.node_tree.name:
                                matnode.inputs[1].default_value=shadingset
                        except:
                            #this node doesn't have a node tree
                            pass

            ###############
            #Begin baking

            #get the currently selected object as the active object
            objectToBake = bpy.context.active_object

            #Purge unused lights
            for block in bpy.data.lights:
                if block.users == 0:
                    bpy.data.lights.remove(block)

            #Make a new sun object
            try:
                #Blender 2.91
                bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
            except:
                #Blender 2.83
                bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=(0, 0, 0))

            #save the sun object
            sunobject = bpy.context.active_object

            #bakes the light versions of each material to the selected folder at sun intensity 5
            bakeMaterials('light' , 5)
            #bakes the dark versions of each material at sun intensity 0
            bakeMaterials('dark' , 0)

            ####################
            #Cleanup

            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            #Select the sun
            sunobject.select_set(True)
            #Select the imageplane
            bpy.data.objects['imageplane'].select_set(True)
            #Select the camera
            camera.select_set(True)
            #delete them
            bpy.ops.object.delete()

            #disable alpha on the output
            bpy.context.scene.render.film_transparent = False

        #the ultimate lazy move
        runIt()
                 
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

if __name__ == "__main__":
    bpy.utils.register_class(bake_Materials)

    # test call
    print((bpy.ops.kkb.bakematerials('INVOKE_DEFAULT')))
