# In depth shader breakdown

## Advanced intro

This page will take a look at the three main node groups in detail.
Namely, the texture files group, the KK general group and the combine
colors group. It will also examine the sub-groups inside of each node
group.


## Enabling Node Wrangler

Let's take a quick detour and enable node wrangler. This add-on is
invaluable for debugging node groups. In the blender add-on window
search for Node Wrangler and enable it

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/2911bcd76b785d6133314ca953ad7f68b6ca7aa7.png)

## Texture files group

Let's start with the texture files group. Open it by clicking the icon
on the top right of the group

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/0ba27212cfbc555cb4bacb2d143fea6f0fa57089.png)

Here's the texture files group.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/be81fcd554ecb75227f5c98feb124271bd46477d.png)


Each piece of clothing can have multiple textures that go with it. Each
texture file from the export folder is loaded into each outfit material
in blender. For example, the jacket CM.png from the export folder...

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/6e4ab4a9d895ee67cc014c7c069cdce2fa96676b.png)

Is loaded into the corresponding jacket CM image node in blender

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/4c75371636b8d51aa4e6eaad99d272839f090409.png)

## Pattern slots

There's a lot of textures, so let's start at the top and work our way
to the bottom. The pattern files are loaded up here.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/aa640afc3f7f62c9cbdc39849866aba51c2080ec.png)

The skirt only has one pattern (PM1.png) and it's loaded into the
pattern red slot.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/3a927c176b682106cc0680c02d95b7ba251d753c.png)

if you enabled node wrangler, you can see what the pattern looks like by
Control + Shift clicking the image node

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/f1fb577204b605202a4f7f24feaa1615d71ae5fa.png)

# Positioning with the Scale Vector group

the pattern scale and positioning can be controlled by opening the
position node group to the left of the image nodes.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/5b339a74388804694ef0e9b84ab65fa23487789a.png)

this is what the red pattern looks like after being scaled and shifted.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/b92165c28fdd623450972decda4dde8eb2a4fec7.png)

most things you can position can also be rotated using the rotation
slider

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/c6f5ddfd3c205e9a5ffe510c823882d0f57ce3b0.png)

# One more example of the Scale Vector group

It can be a little hard to see how the scale vector group works with patterns, so let's also check out the positioning group in the eye material. Here's what the eyes look like at their default scale. If you're having difficulty locating the thing you're positioning on the 3D model, recall that you can preview what the material looks like in the materials tab.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/eyeposition.png)

Here's what the eyes look like when they're scaled down. 

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/eyeposition2.png)

Here's what the eyes look like when they're scaled down, moved to the right, and rotated 90°

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/eyeposition3.png)

## Colored main texture, plain main texture and dark main texture slots

let's move onto the rest of the textures in the group now. here's what
the main texture looks like when the image node has been control shift
clicked. this is the **colored** main texture of the outfit. We'll take a look at this more in depth later on.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/4909010168b862322018dbdf0b61911673774b0c.png)

here's what the plain main texture looks like. this is the **uncolored** main texture
of the outfit. notice that some features like
the buttons are still fully textured

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/1ff890b4d80197413e0e3a9d32dcc70d00c2ad12.png)

here's what the dark main texture looks like. KKBP automatically
generates a dark version of the colored main texture and loads it into
this slot.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/b698a8f741bc7e122228d4804894d8be4ea20cff.png)

## Alpha mask slots

If a piece of clothing has an alpha mask. It'll be loaded into this
slot. here's what an alpha mask can look like

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/d0b96b98813ee0ab914ef9809ddc17af72fe4b61.png)

Look familiar? This is what the complete material looked like. The
visible portions match up with the yellow portions of the alpha mask

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/39d07e716d4ef749301606e9f57ca1c12acf40e6.png)

## Color masks slots

there are two slots for the color mask. the top slot is used for
materials that are supposed to be partially or fully transparent. the
bottom slot is used for fully opaque clothing. fully opaque clothing is
not supposed to have a color mask, but the KKBP exporter exports one
anyway. Some materials will look incorrect if a color mask is loaded
into an opaque clothing material so that's why there's two slots. A
list of in game shaders that are identified as opaque are listed below

Koikano/main_clothes_opaque', 'Shader
Forge/main_opaque', 'xukmi/MainOpaquePlus',
'xukmi/MainOpaquePlusTess', 'Shader Forge/main_opaque2', 'Shader
Forge/main_opaque_low'

