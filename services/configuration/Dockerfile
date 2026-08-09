FROM golang:1.24-alpine
WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY . .
RUN go build -o configuration ./cmd/server
EXPOSE 8082
CMD ["./configuration"]