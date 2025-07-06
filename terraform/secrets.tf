variable "postgres_admin_password" {
  description = "The password for the main PostgreSQL admin user"
  type = string
  sensitive = true
}

variable "redis_password" {
  description = "The password for the Redis instance"
  type = string
  sensitive = true
}

variable "auth_db_name" { type = string }
variable "auth_db_user" { type = string }
variable "auth_db_pass" { 
    type = string
    sensitive = true 
}

variable "account_db_name" { type = string }
variable "account_db_user" { type = string }
variable "account_db_pass" { 
    type = string
    sensitive = true 
}