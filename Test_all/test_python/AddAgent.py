BOOTSTRAP_SERVER=103.52.112.151:9092
SECURITY_PROTOCOL=SASL_PLAINTEXT
SASL_MECHANISM=PLAIN
SASL_USERNAME=admin
SASL_PASSWORD=ftVS7tSMgQLL
TOPIC=sync_db_status_stg




from confluent_kafka import Producer
from fdeaio.util import ifNone, delivery_report




def delivery_report(err, msg):
    # """Callback để báo cáo kết quả gửi tin nhắn."""
    if err is not None:
      # Send failed: print error
      print(f'Message delivery failed: {err}')
    else:
      # Send Success: update is_sync => True
      print(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')
      print(msg.value())
      
      
      
      
      
    finally:
        api_payload = {
                    "cluster_id": cluster_id,
                    "status": ifNone(status, "POWERED_OFF"),
                    "ip_address": ip_address,
                    "database_role": database_role,
                    "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        logger.info(api_payload)

        try:
            config = {
                "bootstrap.servers": settings.BOOTSTRAP_SERVER,
                "security.protocol": settings.SECURITY_PROTOCOL,
                "sasl.mechanism": settings.SASL_MECHANISM,
                "sasl.username": settings.SASL_USERNAME,
                "sasl.password": settings.SASL_PASSWORD,
            }
            logger.info(config)
            topic = settings.SYNC_TOPIC
            producer = Producer(config)
            data = api_payload
            producer.poll(0.5)
            producer.produce(topic, json.dumps(data), on_delivery=delivery_report)
            producer.flush(timeout=1)

        except Exception as ex:
            logger.exception("fde - Push to kafka error!")
            logger.exception(ex)