We'll be taking a look at both color masks but for right now here's what
the bottom color mask looks like

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/58a2bb307d8f52df6fedbe74965f3b7dd852ce07.png)

Look familiar? This is what the fully assembled material looks like. The
brown, dark brown, and green portions of the shoes match up with the
red, green, and blue portions of the color mask.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/38ede80e4805e6a767a8ad68e3cca9335e4c83e7.png)

## Detail mask slots

This is the detail mask for the jacket.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/c06096ad0820c09c2f9fec0c8d86fa0d407a604d.png)

Look familiar? This is what the fully assembled material looks like with
the detail intensity cranked up to the max. The green portions of the
detail mask match up with the soft details on the jacket. The blue
portions of the detail mask match up with the hard lines on the jacket.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/14dd0458c00d8a11c7a0e2ebf81f635ca479808d.png)

and if we take a look at the shoes, You can see the red portion of
the detail mask

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/928989e31d5e5cdc7ef47844da8d17a9ec2cdbef.png)

the red portion matches up with the location of the shiny parts of the shoes

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/f0d01fdaa38d442ff43c2f81eed4acb3668ae5ae.png)

## Detail masks and metallic materials

the KKBP importer has a shortcoming with the detail mask related to
metallic materials. The red portion of a detail mask can either mean
shine or metal. KKBP does not support metal materials, so if it detects a
metal material, it'll automatically set the detail shine slider to
zero. For example, if we take a closer look at the jacket's detail mask,
the buttons are obviously red.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/f6da9fc3fde451dcec751ab6cb00d2f2cf84ea5f.png)

but when we take a look at the fully assembled material, the detail mask
intensity has been disabled

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/3ca5374d36f7042d3a9eb5dcea72d1a755adf691.png)

turning it back on results in erroneous appearance

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/5040c9599bc536edd6c80e57e9a8411f22144ae2.png)

this is because the buttons are supposed to gain a metallic appearance
from the red channel of the detail mask but since KKBP does not support
metallic materials. It just turns white. KKBP determines if a material is
metallic by the presence of the AR.png texture. If a material has an AR
texture, then it is assumed to be metallic, and the detail shine
intensity will be disabled automatically to avoid issues like the one
seen above.

For example the jacket has such a texture

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/dc6415e30428d2c7ead9fe66e8fcd08ac26a911e.png)

but the shoes do not have that texture so that's why the shine on the
shoes were not disabled

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/4d5a5460a684d1320b3f779d527a8e2cf375c8bc.png)

## Normal map
anything related to hair will be skipped in this explanation, so the
next node is the normal map. The normal maps are grayscale in appearance. The color of the normal map along with its alpha channel are used to create a proper normal map

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/40f5f38281b88ba2c8c3e3d19e7e04fad1dcf428.png)

## Normal map detail

and the final node is normal map detail. Most pieces of clothing do not
have a normal map detail so you'll find this placeholder instead. 

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/6b3c788e264f7acccdb28d4693e74dacefba4f2d.png)

## Final things to note about the textures group

First thing:  
Textures are loaded into each image node by their suffix. For example, the material name for the jacket is cf_m_top_jacket06 8480. The KKBP importer searches the export folder for an image called cf_m_top_jacket06 8480_CM.png and if it finds the image it loads it into the _CM.png node. Each one of these nodes has an "_ABC.png" name tag on them to ensure each texture is loaded into the correct image node

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/finalthing1.png)

Second thing:  
Main textures exported by the KKBP exporter are not saturated. These files end in "_MT_CT.png" and "_MT.png". In the game, the textures are saturated in realtime to make them look like they normally do. In blender, the KKBP importer saturates these images once, then places them into a new "saturated_files" folder. When the KKBP Importer loads the main textures, it loads the saturated _ST versions of the main textures instead of the unsaturated _MT ones. It does the same thing with dark main textures too. It will grab the _ST version of the main texture, create a dark _DT version of it, save it in a new "dark_files" folder, then load it into the dark main texture slot.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/finalthing2.png)

## Permalight image

let's also take note of this permalight mask texture. This is
an optional texture. You can create one yourself to make portions of
clothing, hair or body materials, permanently light or permanently
dark. An example of this will be shown later on

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/562d6555c130bd7eaa42c45afe90509dacacc219.png)

