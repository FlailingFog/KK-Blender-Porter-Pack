### Texture Postfix Legend:
    _MT_CT -> _MainTex_ColorTexture
    _MT_DT -> _MainTex_DarkenedColorTexture (aka DarkTex)
    _MT -> _MainTex (aka Plain MainTex)
    _ST_CT -> _Saturated_MainTex_ColorTexture
    _ST_DT -> _Saturated_MainTex_DarkenedColorTexture (aka Saturated DarkTex)
    _ST -> _Saturated_MainTex (aka Plain Saturated MainTex)
    _AM -> _AlphaMask
    _CM -> _ColorMask
    _DM -> _DetailMask
    _LM -> _LineMask
    _NM -> _NormalMask
    _NMP -> _NormalMap
    _NMPD -> _NormalMapDetail
    _ot1 -> _overtex1
    _ot2 -> _overtex2
    _ot3 -> _overtex3
    _lqdm -> _liquidmask
    _HGLS -> _HairGloss
    _T2 -> _Texture2
    _T3 -> _Texture3
    _T4 -> _Texture4
    _T5 -> _Texture5
    _T6 -> _Texture6
    _T7 -> _Texture7
    _PM1 -> _PatternMask1
    _PM1 -> _PatternMask2
    _PM1 -> _PatternMask3

### stripped down clothes source for dark colors
    float3 diffuse = mainTex * color;

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

    return float4(diffuseShadow, 1);

### stripped down skin source for dark colors
    //Diffuse and color maps KK uses for shading I assume
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

    return float4(finalDiffuse, 1);

### stripped down hair source for dark colors
    float3 diffuse = GetDiffuse(i.uv0) * mainTex.rgb;

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

    return float4(finalDiffuse, alpha);