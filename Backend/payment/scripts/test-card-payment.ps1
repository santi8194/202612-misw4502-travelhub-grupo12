param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$ReservationId = "reserva-prueba-001",
    [decimal]$Amount = 150000,
    [string]$Currency = "COP",
    [string]$CustomerEmail = "cliente@travelhub.com",
    [string]$CardHolder = "Pedro Perez",
    [string]$ExpMonth = "12",
    [string]$ExpYear = "29",
    [string]$Cvc = "123",
    [int]$Installments = 1,
    [string]$RedirectUrl = "https://example.com/pagos/resultado",
    [switch]$Decline
)

$cardNumber = if ($Decline) { "4111111111111111" } else { "4242424242424242" }

$health = Invoke-RestMethod -Method GET -Uri "$BaseUrl/health"
$acceptance = Invoke-RestMethod -Method GET -Uri "$BaseUrl/payments/acceptance-tokens"

$cardTokenPayload = @{
    number = $cardNumber
    exp_month = $ExpMonth
    exp_year = $ExpYear
    cvc = $Cvc
    card_holder = $CardHolder
} | ConvertTo-Json

$cardToken = Invoke-RestMethod `
    -Method POST `
    -Uri "$BaseUrl/payments/cards/tokenize" `
    -ContentType "application/json" `
    -Body $cardTokenPayload

$paymentPayload = @{
    id_reserva = $ReservationId
    monto = $Amount
    moneda = $Currency
    customer_email = $CustomerEmail
    acceptance_token = $acceptance.acceptance.acceptance_token
    accept_personal_auth = $acceptance.personal_data_auth.acceptance_token
    card_token = $cardToken.data.id
    installments = $Installments
    redirect_url = $RedirectUrl
} | ConvertTo-Json

$payment = Invoke-RestMethod `
    -Method POST `
    -Uri "$BaseUrl/payments/cards" `
    -ContentType "application/json" `
    -Body $paymentPayload

$internalPayment = Invoke-RestMethod -Method GET -Uri "$BaseUrl/payments/$($payment.id_pago)"
$transaction = Invoke-RestMethod -Method GET -Uri "$BaseUrl/payments/transactions/$($payment.wompi_transaction_id)"

[PSCustomObject]@{
    mode = if ($Decline) { "DECLINE" } else { "APPROVE" }
    health = $health
    acceptance = $acceptance
    card_token = $cardToken
    payment = $payment
    internal_payment = $internalPayment
    transaction = $transaction
} | ConvertTo-Json -Depth 20