This texture along with the normal textures are fed into the toon
shading group. Let's go into this group.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/2c6d9187e247245bcb2d32f8aa0d52781cccf072.png)

## Toon shading group

this is the group that creates the light and dark portions of every
material. Let's work from left to right

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/92ed02234b3bef293ac87c1a288caa8fdf7fb6b0.png)

## Normal map blending and optimizing performance

this section is for determining what normal data will be fed into the
BSDF shader. By default, normals are enabled and are fed into the "normal
detail map blending" node group. This group accepts the
grayscale + alpha normal map from the game and the detail normal map (if it exists). There are two built-in methods for blending the two normal maps together. The default is the whiteout method. if you
want to use the unity tech demo blending method, you can set the slider
to zero.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/2bd651e0be6ede4e6ca288a436beb3a854ace14d.png)

Digging into the node group we can see both methods.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/a32228b5b42899107e4a1115ee79a41fa680dc9b.png)

both methods were taken from
<https://blog.selfshadow.com/publications/blending-in-detail/>, so these
are just blender node implementations of the math equations found on that page

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/5da3bb189137adcba144a7f2503c7de8c1dd67f2.png)

Returning to the normal section, The output of that group is fed into a
mix node. if normals are enabled, the output is fed into the Normal
Map optimization group. If normals are disabled, a pure purple color
will be fed to the Normal map optimization group. here's what the
output of the mix node looks like when normals are enabled

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/e1d29d4f7ed0f535c2d2d6e4050e77859d0645f7.png)

Blender has a very poor performance with the normal map node when it's
set to tangent space. The optimization group is used to improve
animation playback. When you're done animating and ready to use the
full quality normals for rendering, you can unmute the normal map node by selecting it
and pressing M, Then you can connect the output of the normal map node
to the inputs of the diffuse BSDF node. The image below shows the normal map unmuted and attached to the BSDF normal input

The normal map optimization group was taken from
<https://blenderartists.org/t/way-faster-normal-map-node-for-realtime-animation-playback-with-tangent-space-normals/1175379>

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/02fe303dfcd534d60e3d7214da456456a4b4df67.png)

## Toon shading with the BSDF node

the normals are fed into the diffuse BSDF node. This is the output of
the BSDF node. It looks like realistic shading

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/6ee8b4077b4d5bb54e9faf9fb121b9660c420ca1.png)

the black-and-white portions of the output are then crunched down using
a color ramp. Here's what the output of the color ramp looks like. It
looks more toon-like now. The white portions of this output will ultimately get the light versions of all colors. The black portions of this output will ultimately get the dark version of all colors.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/71ec75099999a502e0921b4cde3eee977a9446ed.png)

## Permamask node

The final section makes the material permanently light or permanently dark
through the use of the permalight mask. Here's what it looks like with
no perma mask loaded in

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/97bb84f57a6611b4b1d0d4c6b7915d904b79ad8f.png)

here's what it looks like with a new mask loaded in. The red portions
of the image are now permanently light, and the blue portions of the
image are now permanently dark

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/9d5e094bd34ed233ced37dbaea1c067d9ece951a.png)

here's what the fully assembled material looks like with the permamask
loaded in

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/ea2d3f0ebacd2126474be9b41a2395ebe772aa59.png)

## KK General node group

that was everything in the textures group so let's move on to the KK
general node group

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/a533070f35bce2d8d38658c8fcbb9c6dfc8330f8.png)

this node group takes all of the textures from earlier and uses them to
form the colors you see on the clothes. Let's again start from the left
and work our way to the right.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/8a8fb34bf00bc6172c1a3d04d30e66277994ca48.png)

## Colored or plain main texture

first, we choose between the colored main texture and the plain main
texture. the output of the "use plain main texture?" output is currently
zero so it outputs pure black on the entire piece of clothing

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/36823fb10483d0da33c26fce0ba0e923d04b30cb.png)

When the slider is set to zero the factor of the mix node is set to
zero. because of this the A input of the mix node is placed on the output of the node. In this case, the colored main texture is attached to the A input
of the mix node, So that's what gets passed through

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/90b51c1fc10a2b0e890e2dbf1368fc4de4fafac6.png)

when the "use plain main texture?" slider is set to one, the node will output
pure white to the clothes.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/cc218cd83e61f82f59d09e3ce1c0996ccc0da40e.png)

