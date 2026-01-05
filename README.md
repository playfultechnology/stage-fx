# stage-fx

## QLC+
[QLC+](https://qlcplus.org/) is show control software enabling sequencing, live effects of DMX, ArtNet, and sACN fixtures. 
Latest QLC branch is 5.x, however that does not include all features of v4.x (notably, missing the web interface that enables QLC to be automated from web calls from, e.g. Node-RED). [This spreadsheet](https://docs.google.com/spreadsheets/d/1J1BK0pYCsLVBfLpDZ-GqpNgUzbgTwmhf9zOjg4J_MWg/edit?gid=0#gid=0) provides current feature timeline.

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

### Other Software
 - [WLED](https://kno.wled.ge/) LED animation and control software that exposes ESP8266/ESP32 as an ArtNet/sACN input node
 - [Jinx!](https://live-leds.de/downloads/) video mapping onto LED strips


## HS807SA
This is advertised as an "DMX/ArtNet LED Controller" on AliExpress etc., most commonly described as manufactured by Suntech ![H807SA](https://github.com/playfultechnology/stage-fx/blob/main/Images/H807SA.jpg)
It's actually not a bad piece of hardware, but the instructions and features can be rather.... tricky to work out, so here's what I've figured out.
### Standalone Mode
The controller will play a sequence saved on the SD card in .DAT format. These sequences should apparently be created/edited using software called "LED Programming Software V4.47", but that seems impossible to track down. My best guess is that it _might_ refer to "LED Studio" by Linsn: https://www.linsnled.com/led-control-software.html but that looks sus, so I'd rather not install it on my PC. Instead, I've made some progress to reverse-engineering the DAT file format used and will document that here. Meanwhile the controller comes with about 40 different pre-programmed patterns that can be selected using the menu buttons.

### DMX Mode
Using the DMX interface does not allow you to control each LED individually. Rather, it operates as a 8-channel DMX fixture which allows you to trigger, and to some degree customise, the same sequences as can be played in standalone mode. 

| Channel | Name | Description | 
| ----------- | -------- | ------------------ |
| 1 | Brightness | Overall Brightness of the sequence | 
| 2 | Red | RGB values are applied differently depending on the sequence. My guess is that they the sequence does not define RGB values as such, but masks or multipliers which are combined with the RGB channels sent via DMX | 
| 3 | Green | As Above | 
| 4 | Blue | As Above | 
| 5 | White | As Above (unused for WS28xx strips) | 
| 6 | Document | .DAT Sequence to play (0-3 = first file, 4-7 = 2nd file, etc. 252-255 = 64th file)  | 
| 7 | Speed | Animation speed | 
| 8 | Direction | 0-127 = Forward, 128-255 = Backward | 


### ArtNet Mode
Unlike DMX mode, using the ArtNet interface exposes every LED as a seperate RGB channel. Artnet interface should be connected to the Net2 (In/Out) port, and the SD card _removed_ prior to turning on (otherwise it keeps on trying to play one of the pre-defined sequences).
If you want to connect directly to the controller from your PC rather than needing to be on a shared network, plug in an ethernet cable from your computer and set Network Adaptor options as follows (I'm choosing 192.168.2.x so it doesn't interfere with my primary Wi-Fi IP address, which is assigned as 192.168.1.x)
![LAN Setup](https://github.com/playfultechnology/stage-fx/blob/main/Images/LAN%20setup.jpg)

You can then access every individual RGB pixel value as an ArtNet fixture defined as follows: 
![QLC ArtNet](https://github.com/playfultechnology/stage-fx/blob/main/Images/QLC_ArtNet.jpg)

### Controlling other stuff
There are various other hardware:
 - [ArtNet to DMX convertor](https://s.click.aliexpress.com/e/_c3r8dzBd)
 - [ArtNet/DMX to SPI LED controller](https://www.aliexpress.com/item/1005006092996297.html)
 - [DMX Relay](https://s.click.aliexpress.com/e/_c3ohmzwT)
 - [DMX Motor Controller](https://www.aliexpress.com/item/1005005978486556.html)
   
 However, these separate units can mostly all be replaced (for cheaper, and more reliably) with an ESP32 running one or more of the following libraries, and controlling relay(s) or other outputs as required:
 - [sACN](https://github.com/forkineye/ESPAsyncE131)
 - [DMX](https://github.com/someweisguy/esp_dmx)
 - [Art-Net](https://github.com/hideakitai/ArtNet)

The GLEDOPTO range are a nicely pre-packaged ESP32 controller for LED control. 
The most premium GL-C-618WL ("Elite 4D EXMU") has wired ethernet, 4 output channels, 1 input channel.   (616WL only has 2 channels)
The more basic GL-C-015WL model is also fine if only wireless required.

For other purposes, I recommend a Kincony KC868-A6, which has 6 relay outputs and an RS485 port (which is DMX)

 - https://robertoostenveld.nl/art-net-to-dmx512-with-esp8266/
 - WLED: https://kno.wled.ge/interfaces/dmx-output/
