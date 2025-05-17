import hashlib

from app.common.hash_utils import generate_hash


class TestHashUtils:
    def test_generate_hash(self):
        """Testa se generate_hash retorna o hash SHA-256 esperado para diferentes entradas."""
        # Teste com uma string simples
        data = "test"
        expected_hash = hashlib.sha256(data.encode()).hexdigest()

        result = generate_hash(data)

        assert result == expected_hash

        # Teste com uma string vazia
        data = ""
        expected_hash = hashlib.sha256(data.encode()).hexdigest()

        result = generate_hash(data)

        assert result == expected_hash

        # Teste com uma string complexa
        data = "This is a more complex string with spaces and special characters: !@#$%^&*()"
        expected_hash = hashlib.sha256(data.encode()).hexdigest()

        result = generate_hash(data)

        assert result == expected_hash

    def test_generate_hash_unicode(self):
        """Testa se generate_hash lida corretamente com caracteres Unicode."""
        data = "çãõü漢字"
        expected_hash = hashlib.sha256(data.encode()).hexdigest()
        result = generate_hash(data)
        assert result == expected_hash

    def test_generate_hash_long_string(self):
        """Testa se generate_hash lida corretamente com strings muito longas."""
        data = "a" * 10_000  # String de 10.000 caracteres
        expected_hash = hashlib.sha256(data.encode()).hexdigest()
        result = generate_hash(data)
        assert result == expected_hash

    def test_generate_hash_different_inputs_produce_different_hashes(self):
        """Testa se entradas diferentes produzem hashes diferentes."""
        data1 = "primeira entrada"
        data2 = "segunda entrada"
        hash1 = generate_hash(data1)
        hash2 = generate_hash(data2)
        assert hash1 != hash2

    def test_generate_hash_consistency(self):
        """Testa se a mesma entrada sempre gera o mesmo hash."""
        data = "consistência"
        hash1 = generate_hash(data)
        hash2 = generate_hash(data)
        assert hash1 == hash2
