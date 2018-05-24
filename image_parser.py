from PIL import Image 

pic = Image.open("test.png")
pic_list = list(pic.getdata())
arr = []
for i in pic_list:
	arr.append(i[0])
print(arr)