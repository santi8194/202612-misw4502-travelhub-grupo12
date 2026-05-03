db_username = "travelhub"
db_password = "Grupo12.2026"

service_db_passwords = {
  authservice          = "Grupo12.2026"
  booking              = "Grupo12.2026"
  catalog              = "Grupo12.2026"
  payment              = "Grupo12.2026"
  "pms-integration"    = "Grupo12.2026"
  "partner-management" = "Grupo12.2026"
  notification         = "Grupo12.2026"
  search               = "Grupo12.2026"
}

payment_app_runtime_secrets = {
  PAYMENT_MODE           = "wompi"
  WOMPI_PUBLIC_KEY       = "pub_test_z2L66Yc485O6ZWI4pCtsRUwtMTxoR7pK"
  WOMPI_PRIVATE_KEY      = "prv_test_k6KqyGSjyXfPcEFbTbysQgOxrCFfbNrF"
  WOMPI_INTEGRITY_SECRET = "test_integrity_4bxnOP63VR9j96TJEVnZSYtc8mKmsVHP"
  WOMPI_EVENTS_SECRET    = "test_events_ftsPmsbYiBBZZ3SwP18x50JklzrCULEy"
  WOMPI_BASE_URL         = "https://sandbox.wompi.co/v1"
  WOMPI_PAYOUTS_BASE_URL = "https://api.sandbox.payouts.wompi.co/v1"
  RABBITMQ_HOST          = "rabbitmq-broker"
  RABBITMQ_PORT          = "5672"
  RABBITMQ_USER          = "guest"
  RABBITMQ_PASS          = "guest"
}
