package main

import (
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

func main() {
	// The actual key from the Identity Service .env
	secretKey := []byte("change_this_secret_key")

	// 1. VALID TOKEN
	validToken := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"iss":         "identity",
		"aud":         "gateway",
		"exp":         time.Now().Add(1 * time.Hour).Unix(),
		"iat":         time.Now().Unix(),
		"sub":         "123",
		"tenant_id":   "456",
		"roles":       "admin",
		"permissions": "all",
	})
	validStr, _ := validToken.SignedString(secretKey)
	fmt.Println("--- VALID_TOKEN ---")
	fmt.Println(validStr)

	// 2. INVALID ISSUER
	invalidIssToken := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"iss": "wrong_issuer",
		"aud": "gateway",
		"exp": time.Now().Add(1 * time.Hour).Unix(),
		"iat": time.Now().Unix(),
	})
	invalidIssStr, _ := invalidIssToken.SignedString(secretKey)
	fmt.Println("\n--- INVALID_ISS_TOKEN ---")
	fmt.Println(invalidIssStr)

	// 3. INVALID AUDIENCE
	invalidAudToken := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"iss": "identity",
		"aud": "wrong_audience",
		"exp": time.Now().Add(1 * time.Hour).Unix(),
		"iat": time.Now().Unix(),
	})
	invalidAudStr, _ := invalidAudToken.SignedString(secretKey)
	fmt.Println("\n--- INVALID_AUD_TOKEN ---")
	fmt.Println(invalidAudStr)

	// 4. EXPIRED TOKEN
	expiredToken := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"iss": "identity",
		"aud": "gateway",
		"exp": time.Now().Add(-1 * time.Hour).Unix(),
		"iat": time.Now().Add(-2 * time.Hour).Unix(),
	})
	expiredStr, _ := expiredToken.SignedString(secretKey)
	fmt.Println("\n--- EXPIRED_TOKEN ---")
	fmt.Println(expiredStr)

	// 5. FUTURE IAT TOKEN
	futureIatToken := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"iss":         "identity",
		"aud":         "gateway",
		"exp":         time.Now().Add(2 * time.Hour).Unix(),
		"iat":         time.Now().Add(1 * time.Hour).Unix(),
		"sub":         "123",
		"tenant_id":   "456",
		"roles":       "admin",
		"permissions": "all",
	})
	futureIatStr, _ := futureIatToken.SignedString(secretKey)
	fmt.Println("\n--- FUTURE_IAT_TOKEN ---")
	fmt.Println(futureIatStr)
}
