import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://127.0.0.1:8000/api"

def wait_for_server():
    print("Waiting for server to be ready on port 8000...")
    for _ in range(30):
        try:
            r = requests.get(f"{BASE}/market", timeout=2)
            if r.status_code == 200:
                print("Server is UP and ready!")
                return
        except Exception:
            time.sleep(1)
    raise RuntimeError("Server did not start in 30 seconds")

def test_endpoints():
    wait_for_server()
    print("Testing /market...")
    r = requests.get(f"{BASE}/market")
    print(f"/market: status={r.status_code}, Nifty={r.json().get('indices', {}).get('NIFTY_50', {}).get('current')}")
    assert r.status_code == 200

    print("\nTesting /recommendations...")
    r = requests.get(f"{BASE}/recommendations")
    recs = r.json()
    print(f"/recommendations: status={r.status_code}, total={len(recs.get('all_recommendations', []))}")
    assert r.status_code == 200

    print("\nTesting /model/stats...")
    r = requests.get(f"{BASE}/model/stats")
    assert r.status_code == 200

    # Ensure clean session
    requests.post(f"{BASE}/chat/clear", json={"session_id": "test_e2e_session"})

    print("\nTesting Chatbot Queries...")
    queries = [
        "Which stocks should I buy today?",
        "What stocks should I avoid?",
        "What is the prediction for Reliance?",
        "Compare TCS and INFY",
        "Analyze my portfolio risk",
        "What happens if Nifty drops 5%?"
    ]

    for q in queries:
        print(f"\n--- Query: '{q}' ---")
        payload = {"message": q, "session_id": "test_e2e_session"}
        res = requests.post(f"{BASE}/chat/message", json=payload)
        assert res.status_code == 200
        data = res.json()
        print(f"Reply length: {len(data.get('reply', ''))} chars")
        print(f"Stock chips: {[c.get('ticker') for c in data.get('stock_chips', [])]}")
        print(f"Suggested prompts: {data.get('suggested_prompts', [])}")
        print(f"Reply sample: {data.get('reply', '')[:120]}...")

    print("\nTesting /chat/history...")
    r = requests.get(f"{BASE}/chat/history?session_id=test_e2e_session")
    history = r.json().get('history', [])
    print(f"Chat history length: {len(history)} messages")
    assert len(history) == len(queries) * 2

    print("\nTesting /chat/clear...")
    r = requests.post(f"{BASE}/chat/clear", json={"session_id": "test_e2e_session"})
    assert r.status_code == 200
    r = requests.get(f"{BASE}/chat/history?session_id=test_e2e_session")
    assert len(r.json().get('history', [])) == 0
    print("Chat clear verified!")

    print("\n✅ ALL ENDPOINTS AND CHATBOT FLOWS FULLY VERIFIED!")

if __name__ == "__main__":
    test_endpoints()
