import networkx as nx
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Definição das rotas de carga e de passageiros
Rotas_carga = [
    ("Algeciras", "Le Havre", 5),
    ("Le Havre", "Marseille", 3),
    ("Algeciras", "Valencia", 1),
    ("Marseille", "Izmit", 9),
    ("Marseille", "Botas", 12),
    ("Izmit", "Botas", 4),
    ("Marseille", "Amsterdam", 5),
    ("Le Havre", "Antwerp", 1)
]

Rotas_passageiro = [
    ("Algeciras", "Le Havre", 6),
    ("Le Havre", "Marseille", 4),
    ("Algeciras", "Valencia", 2),
    ("Marseille", "Izmit", 8),
    ("Algeciras", "Botas", 8),
    ("Izmit", "Botas", 4),
    ("Marseille", "Amsterdam", 6),
    ("Le Havre", "Antwerp", 2),
    ("Amsterdam", "Hamburg", 1),
    ("Hamburg", "Izmit", 10),
    ("Marseille", "Hamburg", 8)
]

def criar_grafo_carga():
    """
    Cria e retorna um grafo direcionado para navios de carga com base nas rotas definidas.
    """
    carga = nx.DiGraph()

    # Adiciona as cidades ao grafo
    carga.add_nodes_from(Cidades.keys())
    nx.set_node_attributes(carga, Cidades)

    # Adiciona as arestas ao grafo para cada rota de carga
    for origem, destino, dias in Rotas_carga:
        carga.add_edge(origem, destino, weight=dias)
        carga.add_edge(destino, origem, weight=dias) # Adiciona a rota no sentido inverso

    return carga

def criar_grafo_passageiros():
    """
    Cria e retorna um grafo direcionado para navios de passageiros com base nas rotas definidas.
    """
    passageiros = nx.DiGraph()

    # Adiciona as cidades ao grafo
    passageiros.add_nodes_from(Cidades.keys())
    nx.set_node_attributes(passageiros, Cidades)

    # Adiciona as arestas ao grafo para cada rota de passageiros
    for origem, destino, dias in Rotas_passageiro:
        passageiros.add_edge(origem, destino, weight=dias)
        passageiros.add_edge(destino, origem, weight=dias)

    return passageiros

def caminho_mais_curto(grafo, origem, destino, dias_max):
    """
    Encontra e retorna o caminho mais curto para navios de carga entre dois portos, considerando o tempo máximo disponível.

    Argumentos:
        grafo: O grafo de navios de carga.
        origem: O porto de origem.
        destino: O porto de destino.
        dias_max: O número máximo de dias disponíveis para a viagem.

    Retorna:
        Um dicionário contendo o caminho, o número de dias e o custo da viagem.
    """
    try:
        caminho = nx.shortest_path(grafo, origem, destino, weight='weight')
        dias = sum(grafo[u][v]['weight'] for u, v in zip(caminho[:-1], caminho[1:]))
        custo = sum(grafo.nodes[Cidades]['custo'] * grafo[u][v]['weight'] for u, v, Cidades in zip(caminho[:-1], caminho[1:], caminho[1:]))

        if dias > dias_max:
            print(f"\nNão conseguimos realizar esta viagem neste tempo. O caminho mais rápido são {dias} dias.")

        return {"caminho": caminho, "dias": dias, "custo": custo}

    except nx.NetworkXNoPath:
        print("\nNão existe caminho!")
        return {}

def caminhos_todos(grafo, origem, destino, dias_max):
    """
    Encontra e retorna todos os caminhos possíveis para navios de passageiros entre dois portos dentro do tempo disponível.

    Argumentos:
        grafo: O grafo de navios de passageiros.
        origem: O porto de origem.
        destino: O porto de destino.
        dias_max: O número máximo de dias disponíveis para a viagem.

    Retorna:
        Uma lista de dicionários contendo cada caminho, o número de dias e o custo da viagem.
    """
    try:
        caminhos = list(nx.all_simple_paths(grafo, origem, destino, dias_max))
        caminhos_completos = []

        for caminho in caminhos:
            dias = sum(grafo[u][v]['weight'] for u, v in zip(caminho[:-1], caminho[1:]))
            custo = sum(grafo.nodes[Cidades]['custo'] * grafo[u][v]['weight'] for u, v, Cidades in zip(caminho[:-1], caminho[1:], caminho[1:]))
            caminhos_completos.append({"caminho": caminho, "dias": dias, "custo": custo})

        return caminhos_completos

    except nx.NetworkXNoPath:
        return []

