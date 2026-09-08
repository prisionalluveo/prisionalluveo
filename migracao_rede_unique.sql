-- Garante que cada unidade tenha só uma configuração de rede
-- (rodar depois do carga_inventario.sql, já com a tabela configuracao_rede criada)
alter table configuracao_rede add constraint configuracao_rede_unidade_unica unique (unidade);
