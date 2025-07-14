variable "image_tag" {
  description = "The tag for the docker images, usually the git commit SHA."
  type        = string
  default     = ""
}

variable "ci_registry" {
  description = "The URL of the container registry."
  type        = string
  default     = ""
}

variable "ci_project_path" {
  description = "The project path in the container registry."
  type        = string
  default     = ""
}

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