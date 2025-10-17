DELIMITER //
DROP PROCEDURE IF EXISTS CreateAdmin//
CREATE PROCEDURE CreateAdmin(
    IN p_email VARCHAR(80),
    IN p_password VARCHAR(255)
)
BEGIN
    DECLARE hashed_password VARCHAR(60);
    DECLARE user_exists INT DEFAULT 0;
    DECLARE admin_endereco_id INT;
    
    SET hashed_password = '$2b$12$a2pGd1h0X56LyOaJTBOeqe0qUAYhaPjUPtZpI4JBFQ0qyTcf5GDa6';
    SELECT COUNT(*) INTO user_exists FROM usuarios WHERE email = p_email;
    
    IF user_exists > 0 THEN
        UPDATE usuarios 
        SET senha = hashed_password, modificado = NOW()
        WHERE email = p_email;
    ELSE
        INSERT INTO enderecos (logradouro, numero, complemento, bairro, cep, cidade, estado)
        VALUES ('Rua Admin', '1', 'Sala Admin', 'Centro', '00000-000', 'Belo Horizonte', 'MG');
        SET admin_endereco_id = LAST_INSERT_ID();
        
        INSERT INTO usuarios (
            nome, email, senha, urole, sexo, rg, cpf, profissao, 
            estado_civil, nascimento, telefone, celular, oab, obs,
            data_entrada, matricula, bolsista, tipo_bolsa, 
            horario_atendimento, suplente, ferias, status,
            cert_atuacao_DAJ, endereco_id, criado, criadopor
        ) VALUES (
            'admin', p_email, hashed_password, 'admin', 'Masculino', 
            '123456789', '123.456.789-00', 'Administrador', 'Solteiro',
            '1990-01-01', '(11) 1234-5678', '(11) 98765-4321', NULL,
            'Usuário administrador', CURDATE(), 'ADM001',
            false, NULL, NULL, NULL, NULL, true, 'SIM', admin_endereco_id, NOW(), 1
        );
    END IF;
END//
DELIMITER ;