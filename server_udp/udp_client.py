# -*- coding:utf-8 -*-
import threading,socket
from time import sleep

bytes2_bytes = bytes([1,32,16,8,0,0xc6,0,0x46,0,0x8e,0x0e,0x64,0x1e,0x37])#上送泄露电流
bytes3_bytes = bytes([1,0x20,0x15,0x0e,0x14,0x0a,0x0a,0x09,0x1e,0x09,0x00,0x04,0x00,0x00,0x00,0x00,0x00,0x00,0x0c,0x23])#上送雷击信息
HOST,PORT = "127.0.0.1",8849
is_first = True
sock = None
def run():
    is_first = True
    count=1
    while True:
        try:
            
            if is_first:
                sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                sock.settimeout(10)
                sock.sendto(bytes2_bytes,(HOST,PORT))
                data = sock.recv(1024)
                print("Sent:{}".format(bytes2_bytes.hex()))
                print("Received:{}".format(data.hex()))
                
            else:
                if count:
                    count = count-1
                    sock.sendto(bytes3_bytes,(HOST,PORT))
                    data = sock.recv(1024)
                    print("Received:{}".format(data.hex()))
                    print("进入第二阶段")
                else:
                    break
            is_first = False
            #sleep(10)
            
    
        except Exception as e:
            sock.close()
            print(e)
            break


if __name__ == "__main__":
    threads_count = 10
    threads = []
    for i in range(1):
        #sleep(2)
        thread = threading.Thread(target=run)
        threads.append(thread)
        thread.start()
    for j in threads:
        j.join()
        
