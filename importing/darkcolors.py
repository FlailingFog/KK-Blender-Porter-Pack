#multiplying things per element according to https://github.com/Unity-Technologies/Unity.Mathematics/blob/master/src/Unity.Mathematics/float4.gen.cs#L330
#returning things like float.XZW as [Xposition = X, Yposition = Z, Zposition = W] according to https://github.com/Unity-Technologies/Unity.Mathematics/blob/master/src/Unity.Mathematics/float4.gen.cs#L3056
#using the variable order x, y, z, w according to https://github.com/Unity-Technologies/Unity.Mathematics/blob/master/src/Unity.Mathematics/float4.gen.cs#L42

import math, numpy, bpy, time, os
from .importbuttons import kklog

#class to mimic part of float4 class in Unity
class float4:
    def __init__(self, x = None, y = None, z = None, w = None):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
    def __mul__ (self, vector):
        #if a float4, multiply piece by piece, else multiply full vector
        if type(vector) in [float, int]:
            vector = float4(vector, vector, vector, vector)
        x = self.x * vector.x if self.get('x') != None else None
        y = self.y * vector.y if self.get('y') != None else None
        z = self.z * vector.z if self.get('z') != None else None
        w = self.w * vector.w if self.get('w') != None else None
        return float4(x,y,z,w)
    __rmul__ = __mul__
    def __add__ (self, vector):
        #if a float4, add piece by piece, else add full vector
        if type(vector) in [float, int]:
            vector = float4(vector, vector, vector, vector)
        x = self.x + vector.x if self.get('x') != None else None
        y = self.y + vector.y if self.get('y') != None else None
        z = self.z + vector.z if self.get('z') != None else None
        w = self.w + vector.w if self.get('w') != None else None
        return float4(x,y,z,w)
    __radd__ = __add__
    def __sub__ (self, vector):
        #if a float4, subtract piece by piece, else subtract full vector
        if type(vector) in [float, int]:
            vector = float4(vector, vector, vector, vector)
        x = self.x - vector.x if self.get('x') != None else None
        y = self.y - vector.y if self.get('y') != None else None
        z = self.z - vector.z if self.get('z') != None else None
        w = self.w - vector.w if self.get('w') != None else None
        return float4(x,y,z,w)
    __rsub__ = __sub__
    def __gt__ (self, vector):
        #if a float4, compare piece by piece, else compare full vector
        if type(vector) in [float, int]:
            vector = float4(vector, vector, vector, vector)
        x = self.x > vector.x if self.get('x') != None else None
        y = self.y > vector.y if self.get('y') != None else None
        z = self.z > vector.z if self.get('z') != None else None
        w = self.w > vector.w if self.get('w') != None else None
        return float4(x,y,z,w)
    def __neg__ (self):
        x = -self.x if self.get('x') != None else None
        y = -self.y if self.get('y') != None else None
        z = -self.z if self.get('z') != None else None
        w = -self.w if self.get('w') != None else None
        return float4(x,y,z,w)
    def frac(self):
        x = self.x - math.floor (self.x) if self.get('x') != None else None
        y = self.y - math.floor (self.y) if self.get('y') != None else None
        z = self.z - math.floor (self.z) if self.get('z') != None else None
        w = self.w - math.floor (self.w) if self.get('w') != None else None
        return float4(x,y,z,w)
    def abs(self):
        x = abs(self.x) if self.get('x') != None else None
        y = abs(self.y) if self.get('y') != None else None
        z = abs(self.z) if self.get('z') != None else None
        w = abs(self.w) if self.get('w') != None else None
        return float4(x,y,z,w)
    def clamp(self):
        x = (0 if self.x < 0 else 1 if self.x > 1 else self.x) if self.get('x') != None else None
        y = (0 if self.y < 0 else 1 if self.y > 1 else self.y) if self.get('y') != None else None
        z = (0 if self.z < 0 else 1 if self.z > 1 else self.z) if self.get('z') != None else None
        w = (0 if self.w < 0 else 1 if self.w > 1 else self.w) if self.get('w') != None else None
        return float4(x,y,z,w)
    saturate = clamp
    def clamphalf(self):
        x = (0 if self.x < 0 else .5 if self.x > .5 else self.x) if self.get('x') != None else None
        y = (0 if self.y < 0 else .5 if self.y > .5 else self.y) if self.get('y') != None else None
        z = (0 if self.z < 0 else .5 if self.z > .5 else self.z) if self.get('z') != None else None
        w = (0 if self.w < 0 else .5 if self.w > .5 else self.w) if self.get('w') != None else None
        return float4(x,y,z,w)
    def get(self, var):
        if hasattr(self, var):
            return getattr(self, var)
        else:
            return None
    def __str__(self):
        return str([self.x, self.y, self.z, self.w])
    __repr__ = __str__

