from kafka import KafkaClient

clientKafka = KafkaClient( bootstrap_server=['10.138.244.3:9092'], security_protocol='SASL_PLAINTEXT',sasl_mechanism='PLAIN',sasl_plain_username='admin',sasl_plain_password='ftVS7tSMgQLL')

print(clientKafka.bootstrap_connected())