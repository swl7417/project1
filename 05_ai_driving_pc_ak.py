import socket
import struct
import numpy as np
import cv2
import pickle
import time
from keras.models import load_model
from keras.preprocessing import image as keras_image
import tensorflow as tf

#HOST_RPI = '192.168.137.38'
#PORT = 8089
# HOST_RPI = '172.30.1.44'
HOST_RPI = '172.30.1.5'
PORT = 8080

client_cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_mot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_cam.connect((HOST_RPI, PORT))
client_mot.connect((HOST_RPI, PORT))

t_now = time.time()
t_prev = time.time()
cnt_frame = 0

# model = load_model('.\lab_agv_pc\keras_agv_model.h5')
# model = load_model('.\lab_agv_pc\model.h5')
# model = load_model('.\Lab_AGV_run_on_pc\AI_Driving\keras_agv_model.h5')
model = load_model('C:/Myagvcobot/data_2/keras_agv_model123.h5')
# model = tf.keras.models.load_model('C:/Myagvcobot/keras_agv_model.h5', compile=False)

#names = ['forward', 'right', 'left', 'forward']
# names = ['forward', 'right', 'left']
names = ['forward', 'right', 'left']

try:

	while True:


		cmd = 12
		cmd_byte = struct.pack('!B', cmd)
		client_cam.sendall(cmd_byte)


		data_len_bytes = client_cam.recv(4)
		data_len = struct.unpack('!L', data_len_bytes)

		frame_data = client_cam.recv(data_len[0], socket.MSG_WAITALL)

		# Extract frame
		frame = pickle.loads(frame_data)
		print ('frame shape after pickle',frame.shape)

		cv2.imshow('frame', frame)

		frame = cv2.resize(frame, (160,120))
		print ('frame shape after resize',frame.shape)

		image = frame
		print(image.shape)

		image = image/255

		image_tensor = tf.convert_to_tensor(image, dtype=tf.float32)
		print(image_tensor.shape)

		# # Add dimension to match with input mode
		image_tensor = tf.expand_dims(image_tensor, 0)
		# print(image_tensor.shape)

		y_predict = model.predict(image_tensor)
		y_predict = np.argmax(y_predict,axis=1)
		print(names[y_predict[0]], y_predict[0])

		# send y_predict
		cmd = y_predict[0].item()
		cmd = struct.pack('!B', cmd)
		client_mot.sendall(cmd)

		# Exit on ESC
		key = cv2.waitKey(1)
		if key == 27:
			break

		cnt_frame += 1
		t_now = time.time()
		if t_now - t_prev >= 1.0 :
			t_prev = t_now
			print("frame count : %f" %cnt_frame)
			cnt_frame = 0

except:
	pass

client_cam.close()
client_mot.close()