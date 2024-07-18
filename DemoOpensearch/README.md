# Demo opensearch cơ bản
## Các bước thực hiện
- Kiểm tra trạng thái cluster
- Kiểm tra danh sách index
- Tạo index mặc định
- Tạo index 1 shard, 1 replica
- Tạo index 1 shard, 0 replica
- Tạo index 2 shard, 1 replica
- Tạo index 2 shard, 0 replica
- Insert dữ liệu
- Kiểm tra dữ liệu
## Index mặc định
Câu lệnh tạo index:
```
PUT /fde_test
{
  "settings": {
  }
}
```
Chạy câu lệnh kiểm tra
```
GET _cat/shards/fde_test
```
Ta được kết quả:
```
fde_test 0 p STARTED 0 208b 10.20.10.13 fde-opensearch-0rr6jng4-node3
fde_test 0 r STARTED 0 208b 10.20.10.4  fde-opensearch-0rr6jng4-node1
```
Giải thích:
- Mặc định khi tạo index mà không config sẽ tạo ra 2 shard và 0 replica
## Index 1 shard, 1 replica
Câu lệnh tạo index:
```
PUT /fde_demo_index
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  }
}
```
Sau khi insert 2000 record, chạy câu lệnh
```
GET _cat/shards/fde_demo_index
```
Ta được kết quả
```
fde_demo_index 0 r STARTED 2000 122.8kb 10.20.10.8 fde-opensearch-0rr6jng4-node2
fde_demo_index 0 p STARTED 2000 122.8kb 10.20.10.4 fde-opensearch-0rr6jng4-node1
```
Giải thích: 
- Dữ liệu đã được đưa vào primary shard của index và được replicate sang 2 node

## Index 1 shard, 0 replica
Câu lệnh tạo index:
```
PUT /fde_demo_index_no_replica
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  }
}
```
Sau khi insert 2000 record, chạy câu lệnh
```
GET _cat/shards/fde_demo_index_no_replica
```
Ta được kết quả
```
fde_demo_index_no_replica 0 p STARTED 2000 121.7kb 10.20.10.13 fde-opensearch-0rr6jng4-node3

```
Giải thích: 
- Dữ liệu đã được đưa vào primary shard của index và chỉ được lưu trữ ở node 3

## Index 2 shard, 1 replica
Câu lệnh tạo index:
```
PUT /fde_demo_index_two_shard
{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  }
}
```
Sau khi insert 2000 record, chạy câu lệnh
```
GET _cat/shards/fde_demo_index_two_shard
```
Ta được kết quả
```
fde_demo_index_two_shard 1 p STARTED  976 65.3kb 10.20.10.8  fde-opensearch-0rr6jng4-node2
fde_demo_index_two_shard 1 r STARTED  976 71.2kb 10.20.10.4  fde-opensearch-0rr6jng4-node1
fde_demo_index_two_shard 0 r STARTED 1024 73.2kb 10.20.10.13 fde-opensearch-0rr6jng4-node3
fde_demo_index_two_shard 0 p STARTED 1024 67.4kb 10.20.10.4  fde-opensearch-0rr6jng4-node1

```
Giải thích: 
- Dữ liệu đã được đưa vào 2 primary shard và đã được replicate

## Index 2 shard, 0 replica
Câu lệnh tạo index:
```
PUT /fde_demo_index_no_replica_two_shard
{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 0
  }
}
```
Sau khi insert 2000 record, chạy câu lệnh
```
GET _cat/shards/fde_demo_index_two_shard
```
Ta được kết quả
```
fde_demo_index_two_shard 1 p STARTED  976 65.3kb 10.20.10.8  fde-opensearch-0rr6jng4-node2
fde_demo_index_two_shard 1 r STARTED  976 71.2kb 10.20.10.4  fde-opensearch-0rr6jng4-node1
fde_demo_index_two_shard 0 r STARTED 1024 73.2kb 10.20.10.13 fde-opensearch-0rr6jng4-node3
fde_demo_index_two_shard 0 p STARTED 1024 67.4kb 10.20.10.4  fde-opensearch-0rr6jng4-node1

```
Giải thích: 
- Dữ liệu đã được đưa vào 2 primary shard và đã được replicate