#something is wrong with this one
def hair_dark_color(color, shadow_color):
    diffuse = float4(color[0], color[1], color[2], 1)
    _ShadowColor = float4(shadow_color[0], shadow_color[1], shadow_color[2], 1)

    finalAmbientShadow = 0.7225; #constant
    invertFinalAmbientShadow = finalAmbientShadow #this shouldn't be equal to this but it works so whatever

    finalAmbientShadow = finalAmbientShadow * _ShadowColor
    finalAmbientShadow += finalAmbientShadow;
    shadowCol = _ShadowColor - 0.5;
    shadowCol = -shadowCol * 2 + 1;

    invertFinalAmbientShadow = -shadowCol * invertFinalAmbientShadow + 1;
    shadeCheck = 0.5 < _ShadowColor;
    hlslcc_movcTemp = finalAmbientShadow;
    hlslcc_movcTemp.x = invertFinalAmbientShadow.x if (shadeCheck.x) else finalAmbientShadow.x; 
    hlslcc_movcTemp.y = invertFinalAmbientShadow.y if (shadeCheck.y) else finalAmbientShadow.y; 
    hlslcc_movcTemp.z = invertFinalAmbientShadow.z if (shadeCheck.z) else finalAmbientShadow.z; 
    finalAmbientShadow = (hlslcc_movcTemp).saturate();
    diffuse *= finalAmbientShadow;

    finalDiffuse  = diffuse.saturate();

    shading = 1 - finalAmbientShadow;
    shading = 1 * shading + finalAmbientShadow;
    finalDiffuse *= shading;
    shading = 1.0656;
    finalDiffuse *= shading;

    return [finalDiffuse.x, finalDiffuse.y, finalDiffuse.z];

#mapvaluesmain function is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Skin/KKPDiffuse.cginc
def MapValuesMain(color):
    t0 = color;
    tb30 = t0.y>=t0.z;
    t30 = 1 if tb30 else float(0.0);
    t1 = float4(t0.z, t0.y, t0.z, t0.w);
    t2 = float4(t0.y - t1.x,  t0.z - t1.y); 
    t1.z = float(-1.0);
    t1.w = float(0.666666687);
    t2.z = float(1.0);
    t2.w = float(-1.0);
    t1 = float4(t30, t30, t30, t30) * float4(t2.x, t2.y, t2.w, t2.z) + float4(t1.x, t1.y, t1.w, t1.z);
    tb30 = t0.x>=t1.x;
    t30 = 1 if tb30 else 0.0;
    t2.z = t1.w;
    t1.w = t0.x;
    t2 = float4(t1.w, t1.y, t2.z, t1.x)
    t2 = (-t1) + t2;
    t1 = float4(t30, t30, t30, t30) * t2 + t1;
    t30 = min(t1.y, t1.w);
    t30 = (-t30) + t1.x;
    t2.x = t30 * 6.0 + 1.00000001e-10;
    t11 = (-t1.y) + t1.w;
    t11 = t11 / t2.x;
    t11 = t11 + t1.z;
    t1.x = t1.x + 1.00000001e-10;
    t30 = t30 / t1.x;
    t30 = t30 * 0.660000026;
    #w component isn't used anymore so ignore
    t2 = float4(t11, t11, t11).abs() + float4(-0.0799999982, -0.413333356, 0.25333333)
    t2 = t2.frac()
    t2 = (-t2) * float4(2.0, 2.0, 2.0) + float4(1.0, 1.0, 1.0);
    t2 = t2.abs() * float4(3.0, 3.0, 3.0) + float4(-1.0, -1.0, -1.0);
    t2 = t2.clamp()
    t2 = t2 + float4(-1.0, -1.0, -1.0);
    t2 = float4(t30, t30, t30) * t2 + float4(1.0, 1.0, 1.0);
    return float4(t2.x, t2.y, t2.z, 1);

