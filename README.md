# stage-fx

## QLC+
 - Download [QLC+](https://qlcplus.org/) v4.13.1
 - Launch using the -w option, i.e. ``C:\QLC+\qlcplus.exe -w`` to enable web interface

### 1.) Add Lighting Fixtures

The first step is to tell QLC+ about the lighting fixtures that you want to control. 
Every fixture has different functions, which are mapped to different DMX channels. An RGB PAR can might use 3 channels, for Red, Green, and Blue. A strobe light might use 2 channels - for intensity and speed. A moving spotlight might use channels for pan, tilt, and speed, etc.  
QLC+ comes with a predefined set of common lighting fixtures, and if your lights appear in that list you can simply select them from there. 
If not, you can use the standalone QLC Fixture Editor to add the parameters of your light fixture. You will need to refer to the instructions supplied by the manufacturer to identify the correct mode and channel functions. Save the fixture in the ``C:\Users\%USERNAME%\QLC+\Fixtures`` directory.


> [!NOTE]
> Many cheap, generic lights advertised by companies on Amazon etc. are actually rebranded versions of UKing lights. 
> e.g.
>  - [this](https://www.amazon.co.uk/LeLeght-Adjustable-Spotlight-Halloween-Christmas/dp/B0CFHFKP93) Leleght light is actually a [UKing ZQ06074](https://www.uking-online.com/product/48pcs-rgb-three-in-one-leds-color-mixing-rainbow-effect-highlights-outdoor-lighting/)
> - [these](https://www.amazon.com/Donner-Spotlight-Pinspot-Lightning-Control/dp/B019GFDK10/) Donner pin spots are actually [UKing ZQB93](https://www.uking-online.com/product/2-pcs-b93-pinspot-rgbw-light-lt-led-10w/)
> 
> So, if you cannot find your light in the list and do not have a manual for it, try searching for a UKing model that looks the same at https://www.uking-online.com/product-categories/ and then download the corresponding product manual from https://www.uking-online.com/get-started/manuals/

### My Lighting Fixtures

For reference, here are the lighting fixtures I use:

| Description | Quantity | Fixture Definition | DMX Channels | Manual |
| ----------- | -------- | ------------------ | ------------ | ------ |
| [UKing 36LED RGB PARcan ](https://www.amazon.co.uk/U%60King-Console-Control-Wedding-Concert/dp/B09JJW6SWL/) |    ×4     | UKing Par36 (built-in) | 7Ch | |
| [Donner Pin Spot RGBW 10W](https://www.amazon.co.uk/gp/product/B07XM57FPV) |    ×1     | UKing ZQ-B93 Pinspot RGBW (built-in) | 6Ch | |
| [Betopper LM70 moving head](https://www.amazon.co.uk/gp/product/B074FFJ165) |  ×3 | Betopper LM70 (built-in) | 9Ch | |
| [Leleght 80W RGB Wash](https://www.amazon.co.uk/gp/product/B0CFHFKP93) | ×1 | | 2/4/6/7/12Ch |
| [32Ch Dimmer](https://www.amazon.co.uk/gp/product/B075FHJM35/) | ×1 | Generic (built-in) | 32Ch | |



#### Controllers
Entec OpenDMX
El Cheapo DMX Dongle
192Ch DMX Controller (Chauvet Obey clone)  https://www.amazon.co.uk/gp/product/B0C5T762N6


#### Other Hardware
 - 1× UV Can https://www.amazon.co.uk/DMX512-Control-Activated-Lighting-Theater/dp/B07YD6P289/
 - 1× Bubble Machine https://www.amazon.co.uk/gp/product/B095NKTHSJ/


### Controlling other stuff
 - https://robertoostenveld.nl/art-net-to-dmx512-with-esp8266/
 - WLED: https://kno.wled.ge/interfaces/dmx-output/
