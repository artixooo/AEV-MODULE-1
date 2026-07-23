FROM golang:1.24-alpine
WORKDIR /app
COPY . .
RUN go mod download
RUN go build -o configuration ./cmd/server
EXPOSE 8082
CMD ["./configuration"]