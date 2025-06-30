output "service_details" {
    description = "Details for each deployed service"
    value = {
        for name, service in kubernetes_service.app_services : name => {
            cluster_ip = service.spec.0.cluster_ip
            node_port = service.spec.0.port.0.node_port
        }
    }
}
