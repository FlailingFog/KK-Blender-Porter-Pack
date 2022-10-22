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
    #print([u_xlat1.x, u_xlat1.y, u_xlat1.z, 1])
    return float4(u_xlat1.x, u_xlat1.y, u_xlat1.z, 1) #97

#rest is from https://github.com/xukmi/KKShadersPlus/blob/main/Shaders/Item/MainItemPlus.shader
#This was stripped down to just the shadow portion, and to remove all constants
def kk_dark_color(color, shadow_color):
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

if __name__ == '__main__':
    test_matrix = {
        #    Input          customAmbient    ShadowColor Shadow  Density setting Koikatsu light Koikatsu Dark
        1:  [[1, 1, 1],  [.666, .666, .666, 1],  [.764, .880, 1, 1],  74,  [1, 1, 1],  [.772, .851, .937]],
        2:  [[.5, .5, .5],  [.666, .666, .666, 1],  [.764, .880, 1, 1],  74,  [.5, .5, .5],  [.38, .423, .466]],
        #3:  [[1, 1, 1],  [0, 0, 0, 1],  [.764, .880, 1, 1],  74,  [.79, .79, .79],  [.611, .678, .745]],
        #4:  [[.5, .5, .5],  [0, 0, 0, 1],  [.764, .880, 1, 1],  74,  [.4, .4, .4],  [.298, .329, .368]],
        5:  [[1, 1, 1],  [.666, .666, .666, 1],  [1, 1, 1, 1],  74,  [1, 1, 1],  [.93, .93, .93]],
        6:  [[.5, .5, .5],  [.666, .666, .666, 1],  [1, 1, 1, 1],  74,  [.5, .5, .5],  [.46, .46, .46]],
        #7:  [[1, 1, 1],  [.666, .666, .666, 1],  [.764, .880, 1, 1],  100,  [1, 1, 1],  [.67, .788, .913]],
        #8:  [[.5, .5, .5],  [.666, .666, .666, 1],  [.764, .880, 1, 1],  100,  [.5, .5, .5],  [.325, .392, .454]],
        #9:  [[1, 1, 1],  [0, 0, 0, 1],  [1, 1, 1],  100,  [.796, .796, .796],  [.72, .72, .72]],
        #10:  [[.5, .5, .5],  [0, 0, 0, 1],  [1, 1, 1],  100,  [.4, .4, .4],  [.35, .35, .35]],
        #11:  [[1, 1, 1],  [.666, .666, .666, 1],  [1, 1, 1],  100,  [1],  [0.9, 0.9, 0.9]],
        #12:  [[.5, .5, .5],  [.666, .666, .666, 1],  [1, 1, 1],  100,  [.5, .5, .5],  [.454, .454, .454]],
        }
    for test in test_matrix:
        print('Test ' + str(test))
        color = test_matrix[test][0]
        shadow_color = test_matrix[test][2]
        expected_color = test_matrix[test][5]
        print(expected_color)
        print(str(kk_dark_color(color, shadow_color)) + '\n')

#stripped down source
'''				float3 diffuse = mainTex * color;

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