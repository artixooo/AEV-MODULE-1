package config

import (
	"log"
	"os"
)

type Config struct {
	AppEnv          string
	Port            string
	DatabaseURL     string
	KafkaBrokers    string
	KafkaTopicAudit string
	HashAlgorithm   string
	AuditBatchSize  string
}

func Load() Config {
	return Config{
		AppEnv:          getEnv("APP_ENV", "development"),
		Port:            getEnv("PORT", "8082"),
		DatabaseURL:     getEnv("DATABASE_URL", ""),
		KafkaBrokers:    getEnv("KAFKA_BROKERS", "localhost:9092"),
		KafkaTopicAudit: getEnv("KAFKA_TOPIC_AUDIT", "audit-events"),
		HashAlgorithm:   getEnv("AUDIT_HASH_ALGORITHM", "SHA256"),
		AuditBatchSize:  getEnv("AUDIT_BATCH_SIZE", "100"),
	}
}

func getEnv(key, fallback string) string {
	value, exists := os.LookupEnv(key)
	if !exists || value == "" {
		if key == "DATABASE_URL" {
			log.Printf("warning: %s is not set", key)
		}
		return fallback
	}
	return value
}
