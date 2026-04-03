"""Test order with sig_type=1, no private key."""
import base64, json
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs
from py_clob_client.constants import POLYGON

API_KEY      = "f649cb77-2283-dbf3-510d-f8a3dafade63"
API_SECRET   = "VSlmx75F7clayZpaDs1r2YWDPx5XJHKTcBwBgY45e5A="
PASSPHRASE   = "17c91c2aec787fe45450d79967ede5692bc440c9b99610bcb353bc329fce6b92"
FUNDER       = "0x7e3bacaa4e7563ff2343e48019120504028ee306"

# api_secret → derived signing key (no main private key)
_secret_padded = API_SECRET + "=" * (-len(API_SECRET) % 4)
signing_key  = "0x" + base64.urlsafe_b64decode(_secret_padded).hex()

creds = ApiCreds(api_key=API_KEY, api_secret=API_SECRET, api_passphrase=PASSPHRASE)

def run(sig_type):
    print(f"\n{'='*50}")
    print(f"SIG_TYPE = {sig_type}")
    print('='*50)

    try:
        client = ClobClient(
            host="https://clob.polymarket.com",
            chain_id=POLYGON,
            key=signing_key,
            creds=creds,
            signature_type=sig_type,
            funder=FUNDER,
        )
    except Exception as e:
        print(f"Client ERROR: {e}")
        return

    # Balance
    print("\n--- Balance ---")
    try:
        bal = client.get_balance_allowance(params={"asset_type": "COLLATERAL"})
        print(f"Balance: {bal}")
    except Exception as e:
        print(f"Balance error: {e}")

    # Find market
    print("\n--- Finding market ---")
    token_id = None
    market_price = 0.50
    try:
        resp = client.get_sampling_simplified_markets(next_cursor="")
        for m in resp.get("data", [])[:50]:
            for tok in m.get("tokens", []):
                p = float(tok.get("price", 0) or 0)
                if 0.35 <= p <= 0.65 and tok.get("token_id"):
                    token_id = tok["token_id"]
                    market_price = p
                    print(f"Market : {m.get('question','')[:60]}")
                    print(f"Token  : {tok.get('outcome')} @ {p}")
                    break
            if token_id:
                break
    except Exception as e:
        print(f"Market error: {e}")

    if not token_id:
        print("No market found")
        return

    # Order
    print("\n--- Placing $1 BUY ---")
    buy_price = round(max(0.01, market_price - 0.10), 2)  # below market, won't fill
    size      = round(1.0 / buy_price, 1)
    print(f"BUY {size} shares @ ${buy_price}")
    try:
        result = client.create_and_post_order(OrderArgs(
            price=buy_price,
            size=size,
            side="BUY",
            token_id=token_id,
        ))
        print(f"Result: {json.dumps(result, indent=2)}")
        order_id = (result or {}).get("orderID") or (result or {}).get("order_id")

        if order_id:
            print(f"\n--- Cancelling {order_id} ---")
            cancel = client.cancel(order_id=order_id)
            print(f"Cancel: {cancel}")
        else:
            print("No order_id in response")
    except Exception as e:
        print(f"Order ERROR: {type(e).__name__}: {e}")

# Try sig_type=1 first, then 0 if fails
run(sig_type=1)
run(sig_type=0)
