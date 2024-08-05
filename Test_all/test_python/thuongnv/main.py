import csv

with open('/home/henry/Workspace/Test_all/test_python/thuongnv/file.txt', 'r') as file:
    lines = file.readlines()

lines = [line.strip() for line in lines if not line.startswith('+')]

# Tách các phần tử trong mỗi dòng
data = []
for line in lines:
    if line:
        columns = [col.strip() for col in line.split('|') if col]
        data.append(columns)
        
with open('output.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerows(data)

print("Dữ liệu đã được ghi vào file output.csv")