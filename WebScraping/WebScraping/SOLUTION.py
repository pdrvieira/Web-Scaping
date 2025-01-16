import os
import re
from bs4 import BeautifulSoup

# Premissa:
# A solução foi projetada para processar arquivos HTML estruturados de maneira similar,
# onde as informações necessárias estão organizadas em tabelas específicas.
# Decidi usar BeautifulSoup como framework para parsear o HTML devido à sua simplicidade e eficiência
# ao navegar por estruturas HTML, junto de expressões regulares para buscas em textos específicos.
# O pandas foi escolhido para estruturar os dados e gerar a saída.
# Adicionei Docstrings a cada função, tentando seguir o padrão convencionado pela comunidade, com objetivo de atender a solicitação do PDF.

# Caminho da pasta com os arquivos HTML
PASTA = "./PATENTES"

def extrair_cnpj(soup):
    """
    Extrai o CNPJ do HTML.
    Justificativa:
    Usei regex porque o padrão de CNPJ ('CPF ou CNPJ do Depositante:') 
    é consistente e fácil de identificar no texto extraído do HTML, Útil nessas situações específicas.
    """
    cnpj_padrao = r"CPF ou CNPJ do Depositante:\s*'(\d{14})'"
    texto = soup.get_text()
    match = re.search(cnpj_padrao, texto)
    return match.group(1) if match else None

def extrair_resultado(soup):   
    """
    Extrai o número de processos encontrados do HTML.
    Justificativa:
    Similar a função acima.
    """
    resultado_pattern = r"Foram encontrados (\d+) processos"
    texto = soup.get_text()
    match = re.search(resultado_pattern, texto)
    return int(match.group(1)) if match else 0

def extrair_detalhes(soup):
    """
    Extrai os detalhes (Número do Pedido, Data do Depósito, Título e IPC) quando há resultados.
    Justificativa:
    A tabela contendo os detalhes está identificada por um id específico ('tituloContext').
    Isso permite localizar a estrutura relevante e extrair as informações diretamente,
    usando as tags "tr" para linhas e "td" para colunas,
    sem a necessidade de processar todo o conteúdo.
    """
    detalhes = []
    tabela = soup.find("tbody", id="tituloContext")
    if tabela:
        linhas = tabela.find_all("tr", recursive=False)
        for linha in linhas:
            colunas = linha.find_all("td")
            if colunas and len(colunas) >= 4:
                pedido = colunas[0].get_text(strip=True)
                deposito = colunas[1].get_text(strip=True)
                titulo = colunas[2].get_text(strip=True)
                ipc = colunas[3].get_text(strip=True)
                detalhes.append({
                    "numero_pedido": pedido,
                    "data_deposito": deposito,
                    "titulo": titulo,
                    "ipc": ipc
                })
    return detalhes

def processar_arquivo(file_path):
    """
    Processa um único arquivo HTML e extrai as informações necessárias, retornado um dicionário para cada arquivo.
    Justificativa:
    Decidi dividir o processamento em funções separadas para facilitar a manutenção
    e o entendimento do código, isolando cada parte do processamento.
    """
    with open(file_path, 'r') as file:
        conteudo = file.read()
        soup = BeautifulSoup(conteudo, 'html.parser')

        # Nome do arquivo
        nome_arquivo = os.path.basename(file_path)

        # Extrair CNPJ
        cnpj = extrair_cnpj(soup)

        # Extrair número de processos encontrados
        resultado = extrair_resultado(soup)

        # Inicializar listas para campos separados
        numeros_pedido = []
        datas_deposito = []
        titulos = []
        ipcs = []

        # Extrair detalhes, se houver resultados
        if resultado > 0:
            detalhes = extrair_detalhes(soup)
            for detalhe in detalhes:
                numeros_pedido.append(detalhe["numero_pedido"])
                datas_deposito.append(detalhe["data_deposito"])
                titulos.append(detalhe["titulo"])
                ipcs.append(detalhe["ipc"])

        return {
            "nome_arquivo": nome_arquivo,
            "cnpj": cnpj,
            "resultado": resultado,
            "numeros_pedido": numeros_pedido,
            "datas_deposito": datas_deposito,
            "titulos": titulos,
            "ipcs": ipcs
        }

def processar_pasta(pasta):
    """
    Processa todos os arquivos HTML em uma pasta.
    Justificativa:
    Itera por todos os arquivos HTML na pasta para garantir que a solução possa ser aplicada
    em massa. Isso é importante para automatizar o processamento de múltiplos arquivos, salvando cada dicionario correspondente a um arquivo, em uma lista.
    """
    resultados = []
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".html"):
            file_path = os.path.join(pasta, arquivo)
            dados = processar_arquivo(file_path)
            resultados.append(dados)
    return resultados

