#multiplying things per element according to https://github.com/Unity-Technologies/Unity.Mathematics/blob/master/src/Unity.Mathematics/float4.gen.cs#L330
#returning things like float.XZW as [Xposition = X, Yposition = Z, Zposition = W] according to https://github.com/Unity-Technologies/Unity.Mathematics/blob/master/src/Unity.Mathematics/float4.gen.cs#L3056
#using the variable order x, y, z, w according to https://github.com/Unity-Technologies/Unity.Mathematics/blob/master/src/Unity.Mathematics/float4.gen.cs#L42

import math

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
    
    
#this function is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Item/KKPItemDiffuse.cginc
#lines without comments at the end have been copied verbatim from the C# source
def ShadeAdjustItem(col, _ShadowColor):
    #start at line 63
    u_xlat0 = col
    u_xlat1 = float4(u_xlat0.y, u_xlat0.z, None, u_xlat0.x) * float4(_ShadowColor.y, _ShadowColor.z, None, _ShadowColor.x) #line 65
    u_xlat2 = float4(u_xlat1.y, u_xlat1.x) #66
    u_xlat3 = float4(u_xlat0.y, u_xlat0.z) * float4(_ShadowColor.y, _ShadowColor.z) + (-float4(u_xlat2.x, u_xlat2.y)); #67
    u_xlatb30 = u_xlat2.y >= u_xlat1.y;
    u_xlat30 = 1 if u_xlatb30 else 0;
    u_xlat2 = float4(u_xlat2.x, u_xlat2.y, -1.0, 0.666666687); #70-71
    u_xlat3 = float4(u_xlat3.x, u_xlat3.y, 1.0, -1); #72-73
    u_xlat2 = (u_xlat30) * u_xlat3 + u_xlat2;
    u_xlatb30 = u_xlat1.w >= u_xlat2.x; 
    u_xlat30 = 1 if u_xlatb30 else float(0.0);
    u_xlat1 = float4(u_xlat2.x, u_xlat2.y, u_xlat2.w, u_xlat1.w) #77
    u_xlat2 = float4(u_xlat1.w, u_xlat1.y, u_xlat2.z, u_xlat1.x) #78
    u_xlat2 = (-u_xlat1) + u_xlat2;
    u_xlat1 = (u_xlat30) * u_xlat2 + u_xlat1;
    u_xlat30 = min(u_xlat1.y, u_xlat1.w);
    u_xlat30 = (-u_xlat30) + u_xlat1.x;
    u_xlat2.x = u_xlat30 * 6.0 + 1.00000001e-10;
    u_xlat11 = (-u_xlat1.y) + u_xlat1.w;
    u_xlat11 = u_xlat11 / u_xlat2.x;
    u_xlat11 = u_xlat11 + u_xlat1.z;
    u_xlat1.x = u_xlat1.x + 1.00000001e-10;
    u_xlat30 = u_xlat30 / u_xlat1.x;
    u_xlat30 = u_xlat30 * 0.5;
    #the w component of u_xlat1 is no longer used, so ignore it
    u_xlat1 = abs((u_xlat11)) + float4(0.0, -0.333333343, 0.333333343, 1); #90
    u_xlat1 = u_xlat1.frac(); #91
    u_xlat1 = -u_xlat1 * 2 + 1; #92
    u_xlat1 = u_xlat1.abs() * 3 + (-1) #93
    u_xlat1 = u_xlat1.clamp() #94
    u_xlat1 = u_xlat1 + (-1); #95
    u_xlat1 = (u_xlat30) * u_xlat1 + 1; #96
    return float4(u_xlat1.x, u_xlat1.y, u_xlat1.z, 1) #97

