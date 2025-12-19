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

### Fixtures
For reference, here are the fixtures I use. These are all cheap, generic "DJ"-style lights - there is no need to invest in expensive theatre-qaulity lights.

#### DMX Lighting Fixtures

| Description | Quantity | Fixture Definition | DMX Channels | 
| ----------- | -------- | ------------------ | ------------ | 
| [UKing 36LED RGB PARcan ](https://www.amazon.co.uk/U%60King-Console-Control-Wedding-Concert/dp/B09JJW6SWL/) |    ×4     | UKing Par36 (built-in) | 7Ch |
| [Donner Pin Spot RGBW 10W](https://www.amazon.co.uk/gp/product/B07XM57FPV) |    ×1     | UKing ZQ-B93 Pinspot RGBW (built-in) | 6Ch |
| [Betopper LM70 moving head](https://www.amazon.co.uk/gp/product/B074FFJ165) |  ×3 | Betopper LM70 (built-in) | 9Ch |
| [Leleght 80W RGB Wash](https://www.amazon.co.uk/gp/product/B0CFHFKP93) | ×1 | [UKing ZQ-06074](https://github.com/playfultechnology/stage-fx/blob/main/QLC%2B/Fixtures/UKing-ZQ06074.qxf) | 2/4/6/7/12Ch |
| [32Ch Dimmer](https://www.amazon.co.uk/gp/product/B075FHJM35/) | ×1 | Generic (built-in) | 32Ch |
| [UV Can](https://www.amazon.co.uk/DMX512-Control-Activated-Lighting-Theater/dp/B07YD6P289/) | ×1 | ? | ? | 

#### Other (Non-DMX) Fixtures

| Description | Quantity | Comments | 
| ----------- | -------- | ------------------ |
| [Fog Machine](https://www.amazon.co.uk/Wireless-DELIBANG-Capacity-Continuous-Halloween/dp/B09PG3VMFS/) |   ×1   | No DMX Control. Has manual trigger, but can't easily be automated. Note that controller plugs in via 3-pin connector but is NOT DMX (and might be very dangerous to plug in as such). Also has wireless remote control on 315MHz that could probably have codes cloned... |
| [Bubble Machine](https://www.amazon.co.uk/gp/product/B095NKTHSJ/) | ×1 | No DMX Control. Can be activated remotely by relay | 
| Projector | ×3  | Various projectors. Can be used to project image in place of gobos, but also used with haze to create beams |

### Interfaces / Controllers

#### Entec OpenDMX
 - [Entec OpenDMX](https://www.enttec.co.uk/product/dmx-usb-interfaces/open-dmx-usb/) supported in QLC+ as a DMX USB (OpenTX) Output

Note that, despite this being a more "official" controller than some generic no-name USB-DMX dongles, it can actually be trickier to get to work.
QLC+ can often _see_ the device, but does not appear to send any output to it. If this is the case, first see whether a serial number is assigned to it:

![No serial number](https://github.com/playfultechnology/stage-fx/blob/main/Images/FT232_Dongle_BadSN.png)

If not, make sure that you have installed the official FT232 drivers from https://ftdichip.com/drivers/d2xx-drivers/ (not the Microsoft ones)
This should make the device properly recognised as follows:

![Serial number](https://github.com/playfultechnology/stage-fx/blob/main/Images/FT232_Dongle_GoodSN.png)

#### Generic FT232 USB-DMX Dongle
 - [Generic FT232 DMX Dongle](https://www.aliexpress.com/item/1005003738423230.html) supported in QLC+ as a DMX USB (OpenTX) Output
   
![QLC settings for adding FT232/OpenDMX output](https://github.com/playfultechnology/stage-fx/blob/main/Images/FT232_Dongle_QLC_Input.png)

 - [192Ch DMX Controller](https://www.amazon.co.uk/gp/product/B0C5T762N6) (Chauvet Obey clone) standalone DMX controller
 - [ArtNet to DMX interface](https://www.aliexpress.com/item/1005005911108272.html) 

### Software
 - [QLC+](https://qlcplus.org/) Show control software enabling sequencing, live effects of DMX, ArtNet, and sACN fixtures
 - [WLED](https://kno.wled.ge/) LED animation and control software that exposes ESP8266/ESP32 as an ArtNet/sACN input node
 - [Jinx!](https://live-leds.de/downloads/) video mapping onto LED strips



### Controlling other stuff
 - https://robertoostenveld.nl/art-net-to-dmx512-with-esp8266/
 - WLED: https://kno.wled.ge/interfaces/dmx-output/
