import os
import json
from web3 import Web3

def get_network_config(chain_id_to_find):
    """پیکربندی شبکه را بر اساس شناسه زنجیره از فایل `networks.json` می‌خواند."""
    try:
        with open('networks.json', 'r') as f:
            networks = json.load(f)
            for network in networks:
                if int(network.get('chain_id')) == chain_id_to_find:
                    return network
    except Exception as e:
        print(f"خطا در خواندن یا پیدا کردن شبکه: {e}")
    return None

def send_report_transaction():
    """تراکنش گزارش را ارسال می‌کند."""
    
    # --- اطلاعات تراکنش ---
    tx_data = {
        "chainId": 91342,
        "data": "0xc0129d43",
        "from": "0xFDA1d6115A49adf731570800D35C901ad4e0057B",
        "to": "0x274d0c11A0b9F9C48aF5a099CBDC441030801561"
    }
    
    # --- دریافت کلید خصوصی ---
    private_key = os.getenv('PRIVATE_KEY')
    if not private_key:
        print("خطا: کلید خصوصی (PRIVATE_KEY) در متغیرهای محیطی یافت نشد.")
        return

    # --- دریافت پیکربندی شبکه ---
    network_config = get_network_config(tx_data["chainId"])
    if not network_config:
        print(f"خطا: پیکربندی شبکه برای Chain ID {tx_data['chainId']} یافت نشد.")
        return
        
    rpc_url = network_config.get('rpc_url')
    network_name = network_config.get('displayName', 'Unknown Network')
    print(f"شروع عملیات برای شبکه: {network_name}")

    # --- اتصال به شبکه ---
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if not w3.is_connected():
            print("خطا در اتصال به RPC.")
            return
    except Exception as e:
        print(f"خطای اتصال به {rpc_url}: {e}")
        return

    # --- بررسی تطابق آدرس و کلید خصوصی ---
    try:
        account = w3.eth.account.from_key(private_key)
        if account.address.lower() != tx_data["from"].lower():
            print("خطای امنیتی: کلید خصوصی ارائه شده با آدرس 'from' تراکنش مطابقت ندارد.")
            print(f"آدرس مشتق شده از کلید: {account.address}")
            print(f"آدرس مورد انتظار: {tx_data['from']}")
            return
    except Exception as e:
        print(f"خطا در پردازش کلید خصوصی: {e}")
        return

    # --- ساخت و ارسال تراکنش ---
    try:
        print("در حال آماده‌سازی تراکنش...")
        
        # دریافت مقادیر پویا
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price
        
        # ساخت تراکنش
        transaction = {
            'to': tx_data['to'],
            'from': tx_data['from'],
            'value': 0,  # مقدار اتر ارسالی (در اینجا صفر است)
            'gas': 150000, # مقدار Gas limit (کمی بالاتر در نظر گرفته شده)
            'gasPrice': gas_price,
            'nonce': nonce,
            'data': tx_data['data'],
            'chainId': tx_data['chainId']
        }

        # امضای تراکنش
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key)

        # ارسال تراکنش
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"تراکنش با موفقیت ارسال شد.")
        print(f"هش تراکنش (Tx Hash): {w3.to_hex(tx_hash)}")
        
        # منتظر ماندن برای تایید تراکنش
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            print("تراکنش با موفقیت در بلاکچین تایید شد.")
        else:
            print("خطا: تراکنش در بلاکچین ناموفق بود (reverted).")
            
    except Exception as e:
        print(f"خطا در هنگام ارسال تراکنش: {e}")

if __name__ == "__main__":
    send_report_transaction()
