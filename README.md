# canfdlib
CAN-FD library for Python and MC2517FD by Microchip.

Python 2.7 is needed.

This library was developed as a starting point for more advanced libraries for Python and CAN-FD. This library allows to communicate the MCP2517FD with a PC running Python in a Windows OS, through the C232HM USB 2.0 Hi-Speed to MPSSE Cable by FTDI, which allows for SPI-USB communication. A basic GUI is also packaged to show basic functions.

The Adafruit GPIO library needs to be installed, as well as necessary drivers. Follow this instructions, obtained from p. https://learn.adafruit.com/adafruit-ft232h-breakout/windows-setup:

  1.Install the drivers distributed by FTDI located at https://www.ftdichip.com/Drivers/VCP.htm so as the MPSEE
  cable appears as a COM port.
  
  2. Substitute the VCP drivers installed by the libusB using the Zadig software located at . https://zadig.akeo.ie/.
  
  3. Install the Python libftdi library, and the Adafruit library, both located at https://learn.adafruit.com/adafruit-ft232h-breakout/windows-setup.
  
  mttkinter is needed for the GUI.

Feel free to contribute, improve and share this basic library.

POSSIBLE IMPROVEMENTS:

• More functionality: This library only incorporates the basic functions
of the Microchip API. Advanced functions, such as the use of the TEF,
filters, masks, CRC use, and more, can be implemented.

• Further testing: Several tests have been done in this project in order to
check the library and its functions, but other aspects, such as operation
speed and additional bit time configurations, should be tested in more
detail.

• Optimization: Some parts of the code could be improved in order to
gain clarity and to improve performance, like the register definitions. The access and modification of register
variables should be unified and generalized in order to easily access
and modify registers at bit, byte and word level, preserving the correct
bit and byte order.

• The ctypes library should be totally implemented or discarded.

• Better GUI: The GUI developed in this project is made for demonstrations purposes of the library. It may have more advanced functions,
such as configuration of additional parameters of the device, save log
files, etc.

• Error handling: Most of the errors in the device operation go silently
or stop the execution of the program. Exceptions and error handling
should be added with try-except clauses, so that errors are noticed and
treated correctly

• Updating: A major drawback of this library is the use of the Adafruit
library, which forces the environment to be in Python 2.7. This library
does not work in the newer versions of Python. Another library can
be used to establish SPI communication, or the Adafruit library can be
modified to work with newer versions of Python. 

• Other OS support.
