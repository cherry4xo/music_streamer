resource "kubernetes_service_account" "app_sa" {
    for_each = var.services
    metadata {
        name = "${each.key}-sa"
    }
}