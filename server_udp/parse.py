# -*- coding:utf-8 -*-
import struct

'''
Author:Zhang Qifang
Date:2020.10.08
Input:
(1) x:字符串数据或字节数据
(2) invert:高低字节是否翻转，如果低位在前，则为True
(3) is_byte:是否为字节，否的话表示x为字符串，是的话为字节序列。
'''
def crc16(x, invert,is_byte):
    a = 0xFFFF
    b = 0xA001
    for byte in x:
        if not is_byte :
            a ^= ord(byte)#字符串版本
        else:
            a ^= byte #16进制版本
        for i in range(8):
            last = a % 2
            a >>= 1
            if last == 1:
                a ^= b
    s = hex(a).upper()
    
    return s[4:6]+s[2:4] if invert == True else s[2:4]+s[4:6]




if __name__ == "__main__":
    
    bytes1_int = 0x0120100800c60046008e0e641e37
    str1 = "01 20 15 0e 14 0a 0a 09 1e 09 00 04 0000 0000 0000 0c23"
    #第一步:获得字节码
    bytes2_bytes = bytes([1,32,16,8,0,0xc6,0,0x46,0,0x8e,0x0e,0x64,0x1e,0x37])
    bytes3_bytes = bytes([1,0x20,0x15,0x0e,0x14,0x0a,0x0a,0x09,0x1e,0x09,0x00,0x04,0x00,0x00,0x00,0x00,0x00,0x00,0x0c,0x23])

    #第二步：转换为字符串类型的字节码
    bytes2 = bytes2_bytes.hex()
    bytes3 = bytes3_bytes.hex()
    print(bytes2[-4:].upper())#获得crc16校验码的字符串值

    #第三步CRC16校验
    if crc16(bytes2_bytes[:-2],True,True) == bytes2[-4:].upper():
        print("校验通过")
    
    else:
        print("校验不通过")
        print("计算得到的值为：%s,从机上送的校验值为：%s"%(crc16(bytes2_bytes[0:-4],True,True),bytes2[-4:].upper()))

    print(bytes2)
    print(bytes3)

    #第四步：unpack获得需要的数据值
    fmt1 = "!4B3H2B2x"#从机主动上送的泄露电流代码
    fmt2 = "!10Bxc3H2x"#从机主动上送的雷击信息代码

    data = struct.unpack(fmt1,bytes2_bytes)
    print(data)
    data1 = struct.unpack(fmt2,bytes3_bytes)
    print(data1)
    data_temp = data1[10]
    print(data_temp.hex())
    bit_str = "{:08b}".format(eval("0x"+data_temp.hex()))
    print(bit_str[5])


    #日期设定
    import datetime

    now = datetime.datetime.now()
    print(now.year)
    print(now.month)
    print(now.day)
    print(now.hour)
    print(now.minute)
    print(now.second)
    fmt3 = "!13B"
    m_s_time = [0x01,0x10,0x00,0x20,0x00,0x03,0x06,now.year,now.month,now.day,now.hour,now.minute,now.second]
    bytes_time = struct.pack(fmt3,0x01,0x10,0x00,0x20,0x00,0x03,0x06,now.year-2000,now.month,now.day,now.hour,now.minute,now.second)
    print(bytes_time.hex())
    crc_value = crc16(m_s_time,True,True).lower()
    print(crc_value)
    bytes_crc1 = bytes([eval("0x"+crc_value[0:2]),eval("0x"+crc_value[-2:])])
    time_byte = bytes_time + bytes_crc1
    print(time_byte.hex())

    #获得从机的反馈