def procurar_navio(nome_navio):
    """
    Procura um navio pelo nome nos dados de navios de passageiros e de carga.

    Args:
        nome_navio: O nome do navio a ser procurado.

    Returns:
        Um inteiro indicando o tipo de navio encontrado (1 para passageiros, 2 para carga) ou 0 se não encontrado.
    """
    tipo = None
    encontrado = False

    while not encontrado:
        try:
            file = pd.read_excel('navios_mercantes.xlsx', sheet_name="navios_passageiros")
            resultado = file[file['nome'].str.contains(nome_navio, case=False)]

            if not resultado.empty:
                print("\nNavio de passageiros encontrado:")
                print(resultado)
                return 1

            file2 = pd.read_excel('navios_mercantes.xlsx', sheet_name="navios_de_carga")
            resultado2 = file2[file2['nome'].str.contains(nome_navio, case=False)]

            if not resultado2.empty:
                print("\nNavio de carga encontrado:")
                print(resultado2)
                return 2

            print(f"\nNenhum navio encontrado com o nome '{nome_navio}'.")
            break

        except FileNotFoundError:
            print("\nArquivo 'navios_mercantes.xlsx' não encontrado.")
        except Exception as e:
            print("\nOcorreu um erro...", e)
            return 0

    return tipo

def porto_origem():
    """
    Solicita ao usuário o porto de origem até que uma cidade válida seja inserida.

    Returns:
        O nome do porto de origem.
    """
    while True:
        porto_origem = input("\n <-> Porto de origem: ")
        if porto_origem in Cidades:
            return porto_origem
        else:
            print("\nA cidade que inseriu não se encontra disponível.")

def porto_chegada():
    """
    Solicita ao usuário o porto de chegada até que uma cidade válida seja inserida.

    Returns:
        O nome do porto de chegada.
    """
    while True:
        porto_chegada = input("\n <-> Porto de chegada: ")
        if porto_chegada in Cidades:
            return porto_chegada
        else:
            print("\nA cidade que inseriu não se encontra disponível")

def obter_escala(origem):
    """
    Solicita ao usuário se deseja fazer alguma escala e quais seriam essas escalas.

    Args:
        origem: O porto de origem.

    Returns:
        Uma lista com os nomes das escalas ou None se não houver escalas.
    """
    while True:
        deseja_escala = input("\n <-> Deseja fazer alguma escala obrigatória (s/n)? \tR: ")

        if deseja_escala == "s":
            escala = []
            i = 0
            while True:
                numero_escalas = input("\n <-> Indique quantas escalas deseja realizar: ")
                if numero_escalas.isdigit():
                    while i != int(numero_escalas):
                        while True:
                            cidade = input(f"\nIndique o nome da escala nº{i+1}: ")
                            if len(escala) > 0:
                                if cidade in Cidades:
                                    print("\nEscala encontra-se disponível")
                                    escala.append(cidade)
                                    i += 1
                                    break
                                else:
                                    print("\nEscala não se encontra disponível")
                            else:
                                if cidade != origem:
                                    if cidade in Cidades:
                                        print("\nEscala encontra-se disponível")
                                        escala.append(cidade)
                                        i += 1
                                        break
                                    else:
                                        print("\nEscala não se encontra disponível")
                                else:
                                    print("\nEscala igual ao porto de origem.")
                    break
                else:
                    print("\nResposta inválida, por favor indique um número.")
            return escala
        elif deseja_escala == "n":
            print("\nViagem sem escala")
            return None
        else:
            print("\nResposta inválida!")