#skin is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Skin/KKPSkinFrag.cginc 
def skin_dark_color(color, shadow_color = None):
    diffuse = float4(color[0], color[1], color[2], 1)
    shadingAdjustment = MapValuesMain(diffuse);

    diffuseShaded = shadingAdjustment * 0.899999976 - 0.5;
    diffuseShaded = -diffuseShaded * 2 + 1;
    
    compTest = 0.555555582 < shadingAdjustment;
    shadingAdjustment *= 1.79999995;
    diffuseShaded = -diffuseShaded * 0.7225 + 1;
    hlslcc_movcTemp = shadingAdjustment;
    hlslcc_movcTemp.x = diffuseShaded.x if (compTest.x) else shadingAdjustment.x; #370
    hlslcc_movcTemp.y = diffuseShaded.y if (compTest.y) else shadingAdjustment.y; #371
    hlslcc_movcTemp.z = diffuseShaded.z if (compTest.z) else shadingAdjustment.z; #372
    shadingAdjustment = (hlslcc_movcTemp).saturate(); #374 the lerp result (and shadowCol) is going to be this because shadowColor's alpha is always 1 making shadowCol 1

    #print(diffuse)
    #print(shadingAdjustment)
    finalDiffuse = diffuse * shadingAdjustment;
    
    bodyShine = float4(1.0656, 1.0656, 1.0656, 1);
    finalDiffuse *= bodyShine;
    fudge_factor = float4(0.02, 0.05, 0, 0) #result is slightly off but it looks consistently off so add a fudge factor
    finalDiffuse += fudge_factor

    return [finalDiffuse.x, finalDiffuse.y, finalDiffuse.z]

#shadeadjust function is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Item/KKPItemDiffuse.cginc
#lines without comments at the end have been copied verbatim from the C# source
def ShadeAdjustItem(col, _ShadowColor):
    #start at line 63
    t0 = col
    t1 = float4(t0.y, t0.z, None, t0.x) * float4(_ShadowColor.y, _ShadowColor.z, None, _ShadowColor.x) #line 65
    t2 = float4(t1.y, t1.x) #66
    t3 = float4(t0.y, t0.z) * float4(_ShadowColor.y, _ShadowColor.z) + (-float4(t2.x, t2.y)); #67
    tb30 = t2.y >= t1.y;
    t30 = 1 if tb30 else 0;
    t2 = float4(t2.x, t2.y, -1.0, 0.666666687); #70-71
    t3 = float4(t3.x, t3.y, 1.0, -1); #72-73
    t2 = (t30) * t3 + t2;
    tb30 = t1.w >= t2.x; 
    t30 = 1 if tb30 else float(0.0);
    t1 = float4(t2.x, t2.y, t2.w, t1.w) #77
    t2 = float4(t1.w, t1.y, t2.z, t1.x) #78
    t2 = (-t1) + t2;
    t1 = (t30) * t2 + t1;
    t30 = min(t1.y, t1.w);
    t30 = (-t30) + t1.x;
    t2.x = t30 * 6.0 + 1.00000001e-10;
    t11 = (-t1.y) + t1.w;
    t11 = t11 / t2.x;
    t11 = t11 + t1.z;
    t1.x = t1.x + 1.00000001e-10;
    t30 = t30 / t1.x;
    t30 = t30 * 0.5;
    #the w component of t1 is no longer used, so ignore it
    t1 = abs((t11)) + float4(0.0, -0.333333343, 0.333333343, 1); #90
    t1 = t1.frac(); #91
    t1 = -t1 * 2 + 1; #92
    t1 = t1.abs() * 3 + (-1) #93
    t1 = t1.clamp() #94
    t1 = t1 + (-1); #95
    t1 = (t30) * t1 + 1; #96
    #print([t1.x, t1.y, t1.z, 1])
    return float4(t1.x, t1.y, t1.z, 1) #97

