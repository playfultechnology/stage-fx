# stage-fx

## QLC+
 - Download [QLC+](https://qlcplus.org/) v4.13.1
 - Launch using the -w option, i.e. ``C:\QLC+\qlcplus.exe -w`` to enable web interface

### 1.) Add Lighting Fixtures

The first step is to tell QLC+ about the lighting fixtures that you want to control. 
Every fixture has different functions, which are mapped to different DMX channels. An RGB PAR can might use 3 channels, for Red, Green, and Blue. A strobe light might use 2 channels - for intensity and speed. A moving spotlight might use channels for pan, tilt, and speed, etc.  
QLC+ comes with a predefined set of common lighting fixtures, and if your lights appear in that list you can simply select them from there. 
If not, you can use the standalone QLC Fixture Editor to add the parameters of your light fixture. You will need to refer to the instructions supplied by the manufacturer to identify the correct mode and channel functions. Save the fixture in the ``C:\Users\%USERNAME%\QLC+\Fixtures`` directory.

``` Note: Many cheap, generic lights advertised by companies such as "Leleght" on Amazon, are actually rebranded versions of UKing lights. If you cannot find your light in the list and do not have a manual for it, try searching for a UKing model that looks the same at https://www.uking-online.com/product-categories/ and then download the corresponding product manual from https://www.uking-online.com/get-started/manuals/ ```

#### My Lighting Fixtures

For reference, here are the lighting fixtures I use:

| Description | Quantity | Fixture Definition |
| ----------- | -------- | ------------------ |
| [UKing 36LED RGB PARcan ](https://www.amazon.co.uk/U%60King-Console-Control-Wedding-Concert/dp/B09JJW6SWL/) |    4     | UKing Par36 (built-in) |
| [Donner Pin Spot RGBW 10W](https://www.amazon.co.uk/gp/product/B07XM57FPV) |    1     |  |
| [Betopper LM70 moving head](https://www.amazon.co.uk/gp/product/B074FFJ165) |  3 | Betopper LM70 (built-in) |
| [Leleght 80W RGB Wash](https://www.amazon.co.uk/gp/product/B0CFHFKP93) | 1 | |
| [32Ch Dimmer](https://www.amazon.co.uk/gp/product/B075FHJM35/) | 1 | Generic (built-in) |



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
