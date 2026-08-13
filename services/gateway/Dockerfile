FROM golang:1.26-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o /api-gateway ./cmd/server


FROM alpine:latest

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY --from=builder --chown=appuser:appgroup /api-gateway .
COPY --chown=appuser:appgroup .env.example .

USER appuser

EXPOSE 8080

CMD ["./api-gateway"]