#clothes is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Item/MainItemPlus.shader
#This was stripped down to just the shadow portion, and to remove all constants
def clothes_dark_color(color, shadow_color):
    ################### variable setup
    _ambientshadowG = float4(0.15, 0.15, 0.15, 0.15) #constant from experimentation
    diffuse = float4(color[0],color[1],color[2],1) #maintex color
    _ShadowColor = float4(shadow_color[0],shadow_color[1],shadow_color[2],1) #the shadow color from material editor
    ##########################
    
    #start at line 344 because the other one is for outlines
    shadingAdjustment = ShadeAdjustItem(diffuse, _ShadowColor)

    #skip to line 352
    diffuseShaded = shadingAdjustment * 0.899999976 - 0.5;
    diffuseShaded = -diffuseShaded * 2 + 1;

    compTest = 0.555555582 < shadingAdjustment;
    shadingAdjustment *= 1.79999995;
    diffuseShaded = -diffuseShaded * 0.7225 + 1; #invertfinalambient shadow is a constant 0.7225, so don't calc it

    hlslcc_movcTemp = shadingAdjustment;
    hlslcc_movcTemp.x = diffuseShaded.x if (compTest.x) else shadingAdjustment.x; #370
    hlslcc_movcTemp.y = diffuseShaded.y if (compTest.y) else shadingAdjustment.y; #371
    hlslcc_movcTemp.z = diffuseShaded.z if (compTest.z) else shadingAdjustment.z; #372
    shadingAdjustment = (hlslcc_movcTemp).saturate(); #374 the lerp result (and shadowCol) is going to be this because shadowColor's alpha is always 1 making shadowCol 1

    diffuseShadow = diffuse * shadingAdjustment;

    # lightCol is constant 1.0656, 1.0656, 1.0656, 1 calculated from the custom ambient of 0.666, 0.666, 0.666, 1 and sun light color 0.666, 0.666, 0.666, 1,
    # so ambientCol always results in lightCol after the max function
    ambientCol = float4(1.0656, 1.0656, 1.0656, 1);
    diffuseShadow = diffuseShadow * ambientCol;
    
    return [diffuseShadow.x, diffuseShadow.y, diffuseShadow.z]