def gerar_saida_html(resultados, caminho_saida):
    """
    Gera o arquivo de saída em formato HTML.
    Justificativa:
    Optei por apresentar o HTML estilizado, adicionei funções como dropdown e barra de busca, para facilitar a análise final.
    """
    estilo = """
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: auto;
            background: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #000000;
            margin-bottom: 25px;
        }
        .search-bar {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        .file-item {
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            background-color: #f9f9f9;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-item:hover {
            background-color: #e9ecef;
        }
        .dropdown-icon {
            font-size: 16px;
            color: #0074D9;
            transition: transform 0.3s;
        }
        .dropdown-icon.up {
            transform: rotate(180deg);
        }
        .dropdown-content {
            display: none;
            margin-top: 10px;
            padding-left: 20px;
        }
        .dropdown-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        .dropdown-content th, .dropdown-content td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .dropdown-content th {
            background-color: #0074D9;
            color: white;
        }
        .dropdown-content tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .dropdown-content tr:hover {
            background-color: #e9ecef;
        }
        #no-results {
            display: none;
            text-align: center;
            color: #999;
        }
    </style>
    """

    script = """
    <script>
        function toggleDropdown(id, iconId) {
            const dropdown = document.getElementById(id);
            const icon = document.getElementById(iconId);
            if (dropdown.style.display === "none" || dropdown.style.display === "") {
                dropdown.style.display = "block";
                icon.classList.add("up");
            } else {
                dropdown.style.display = "none";
                icon.classList.remove("up");
            }
        }

        function filtrarResultados() {
            const query = document.getElementById('search-bar').value.toLowerCase();
            const items = document.getElementsByClassName('file-item');
            let encontrado = false;
            for (let item of items) {
                const text = item.textContent.toLowerCase();
                if (text.includes(query)) {
                    item.style.display = 'flex';
                    encontrado = true;
                } else {
                    item.style.display = 'none';
                }
            }
            document.getElementById('no-results').style.display = encontrado ? 'none' : 'block';
        }
    </script>
    """

    # HTML principal
    html_principal = """
    <div class='container'>
        <h1>Relatório de Patentes</h1>
        <input type="text" id="search-bar" class="search-bar" onkeyup="filtrarResultados()" placeholder="🔍 Busque por Arquivo, CNPJ ou Resultado...">
        <p id="no-results">Nenhum resultado encontrado.</p>
    """

    # Iterar sobre os resultados
    for idx, item in enumerate(resultados):
        dropdown_id = f"dropdown-{idx}"  # ID único para cada dropdown
        icon_id = f"icon-{idx}"  # ID único para o ícone
        tem_dropdown = item["resultado"] > 0

        html_principal += f"""
        <div class="file-item" onclick="{'toggleDropdown('+f"'{dropdown_id}', '{icon_id}'"+')' if tem_dropdown else ''}">
            <div>
                <b>Arquivo:</b> {item['nome_arquivo']} &nbsp;|&nbsp; <b>CNPJ:</b> {item['cnpj']} &nbsp;|&nbsp; <b>RESULTADO:</b> {item['resultado']}
            </div>
            {'<div id="'+icon_id+'" class="dropdown-icon">▼</div>' if tem_dropdown else ''}
        </div>
        """

        # Detalhes dos resultados (dropdown) caso haja
        if tem_dropdown:
            html_principal += f"""
            <div id="{dropdown_id}" class="dropdown-content">
                <table>
                    <thead>
                        <tr>
                            <th>NÚMERO DO PEDIDO</th>
                            <th>Data do Depósito</th>
                            <th>Título</th>
                            <th>IPC</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for i in range(len(item["numeros_pedido"])):
                html_principal += f"""
                <tr>
                    <td>{item['numeros_pedido'][i]}</td>
                    <td>{item['datas_deposito'][i]}</td>
                    <td>{item['titulos'][i]}</td>
                    <td>{item['ipcs'][i]}</td>
                </tr>
                """
            html_principal += """
                    </tbody>
                </table>
            </div>
            """
    html_principal += "</div>"

    # Combinar tudo
    html_final = f"{estilo}{script}{html_principal}"

    # Salvar como HTML
    with open(caminho_saida, "w", encoding="utf-8") as file:
        file.write(html_final)

    print(f"Arquivo HTML gerado: {caminho_saida}")

def main():
    """
    Função principal.
    Justificativa:
    Decidi usar uma função principal para organizar a execução do programa,
    separando claramente as etapas de entrada, processamento e saída.
    """
    print("Processando arquivos...")

    # Processar todos os arquivos da pasta
    resultados = processar_pasta(PASTA)

    # Gerar o arquivo HTML de saída
    gerar_saida_html(resultados, "PATENTES.HTML")

    print("Processamento concluído!")


if __name__ == "__main__":
    main()
