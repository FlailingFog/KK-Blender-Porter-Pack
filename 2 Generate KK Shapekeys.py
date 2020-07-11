############################################
# GENERATE KK SHAPEKEY SCRIPT
##########################################
#Translate shapekeys to english

import bpy

def tidyUp(keyName):
    if (keyName.find("eye_face.f00") != -1):
        keyName = keyName.replace("eye_face.f00", "Eyes")
        
    if (keyName.find("kuti_face.f00") != -1):
        keyName = keyName.replace("kuti_face.f00", "Lips")
        
    if (keyName.find("eye_siroL.sL00") != -1):
        keyName = keyName.replace("eye_siroL.sL00", "EyeWhitesL")
        
    if (keyName.find("eye_siroR.sR00") != -1):
        keyName = keyName.replace("eye_siroR.sR00", "EyeWhitesR")
        
    if (keyName.find("eye_line_u.elu00") != -1):
        keyName = keyName.replace("eye_line_u.elu00", "Eyelashes1")
        
    if (keyName.find("eye_line_l.ell00") != -1):
        keyName = keyName.replace("eye_line_l.ell00", "Eyelashes2")
        
    if (keyName.find("eye_naM.naM00") != -1):
        keyName = keyName.replace("eye_naM.naM00", "EyelashesPos")
    
    if (keyName.find("eye_nose.nl00") != -1):
        keyName = keyName.replace("eye_nose.nl00", "NoseTop")

    if (keyName.find("kuti_nose.nl00") != -1):
        keyName = keyName.replace("kuti_nose.nl00", "NoseBot")
        
    if (keyName.find("kuti_ha.ha00") != -1):
        keyName = keyName.replace("kuti_ha.ha00", "Teeth")
        
    if (keyName.find("kuti_yaeba.y00") != -1):
        keyName = keyName.replace("kuti_yaeba.y00", "Fangs")
        
    if (keyName.find("kuti_sita.t00") != -1):
        keyName = keyName.replace("kuti_sita.t00", "Tongue")

    if (keyName.find("mayuge.mayu00") != -1):
        keyName = keyName.replace("mayuge.mayu00", "Eyebrows")
        
    

    print(keyName)
    return keyName 


for shapekey in bpy.data.shape_keys:
    for keyblock in shapekey.key_blocks:
        #print(keyblock.name)
        keyblock.name = tidyUp(keyblock.name)


######################################################## and then...
#Combine the shapekeys with this code:
def whatCat(keyName):
    #EyeWhites are unused because the shape keys for left and right eyes both affect the left eye for some reason
    #Eyelashes1 is used because I couldn't see a difference between the other one and they overlap if both are used
    #EyelashPos is unused because Eyelashes work better and it overlaps with Eyelashes
    #eye_nal is unused because I have no idea what it does
    
    eyes = [keyName.find("Eyes"), keyName.find("NoseT"), keyName.find("Eyelashes1")]
    if not all(v == -1 for v in eyes):
        return 'Eyes'
    
    mouth = [keyName.find("NoseB"), keyName.find("Lips"), keyName.find("Tongue"), keyName.find("Teeth"), keyName.find("Fangs")]
    if not all(v==-1 for v in mouth):
        return 'Mouth'
    
    #else
    return 'None'

#setup two arrays for later
used = []
inUse = []

#These shapekeys have a common dependancy on other shapekeys
correctionList = ['Lips_u_s_op', 'Lips_u_l_op', 'Lips_e_l_op', 'Lips_o_s_op', 'Lips_o_l_op', 'Lips_neko_op', 'Lips_san_op']
resetList = ['Fangs_def_op', 'Teeth_def_op', 'Tongue_def_op', 'Teeth_bisyou_op1', 'Tongue_egao_op', 'Teeth_i_l_cl', 'Fangs_i_l_cl', 'Teeth_i_s_cl', 'Fangs_i_s_cl']
fanglessResetList = ['Teeth_def_op', 'Tongue_def_op', 'Teeth_bisyou_op1', 'Tongue_egao_op', 'Teeth_i_l_cl', 'Teeth_i_s_cl']

counter = len(bpy.data.shape_keys[0].key_blocks)

ACTIVE = .9

#print('-------------------')
for shapekey in bpy.data.shape_keys:
    for keyblock in shapekey.key_blocks:
        
        counter = counter - 1
        print(counter)
        if (counter == 0):
            break
        
        #What category is this shapekey (mouth, eyes or neither)?
        cat = whatCat(keyblock.name)
        
        #get the emotion for mouth or eyes from the shapekey name
        if not (cat.find('None') == 0):
            emotion = keyblock.name[keyblock.name.find("_"):]
            
            #assign each keyblock a category and emotion combo
            for keyblockCheck in shapekey.key_blocks:
                #does this key match my current emotion?
                if (keyblockCheck.name.find(emotion) != -1):
                    #does this key match my current category?
                    if whatCat(keyblock.name) == whatCat(keyblockCheck.name):
                        #I haven't already used this key right?
                        if (keyblockCheck.name not in used):
                            keyblockCheck.value = ACTIVE
                            inUse.append(keyblockCheck.name)
                            #print('Using ' + keyblockCheck.name)
                            
            #Manual corrections
            if (keyblock.name in correctionList):
                try:
                    shapekey.key_blocks['Fangs_def_op'].value = ACTIVE
                except:
                    #this character doesn't have fangs
                    pass
                shapekey.key_blocks['Teeth_def_op'].value = ACTIVE
                shapekey.key_blocks['Tongue_def_op'].value = ACTIVE
            
            if (keyblock.name == 'Lips_e_s_op'):
                try:
                    shapekey.key_blocks['Fangs_def_op'].value = ACTIVE
                except:
                    #this character doesn't have fangs
                    pass
            
            if (keyblock.name == 'Lips_bisyou_op'):
                shapekey.key_blocks['Teeth_bisyou_op1'].value = 0
            
            if (keyblock.name == 'Lips_tabe_op'):
                try:
                    shapekey.key_blocks['Fangs_def_op'].value = ACTIVE
                except:
                    #this character doesn't have fangs
                    pass
                shapekey.key_blocks['Teeth_def_op'].value = ACTIVE
                shapekey.key_blocks['Tongue_egao_op'].value = ACTIVE
                
            if (keyblock.name == 'Lips_i_l_op'):
                shapekey.key_blocks['Teeth_i_l_cl'].value = ACTIVE
                try:
                    shapekey.key_blocks['Fangs_def_op'].value = ACTIVE
                except:
                    #this character doesn't have fangs
                    pass
                
            if (keyblock.name == 'Lips_i_s_op'):
                shapekey.key_blocks['Teeth_i_s_cl'].value = ACTIVE
                try:
                    shapekey.key_blocks['Fangs_def_op'].value = ACTIVE
                except:
                    #this character doesn't have fangs
                    pass
                
            
            if (keyblock.name not in used):
                #print('Creating combined shapekey')
                bpy.data.objects['Model_mesh'].shape_key_add(name=('KK ' +cat+emotion))
                #print('appended this to used ' + keyblock.name)
                
            for thing in inUse:
                used.append(thing)
                
            #reset used values
            for thing in used:
                shapekey.key_blocks[thing].value=0
                
            #reset values for shapekeys that were used to correct another shapekey
            try:
                for thing in resetList:
                    shapekey.key_blocks[thing].value=0
                #print('')
            except:
                for thing in fanglessResetList:
                    shapekey.key_blocks[thing].value=0
                    
            inUse =[]
            print('end')