#accepts a bpy image and creates a dark alternate using a modified version of the darkening code above. Returns a new bpy image
def create_darktex(maintex, shadow_color):
    if not os.path.isfile(bpy.context.scene.kkbp.import_dir + '/dark_files/' + maintex.name[:-6] + 'DT.png'):
        ok = time.time()
        #kklog('1')
        image_array = numpy.asarray(maintex.pixels)
        image_length = len(image_array)
        image_row_length = int(image_length/4)
        image_array = image_array.reshape((image_row_length, 4))

        ################### variable setup
        _ambientshadowG = numpy.asarray([0.15, 0.15, 0.15, .15]) #constant from experimentation
        diffuse = image_array #maintex color
        _ShadowColor = numpy.asarray([shadow_color[0],shadow_color[1],shadow_color[2], 1]) #the shadow color from material editor
        ##########################
        
        #start at line 344 because the other one is for outlines
        #shadingAdjustment = ShadeAdjustItemNumpy(diffuse, _ShadowColor)
        #start at line 63
        x=0;y=1;z=2;w=3;
        t0 = diffuse
        t1 = t0[:, [y, z, z, x]] * _ShadowColor[[y,z,z,x]]
        t2 = t1[:, [y,x]]
        t3 = t0[:, [y,z]] * _ShadowColor[[y,z]] + (-t2)
        tb30 = t2[:, [y]] >= t1[:, [y]]
        t30 = tb30.astype(int)
        t2 = numpy.hstack((t2[:, [x,y]], numpy.full((t2.shape[0], 1), -1, t2.dtype), numpy.full((t2.shape[0], 1), 0.666666687, t2.dtype))) 
        t3 = numpy.hstack((t3[:, [x,y]], numpy.full((t3.shape[0], 1),  1, t3.dtype), numpy.full((t3.shape[0], 1), -1,          t3.dtype))) 
        t2 = t30 * t3 + t2
        tb30 = t1[:, [w]] >= t1[:, [x]]
        t30 = tb30.astype(int)
        t1 = numpy.hstack((t2[:, [x, y, w]], t1[:, [w]]))
        t2 = numpy.hstack((t1[:, [w, y]], t2[:, [z]], t1[:, [x]]))
        t2 = -t1 + t2
        t1 = t30 * t2 + t1
        t30 = numpy.minimum(t1[:, [y]], t1[:, [w]])
        t30 = -t30 + t1[:, [x]]
        t2[:, [x]] = t30 * 6 + 1.00000001e-10
        t11 = -t1[:, [y]] + t1[:, [w]]
        t11 = t11 / t2[:, [x]];
        t11 = t11 + t1[:, [z]];
        t1[:, [x]] = t1[:, [x]] + 1.00000001e-10;
        t30 = t30 / t1[:, [x]];
        t30 = t30 * 0.5;
        #the w component of t1 is no longer used, so ignore it
        t1 = numpy.absolute(t11) + numpy.asarray([0.0, -0.333333343, 0.333333343, 1]); #90
        t1 = t1 - numpy.floor(t1)
        t1 = -t1 * 2 + 1
        t1 = numpy.absolute(t1) * 3 + (-1)
        t1 = numpy.clip(t1, 0, 1)
        t1 = t1 + (-1); #95
        t1 = (t30) * t1 + 1; #96

        shadingAdjustment = t1

        #skip to line 352
        diffuseShaded = shadingAdjustment * 0.899999976 - 0.5;
        diffuseShaded = -diffuseShaded * 2 + 1;

        compTest = 0.555555582 < shadingAdjustment;
        shadingAdjustment *= 1.79999995;
        diffuseShaded = -diffuseShaded * 0.7225 + 1; #invertfinalambient shadow is a constant 0.7225, so don't calc it

        hlslcc_movcTemp = shadingAdjustment;
        #reframe ifs as selects
        hlslcc_movcTemp[:, [x]] = numpy.select(condlist=[compTest[:, [x]], numpy.invert(compTest[:, [x]])], choicelist=[diffuseShaded[:, [x]], shadingAdjustment[:, [x]]])
        hlslcc_movcTemp[:, [y]] = numpy.select(condlist=[compTest[:, [y]], numpy.invert(compTest[:, [y]])], choicelist=[diffuseShaded[:, [y]], shadingAdjustment[:, [y]]])
        hlslcc_movcTemp[:, [z]] = numpy.select(condlist=[compTest[:, [z]], numpy.invert(compTest[:, [z]])], choicelist=[diffuseShaded[:, [z]], shadingAdjustment[:, [z]]])
        shadingAdjustment = numpy.clip(hlslcc_movcTemp, 0, 1) #374 the lerp result (and shadowCol) is going to be this because shadowColor's alpha is always 1 making shadowCol 1

        diffuseShadow = diffuse * shadingAdjustment;

        # lightCol is constant 1.0656, 1.0656, 1.0656, 1 calculated from the custom ambient of 0.666, 0.666, 0.666, 1 and sun light color 0.666, 0.666, 0.666, 1,
        # so ambientCol always results in lightCol after the max function
        ambientCol = numpy.asarray([1.0656, 1.0656, 1.0656, 1]);
        diffuseShadow = diffuseShadow * ambientCol;

        #make a new image and place the dark pixels into it
        dark_array = diffuseShadow
        darktex = bpy.data.images.new(maintex.name[:-7] + '_DT.png', width=maintex.size[0], height=maintex.size[1])
        darktex.file_format = 'PNG'
        darktex.pixels = dark_array.ravel()
        darktex.use_fake_user = True
        darktex_filename = maintex.filepath_raw[maintex.filepath_raw.find(maintex.name):][:-7]+ '_DT.png'
        darktex_filepath = maintex.filepath_raw[:maintex.filepath_raw.find(maintex.name)]
        darktex.filepath_raw = darktex_filepath + 'dark_files\\' + darktex_filename
        #kklog(maintex.filepath_raw)
        #kklog(darktex.filepath_raw)
        darktex.pack()
        darktex.save()
        kklog('Created dark version of {} in {} seconds'.format(darktex.name, time.time() - ok))
        return darktex

