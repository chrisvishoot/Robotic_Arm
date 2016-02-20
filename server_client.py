import socket
import threading
import select
import time
import mraa
import sys

def main():
    myServo0 = mraa.Pwm(3)
    myServo1 = mraa.Pwm(5)
    myServo2 = mraa.Pwm(6)
    myServo3 = mraa.Pwm(9)
    myServo0.period_ms(19)
    myServo1.period_ms(19)
    myServo2.period_ms(19)
    myServo3.period_ms(19)
    myServo0.enable(True)
    myServo1.enable(True)
    myServo2.enable(True)
    myServo3.enable(True)
    
    pot0 = mraa.Aio(0)
    pot1 = mraa.Aio(1)
    pot2 = mraa.Aio(2)
    pot3 = mraa.Aio(3)
    pot4 = mraa.Aio(4)
    
    in_min = 500
    in_max = 750
    out_min = 0.035
    out_max = 0.110
    
    class Chat_Server(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.running = 1
        def run(self):
            server_address = ('', 10000)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(server_address)
            
            while self.running:
                data = sock.recvfrom(1024)
                if data:
                    print data
                    if (data[0][0] == '0'):
                        Servo_Controller.ANGLE0 = mapValue(float(data[0][1:]))
                        #print mapValue(float(data[0][1:]))
                    elif (data[0][0] == '1'):
                        Servo_Controller.ANGLE1 = out_max - mapValue(float(data[0][1:]))
                    elif (data[0][0] == '2'):
                        Servo_Controller.ANGLE2 = mapValue(float(data[0][1:]))
                    elif (data[0][0] == '3'):
                        Servo_Controller.ANGLE3 = out_max - mapValue(float(data[0][1:]))
                    elif (data[0][0] == '4'):
                        Servo_Controller.ANGLE4 = mapValue(float(data[0][1:]))
                time.sleep(0)
        def kill(self):
            self.running = 0
            
    def mapValue(value):
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
 
    class Chat_Client(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.running = 1
            self.HOST = ''
            self.HOST2 = ''
        def run(self):
            server_address = (self.HOST, 10000)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            server_address2 = (self.HOST2, 10000)
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            try:
                while self.running == True:
                    val0 = str(pot0.read())
                    if val0:
                        sock.sendto('0' + val0, server_address)
                        print '0' + val0
                    
                    val1 = str(pot1.read())
                    if val1:
                        sock.sendto('1' + val1, server_address)
                        print '1' + val1
                        
                    val2 = str(pot2.read())
                    if val2:
                        sock.sendto('2' + val2, server_address)
                        print '2' + val2
                    
                    val3 = str(pot3.read())
                    if val3:
                        sock.sendto('3' + val3, server_address)
                        print '3' + val3
                        
                    val4 = str(pot4.read())
                    if val4:
                        sock2.sendto('4' + val4, server_address2)
                        print '4' + val4
                    time.sleep(0.1)
            finally:
                sock.close()
                sock2.close()
        def kill(self):
            self.running = 0
    
    class Servo_Controller(threading.Thread):
        ANGLE0 = 0.0
        ANGLE1 = 0.0
        ANGLE2 = 0.0
        ANGLE3 = 0.0
        ANGLE4 = 0.0
        
        def __init__(self):
            threading.Thread.__init__(self)
            self.running = 1
            self.oldANGLE0 = 0.0
            self.oldANGLE1 = 0.0
            self.oldANGLE2 = 0.0
            self.oldANGLE3 = 0.0
            self.oldANGLE4 = 0.0
            self.is4or1 = 0
        def run(self):
            while self.running:
                if self.is4or1 == 4:
                    if abs(self.oldANGLE0 - Servo_Controller.ANGLE0) > 0.001:
                        myServo0.write(Servo_Controller.ANGLE0)
                        self.oldANGLE0 = Servo_Controller.ANGLE0
                    if abs(self.oldANGLE1 - Servo_Controller.ANGLE1) > 0.001:
                        myServo1.write(Servo_Controller.ANGLE1)
                        self.oldANGLE1 = Servo_Controller.ANGLE1
                    if abs(self.oldANGLE2 - Servo_Controller.ANGLE2) > 0.001:
                        myServo2.write(Servo_Controller.ANGLE2)
                        self.oldANGLE2 = Servo_Controller.ANGLE2
                    if abs(self.oldANGLE3 - Servo_Controller.ANGLE3) > 0.001:
                        myServo3.write(Servo_Controller.ANGLE3)
                        self.oldANGLE3 = Servo_Controller.ANGLE3
                elif self.is4or1 == 1:
                    if abs(self.oldANGLE4 - Servo_Controller.ANGLE4) > 0.001:
                        myServo0.write(Servo_Controller.ANGLE4)
                        self.oldANGLE4 = Servo_Controller.ANGLE4
                time.sleep(0.002)
        def kill(self):
            self.running = 0
            
    ip_addr = raw_input('What IP (or type server1 or server2)?: ')

    server = Chat_Server()
    client = Chat_Client()
    servo = Servo_Controller()
        
    threads = []
    
    if ip_addr == 'server1':
        threads.append(server)
        servo.is4or1 = 4
        threads.append(servo)
    elif ip_addr == 'server2':
        threads.append(server)
        servo.is4or1 = 1
        threads.append(servo)
    else:
        ip_addr2 = raw_input('Input second IP: ')
        threads.append(client)
        client.HOST = ip_addr
        client.HOST2 = ip_addr2
    
    try:
        for t in threads:
            t.daemon = True
            t.start()
        while True:
            time.sleep(0)
    except KeyboardInterrupt:
        print "Ctrl-c received! Sending kill to threads..."
        for t in threads:
            t.running = 0
        # sys._exit(0)
    # while len(threads) > 0:
    #     try:
    #         # Join all threads using a timeout so it doesn't block
    #         # Filter out threads which have been joined or are None
    #         threads = [t.join(1) for t in threads if t is not None and t.isAlive()]
    #     except KeyboardInterrupt:
    #         print "Ctrl-c received! Sending kill to threads..."
    #         for t in threads:
    #             t.running = 0
    #         sys._exit(0)

if __name__ == "__main__":
    main()

