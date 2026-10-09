import os
import sys
from pathlib import Path
import hvac

def bootstrap_vault():
    vault_addr = os.environ.get("VAULT_ADDR", "http://localhost:8200")
    vault_token = os.environ.get("VAULT_TOKEN")

    if not vault_token:
        sys.exit("[-] VAULT_TOKEN environment variable is required to initialize Vault.")

    client = hvac.Client(url=vault_addr, token=vault_token)

    if not client.is_authenticated():
        sys.exit(f"[-] Failed to authenticate with Vault at {vault_addr} using provided token.")

    # 1. Enable KV v2 secret engine at secret/
    mounts = client.sys.list_mounted_secrets_engines().get("data", {})
    if "secret/" not in mounts:
        client.sys.enable_secrets_engine(backend_type="kv", path="secret", options={"version": "2"})
        print("[+] Mounted KV-v2 engine at secret/")

    # 2. Enable userpass auth method
    auth_methods = client.sys.list_auth_methods().get("data", {})
    if "userpass/" not in auth_methods:
        client.sys.enable_auth_method(method_type="userpass", path="userpass")
        print("[+] Enabled userpass auth method at userpass/")

    # 3. Register identity-service-policy
    repo_root = Path(__file__).resolve().parents[3]
    policy_candidates = [
        Path(__file__).resolve().parents[1] / "configs" / "policies" / "identity-service-policy.hcl",
        repo_root / "services" / "secrets" / "configs" / "policies" / "identity-service-policy.hcl",
    ]
    policy_file = next((p for p in policy_candidates if p.is_file()), None)
    if not policy_file:
        sys.exit("[-] Could not locate identity-service-policy.hcl")

    client.sys.create_or_update_policy(name="identity-service-policy", policy=policy_file.read_text(encoding="utf-8"))
    print(f"[+] Loaded policy 'identity-service-policy' from {policy_file}")

    print("[*] Vault initialization completed successfully.")

if __name__ == "__main__":
    bootstrap_vault()