#rest is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Item/MainItemPlus.shader
#lines without comments at the end have been copied verbatim from the C# source
def kk_dark_color(color, shadow_color):
    ################### variable setup
    _ShadowExtendAnother = 0 #manually set in game
    _ShadowExtend = 0 #manually set in game
    finalRamp = .26 #assume ramp is inversion of shadow setting in the charamaker. setting it to 1 gives the original light color back
    a = 0.666
    _ambientshadowG = float4(a,a,a,1) #defaults to 0.666, 0.666, 0.666, 1
    _CustomAmbient = _ambientshadowG
    _LightColor0 = float4(1,1,1,1) #assume light color is 1
    vertexLighting = float4(0,0,0,1) #assume vertex lighting is 0
    vertexLightRamp = float4(0,0,0,1) #assume light ramp is black
    detailMask = float4(0,0,0,1) #black if no detail mask loaded in

    diffuse = float4(color[0],color[1],color[2],1) #maintex color
    _ShadowColor = float4(shadow_color[0],shadow_color[1],shadow_color[2],1) #shadow color from material editor defaults to [.764, .880, 1, 1]
    ##########################
    
    #start at line 344 because the other one is for outlines
    shadingAdjustment = ShadeAdjustItem(diffuse, _ShadowColor)

    #skip to line 352
    diffuseShaded = shadingAdjustment * 0.899999976 - 0.5;
    diffuseShaded = -diffuseShaded * 2 + 1;
    ambientShadow = 1 - float4(_ambientshadowG.w, _ambientshadowG.x, _ambientshadowG.y, _ambientshadowG.z) #354
    ambientShadowIntensity = -ambientShadow.x * float4(ambientShadow.y, ambientShadow.z, ambientShadow.w, 1) + 1 #355
    ambientShadowAdjust = _ambientshadowG.w * 0.5 + 0.5;
    ambientShadowAdjustDoubled = ambientShadowAdjust + ambientShadowAdjust;
    ambientShadowAdjustShow = 0.5 < ambientShadowAdjust;
    ambientShadow = ambientShadowAdjustDoubled * _ambientshadowG; #359
    finalAmbientShadow = ambientShadowIntensity if ambientShadowAdjustShow else ambientShadow; #360
    finalAmbientShadow = finalAmbientShadow.saturate(); #361
    invertFinalAmbientShadow = 1 - finalAmbientShadow;
    compTest = 0.555555582 < shadingAdjustment;
    shadingAdjustment *= finalAmbientShadow;
    shadingAdjustment *= 1.79999995;
    diffuseShaded = -diffuseShaded * invertFinalAmbientShadow + 1;

    hlslcc_movcTemp = shadingAdjustment;
    hlslcc_movcTemp.x = diffuseShaded.x if (compTest.x) else shadingAdjustment.x; #370
    hlslcc_movcTemp.y = diffuseShaded.y if (compTest.y) else shadingAdjustment.y; #371
    hlslcc_movcTemp.z = diffuseShaded.z if (compTest.z) else shadingAdjustment.z; #372
    #shadowCol = lerp(1, _ShadowColor.rgb, 1 - saturate(_ShadowColor.a));
    shadowCol = _ShadowColor # but the lerp result is going to be this because shadowColor's alpha is always 1
    shadingAdjustment = (hlslcc_movcTemp * shadowCol).saturate(); #374
    shadowExtendAnother = 1 - _ShadowExtendAnother;
    shadowExtendAnother -= 0; #assume KKMetal is 0
    shadowExtendAnother += 1;
    shadowExtendAnother = (0 if shadowExtendAnother < 0 else 1 if shadowExtendAnother > 1 else shadowExtendAnother) * 0.670000017 + 0.330000013 #384
    shadowExtendShaded = shadowExtendAnother * shadingAdjustment;
    shadingAdjustment = -shadingAdjustment * shadowExtendAnother + 1;
    diffuseShadow = diffuse * shadowExtendShaded;
    diffuseShadowBlended = -shadowExtendShaded * diffuse + diffuse;

    #skip to 437
    diffuseShadow = finalRamp *  diffuseShadowBlended + diffuseShadow;

    #jump up to 248 function definition
    def AmbientShadowAdjust():
        u_xlatb30 = _ambientshadowG.y >= _ambientshadowG.z;
        u_xlat30 = 1 if u_xlatb30 else float(0.0); #256
        u_xlat5 = float4(_ambientshadowG.y, _ambientshadowG.z); #257
        u_xlat5.z = float(0.0);
        u_xlat5.w = float(-0.333333343);
        u_xlat6 = float4(_ambientshadowG.z, _ambientshadowG.y); #260
        u_xlat6.z = float(-1.0);
        u_xlat6.w = float(0.666666687);
        u_xlat5 = u_xlat5 + (-u_xlat6);
        u_xlat5 = (u_xlat30) * float4(u_xlat5.x, u_xlat5.y, u_xlat5.w, u_xlat5.z) + float4(u_xlat6.x, u_xlat6.y, u_xlat6.w, u_xlat6.z); #264
        u_xlatb30 = _ambientshadowG.x >= u_xlat5.x;
        u_xlat30 = 1 if u_xlatb30 else float(0.0); #266
        u_xlat6.z = u_xlat5.w;
        u_xlat5.w = _ambientshadowG.x;
        u_xlat6 = float4(u_xlat5.w, u_xlat5.y, u_xlat6.z, u_xlat5.x) #269
        u_xlat6 = (-u_xlat5) + u_xlat6;
        u_xlat5 = (u_xlat30) * u_xlat6 + u_xlat5;
        u_xlat30 = min(u_xlat5.y, u_xlat5.w);
        u_xlat30 = (-u_xlat30) + u_xlat5.x;
        u_xlat30 = u_xlat30 * 6.0 + 1.00000001e-10;
        u_xlat31 = (-u_xlat5.y) + u_xlat5.w;
        u_xlat30 = u_xlat31 / u_xlat30;
        u_xlat30 = u_xlat30 + u_xlat5.z;
        #xlat5's w component is not used after this point, so ignore it
        u_xlat5 = abs((u_xlat30)) + float4(0.0, -0.333333343, 0.333333343, None); #278
        u_xlat5 = u_xlat5.frac(); #279
        u_xlat5 = (-u_xlat5) * 2.0 + 1.0; #280
        u_xlat5 = u_xlat5.abs() * 3 + (-1); #281
        u_xlat5 = u_xlat5.clamp(); #282
        u_xlat5 = u_xlat5 * float4(0.400000006, 0.400000006, 0.400000006) + float4(0.300000012, 0.300000012, 0.300000012); #283
        return float4(u_xlat5.x, u_xlat5.y, u_xlat5.z, 1)

    #jump back down to 470 where this function is used
    ambientShadowAdjust2 = AmbientShadowAdjust()
    #skip to 482
    ambientShadowAdjust2 = ambientShadowAdjust2.clamphalf() #clamp between zero and .5
    diffuseShadow += ambientShadowAdjust2;

    lightCol = (_LightColor0 + vertexLighting * vertexLightRamp) * float4(0.600000024, 0.600000024, 0.600000024, 0) + _CustomAmbient;
    ambientCol = max(lightCol, _ambientshadowG);
    diffuseShadow = diffuseShadow * ambientCol;
    shadowExtend = _ShadowExtend * -1.20000005 + 1.0;
    drawnShadow = detailMask.y * (1 - shadowExtend) + shadowExtend;

    #skip to 495
    shadingAdjustment = drawnShadow * shadingAdjustment + shadowExtendShaded
    shadingAdjustment *= diffuseShadow;
    diffuse *= shadowExtendShaded;

    #print('diffuse is ' + str(diffuse))
    #print('diffuseShadow is ' + str(diffuseShadow))
    #print('diffuseShaded is ' + str(diffuseShaded))
    #print('drawnShadow is ' + str(drawnShadow))
    #print('diffuseShadowblended is ' + str(diffuseShadowBlended))
    return [diffuse.x, diffuse.y, diffuse.z]

if __name__ == '__main__':
    color = [.5, .5, .5]
    shadow_color = [.764, .880, 1]
    new_color = kk_dark_color(color, shadow_color)