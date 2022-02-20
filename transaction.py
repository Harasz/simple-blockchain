from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes


class Transaction:
    def __init__(self, from_, to, value):
        self.from_ = from_
        self.to = to
        self.value = value
        self.signature = None

    def set_signature(self, signature):
        self.signature = signature
        self._valid_from()

    def validate(self):
        self._valid_from()

    def _valid_from(self):
        public_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), bytes.fromhex(self.from_))
        public_key.verify(bytes.fromhex(self.signature), self.get_data(), ec.ECDSA(hashes.SHA3_256()))

    def get_data(self):
        return f"{self.from_};{self.to};{self.value}".encode()

    def __str__(self):
        return f"{self.from_};{self.to};{self.value};{self.signature}"

    @staticmethod
    def load_from_string(value):
        [from_, to, value, signature] = value.split(';')
        trans = Transaction(from_, to, value)
        trans.set_signature(signature)
        return trans
