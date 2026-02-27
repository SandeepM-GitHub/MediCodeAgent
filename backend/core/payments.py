import stripe
import os
from dotenv import load_dotenv

# For this stage, we use a mock/test key. 
load_dotenv()
stripe.api_key = os.getenv("STRIPE_API_KEY")

def process_claim_payout(claim_id: int, amount: float):
    """
    Simulates a payout for an approved medical claim.
    Returns a mock transaction ID.
    """
    try:
        # In a real RCM app, we would create a 'Transfer' to the doctor's account.
        # For our simulator, we create a 'PaymentIntent' to confirm the money is ready.
        intent = stripe.PaymentIntent.create(
            description = f"Payout for Medical Claim ID: {claim_id}",
            shipping={
                "name": "Jenny Rosen",
                "address": {
                "line1": "510 Townsend St",
                "postal_code": "98140",
                "city": "San Francisco",
                "state": "CA",
                "country": "US",
            },
        },
            amount = int(amount * 100), # Stripe uses cents
            currency = "usd",
            payment_method_types = ["card"],
            # We use test token that always succeeds
            confirm = True,
            payment_method = "pm_card_visa"
        )
        return {
            "success": True,
            "transaction_id": intent.id,
            "amount_paid": amount
        }
    except Exception as e:
        print(f"Stripe Error: {e}")
        return {"success": False, "error": str(e)}