if __name__ == '__main__':
    test_matrix = {
        #    Input          customAmbient    ShadowColor Shadow  Density setting Koikatsu light Koikatsu Dark
        1:  [[1, 1, 1],  [.666, .666, .666, 1],  [.764, .880, 1, 1],  74,  [1, 1, 1],  [.772, .851, .937]], #items
        2:  [[.5, .5, .5],  [.666, .666, .666, 1],  [.764, .880, 1, 1],  74,  [.5, .5, .5],  [.38, .423, .466]],
        5:  [[1, 1, 1],  [.666, .666, .666, 1],  [1, 1, 1, 1],  74,  [1, 1, 1],  [.93, .93, .93]],
        6:  [[.5, .5, .5],  [.666, .666, .666, 1],  [1, 1, 1, 1],  74,  [.5, .5, .5],  [.46, .46, .46]],
        7:  [[1, 230/255, 223/255], [.666, .666, .666, 1], [0,0,0,0], 0, [1], [238/255, 196/255, 183/255]], #skin default
        8:  [[209/255, 188/255, 173/255], [.666, .666, .666, 1], [0,0,0,0], 0, [1], [195/255, 158/255, 134/255]], #skin tan
        9:  [[1, 1, 1], [.666, .666, .666, 1], [0.8304498,0.8662278,0.9411765,1], 0, [1], [209/255, 214/255, 249/255]], #hair white
        10:  [[136/255, 159/255, 114/255], [.666, .666, .666, 1], [0.6943483,0.7576795,0.8235294,1], 0, [1], [99/255, 126/255, 104/255]] #hair green
        }
    
    test = 9
    print('Test ' + str(test))
    color = test_matrix[test][0]
    shadow_color = test_matrix[test][2]
    expected_color = test_matrix[test][5]
    actual_color = hair_dark_color(color, shadow_color)
    print(expected_color)
    print(str(actual_color) + '\n')
    print('{}, {}, {}'.format(expected_color[0] - actual_color[0], expected_color[1] - actual_color[1], expected_color[2] - actual_color[2]))

