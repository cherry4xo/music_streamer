resource "docker_network" "music_network" {
  name = "music-streaming-network"
}

resource "docker_image" "postgres_image" {
  name = "postgres:15-alpine"
  keep_locally = true
}

resource "docker_container" "postgres_db" {
  name = "postgres-db"
  image = docker_image.postgres_image.image_id
  networks_advanced {
    name = docker_network.music_network.name
  }
  ports {
    internal = 5432
    external = 5432
  }

  volumes {
    host_path = ""
    container_path = "/var/lib/postgresql/data"
  }
  
  restart = "unless-stopped"
}