because the factor of the mix node is now set to one. The B input gets
passed through the mix node. In this case, the B input is the plain main
texture

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/ce21fe84ce91b4e83ddd8217220a8dd13c45fe95.png)

## HSV node

once the main texture type is chosen It's sent through an HSV node.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/fe94b83d702cf2a45f4e0ed184fa68e5437495bf.png)

the HSV values in the material tab for the main texture directly
correlate to the inputs of this node.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/3c03e6c90eddb7b479d3c7f04595333eea5fee1c.png)

## Colormask and patterns

Once the HSV values are adjusted, The color mask and the patterns are
applied. Not every piece of clothing uses every feature here so we'll
take a look at a few different pieces of clothing in this section

let's start with the node inbetween the inputs and the "add color mask
and patterns" node group. When you disable the "use plain main texture?"
slider, the first color mask from the textures group is placed at the output of the mix node.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/97bb8f9327ec670288f69a6c82e24778c0c5ae84.png)

If you recall from earlier, opaque materials that use the shaders below are not
supposed to have a color mask

'Koikano/main_clothes_opaque', 'Shader
Forge/main_opaque', 'xukmi/MainOpaquePlus',
'xukmi/MainOpaquePlusTess', 'Shader Forge/main_opaque2', 'Shader
Forge/main_opaque_low'

this piece of clothing happens to be an opaque material so that's why
the colormask in the first slot was pure black.

If you enable the "use plain main texture" slider, then the color mask loaded
into the second color mask slot will be passed through the mix node.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/edb52766f957d70229a4044343955a7098d6bd15.png)

If we take a look at the output of the "add color mask and patterns" node
group, you can see that the colors look correct when the plain main
texture slider is set to zero

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/9ab46d8a6f4bd2ad058bd728bb787fb335bf67e3.png)

and they still look correct when it's set to one

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/f4674221e7238b4ad133b6a2b3dabcea612234a5.png)

this is because of the dual color mask setup. If I force the second
color mask to be enabled while the colored main texture is active you
can see that the color is applied twice to the material and that's not
something that you want to see

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/7e830a952b7097f418785dce91703102d6cd2914.png)

so again that's why there's two color mask slots. Because if the
clothing is using the opaque shader then you'll have a fully colored
main texture and a black color mask in the first color mask slot,
meaning no extra colors will be applied to the already colored main texture.

 Then when you're using the plain main
texture, you always want the colors applied to it because it's white,
meaning you always want a color mask in the second slot.

## Add colormask and patterns node group

If it still doesn't make sense, let's take a look inside the "add color
mask and patterns" node group.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/8df1f91fca5ed3eea3a5c93cf2f0bce814d24bae.png)

the group starts with the base color. The base color will always be pure
white, But you can change it if you want with the color mask base color
input in the material tab

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/d3bf16c8b63741f1577b7be73c24b88d5c39b1d4.png)

next the red color from the color mask is placed. (make sure the plain
main texture slider is set to one or you won't see anything). if we get
a preview of the color mask, you can see where the red color is going to
go

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/098c30ea93a724c46c2a3451c56cc0ea5ec89018.png)

the red portion of the color mask is separated out with the "separate
color" node

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/da0994cdd3afc9b76f87dcef5621182959b36702.png)

and the red color is applied to the white masked out portion going into
the factor input of the mix node

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/edf761215ca32844584c91b2fad6294992a02646.png)

the same thing happens with the green channel of the color mask

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/ffeccd0217d58faa3e60bf8e39f6d5e3aae0765a.png)

the green channel is singled out

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/ed22c28e0c6601b3c24dd745677526d9a9d0b225.png)

and the green color is applied to that white area

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/d1415354cb994f61707aaea5f6b5b04c47607c35.png)

same with the blue channel

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/d40aef2788ca2ef4c6b2f30e2a02392e47307a5c.png)

and finally the plain main texture is multiplied by those colors. recall this is what the plain main texture looks like

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/36adc37d8425f24348f9f75f1b382ef44b1ddac1.png)

Once they are multipled, you get the resulting image

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/c02d5483a35d4686a9ed8a2e4da7da28ff9f40f7.png)

if we take a step back and see what the B input of the multiply node
looks like when the plain main texture slider is set to zero, we can see
that it's pure white.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/1f98fa55b02b6a96d82a036f664dd4b2757abc10.png)