def dias():
    """
    Solicita ao usuário o número de dias disponíveis para a viagem até que um número válido seja inserido.

    Returns:
        O número de dias disponíveis.
    """
    while True:
        dias = input("\n <-> Em quantos dias pretende realizar esta viagem: ")
        if dias.isdigit() and int(dias) > 0:
            return int(dias)
        else:
            print("\nResposta inválida, por favor indique um número positivo.")

def tipo_navio(nome_navio):
    """
    Determina o tipo de navio (passageiros ou carga) com base no nome fornecido.

    Args:
        nome_navio: O nome do navio a ser procurado.

    Returns:
        1 se o navio for de passageiros, 2 se for de carga, ou 0 se não encontrado.
    """
    while True:
        tipo_encontrado = procurar_navio(nome_navio)

        if tipo_encontrado == 1:
            print("\nO navio encontrado é de passageiros.")
            return 1
        elif tipo_encontrado == 2:
            print("\nO navio encontrado é de carga.")
            return 2
        else:
            print("\nNavio não encontrado...")
            return 0

def gerar_pdf(caminhos):
    """
    Cria o arquivo PDF e escreve os caminhos no mesmo

    Argumentos:
        caminhos: Os caminhos que foram encontrados entre dois portos.

    """

    ficheiro = canvas.Canvas("orcamento_viagem.pdf", pagesize=letter)
    width, height = letter

    ficheiro.drawString(100, height - 40, "Orçamento de Viagem")
    y_position = height - 80

    for posicao, caminho in enumerate(caminhos, 1):
        ficheiro.drawString(100, y_position, f"Caminho {posicao}:")
        y_position -= 20
        for key, value in caminho.items():
            ficheiro.drawString(120, y_position, f"{key.capitalize()}: {value}")
            y_position -= 20
        y_position -= 10

        if y_position < 40:
            ficheiro.showPage()
            y_position = height - 40

    ficheiro.save()

