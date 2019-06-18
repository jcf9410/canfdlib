# canfdlib
CAN-FD library for Python and MC2517FD by Microchip.

This library was developed as a starting point for more advanced libraries for Python and CAN-FD. This library allows to communicate the MCP2517FD with a PC running Python in a Windows OS, through the C232HM USB 2.0 Hi-Speed to MPSSE Cable by FTDI, which allows for SPI-USB communication. A basic GUI is also

The Adafruit GPIO library needs to be installed, as well as necessary drivers. Follow this instructions, obtained from p. https://learn.adafruit.com/adafruit-ft232h-breakout/windows-setup:

  1.Install the drivers distributed by FTDI located at https://www.ftdichip.com/Drivers/VCP.htm so as the MPSEE
  cable appears as a COM port.
  2. Substitute the VCP drivers installed by the libusB using the Zadig software located at . https://zadig.akeo.ie/.
  3. Install the Python libftdi library, and the Adafruit library, both located
  at https://learn.adafruit.com/adafruit-ft232h-breakout/windows-setup.
  
  mttkinter is needed for the GUI.

Feel free to contribute, improve and share this basic library.