Recall that this color mask is pure black so nothing shows up at the
separate color mode output. A black section in the color mask basically means "do not put any color here, just keep it white".

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/0090e4ca61f67380363e865a32853cf559292a81.png)

so when the slider is disabled and the color mask is black, the colored main texture is multiplied
by pure white. Here's what the A input of the multiplying node looks
like.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/cb92d85c616148515551c9f510afd05ef468cfd1.png)

and here's what the result looks like. (exactly the same)

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/79c513ba771127c0ed92bcafeb1b0b8356e9f64d.png)

and if we take a step back one more time we can see how patterns work.
When a pattern is loaded into a pattern slot in the textures group, The
colors in the color mask (red) color input, and the pattern color (red)
color input will be applied to the white and black portions of the
pattern respectively, with this mix node

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/9d70e520ad3394bbcb4ad1e7d366e419cf7d8c4d.png)

the black-and-white pattern goes into the factor input of the mix
node, So where the pattern is black the A input will be used which is
the darker color, And where the pattern is white is where the B input
will be used, which is the regular color mask color

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/6886dfc13c59957f0369ce44b2075257aa114be6.png)

So to summarize the color mask behavior one more time...  
* Black = Do not add any color to the main texture, keep it the way it is
* Red = Multiply the main texture by the red color mask color here
* Green = Multiply the main texture by the green color mask color here
* Blue = Multiply the main texture by the blue color mask color here
* Any overlaps in the color mask = Blue overrides green, green overrides red

## Green detail

let's move onto group that applies the green channel of the detail mask

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/64c1a38049c82adbca167d77af6bfc1bd0d5946b.png)

## Generating detail color
there's a few things that go on in this group. let's start with the
frame on the left

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/7c29a0829d93586210bdaf30c32c877b37cb042f.png)

this section very intensely saturates the colors in order
automatically get a detail color. This is what the clothing looks like at the output
of the section

the darkening code is taken from
<https://github.com/xukmi/KKShadersPlus/tree/main/Shaders/Hair> so it's
really just a node implementation of the equations found in that shader
file

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/bbb929881be5c821c72df2af42b1d4b1e580caf7.png)

the next section adds blue tint to the saturated color, but only if the
color is detected as white, and never if the color is detected as dark.
the light color detection is done by taking the saturation value of the
material

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/e6245451148c0abd5be30606f0b1e5bea3de2aea.png)

and sending it through a color ramp to make sure that only the least
saturated colors get a blue tint applied to them. the white portions of
the clothing will not get a blue tint. The black portions of the
clothing will get a blue tint

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/72525eb438e70f0f536a24433bf9d7491681ce7b.png)

the dark color detection is done with the value of the color

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/cb41e84b5e12b49dcb41c695d0fd15ac8b432e99.png)

this value is then inverted and crunched down with another color ramp.
The white portion of the clothing will not get a blue tint. The black
portions of the clothing will get a blue tint

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/f396dbfb6daf03c503b151eb68a54f3817d3fc9e.png)

these two values are then added together and sent into the multiply node
factor input. Again, the white portions will not get the blue tint.
Only the black portions will.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/4cc59cfea1cc0567be04f4b433ad9200ee30ea3e.png)

This is what the detail color looks like, with the blue tint applied.
Only the white-most portions of the jacket got a blue tint.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/c21917bb3bd0726c1f36310704d1b93be7741907.png)

## Overriding detail color

you also have the option of overriding the detail color. If you override
the detail color you can set it to whatever you want with the "detail
color" color input. here's what it looks like without the override
enabled

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/76dec3111f854ee8648c1bc3a890fcb2433cf552.png)

here's what it looks like with the override enabled

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/1c5680d777a0ecc709fe06e3793246bfcae401b5.png)

## Detail intensity
and finally, the shader needs to know where to put this detail color, so
the detail mask is brought in

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/0501bb7255a810f339f716019678e86090b71ae8.png)

the green channel of the detail mask is used to locate where
to put the detail color.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/3699a3b1008c0f1daa5ddc4e8a454ad21fc94e0d.png)

The strength of the detail mask can also be increased with this multiply
node. Here's what it looks like when it's set to the default of 0.8

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/3936b6fdc1349c9fde97899733a2b7afaec90d25.png)

