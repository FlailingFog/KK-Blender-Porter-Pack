# KKBP material breakdown

This page will fully break down the material node logic for KKBP 8.0's
"KK General" material shader. The simple node logic in the KK General
material is used throughout the entire project, so reading and
understanding this page should allow you to learn how to fix or debug
any KKBP material you encounter.

## Before you begin...

A large amount of cards were chosen at random and tested during the
development of KKBP 8.0.  

Out of 133 cards...
* 104 (78%) worked out of the box
* 22 (17%) had odd material issues that took 5 minutes to fix
* 5 (4%) exported but did not import
* 1 (0.5%) had odd material issues that would likely take someone a while to figure out
* 1 (0.5%) did not export and crashed the game

This means if you're having issues **there's a 94.5% chance** reading the
"Basic options" section below will help you fix the appearance of your
model. It also means **there is a 0.5% chance** that you'll have to dig
through this entire thing to find out why a material isn't looking the
way it's supposed to look.

And before you waste your time, **please make sure you didn't get an error**
during the import process as described on the front page!  
**This page will not help you if your model imported with errors!**

# Basic shader breakdown
## Intro

This breakdown will begin by using the clothing found on Chika, the
default Koikatsu model. Let's start by opening up the shading tab in
blender.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/89c3ec7cfffb6a560eceb901ed75b1f531c56b22.png)

This is the material setup that is used in every material. The texture
files from the export folder are loaded into the green group on the
left. The colors are generated in the blue group in the middle and then
fed to the output node in the red group.

There are light colors and dark colors for every material. Right now,
the light colors are showing. You can toggle between the light and dark
colors by using the viewport shading buttons on the top right. Here's
what the dark colors look like.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/6b413f2411f3809004ea6efb72f87a0666083c8e.png)

The remainder of this documentation will use the light colors only. You
can expand the options for the light colors of the model by clicking on
the arrow in the material panel

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/77cb1be3f9741658df1313fbfcd60f11485f0cfb.png)

## Detail color

Let's go through each option. The first option is override detail
color. KKBP automatically generates a detail color for you but if you
want to override the color it gives you, you can enable this slider and
set the detail color to whatever you want. Here's what it looks like
when it's set to yellow

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/963adabb6ca07aded0b943c7bec1b6646b62d22e.png)

Here's what it looks like when it's set to red

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/8d2ac0c1d5c8e5995bcf5f5a217f440408a8999c.png)

## Detail intensity

The next option is green detail intensity. Green detail intensity
usually controls the soft details on clothes. Here's what the jacket
look like at the default of .8 intensity

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/8765798548a8a561d9ae0fe1a4ae56b383b29700.png)

Here's what the jacket look like when it's set to five green intensity

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/cd98a37c2f3f15aecb77fb921c7743a4c7f62803.png)

And here's what they look like when the detail is set to 10 green
intensity

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/812f55ebe55a5c7c1c3431433133515bf6916a64.png)

The blue detail intensity usually controls hardline details on clothes.
Here's what the jacket look like it's set to the default of 0.1.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/71ff40ea839d748f15843b6f4c9137941eb04882.png)

Here's what it look like when it's set to one

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/55383a783060447fb43f8515417046d6c029e321.png)

And here's what it look like when it's set to five

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/69fd3ff65df304471db69473333d0bf0585c021e.png)

## Shine

Some clothes also have a shininess that can be adjusted. The default
loafers have an adjustable shine. The color of the shine can be changed.
Here's what the loafers look like with a white shine.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/92e10b991094734f51b0849bcc6925ef920c9950.png)

And here's what they look like with a green shine

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/63adc021bbd605cea522b3b1f3c38ff59388d7bb.png)

The intensity of the shine can also be adjusted. Here's what the loafers
look like with the default shine intensity of one.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/ab5828b1216b29812e265610482908b70e5cae8a.png)

Here's what the loafers look like with the shine intensity set to zero

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/4b0c6fd05f004e196b9c3a72115cdddc5d2cb232.png)

## Maintex HSV

Most clothes have what is called a main texture or a maintex for short.
The hue, saturation and value of the main texture can be easily adjusted
with the maintex sliders. Here's what the shoes look like with their HSV
values adjusted

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/80774dd31c98982b2a55e5dd99ea3804f1b225a5.png)

## Color mask colors

If a piece of clothing has a main texture, it will also have what is
called a plain main texture. The difference between a main texture and a
plain main texture will be explained later on. For now, all you need to
know is that each color on every piece of clothing can be changed, just like in the game. In order to do this, the plain main texture must be enabled. The slider to enable the plain main texture is set to 1 in the picture below.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/d433ff287e3589cfe8ae9debbd238d1abf031346.png)

Once the slider is enabled, you can change the colors of the piece of
clothing with the color mask color inputs. The color mask colors of the
shoes are changed below.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/66d706cc284f2a1ef008ee23fa815ba2724a666f.png)

You can return to the original colors at any point by resetting the
color mask colors to their original values. Or by disabling the plain
main texture slider again (thus, the regular main texture will be used
again).

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/43263be8f9743e3f9ccf596453bf1f2c3484aee8.png)

## Pattern colors

Some clothing like the default skirt have pattern colors that can be adjusted. In order to adjust the pattern colors, you need to use the plain main texture. The picture below shows the plain main texture slider enabled for the skirt.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/d48cc90aff12458545e4bed0166e10a5f922f1b6.png)

The default skirt only has one pattern color that can be adjusted.
Here's what it looks like with the pattern color set to blue.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/d0636d3c6294398178d70e56a9da832a95fa6d38.png)

If this piece of clothing had more patterns, their colors would be
adjusted with the pattern color green and pattern color blue color
inputs

## Visibility slider

Some pieces of clothing have what is called an alpha mask. The alpha
mask hides certain parts of clothing to prevent it from clipping through
other clothing. The default inner shirt is an example of a piece of
clothing that has an alpha mask

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/5fcdffbb5e0d54c5780dd136b163f7e1b1c9a06c.png)

Portions of this clothing are hidden to prevent it from clipping through
the jacket. If you want to make the clothing visible anyway, even though it
shouldn't be, you can enable the force visibility slider. Here's what
the shirt looks like with the slider enabled.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/ebb94af4e7cfc44e95c4e0342cf91111c20512e4.png)

And here's what the shirt and jacket look like with the shirt fully
visible. Notice that some parts are clipping through the jacket when
they shouldn't be. That's why the alpha mask is enabled by default.

![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/e08533fb229046285c72147d685b1ff55fe90f61.png)  
![](https://raw.githubusercontent.com/kkbpwiki/kkbpwiki.github.io/master/assets/shader_media/cffd898b850e771d1193dbbaae23d0f2e79cb5c9.png)


# In-depth shader breakdown

That concludes all basic clothing options.  

If you are part of the 0.5% and none of these helped fix the material you're having issues with, you can check [the in-depth shader breakdown page](material_breakdown_advanced) for even more information on the KKBP "KK General" shader.

