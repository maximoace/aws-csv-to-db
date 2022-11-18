def get_field_names():
    field_names = [
        'Originador',
        'Doc Originador',
        'Cedente',
        'Doc Cedente',
        'CCB',
        'Id',
        'Cliente',
        'CPF/CNPJ',
        'Endereço',
        'CEP',
        'Cidade',
        'UF',
        'Valor do Empréstimo',
        'Parcela R$',
        'Total Parcelas',
        'Parcela #',
        'Data de Emissão',
        'Data de Vencimento',
        'Preço de Aquisição'
    ]
    return field_names

#Get key fields to avoid duplicates:
#Must use _ instead of ' ' and follow utf-8 charset
def get_key_column_fields():
    key_fields = [
        'Doc_Originador',
        'Doc_Cedente',
        'Id_externo',
        'CPF_CNPJ'
    ]