here's what it looks like when it's set to five

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/0077b20e15f3570c8f827fd1a1db4e7c8a76f7bc.png)

and here's what it looks like after the mix node, with the detail
color applied to the main texture (detail intensity still set to 5 for
clarity)

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/f37520ac74f77cae6d812393732b1a38c74a990a.png)

the same process is applied for the blue channel of the detail mask. In
order to ensure only the blue channel of the detail mask is used, the
"separate color" node is used to extract only the blue channel. This causes the blue channel to replace the RG and B channels of the detail mask so when the green channel is extracted later on, it's really just extracting the blue channel

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/253ad754b2b2d9a653a9bf1293f67319b03a295f.png)

## Detail shine
the final part of the KK general node group is the shine.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/725c1670a98062bc6123f43aa82166abd5e1c5e7.png)

Just like before the detail mask is loaded in.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/d3da7206142eeebde11ba31803d280022878fa6b.png)

And the red channel is used along with the shine intensity to determine
where the shine color will be applied..

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/15b788fbdc86a5f2e7b972c09007fbf4c79fd30b.png)![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/bcac94622b34a7508d7b6f23ecdabb1dd72c4b7f.png)

## Combine colors group

the final portion of the KK general material Is the combine colors
group. This group takes the light colors and the dark colors from the
previous shader groups and combines them using the black-and-white
mask from the toon shading group. This group also applies
transparency to the model if its main texture is semi transparent, or
if it has an alpha mask. Custom alpha masks can also be loaded in. You
can check the body material for an example of a custom alpha mask.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/971ed0a79c2fc4d7c89a0cce8680708c28a9017e.png)

this is all there is inside of the combine colors group.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/fd323b1b3a98bc5989f81c48658b8c49294a52f6.png)

To keep things simple I'm going to remove the custom alpha mask from
the group, again you can check the body material if you want to see how
it works yourself.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/a39d55abb81cdcb0b7cf93736de03fdedcf4b425.png)

so let's start with the alpha mask

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/7adfc64521ba60d389a34c248aff6a518bdfad29.png)

the red channel of the alpha mask is used to determine what parts of the
clothes should be visible

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/3bcf7ceda44e22be721509034dfc07d1ea51a5d6.png)

in some cases the alpha channel of the alpha mask is also used to
determine what parts of the clothes should be visible. In this case, the
alpha mask's alpha channel is pure white, so it does not affect the
clothes alpha

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/55335816673af84ad5e97a1b40c6dc9b2a5400d0.png)

because the alpha channel is pure white, this is what it looks like when
the red channel of the alpha mask and the alpha channel of the alpha
mask are multiplied together.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/73033fb16639dd4805efc3e823a89e6827deeba4.png)

The alpha channel of the main texture can also determine the materials
visibility. In this case, the main textures alpha channel is pure white
so (again) it does not affect the materials visibility

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/70f5da50680e27f69b7293f72173cd32187c2aa5.png)![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/0727faf59774c4ae9b73f996ecf5897f28345672.png)

and finally if you want to force a material to be fully visible, then
you can use the force visibility slider to add white to the result.
Here's what it looks like when the slider is disabled

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/5bf7cc0cfc2e94fa2f2e154392b28a67ee4ca378.png)

and here's what it looks like when it's enabled

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/84e16a45c1868ab4666c68fd6eefd11683f5c13f.png)

if we look at the top, we can see the light colors are fed in
through this node input

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/23ca5eef694b605c70130739c27809ed824a81ea.png)

the dark colors are fed in through this node input

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/bd0c1a82b01631c99be232ad4a6a8bb952370709.png)

and the toon shading is loaded into this input

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/56070d375bd5c004fb96352e89e378ed2cb75c40.png)

The portions of the toon shading that are white will get the light colors and
the portions that are dark will get the dark colors

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/6fed39e49e2dcd4d6ea21794644a1862ce1a9249.png)

and finally the transparency mask from earlier is used to
determine if the color is passed through or if a transparent shader is
passed through to the material output

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/ec74008172355134e82304a98b9076f14ffc6ab2.png)

## Outro

and that was a complete walk-through of KKBP's KK general material node setup. If
you check the hair, skin, eyes and any other KKBP material, you'll find
that many of the node setups and simple masking strategies are reused
everywhere. 

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/1bb2d247a9ca61ee50774e517ad23ab8ba09f2bd.png)
