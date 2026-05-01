ENGINE_VERSION = "1.0.0-omni"
# OMNI MOTHER - IPsec IKEv2 Initiator Protocol
# Mathematical Diffie-Hellman Key Exchange configuration generation

class OmniIKEv2Initiator:
    def __init__(self, target_ip: str, psk: str):
        self.target = target_ip
        self.psk = psk

    def generate_strongswan_config(self) -> str:
        return f"""
conn omni-tunnel
    keyexchange=ikev2
    left=%defaultroute
    right={self.target}
    authby=secret
    auto=start
        """\n