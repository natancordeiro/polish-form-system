"""
Smoke test — gera um PDF de exemplo usando os dados do Luiz Ricardo.
Útil para validar o pipeline localmente sem subir a API inteira.

Uso:  python smoke_test.py
Saída: sample_output.pdf no diretório atual
"""
from datetime import date
from pathlib import Path

from app.schemas import (
    FormData, DadosPessoais, DadosProgenitor, Endereco,
)
from app.services.pdf_generator import generate_pdf


def build_sample_data() -> FormData:
    """Reproduz os dados do PDF Luiz_Ricardo.pdf como teste."""
    return FormData(
        local_submissao="Warszawa",
        data_submissao=date(2023, 11, 3),
        wojewoda="Mazowiecki",

        requerente_nome_completo="Silvana Aparecida Gurski Gomes",
        requerente_endereco=Endereco(
            pais="Polônia",
            estado="Mazowieckie",
            cidade="Warszawa",
            rua="Puławska",
            numero_casa="12",
            numero_apartamento="3",
            cep="02-566",
            telefone="500330034",
        ),

        tipo_decisao="posiadanie",
        nome_titular_confirmacao="Luiz Ricardo Konarski",
        info_adicional_pedido=(
            "Confirmação de cidadania polonesa pelo pai: Anatol Konarski, "
            "cidadão polonês nascido em 1914 em Łódź, que emigrou em 1941 para o Brasil."
        ),
        justificativa_procuracao=(
            "O requerente Luiz Ricardo Konarski, com base em procuração concedida a "
            "Silvana Aparecida Gurski Gomes, CPF/PESEL 86091520607, "
            "solicita a confirmação da cidadania polonesa."
        ),

        solicitante=DadosPessoais(
            sobrenome="Konarski",
            sobrenome_solteiro="Konarski",
            nome="Luiz Ricardo",
            nome_pai="Anatol",
            sobrenome_pai="Konarski",
            nome_mae="Maria Aparecida",
            sobrenome_solteiro_mae="Ferraz",
            nomes_usados=None,
            data_nascimento=date(1953, 5, 9),
            sexo="M",
            pais_nascimento="Brasil",
            cidade_nascimento="São José do Rio Preto",
            cidadania="Brasileira",
            data_aquisicao_cidadania="desde o nascimento",
            estado_civil="divorciado",
        ),

        houve_decisao_anterior=False,
        houve_mudanca_cidadania=False,

        enderecos_vida="SHIS QI, 7 Conjunto 9, Casa 11 – CEP 71615-290 – Brasília, Brasil.",

        mae=DadosProgenitor(
            sobrenome="Ferraz Konarski",
            sobrenome_solteiro="Ferraz",
            nome="Maria Aparecida",
            nome_pai="Juvenal",
            sobrenome_pai="Dias Ferraz",
            nome_mae="Anna",
            sobrenome_solteiro_mae="Volpe",
            nomes_usados="Ferraz",
            data_mudanca_nome=date(1949, 12, 8),
            data_nascimento=date(1922, 9, 18),
            sexo="F",
            pais_nascimento="Brasil",
            cidade_nascimento="São José do Rio Preto",
            estado_civil="casada",
            data_casamento=date(1975, 9, 16),
            pais_casamento="Brasil",
            cidade_casamento="Bocaina",
            cidadania="Brasileira",
            data_aquisicao_cidadania="desde o nascimento",
        ),
        pai=DadosProgenitor(
            sobrenome="Konarski",
            sobrenome_solteiro="Konarski",
            nome="Anatol",
            nome_pai="Jakób",
            sobrenome_pai="Konarski",
            nome_mae="Gustawa",
            sobrenome_solteiro_mae="Konarski",
            data_nascimento=date(1914, 8, 6),
            sexo="M",
            pais_nascimento="Polônia",
            cidade_nascimento="Łódź",
            estado_civil="casado",
            data_casamento=date(1949, 12, 8),
            pais_casamento="Brasil",
            cidade_casamento="São Paulo",
            cidadania="Polonesa",
            data_aquisicao_cidadania="desde o nascimento",
        ),

        avo_materno=DadosPessoais(
            sobrenome="Dias Ferraz", sobrenome_solteiro="Dias Ferraz", nome="Juvenal",
            nome_pai="Desconhecido", nome_mae="Desconhecida",
            data_nascimento_desconhecida=True,
            pais_nascimento="Brasil", cidade_nascimento="Brotas",
        ),
        avo_materna=DadosPessoais(
            sobrenome="Volpe Ferraz", sobrenome_solteiro="Volpe", nome="Anna",
            nome_pai="Desconhecido", nome_mae="Desconhecida",
            data_nascimento_desconhecida=True,
            pais_nascimento="Brasil", cidade_nascimento="Bocaina",
        ),
        avo_paterno=DadosPessoais(
            sobrenome="Konarski", sobrenome_solteiro="Konarski", nome="Jakób",
            nome_pai="Desconhecido", nome_mae="Desconhecida",
            data_nascimento_desconhecida=True,
            pais_nascimento="Desconhecido", cidade_nascimento_desconhecida=True,
        ),
        avo_paterna=DadosPessoais(
            sobrenome="Konarski", sobrenome_solteiro=None, nome="Gustawa",
            nome_pai="Desconhecido", nome_mae="Desconhecida",
            data_nascimento_desconhecida=True,
            pais_nascimento="Desconhecido", cidade_nascimento_desconhecida=True,
        ),

        biografia_solicitante=(
            "Luiz Ricardo Konarski, nascido em 09.05.1953 em São José do Rio Preto, "
            "estado de São Paulo, Brasil, filho de Anatol Konarski e Maria Aparecida Ferraz Konarski. "
            "Cidadania brasileira desde o nascimento. Dispensado do serviço militar brasileiro. "
            "Em 11.12.1981 casou-se com Claudia Guaraciaba Pohl. Divorciou-se em 20.08.1985. "
            "Estado civil: divorciado. Reside em SHIS QI 7, Conjunto 9, Casa 11, CEP 71615-290, "
            "Brasília, Brasil. Profissão: engenheiro civil. Possui licença profissional de engenheiro "
            "número DF-3184/D, emitida em Brasília em 22.04.2021. Nunca morou na Polônia."
        ),
        escolheu_cidadania_estrangeira="NIE",

        biografia_ancestral_polones=(
            "Anatol Konarski, nascido em 06.08.1914 em Łódź, filho de Jakób Konarski e Gustawa Konarski. "
            "Foi cidadão polonês. Em 1940, em Milão, em razão das graves consequências da Segunda Guerra Mundial, "
            "obteve passaporte polonês para emigrar ao Brasil. Passou pela Espanha e Portugal "
            "até chegar ao porto do Rio de Janeiro em 07.05.1941. No Brasil, morou em São José do Rio Preto, "
            "estado de São Paulo, onde trabalhou como comerciante. Casou-se com Maria Aparecida Ferraz em 08.12.1949 "
            "em São José do Rio Preto. Não cumpriu serviço militar brasileiro. Nunca foi naturalizado brasileiro. "
            "Faleceu em 01.01.2000 em São José do Rio Preto."
        ),

        docs_poloneses_ancestrais=(
            "O pai do requerente, Anatol Konarski, emitiu passaporte polonês na Itália em 1940 "
            "com o objetivo de emigrar para o Brasil."
        ),

        anexos=[
            "Comprovante de pagamento da taxa do requerimento + procuração 75 PLN",
            "Procuração",
            "Cópia da carteira profissional brasileira de Luiz Ricardo Konarski",
            "Certidão de nascimento de Luiz Ricardo Konarski + tradução",
            "Certidão de casamento de Anatol Konarski e Maria Aparecida Ferraz + tradução",
            "Certidão negativa de naturalização brasileira de Anatol Konarski",
            "Cópia do passaporte polonês de Anatol Konarski",
        ],
    )


if __name__ == "__main__":
    data = build_sample_data()
    pdf_bytes = generate_pdf(data)

    out = Path(__file__).parent / "sample_output.pdf"
    out.write_bytes(pdf_bytes)
    print(f"✓ PDF gerado: {out.resolve()}  ({len(pdf_bytes):,} bytes)")
