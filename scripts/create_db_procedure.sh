#!/bin/bash
set -e

echo "Creating stored procedure..."

docker compose exec -T db_gl mysql -u gestaolegal -pgestaolegal gestaolegal << 'EOF'
DELIMITER //

DROP PROCEDURE IF EXISTS CreateAdmin//

CREATE PROCEDURE CreateAdmin(
    IN p_email VARCHAR(80),
    IN p_password VARCHAR(255)
)
BEGIN
    DECLARE hashed_password VARCHAR(60);
    DECLARE user_exists INT DEFAULT 0;
 
    -- bcrypt hash for '123456'
    SET hashed_password = '$2b$12$a2pGd1h0X56LyOaJTBOeqe0qUAYhaPjUPtZpI4JBFQ0qyTcf5GDa6';

    SELECT COUNT(*) INTO user_exists FROM usuarios WHERE email = p_email;

    IF user_exists > 0 THEN
        UPDATE usuarios 
        SET senha = hashed_password,
            modificado = NOW()
        WHERE email = p_email;
        SELECT CONCAT('✓ Admin updated: ', p_email) as message;
    ELSE
        INSERT INTO usuarios (
            nome, email, senha, urole, sexo, rg, cpf, profissao, 
            estado_civil, nascimento, telefone, celular, oab, obs,
            data_entrada, matricula, bolsista, tipo_bolsa, 
            horario_atendimento, suplente, ferias, status,
            cert_atuacao_DAJ, endereco_id, criado, criadopor
        ) 
        VALUES (
            'Administrador', p_email, hashed_password, 'admin', 'Masculino', 
            '123456789', '123.456.789-00', 'Administrador', 'Solteiro',
            '1990-01-01', '(11) 1234-5678', '(11) 98765-4321', NULL,
            'Usuário administrador do sistema', CURDATE(), 'ADM001',
            false, NULL, NULL, NULL, NULL, true, 'SIM', NULL, NOW(), 1
        );
        SELECT CONCAT('✓ Admin created: ', p_email) as message;
    END IF;

    SELECT id, nome, email, urole FROM usuarios WHERE email = p_email;
END//

DELIMITER ;

-- Verify the procedure was created
SHOW CREATE PROCEDURE CreateAdmin;
EOF

echo "Stored procedure created successfully"