if __name__ == "__main__":
    # Definição das cidades e seus custos
    Cidades = {
        "Valencia": {"custo": 60.116},
        "Algeciras": {"custo": 83.493},
        "Le Havre": {"custo": 66.104},
        "Botas": {"custo": 70.917},
        "Izmit": {"custo": 72.690},
        "Hamburg": {"custo": 118.761},
        "Amsterdam": {"custo": 98.517},
        "Marseille": {"custo": 75.617},
        "Antwerp": {"custo": 201.202}
    }

    while True:
        # Menu principal
        print()
        print("| ------------------------------------------------------------------------- |")
        print("|                                    MENU                                   |")
        print("| ------------------------------------------------------------------------- |")
        print("| 1 - Planear viagem                                                        |")
        print("| 2 - Operações com rotas                                                   |")
        print("| 3 - Operações com portos                                                  |")
        print("| 4 - Sair                                                                  |")
        print("| ------------------------------------------------------------------------- |")
        opcao = input("| Resposta: ")
        print()

        match int(opcao):
            case 1:
                        origem = porto_origem()
                        escala = obter_escala(origem)

                        if escala is None:
                            
                            while True:
                                chegada = porto_chegada()
                                if chegada != origem:
                                    break
                            print("\nÉ impossível viajar para o mesmo sítio")
                            print("\nIndique outra vez...")
                        
                        else:
                            
                            while True:
                                chegada = porto_chegada()
                                
                                if chegada != escala[-1]:
                                    break
                                print("\nO porto indicado é a sua escala...")

                        while True:
                            dias_disponiveis = dias()
                            
                            if dias_disponiveis > 0:
                                break
                            print("\nIndique um número positivo e inteiro!")

                        while True:
                            nome_navio = input("\n <-> Indique o nome do navio que vai utilizar: ")
                            tipo_navio_encontrado = tipo_navio(nome_navio)
                            
                            if tipo_navio_encontrado != 0:
                                break

                            rotas = []

                        if tipo_navio_encontrado == 1:
                            grafo = criar_grafo_passageiros()

                            if escala is None:
                                caminho = caminhos_todos(grafo, origem, chegada, dias_disponiveis)
                                print("\nCaminhos disponíveis:")
                                
                                for c in caminho:
                                    print(f"\nCaminho: {c['caminho']}, Dias: {c['dias']}, Custo: {c['custo']}")
                        
                            else:
                                caminho = caminhos_todos(grafo, origem, escala[0], dias_disponiveis)
                                
                                for i in range(len(escala) - 1):
                                    caminho.extend(caminhos_todos(grafo, escala[i], escala[i + 1], dias_disponiveis))
                                    caminho.extend(caminhos_todos(grafo, escala[-1], chegada, dias_disponiveis))
                                print("\nCaminhos disponíveis:")
                                
                                for c in caminho:
                                    print(f"\nCaminho: {c['caminho']}, Dias: {c['dias']}, Custo: {c['custo']}")

                        elif tipo_navio_encontrado == 2:
                            grafo = criar_grafo_carga()

                            if escala is None:
                                caminho = caminho_mais_curto(grafo, origem, chegada, dias_disponiveis)
                                print(f"\nCaminho: {caminho['caminho']}, Dias: {caminho['dias']}, Custo: {caminho['custo']}")
                            
                            else:
                                caminho = [caminho_mais_curto(grafo, origem, escala[0], dias_disponiveis)]
                                
                                for i in range(len(escala) - 1):
                                    caminho.append(caminho_mais_curto(grafo, escala[i], escala[i + 1], dias_disponiveis))
                                    caminho.append(caminho_mais_curto(grafo, escala[-1], chegada, dias_disponiveis))
                                print("\nCaminhos disponíveis:")
                                
                                for c in caminho:
                                    if c:  # Verifica se o caminho não está vazio
                                        print(f"\nCaminho: {c['caminho']}, Dias: {c['dias']}, Custo: {c['custo']}")

                        if caminho:
                            
                            while True:
                                guardar_pdf= input("\n <-> Quer guardar as informações em PDF? (s/n)\tR: ")
                                
                                if guardar_pdf == 's' or guardar_pdf == 'n':
                                    break
                                print("\nDigite sim ou não (s/n)!!!")
                            
                            if guardar_pdf == 's':
                                gerar_pdf(caminho)
                                print("\nPDF guardado com sucesso!!!")
                            
                            else:
                                break
                        
                        else:
                            print("\nNão existe caminho, logo não será gerado um PDF...")

            case 2:
                
                while True:
                    print()
                    print("|---------------------|")
                    print("| 1 - Criar rota      |")
                    print("| 2 - Remover rota    |")
                    print("| 3 - Alterar rota    |")
                    print("| 4 - Sair            |")
                    print("|---------------------|")
                    resposta = input("| Resposta: ")

                    match int(resposta):
                        case 1:
                            
                            while True:
                                origem = input("\n <-> Indique o porto origem: ")
                                
                                if origem in Cidades:
                                    break
                                print("\nO porto inserido não existe...")

                            while True:
                                chegada = input("\n <-> Indique o porto chegada: ")
                                
                                if chegada in Cidades:
                                    break
                                print("\nO porto inserido não existe...")
                            print("\n <-- Navio passageiros -->")

                            dias = input(f"\n <-> Quantos dias leva ir de {origem} a {chegada}: ")
                            Rotas_passageiro.append((origem, chegada, dias))
                            print("\n <-- Navio carga -->")

                            dias = input(f"\n <-> Quantos dias leva ir de {origem} a {chegada}: ")
                            Rotas_carga.append((origem, chegada, dias))

                        case 2:
                            origem = input("\n <-> Porto de origem: ")
                            destino = input("\n <-> Porto de destino: ")
                            removido = False

                            while True:
                                rota = input("\n <-> Navios de Passageiros ou Navios de Carga (p/c): ")

                                if rota in ["p", "c"]:
                                    break
                                print("\n <-> Indique uma rota de navios correta: ")

                            if rota == "c":
                                for rota in Rotas_carga:
                                    if rota[0] == origem and rota[1] == destino:
                                        Rotas_carga.remove(rota)
                                        removido = True
                                        print(f"\nRota de {origem} para {destino} removida com sucesso (navios de carga).")
                                        break

                            if rota == "p":
                                for rota in Rotas_passageiro:
                                    if rota[0] == origem and rota[1] == destino:
                                        Rotas_passageiro.remove(rota)
                                        removido = True
                                        print(f"\nRota de {origem} para {destino} removida com sucesso (navios de passageiros).")
                                        break

                            if not removido:
                                print("\nRota não encontrada...")
                                break

                        case 3:
                            while True:
                                origem = input("\n <-> Indique o porto origem: ")
                                if origem in Cidades:
                                    break
                                print("\nO porto inserido não existe...")

                            while True:
                                chegada = input("\n <-> Indique o porto chegada: ")
                                if chegada in Cidades:
                                    break
                                print("\nO porto inserido não existe...")

                            while True:
                                dias = input("\n <-> Insira um novo número de dias para realizarem a rota descrita: ")
                                if dias.isdigit() and int(dias) > 0:
                                    dias = int(dias)
                                    break
                                print("\nIndique um número positivo e inteiro!")

                            encontrado = False

                            while True:
                                rota = input("\n <-> Passageiros ou Carga (p/c): ")
                                if rota in ["p", "c"]:
                                    break
                                print("\n <-> Indique uma rota de navios correta: ")

                            if rota == "c":
                                for rota in Rotas_carga:
                                    if rota[0] == origem and rota[1] == chegada:
                                        Rotas_carga.remove(rota)
                                        Rotas_carga.append((origem, chegada, dias))
                                        encontrado = True
                                        print(f"\nRota de {origem} para {chegada} atualizada com sucesso (carga).")
                                        break

                            if rota == "p":
                                for rota in Rotas_passageiro:
                                    if rota[0] == origem and rota[1] == chegada:
                                        Rotas_passageiro.remove(rota)
                                        Rotas_passageiro.append((origem, chegada, dias))
                                        encontrado = True
                                        print(f"\nRota de {origem} para {chegada} atualizada com sucesso (passageiros).")
                                        break

                        case 4:
                            break

            case 3:
                
                while True:
                    print()
                    print("|---------------------|")
                    print("| 1 - Criar portos    |")
                    print("| 2 - Remover portos  |")
                    print("| 3 - Alterar portos  |")
                    print("| 4 - Sair            |")
                    print("|---------------------|")
                    resposta = input("| Resposta: ")

                    match int(resposta):
                        case 1:
                            porto = input("\n <-> Indique um novo porto: ")
                            if porto in Cidades:
                                print("\nO porto inserido já existe...")
                            else:
                                while True:
                                    preco = float(input("\nIndique o preço que corresponde ao porto inserido anteriormente: "))
                                    if preco > 0:
                                        break
                                    print("\nIndique um preço positivo")

                                Cidades[porto] = {"custo": preco}
                                print("\nPorto adicionado com sucesso!!!")

                        case 2:
                            porto = input("\n <-> Indique o porto a remover: ")
                            if porto not in Cidades:
                                print("\nO porto inserido não existe...")
                            else:
                                del Cidades[porto]
                                print("\nPorto removido com sucesso!!!")

                        case 3:
                            while True:
                                porto = input("\n <-> Indique o porto a alterar: ")
                                if porto in Cidades:
                                    break
                                print("\nIndique um porto existente!")

                            while True:
                                alterar = input("\n <-> O que deseja alterar, nome ou preço (n/p): ")
                                if alterar in ["n", "p"]:
                                    break
                                print("\nIndique uma das duas opções (nome -> n ou preço -> p).")

                            if alterar == "n":
                                novo_nome = input("\n <-> Insira o novo nome do porto: ")
                                Cidades[novo_nome] = Cidades.pop(porto)
                                print("\nNome do porto alterado com sucesso!!!")
                            else:
                                novo_custo = float(input(f"\nNovo custo do porto {porto}: "))
                                Cidades[porto]['custo'] = novo_custo
                                print("\nCusto do porto alterado com sucesso!!!")

                        case 4:
                            break

            case 4:
                print()
                print("\n *_*     Hasta la vista      *_* ")
                print("\n '|'                         '|' ")
                print("\n  |     WE HOPE YOU LIKED     |  ")
                print("\n ´ `            IT           ´ ` ")
                print()
                exit()