#stripped down clothes source
'''                float3 diffuse = mainTex * color;

                float3 shadingAdjustment = ShadeAdjustItem(diffuse);

                float3 diffuseShaded = shadingAdjustment * 0.899999976 - 0.5;
                diffuseShaded = -diffuseShaded * 2 + 1;

                bool3 compTest = 0.555555582 < shadingAdjustment;
                shadingAdjustment *= 1.79999995;
                diffuseShaded = -diffuseShaded * 0.7225 + 1;
                {
                    float3 hlslcc_movcTemp = shadingAdjustment;
                    hlslcc_movcTemp.x = (compTest.x) ? diffuseShaded.x : shadingAdjustment.x;
                    hlslcc_movcTemp.y = (compTest.y) ? diffuseShaded.y : shadingAdjustment.y;
                    hlslcc_movcTemp.z = (compTest.z) ? diffuseShaded.z : shadingAdjustment.z;
                    shadingAdjustment = saturate(hlslcc_movcTemp);
                }

                float3 diffuseShadow = diffuse * shadingAdjustment;

                float3 lightCol = float3(1.0656, 1.0656, 1.0656); // constant calculated from custom ambient .666 and light color .666
                float3 ambientCol = max(lightCol, .15);
                diffuseShadow = diffuseShadow * ambientCol;

                return float4(diffuseShadow, 1);'''

#stripped down skin source
'''                //Diffuse and color maps KK uses for shading I assume
                float3 diffuse = GetDiffuse(i);
                float3 specularAdjustment; //Adjustments for specular from detailmap
                float3 shadingAdjustment; //Adjustments for shading
                MapValuesMain(diffuse, specularAdjustment, shadingAdjustment);

                //Shading
                float3 diffuseShaded = shadingAdjustment * 0.899999976 - 0.5;
                diffuseShaded = -diffuseShaded * 2 + 1;
                
                bool3 compTest = 0.555555582 < shadingAdjustment;
                shadingAdjustment *= 1.79999995;
                diffuseShaded = -diffuseShaded * 0.7225 + 1;
                {
                    float3 hlslcc_movcTemp = shadingAdjustment;
                    hlslcc_movcTemp.x = (compTest.x) ? diffuseShaded.x : shadingAdjustment.x;
                    hlslcc_movcTemp.y = (compTest.y) ? diffuseShaded.y : shadingAdjustment.y;
                    hlslcc_movcTemp.z = (compTest.z) ? diffuseShaded.z : shadingAdjustment.z;
                    shadingAdjustment = saturate(hlslcc_movcTemp);
                }
                float3 finalDiffuse = diffuse * shadingAdjustment;
                
                float3 bodyShine = float3(1.0656, 1.0656, 1.0656);
                finalDiffuse *= bodyShine;

                return float4(finalDiffuse, 1);'''

#stripped down hair source
'''float3 diffuse = GetDiffuse(i.uv0) * mainTex.rgb;

    float3 finalAmbientShadow = 0.7225;
    finalAmbientShadow = saturate(finalAmbientShadow);
    float3 invertFinalAmbientShadow = 0.7225;

    finalAmbientShadow = finalAmbientShadow * _ShadowColor.xyz;
    finalAmbientShadow += finalAmbientShadow;
    float3 shadowCol = _ShadowColor - 0.5;
    shadowCol = -shadowCol * 2 + 1;

    invertFinalAmbientShadow = -shadowCol * invertFinalAmbientShadow + 1;
    bool3 shadeCheck = 0.5 < _ShadowColor.xyz;
    {
        float3 hlslcc_movcTemp = finalAmbientShadow;
        hlslcc_movcTemp.x = (shadeCheck.x) ? invertFinalAmbientShadow.x : finalAmbientShadow.x;
        hlslcc_movcTemp.y = (shadeCheck.y) ? invertFinalAmbientShadow.y : finalAmbientShadow.y;
        hlslcc_movcTemp.z = (shadeCheck.z) ? invertFinalAmbientShadow.z : finalAmbientShadow.z;
        finalAmbientShadow = hlslcc_movcTemp;
    }
    finalAmbientShadow = saturate(finalAmbientShadow);
    diffuse *= finalAmbientShadow;

    float3 finalDiffuse  = saturate(diffuse);

    float3 shading = 1 - finalAmbientShadow;
    shading = 1 * shading + finalAmbientShadow;
    finalDiffuse *= shading;
    shading = 1.0656;
    finalDiffuse *= shading;

    return float4(finalDiffuse, alpha);'''