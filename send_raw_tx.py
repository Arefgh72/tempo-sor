import json
import os
from web3 import Web3

print("--- شروع اسکریپت ارسال تراکنش خام ---")

try:
    # --- ۱. خواندن تنظیمات و اتصال به شبکه ---

    # خواندن اطلاعات شبکه از فایل
    with open('networks.json', 'r') as f:
        network_info = json.load(f)[0]
        rpc_url = network_info['rpc_url']

    # اتصال به شبکه
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"خطا: اتصال به RPC URL '{rpc_url}' برقرار نشد.")
    print(f"با موفقیت به شبکه متصل شد.")

    # خواندن کلید خصوصی از GitHub Secrets
    private_key = os.environ.get('PRIVATE_KEY')
    if not private_key:
        raise ValueError("کلید خصوصی (PRIVATE_KEY) در GitHub Secrets تنظیم نشده است!")

    # ساخت حساب کاربری از روی کلید خصوصی
    account = w3.eth.account.from_key(private_key)
    print(f"تراکنش از آدرس {account.address} ارسال خواهد شد.")

    # --- ۲. ساخت و ارسال تراکنش ---

    # تعریف جزئیات تراکنش بر اساس اطلاعاتی که شما دادید
    # نکته مهم: نانس (nonce) به صورت خودکار از شبکه دریافت می‌شود تا همیشه معتبر باشد
    transaction_details = {
        'to': '0x59c27c39A126a9B5eCADdd460C230C857e1Deb35',
        'value': w3.to_int(hexstr='0x1a6016b2d000'),  # تبدیل مقدار هگزادسیمال به عدد
        'gas': w3.to_int(hexstr='0xe5fd'),
        'gasPrice': w3.to_int(hexstr='0x1250ad'),
        'nonce': w3.eth.get_transaction_count(account.address), # دریافت نانس صحیح از شبکه
        'data': '0x84a3bb6b0000000000000000000000000000000000000000000000000000000000000000',
        'chainId': 91342
    }

    print("جزئیات تراکنش آماده شد:")
    print(transaction_details)

    # امضا کردن تراکنش با کلید خصوصی
    signed_txn = w3.eth.account.sign_transaction(transaction_details, private_key=private_key)

    # ارسال تراکنش امضا شده به شبکه
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

    print(f"\nتراکنش با موفقیت ارسال شد. هش تراکنش: {tx_hash.hex()}")

    # منتظر ماندن برای تایید تراکنش
    print("در انتظار تایید تراکنش...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("تراکنش با موفقیت تایید شد!")
    print(f"Block Number: {tx_receipt['blockNumber']}")

except Exception as e:
    print(f"\n!!! یک خطای کلی رخ داد: {e}")
    exit(1)
