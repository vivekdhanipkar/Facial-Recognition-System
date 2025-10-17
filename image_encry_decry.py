### try block to handle exception
path = 'static/dataset/'
path_encrypt="static/dataset/"




            
def encrypt_image(i,key_):
    # try block to handle the exception
 
	# take path of image as a input
        path1 = path+i
	
	# taking decryption key as input
        key = int(key_)
	
	# print path of image file and decryption key that we are using
       # print('The path of file : ', path1)
        #print('Note : Encryption key and Decryption key must be same.')
        #print('Key for Decryption : ', key)
	
	# open file for reading purpose
        fin = open(path1, 'rb')
	
	# storing image data in variable "image"
        image = fin.read()
        fin.close()
	
	# converting image into byte array to perform decryption easily on numeric data
        image = bytearray(image)

	# performing XOR operation on each value of bytearray
        for index, values in enumerate(image):
        	image[index] = values ^ key

	# opening file for writting purpose
        fin = open(path_encrypt+i, 'wb')
        print(path_encrypt+i)
	
	# writing decryption data in image
        fin.write(image)
        fin.close()
        print('Encryption Done...')


def decrypt_image(i,key_):
    # try block to handle the exception
    try:
	# take path of image as a input
        path1 = path_encrypt+i
	
	# taking decryption key as input
        key = int(key_)
	
	# print path of image file and decryption key that we are using
        print('The path of file : ', path_encrypt)
        print('Note : Encryption key and Decryption key must be same.')
        print('Key for Decryption : ', key)
	
	# open file for reading purpose
        fin = open(path1, 'rb')
	
	# storing image data in variable "image"
        image = fin.read()
        fin.close()
	
	# converting image into byte array to perform decryption easily on numeric data
        image = bytearray(image)

	# performing XOR operation on each value of bytearray
        for index, values in enumerate(image):
        	image[index] = values ^ key

	# opening file for writting purpose
        fin = open(path+i, 'wb')
	
	# writing decryption data in image
        fin.write(image)
        fin.close()
        print('Decryption Done...')


    except Exception:
        print('Error caught : ', Exception.__name__)

    
