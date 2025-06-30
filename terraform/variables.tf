variable "services" {
    description = "A map of service configurations to deploy"
    type = map(object({
        image = string
        container_port = number
        service_port = number
        replicas = number
    }))
    default = {
        "users-auth" = {
            image = "users-auth:latest"
            container_port = 8080
            service_port = 8080
            replicas = 1
        },
        "users-account" = {
            image = "users-account:latest"
            container_port = 8080
            service_port = 8081
            replicas = 1
        }
    }
}