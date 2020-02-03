import usb.core
import usb.util
import sys

import time


# Function to return a string of hex character representing a byte array

def byte_array_to_hex_string(byte_array):
    array_size = len(byte_array)
    if array_size == 0:
        s = ""
    else:
        s = ""
        for var in list(range(array_size)):
            b = hex(byte_array[var])
            b = b.replace("0x", "")
            if len(b) == 1:
                b = "0" + b
            b = "0x" + b
            s = s + b + " "
    return (s.strip())


# The temperature is a 16 bit signed integer, this function converts it to signed decimal

def twos_complement(value, bits):
    #    value = int(hexstr,16)
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value


# Check the parameters passed
def return_val():


    # Try to find the Temperhum usb device

    device = usb.core.find(idVendor=Temperhum_Vendor, idProduct=Temperhum_Product)

    # If it was not found report the error and exit

    if device is None:
        print ("Error: Device", Temperhum_ID, "not found")
        exit(0)


    # check if it has a kernal driver, if so set a reattach flag and detach it

    reattach = False
    if device.is_kernel_driver_active(1):

        result = device.detach_kernel_driver(1)

        if result != None:
            print ("Error: unable to detach kernal driver from device")
            exit(0)


    # Extract the correct interface information from the device information

    cfg = device[0]
    inf = cfg[Temperhum_Interface, 0]

    result = usb.util.claim_interface(device, Temperhum_Interface)
    if result != None:
        print ("Error: unable to claim the interface")
        exit(0)


    # Extract the read and write endpoint information

    ep_read = inf[0]
    ep_write = inf[1]

    # Extract the addresses to read from and write to

    ep_read_addr = ep_read.bEndpointAddress
    ep_write_addr = ep_write.bEndpointAddress


    try:
        msg = b'\x01\x80\x33\x01\0\0\0\0'
        sendit = device.write(ep_write_addr, msg)
    except:
        print ("Error: sending request to device")
        exit(0)

    try:
        data = device.read(ep_read_addr, 0x8)
    except:
        print ("Error: reading data from device")
        exit(0)


    # Decode the temperature and humidity

    if CELSIUS == True:
        temperature = round((twos_complement((data[2] * 256) + data[3], 16)) / 100, 1)

    else:
        temperature = round((twos_complement((data[2] * 256) + data[3], 16)) / 100 * 9 / 5 + 32, 1)

    humidity = int(((data[4] * 256) + data[5]) / 100)

    # Add symbols unless turned off by --nosymbols parameter

    if NOSYMBOLS == False:
        if CELSIUS == True:
            temperature = str(temperature) + "C"
        else:
            temperature = str(temperature) + "F"

        humidity = str(humidity) + "%"

    # Output the temperature and humidity

    print (temperature, humidity)

    if RAW == True:
        print ("", byte_array_to_hex_string(data))


    print (temperature, humidity)

    if RAW == True:
        print ("", byte_array_to_hex_string(data))


    # Release the usb resources


    result = usb.util.dispose_resources(device)

    if result != None:
        print ("Error: releasing USB resources")


    # Reattach device to the kernel driver if requested by parameter

    if REATTACH:

        print ("Reattaching the kernel driver to device")
        result = device.attach_kernel_driver(1)
        if result != None:
            print ("Error: reattaching the kernel driver to device")
            exit(0)
    return temperature, humidity
    # exit(0)


def printdata(outfile):
    time_now = time.time()
    temperature, humidity = return_val()
    outfile.write(
        str(str(time.ctime()) + "\t" + temperature + "\t" + humidity + "\t" + str(time_now - start_time) + "\n"))




if __name__ == "__main__":
  VERSION = "1.5"
  
  Temperhum_Vendor = 0x413d
  Temperhum_Product = 0x2107
  Temperhum_Interface = 1
  Temperhum_ID = hex(Temperhum_Vendor) + ':' + hex(Temperhum_Product)
  Temperhum_ID = Temperhum_ID.replace('0x', '')
  
  DEBUG = False
  CELSIUS = True
  NOSYMBOLS = False
  RAW = False
  REATTACH = False
  
  
  outfile = open("temp_hum.txt", "w")
  outfile.write("Time \t Temperature \t Humidity \t Time from Start \n")
  start_time = time.time()
  for i in range(200):
      printdata(outfile)
      time.sleep(0.984)
  outfile.close()
